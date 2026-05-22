"""Ingest stage result types (Step 5 — no persistence)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from pipeline.models import RawDocument


class SourceProcessStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class DedupAction(StrEnum):
    ACCEPT = "accept"
    SKIP = "skip"


class DedupDecision(BaseModel):
    action: DedupAction
    content_hash: str
    reason: str | None = None

    model_config = {"extra": "forbid"}


class SkippedDocument(BaseModel):
    content_hash: str
    title: str
    reason: str

    model_config = {"extra": "forbid"}


class SourceIngestResult(BaseModel):
    """Outcome of processing one configured source."""

    source_id: str
    status: SourceProcessStatus
    accepted: list[RawDocument] = Field(default_factory=list)
    skipped: list[SkippedDocument] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    items_fetched: int = 0

    model_config = {"extra": "forbid"}
