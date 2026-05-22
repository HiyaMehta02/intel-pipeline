"""Database migrations and repository tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import inspect

from pipeline.config.settings import Settings
from pipeline.db import (
    DocumentRepository,
    DuplicateContentHashError,
    IngestEventRepository,
    PipelineRunRepository,
    apply_migrations,
    create_db_engine,
)
from pipeline.models import DomainTag, PipelineRun, RawDocument, RunStatus
from pipeline.storage import LocalFilesystemBackend


@pytest.fixture
def db_engine(tmp_path: Path):
    db_path = tmp_path / "test.db"
    url = f"sqlite:///{db_path.as_posix()}"
    engine = create_db_engine(url)
    apply_migrations(engine)
    yield engine
    engine.dispose()


def test_migrations_create_tables(db_engine) -> None:
    tables = set(inspect(db_engine).get_table_names())
    assert tables >= {"pipeline_runs", "documents", "ingest_events"}


def test_pipeline_run_repository(db_engine) -> None:
    run = PipelineRun(run_id="550e8400-e29b-41d4-a716-446655440000", status=RunStatus.RUNNING)
    with db_engine.begin() as conn:
        runs = PipelineRunRepository(conn)
        runs.create(run)
        row = runs.get(run.run_id)
        assert row is not None
        assert row["status"] == RunStatus.RUNNING.value
        runs.update_status(run.run_id, RunStatus.COMPLETED, finished_at="2026-05-21T12:00:00+00:00")
        updated = runs.get(run.run_id)
        assert updated is not None
        assert updated["status"] == RunStatus.COMPLETED.value


def test_document_repository_unique_hash(db_engine) -> None:
    doc = RawDocument.from_normalized(
        source_id="cyber-thehackernews",
        source_name="The Hacker News",
        domain_tag=DomainTag.CYBERSECURITY,
        title="Title",
        normalized_text="Unique body for db test.",
    )
    with db_engine.begin() as conn:
        docs = DocumentRepository(conn)
        doc_id = docs.insert(doc)
        assert doc_id == str(doc.id)
        assert docs.exists_by_hash(doc.content_hash)
        with pytest.raises(DuplicateContentHashError):
            docs.insert(doc)


def test_document_repository_with_artifact(db_engine, tmp_path: Path) -> None:
    storage = LocalFilesystemBackend(tmp_path)
    doc = RawDocument.from_normalized(
        source_id="tech-hackernews",
        source_name="Hacker News",
        domain_tag=DomainTag.AI,
        title="HN",
        normalized_text="Artifact linkage test.",
    )
    artifact = storage.write_raw_document(doc)
    with db_engine.begin() as conn:
        docs = DocumentRepository(conn)
        docs.insert(doc, artifact=artifact)
        row = docs.get_by_hash(doc.content_hash)
        assert row is not None
        assert row["raw_artifact_key"] == artifact.key
        assert row["raw_artifact_uri"] == artifact.uri


def test_ingest_event_repository(db_engine) -> None:
    run_id = "550e8400-e29b-41d4-a716-446655440001"
    with db_engine.begin() as conn:
        PipelineRunRepository(conn).create(
            PipelineRun(run_id=run_id, status=RunStatus.RUNNING),
        )
        events = IngestEventRepository(conn)
        events.record(
            run_id=run_id,
            source_id="cyber-thehackernews",
            status="success",
            documents_ingested=3,
        )
        events.record(
            run_id=run_id,
            source_id="bad-source",
            status="failed",
            documents_ingested=0,
            error_message="connection refused",
        )
        listed = events.list_for_run(run_id)
    assert len(listed) == 2
    assert listed[0].status == "success"
    assert listed[1].error_message == "connection refused"


def test_engine_from_settings_uses_resolved_path(repo_root: Path, tmp_path: Path) -> None:
    settings = Settings(
        _env_file=None,
        project_root=repo_root,
        database_url=f"sqlite:///{(tmp_path / 'pipeline.db').as_posix()}",
    )
    from pipeline.db.session import engine_from_settings

    engine = engine_from_settings(settings)
    assert (tmp_path / "pipeline.db").is_file()
    engine.dispose()
