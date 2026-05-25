"""Persisted ingest run: storage + database + processor."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import structlog

from pipeline.config.settings import Settings, get_settings
from pipeline.config.sources import load_sources_yaml
from pipeline.db.repositories import (
    DocumentRepository,
    DuplicateContentHashError,
    IngestEventRepository,
    PipelineRunRepository,
)
from pipeline.db.session import db_connection
from pipeline.db.timeutil import to_iso
from pipeline.ingest.dedup import DedupService
from pipeline.ingest.processor import IngestProcessor
from pipeline.ingest.results import SkippedDocument, SourceIngestResult, SourceProcessStatus
from pipeline.models import PipelineRun, RawDocument, RunStatus, StageName, StageResult
from pipeline.models.source import SourceConfig
from pipeline.storage import LocalFilesystemBackend, build_local_storage

logger = structlog.get_logger(__name__)


@dataclass
class IngestRunSummary:
    run_id: str
    status: RunStatus
    sources_processed: int = 0
    documents_accepted: int = 0
    documents_skipped: int = 0
    sources_failed: int = 0
    source_results: list[SourceIngestResult] = field(default_factory=list)


class IngestRunner:
    """Execute a full ingest run with persistence."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def run(
        self,
        run_id: str,
        *,
        sources_path: Path | None = None,
        use_fixtures: bool = False,
        source_ids: list[str] | None = None,
        max_items_per_source: int | None = None,
    ) -> IngestRunSummary:
        UUID(run_id)
        path = sources_path or self._settings.resolved_sources_path()
        registry = load_sources_yaml(path)
        sources = registry.enabled_sources()
        if source_ids:
            allowed = set(source_ids)
            sources = [s for s in sources if s.id in allowed]

        storage = build_local_storage(self._settings.resolved_data_dir())
        summary = IngestRunSummary(run_id=run_id, status=RunStatus.RUNNING)

        run = PipelineRun(run_id=run_id, status=RunStatus.RUNNING)
        run.stages.append(
            StageResult(stage=StageName.INGEST, status=RunStatus.RUNNING),
        )

        with db_connection(self._settings) as conn:
            runs_repo = PipelineRunRepository(conn)
            docs_repo = DocumentRepository(conn)
            events_repo = IngestEventRepository(conn)
            runs_repo.create(run)

            dedup = DedupService(storage=storage, document_repo=docs_repo)
            processor = IngestProcessor(
                self._settings,
                dedup,
                use_fixtures=use_fixtures,
            )

            for source in sources:
                result = self._process_and_persist(
                    run_id,
                    processor,
                    source,
                    storage,
                    docs_repo,
                    events_repo,
                    max_items_per_source=max_items_per_source,
                )
                summary.source_results.append(result)
                summary.sources_processed += 1
                summary.documents_accepted += len(result.accepted)
                summary.documents_skipped += len(result.skipped)
                if result.status == SourceProcessStatus.FAILED:
                    summary.sources_failed += 1

            summary.status = _aggregate_run_status(summary)
            runs_repo.update_status(
                run_id,
                summary.status,
                finished_at=to_iso(datetime.now(UTC)),
            )

        logger.info(
            "ingest_run_finished",
            run_id=run_id,
            status=summary.status.value,
            accepted=summary.documents_accepted,
            skipped=summary.documents_skipped,
            sources_failed=summary.sources_failed,
        )
        return summary

    def _process_and_persist(
        self,
        run_id: str,
        processor: IngestProcessor,
        source: SourceConfig,
        storage: LocalFilesystemBackend,
        docs_repo: DocumentRepository,
        events_repo: IngestEventRepository,
        *,
        max_items_per_source: int | None,
    ) -> SourceIngestResult:
        if max_items_per_source is not None:
            result = processor.process_source(source, max_items=max_items_per_source)
        else:
            result = processor.process_source(source)

        persisted: list[RawDocument] = []
        for document in list(result.accepted):
            artifact = storage.write_raw_document(document)
            try:
                docs_repo.insert(document, artifact=artifact)
                persisted.append(document)
                logger.info(
                    "document_persisted",
                    run_id=run_id,
                    source_id=source.id,
                    content_hash=document.content_hash,
                    artifact_key=artifact.key,
                    created=artifact.created,
                )
            except DuplicateContentHashError:
                result.skipped.append(
                    SkippedDocument(
                        content_hash=document.content_hash,
                        title=document.title,
                        reason="duplicate_on_insert",
                    ),
                )

        result.accepted = persisted

        events_repo.record(
            run_id=run_id,
            source_id=source.id,
            status=_event_status_for_source(result),
            documents_ingested=len(persisted),
            error_message="; ".join(result.errors) if result.errors else None,
        )

        logger.info(
            "source_ingest_complete",
            run_id=run_id,
            source_id=source.id,
            status=result.status.value,
            accepted=len(persisted),
            skipped=len(result.skipped),
            fetched=result.items_fetched,
        )
        return result


def _aggregate_run_status(summary: IngestRunSummary) -> RunStatus:
    if summary.sources_processed == 0:
        return RunStatus.FAILED
    if summary.sources_failed == summary.sources_processed:
        return RunStatus.FAILED
    if summary.sources_failed > 0 or any(
        r.status == SourceProcessStatus.PARTIAL for r in summary.source_results
    ):
        return RunStatus.COMPLETED_WITH_ERRORS
    return RunStatus.COMPLETED


def _event_status_for_source(result: SourceIngestResult) -> str:
    if result.status == SourceProcessStatus.FAILED:
        return "failed"
    if result.status == SourceProcessStatus.PARTIAL:
        return "partial"
    return "success"
