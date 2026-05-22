"""Pipeline run tracking models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from pipeline.models.enums import RunStatus, StageName


def _utc_now() -> datetime:
    return datetime.now(UTC)


class StageResult(BaseModel):
    """Outcome of a single stage within a run."""

    stage: StageName
    status: RunStatus
    started_at: datetime = Field(default_factory=_utc_now)
    finished_at: datetime | None = None
    error_message: str | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "forbid"}


class PipelineRun(BaseModel):
    """Top-level ingest/eval/synth run."""

    run_id: str = Field(default_factory=lambda: str(uuid4()))
    status: RunStatus = RunStatus.PENDING
    started_at: datetime = Field(default_factory=_utc_now)
    finished_at: datetime | None = None
    stages: list[StageResult] = Field(default_factory=list)
    artifact_uris: dict[str, str] = Field(default_factory=dict)

    model_config = {"extra": "forbid"}

    @field_validator("run_id")
    @classmethod
    def validate_run_id_uuid(cls, value: str) -> str:
        UUID(value)
        return value
