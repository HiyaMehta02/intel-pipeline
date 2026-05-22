"""Exact content_hash deduplication (ADR-002)."""

from __future__ import annotations

from pipeline.db.repositories import DocumentRepository
from pipeline.ingest.results import DedupAction, DedupDecision
from pipeline.storage.protocol import StorageBackend


class DedupService:
    """
    Check duplicates via in-run memory, storage, and/or DB.

    Sprint 1: exact SHA-256 only (no SimHash).
    """

    def __init__(
        self,
        *,
        storage: StorageBackend | None = None,
        document_repo: DocumentRepository | None = None,
        run_seen_hashes: set[str] | None = None,
    ) -> None:
        self._storage = storage
        self._document_repo = document_repo
        self._run_seen = run_seen_hashes if run_seen_hashes is not None else set()

    def evaluate(self, content_hash: str) -> DedupDecision:
        if content_hash in self._run_seen:
            return DedupDecision(
                action=DedupAction.SKIP,
                content_hash=content_hash,
                reason="duplicate_in_run",
            )
        if self._storage is not None and self._storage.raw_document_exists(content_hash):
            return DedupDecision(
                action=DedupAction.SKIP,
                content_hash=content_hash,
                reason="duplicate_in_storage",
            )
        if self._document_repo is not None and self._document_repo.exists_by_hash(content_hash):
            return DedupDecision(
                action=DedupAction.SKIP,
                content_hash=content_hash,
                reason="duplicate_in_database",
            )
        return DedupDecision(action=DedupAction.ACCEPT, content_hash=content_hash)

    def register_accepted(self, content_hash: str) -> None:
        self._run_seen.add(content_hash)
