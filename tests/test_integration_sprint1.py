"""Sprint 1 end-to-end integration tests (blueprint Tests 1.1–1.5)."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import pytest
from typer.testing import CliRunner

from pipeline.cli.main import app
from pipeline.config.settings import get_settings
from pipeline.db import create_db_engine, apply_migrations
from pipeline.db.repositories import DocumentRepository, IngestEventRepository, PipelineRunRepository
from pipeline.ingest.runner import IngestRunner
from pipeline.models import RawDocument


@pytest.fixture
def isolated_env(repo_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "pipeline.db"
    data_dir = tmp_path / "data"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.chdir(repo_root)
    get_settings.cache_clear()
    yield repo_root, tmp_path, data_dir, db_path
    get_settings.cache_clear()


def test_integration_ingest_runner_persists_all_layers(isolated_env) -> None:
    repo_root, _tmp, data_dir, db_path = isolated_env
    run_id = str(uuid4())
    settings = get_settings()

    summary = IngestRunner(settings).run(
        run_id,
        sources_path=repo_root / "configs" / "sources.yaml",
        use_fixtures=True,
    )

    assert summary.status.value in ("completed", "completed_with_errors")
    assert summary.documents_accepted == 3
    assert len(list((data_dir / "raw").rglob("*.json"))) == 3

    engine = create_db_engine(f"sqlite:///{db_path.as_posix()}")
    apply_migrations(engine)
    with engine.connect() as conn:
        assert DocumentRepository(conn).count() == 3
        run_row = PipelineRunRepository(conn).get(run_id)
        assert run_row is not None
        events = IngestEventRepository(conn).list_for_run(run_id)
        assert len(events) == 3
    engine.dispose()


def test_integration_idempotent_reingest(isolated_env) -> None:
    repo_root, _tmp, data_dir, db_path = isolated_env
    settings = get_settings()
    kwargs = {
        "sources_path": repo_root / "configs" / "sources.yaml",
        "use_fixtures": True,
    }

    first = IngestRunner(settings).run(str(uuid4()), **kwargs)
    raw_count_after_first = len(list((data_dir / "raw").rglob("*.json")))

    second = IngestRunner(settings).run(str(uuid4()), **kwargs)
    raw_count_after_second = len(list((data_dir / "raw").rglob("*.json")))

    assert first.documents_accepted == 3
    assert second.documents_skipped == 3
    assert second.documents_accepted == 0
    assert raw_count_after_first == raw_count_after_second == 3

    engine = create_db_engine(f"sqlite:///{db_path.as_posix()}")
    with engine.connect() as conn:
        assert DocumentRepository(conn).count() == 3
    engine.dispose()


def test_integration_raw_json_matches_raw_document_schema(isolated_env) -> None:
    repo_root, _tmp, data_dir, _db = isolated_env
    IngestRunner(get_settings()).run(
        str(uuid4()),
        sources_path=repo_root / "configs" / "sources.yaml",
        use_fixtures=True,
    )
    raw_files = list((data_dir / "raw").rglob("*.json"))
    assert len(raw_files) == 3

    valid = 0
    for path in raw_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        RawDocument.model_validate(data)
        valid += 1
    assert valid >= 1


def test_integration_failure_isolation_partial_sources(
    isolated_env,
    tmp_path: Path,
) -> None:
    repo_root, _tmp, data_dir, db_path = isolated_env
    bad_sources = tmp_path / "sources_mixed.yaml"
    bad_sources.write_text(
        (repo_root / "configs" / "sources.yaml").read_text(encoding="utf-8")
        + """
  - id: bad-source
    name: Bad
    type: rss
    url: http://127.0.0.1:59999/feed.xml
    domain_tag: AI
    enabled: true
""",
        encoding="utf-8",
    )

    summary = IngestRunner(get_settings()).run(
        str(uuid4()),
        sources_path=bad_sources,
        use_fixtures=True,
    )

    assert summary.sources_failed >= 1
    assert summary.documents_accepted >= 3
    assert len(list((data_dir / "raw").rglob("*.json"))) >= 3

    engine = create_db_engine(f"sqlite:///{db_path.as_posix()}")
    with engine.connect() as conn:
        events = IngestEventRepository(conn).list_for_run(summary.run_id)
        statuses = {e.source_id: e.status for e in events}
        assert statuses.get("bad-source") == "failed"
    engine.dispose()


def test_integration_cli_matches_runner(isolated_env) -> None:
    repo_root, _tmp, data_dir, db_path = isolated_env
    run_id = str(uuid4())
    result = CliRunner().invoke(
        app,
        [
            "ingest",
            "--sources",
            str(repo_root / "configs" / "sources.yaml"),
            "--run-id",
            run_id,
            "--fixtures",
        ],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    assert len(list((data_dir / "raw").rglob("*.json"))) == 3

    engine = create_db_engine(f"sqlite:///{db_path.as_posix()}")
    with engine.connect() as conn:
        assert PipelineRunRepository(conn).get(run_id) is not None
    engine.dispose()
