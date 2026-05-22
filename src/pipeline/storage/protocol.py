"""Storage backend interface."""

from __future__ import annotations

from typing import Protocol

from pipeline.models import RawDocument
from pipeline.storage.artifacts import StoredArtifact


class StorageBackend(Protocol):
    """Blob store for pipeline artifacts (local FS now; S3 in Sprint 4)."""

    def write_raw_document(self, document: RawDocument) -> StoredArtifact:
        """Persist raw JSON; return artifact metadata (skip if already stored)."""
        ...

    def raw_document_exists(self, content_hash: str) -> bool:
        """True if any raw/{date}/{hash}.json exists for this hash."""
        ...

    def read_raw_document(self, content_hash: str) -> RawDocument | None:
        """Load document by content hash, searching date prefixes."""
        ...
