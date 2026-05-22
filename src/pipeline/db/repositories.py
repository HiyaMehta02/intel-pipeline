"""Repository layer over SQLAlchemy Core."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from sqlalchemy import select
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError

from pipeline.db import schema
from pipeline.db.timeutil import to_iso, utc_now_iso
from pipeline.models import DomainTag, PipelineRun, RawDocument, RunStatus
from pipeline.storage.artifacts import StoredArtifact


class DuplicateContentHashError(Exception):
    """Raised when inserting a document with an existing content_hash."""


@dataclass(frozen=True)
class IngestEventRecord:
    run_id: str
    source_id: str
    status: str
    documents_ingested: int
    error_message: str | None
    created_at: str


class PipelineRunRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def create(self, run: PipelineRun) -> None:
        self._conn.execute(
            schema.pipeline_runs.insert().values(
                run_id=run.run_id,
                status=run.status.value,
                started_at=to_iso(run.started_at),
                finished_at=to_iso(run.finished_at) if run.finished_at else None,
                stages_json=json.dumps([s.model_dump(mode="json") for s in run.stages]),
                artifact_uris_json=json.dumps(run.artifact_uris),
            ),
        )

    def update_status(
        self,
        run_id: str,
        status: RunStatus,
        *,
        finished_at: str | None = None,
    ) -> None:
        values: dict[str, Any] = {"status": status.value}
        if finished_at is not None:
            values["finished_at"] = finished_at
        self._conn.execute(
            schema.pipeline_runs.update()
            .where(schema.pipeline_runs.c.run_id == run_id)
            .values(**values),
        )

    def get(self, run_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            schema.pipeline_runs.select().where(schema.pipeline_runs.c.run_id == run_id),
        ).mappings().first()
        return dict(row) if row else None


class DocumentRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def insert(
        self,
        document: RawDocument,
        artifact: StoredArtifact | None = None,
    ) -> str:
        """Insert document; return id. Raises DuplicateContentHashError on conflict."""
        doc_id = str(document.id)
        try:
            self._conn.execute(
                schema.documents.insert().values(
                    id=doc_id,
                    content_hash=document.content_hash,
                    source_id=document.source_id,
                    source_name=document.source_name,
                    domain_tag=document.domain_tag.value,
                    title=document.title,
                    normalized_text=document.normalized_text,
                    canonical_url=str(document.canonical_url) if document.canonical_url else None,
                    raw_artifact_key=artifact.key if artifact else None,
                    raw_artifact_uri=artifact.uri if artifact else None,
                    ingested_at=to_iso(document.ingested_at),
                    published_at=to_iso(document.published_at) if document.published_at else None,
                    created_at=utc_now_iso(),
                ),
            )
        except IntegrityError as exc:
            raise DuplicateContentHashError(document.content_hash) from exc
        return doc_id

    def exists_by_hash(self, content_hash: str) -> bool:
        row = self._conn.execute(
            select(schema.documents.c.id).where(
                schema.documents.c.content_hash == content_hash,
            ),
        ).first()
        return row is not None

    def get_by_hash(self, content_hash: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            schema.documents.select().where(schema.documents.c.content_hash == content_hash),
        ).mappings().first()
        return dict(row) if row else None

    def count(self) -> int:
        row = self._conn.execute(
            select(schema.documents.c.id),
        ).all()
        return len(row)


class IngestEventRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def record(
        self,
        *,
        run_id: str,
        source_id: str,
        status: str,
        documents_ingested: int = 0,
        error_message: str | None = None,
    ) -> None:
        self._conn.execute(
            schema.ingest_events.insert().values(
                run_id=run_id,
                source_id=source_id,
                status=status,
                documents_ingested=documents_ingested,
                error_message=error_message,
                created_at=utc_now_iso(),
            ),
        )

    def list_for_run(self, run_id: str) -> list[IngestEventRecord]:
        rows = self._conn.execute(
            schema.ingest_events.select()
            .where(schema.ingest_events.c.run_id == run_id)
            .order_by(schema.ingest_events.c.id),
        ).mappings().all()
        return [
            IngestEventRecord(
                run_id=row["run_id"],
                source_id=row["source_id"],
                status=row["status"],
                documents_ingested=row["documents_ingested"],
                error_message=row["error_message"],
                created_at=row["created_at"],
            )
            for row in rows
        ]


def init_database(engine: Any) -> None:
    """Apply migrations (module-level helper for CLI/tests)."""
    from pipeline.db.migrate import apply_migrations

    apply_migrations(engine)
