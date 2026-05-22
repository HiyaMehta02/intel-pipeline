"""Source registry models."""

from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl, field_validator

from pipeline.models.enums import DomainTag, SourceType


class SourceConfig(BaseModel):
    """Single configured intelligence source."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    type: SourceType
    url: HttpUrl
    domain_tag: DomainTag
    enabled: bool = True

    model_config = {"extra": "forbid"}


class SourceRegistry(BaseModel):
    """Parsed configs/sources.yaml."""

    version: int = Field(ge=1)
    sources: list[SourceConfig] = Field(min_length=1)

    model_config = {"extra": "forbid"}

    @field_validator("sources")
    @classmethod
    def unique_source_ids(cls, sources: list[SourceConfig]) -> list[SourceConfig]:
        ids = [s.id for s in sources]
        if len(ids) != len(set(ids)):
            raise ValueError("source ids must be unique within the registry")
        return sources

    def enabled_sources(self) -> list[SourceConfig]:
        return [s for s in self.sources if s.enabled]
