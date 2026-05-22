"""Local filesystem storage backend tests."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from pipeline.config.settings import Settings
from pipeline.models import DomainTag, RawDocument
from pipeline.storage import LocalFilesystemBackend, build_local_storage, raw_document_key


def _sample_document(
    *,
    content: str = "Normalized article body.",
    ingested_at: datetime | None = None,
) -> RawDocument:
    return RawDocument.from_normalized(
        source_id="cyber-thehackernews",
        source_name="The Hacker News",
        domain_tag=DomainTag.CYBERSECURITY,
        title="Sample title",
        normalized_text=content,
        canonical_url="https://example.com/post/1",
    )


def test_write_raw_document_creates_expected_path(tmp_path: Path) -> None:
    backend = LocalFilesystemBackend(tmp_path)
    doc = _sample_document()
    artifact = backend.write_raw_document(doc)

    expected_key = raw_document_key(doc.content_hash, doc.ingested_at)
    assert artifact.key == expected_key
    assert artifact.created is True
    assert artifact.local_path is not None
    assert artifact.local_path.is_file()
    assert artifact.uri.startswith("file:")

    loaded = backend.read_raw_document(doc.content_hash)
    assert loaded is not None
    assert loaded.content_hash == doc.content_hash
    assert loaded.title == doc.title


def test_write_raw_document_is_idempotent(tmp_path: Path) -> None:
    backend = LocalFilesystemBackend(tmp_path)
    doc = _sample_document()

    first = backend.write_raw_document(doc)
    second = backend.write_raw_document(doc)

    assert first.created is True
    assert second.created is False
    assert second.key == first.key
    assert len(backend.list_raw_keys()) == 1


def test_raw_document_exists(tmp_path: Path) -> None:
    backend = LocalFilesystemBackend(tmp_path)
    doc = _sample_document()
    assert backend.raw_document_exists(doc.content_hash) is False
    backend.write_raw_document(doc)
    assert backend.raw_document_exists(doc.content_hash) is True


def test_build_local_storage_uses_settings_data_dir(repo_root: Path, tmp_path: Path) -> None:
    settings = Settings(_env_file=None, project_root=repo_root, data_dir=tmp_path)
    backend = build_local_storage(settings.resolved_data_dir())
    doc = _sample_document(content="Factory path test.")
    backend.write_raw_document(doc)
    assert (tmp_path / "raw").is_dir()


def test_read_missing_hash_returns_none(tmp_path: Path) -> None:
    backend = LocalFilesystemBackend(tmp_path)
    assert backend.read_raw_document("a" * 64) is None


def test_same_hash_different_ingest_date_does_not_duplicate_file(tmp_path: Path) -> None:
    """Global content_hash dedup: second write same body, new date → no new file."""
    backend = LocalFilesystemBackend(tmp_path)
    doc = _sample_document(content="Shared hash body.")
    backend.write_raw_document(doc)

    other_day = doc.model_copy(
        update={"ingested_at": datetime(2020, 1, 1, tzinfo=UTC)},
    )
    again = backend.write_raw_document(other_day)
    assert again.created is False
    assert len(backend.list_raw_keys()) == 1
    assert backend.read_raw_document(doc.content_hash) is not None
