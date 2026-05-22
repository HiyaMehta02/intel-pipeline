"""Storage operation result types."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class StoredArtifact(BaseModel):
    """Reference to a persisted blob."""

    key: str = Field(min_length=1)
    uri: str = Field(min_length=1)
    local_path: Path | None = None
    created: bool = Field(
        default=True,
        description="False when an existing object was returned (idempotent write).",
    )

    model_config = {"extra": "forbid"}
