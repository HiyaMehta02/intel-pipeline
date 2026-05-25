"""Ingest processing orchestration (fetch → normalize → dedup)."""

from __future__ import annotations

import logging

from pipeline.config.settings import Settings
from pipeline.ingest.adapters.registry import adapter_for_source
from pipeline.ingest.dedup import DedupService
from pipeline.ingest.normalize import NormalizationError, normalize_item
from pipeline.ingest.results import (
    DedupAction,
    SkippedDocument,
    SourceIngestResult,
    SourceProcessStatus,
)
from pipeline.models import SourceConfig

logger = logging.getLogger(__name__)


class IngestProcessor:
    """Fetch, normalize, and deduplicate items from a source (persistence in IngestRunner)."""

    def __init__(
        self,
        settings: Settings,
        dedup: DedupService,
        *,
        use_fixtures: bool = False,
    ) -> None:
        self._settings = settings
        self._dedup = dedup
        self._use_fixtures = use_fixtures

    def process_source(self, source: SourceConfig, *, max_items: int | None = None) -> SourceIngestResult:
        result = SourceIngestResult(source_id=source.id, status=SourceProcessStatus.SUCCESS)
        adapter = adapter_for_source(
            source,
            settings=self._settings,
            use_fixtures=self._use_fixtures,
        )

        try:
            raw_items = adapter.fetch(source)
            if max_items is not None:
                raw_items = raw_items[:max_items]
            result.items_fetched = len(raw_items)
        except Exception as exc:
            logger.exception("Source fetch failed", extra={"source_id": source.id})
            result.status = SourceProcessStatus.FAILED
            result.errors.append(str(exc))
            return result

        close = getattr(adapter, "close", None)
        if callable(close):
            close()

        for item in raw_items:
            try:
                document = normalize_item(
                    item,
                    max_chars=self._settings.max_normalized_chars,
                )
            except NormalizationError as exc:
                result.errors.append(f"{item.title}: {exc}")
                continue

            decision = self._dedup.evaluate(document.content_hash)
            if decision.action == DedupAction.SKIP:
                result.skipped.append(
                    SkippedDocument(
                        content_hash=document.content_hash,
                        title=document.title,
                        reason=decision.reason or "duplicate",
                    ),
                )
                continue

            self._dedup.register_accepted(document.content_hash)
            result.accepted.append(document)

        if result.errors and result.accepted:
            result.status = SourceProcessStatus.PARTIAL
        elif result.errors and not result.accepted:
            result.status = SourceProcessStatus.FAILED
        elif not result.accepted and not result.errors and result.items_fetched == 0:
            result.status = SourceProcessStatus.SUCCESS

        return result

    def process_sources(self, sources: list[SourceConfig]) -> list[SourceIngestResult]:
        """Process each source independently (failure isolation)."""
        return [self.process_source(source) for source in sources]
