"""Dedup service tests."""

from __future__ import annotations

from pathlib import Path

from pipeline.db import DocumentRepository, apply_migrations, create_db_engine
from pipeline.ingest.dedup import DedupService
from pipeline.ingest.normalize import normalize_item
from pipeline.ingest.results import DedupAction
from pipeline.models import DomainTag, RawItem
from pipeline.storage import LocalFilesystemBackend


def test_dedup_skip_in_run_memory() -> None:
    dedup = DedupService()
    doc = normalize_item(
        RawItem(
            source_id="a",
            source_name="A",
            domain_tag=DomainTag.AI,
            title="Title",
            summary="Enough text here for normalization to succeed cleanly.",
        ),
    )
    assert dedup.evaluate(doc.content_hash).action == DedupAction.ACCEPT
    dedup.register_accepted(doc.content_hash)
    assert dedup.evaluate(doc.content_hash).action == DedupAction.SKIP


def test_dedup_skip_when_in_storage(tmp_path: Path) -> None:
    storage = LocalFilesystemBackend(tmp_path)
    doc = normalize_item(
        RawItem(
            source_id="b",
            source_name="B",
            domain_tag=DomainTag.CYBERSECURITY,
            title="Cyber",
            summary="Another body of text long enough for the normalizer threshold.",
        ),
    )
    storage.write_raw_document(doc)
    dedup = DedupService(storage=storage)
    assert dedup.evaluate(doc.content_hash).action == DedupAction.SKIP


def test_dedup_skip_when_in_database(tmp_path: Path) -> None:
    engine = create_db_engine(f"sqlite:///{tmp_path / 'd.db'}")
    apply_migrations(engine)
    doc = normalize_item(
        RawItem(
            source_id="c",
            source_name="C",
            domain_tag=DomainTag.DATA_SCIENCE,
            title="DS",
            summary="Data science article text with sufficient length for hashing.",
        ),
    )
    with engine.begin() as conn:
        DocumentRepository(conn).insert(doc)
    with engine.connect() as conn:
        dedup = DedupService(document_repo=DocumentRepository(conn))
        assert dedup.evaluate(doc.content_hash).action == DedupAction.SKIP
    engine.dispose()
