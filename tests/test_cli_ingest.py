"""CLI ingest end-to-end tests (fixture mode)."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from typer.testing import CliRunner

from pipeline.cli.main import app
from pipeline.config.settings import get_settings
from pipeline.db import create_db_engine, apply_migrations
from pipeline.db.repositories import DocumentRepository, PipelineRunRepository


def test_cli_ingest_fixtures(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "pipeline.db"
    data_dir = tmp_path / "data"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.chdir(repo_root)

    get_settings.cache_clear()
    runner = CliRunner()
    run_id = str(uuid4())
    result = runner.invoke(
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
    assert "accepted=3" in result.stdout or "accepted=" in result.stdout

    engine = create_db_engine(f"sqlite:///{db_path.as_posix()}")
    apply_migrations(engine)
    with engine.connect() as conn:
        run_row = PipelineRunRepository(conn).get(run_id)
        assert run_row is not None
        assert run_row["status"] in ("completed", "completed_with_errors")
        assert DocumentRepository(conn).count() == 3

    raw_files = list((data_dir / "raw").rglob("*.json"))
    assert len(raw_files) == 3
    engine.dispose()
    get_settings.cache_clear()


def test_cli_ingest_idempotent_skips(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "pipeline.db"
    data_dir = tmp_path / "data"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.chdir(repo_root)
    get_settings.cache_clear()

    runner = CliRunner()
    args = [
        "ingest",
        "--sources",
        str(repo_root / "configs" / "sources.yaml"),
        "--fixtures",
    ]
    assert runner.invoke(app, [*args, "--run-id", str(uuid4())]).exit_code == 0
    second = runner.invoke(app, [*args, "--run-id", str(uuid4())])
    assert second.exit_code == 0
    assert "skipped=" in second.stdout

    engine = create_db_engine(f"sqlite:///{db_path.as_posix()}")
    with engine.connect() as conn:
        assert DocumentRepository(conn).count() == 3
    engine.dispose()
    get_settings.cache_clear()
