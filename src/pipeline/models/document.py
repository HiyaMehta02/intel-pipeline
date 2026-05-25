"""Document models for ingest and persistence."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, field_validator

from pipeline.models.enums import DomainTag
from pipeline.models.hashing import CONTENT_HASH_HEX_LENGTH, compute_content_hash


def _utc_now() -> datetime:
    return datetime.now(UTC)


class RawItem(BaseModel):
    """Pre-normalization item from a source adapter."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    domain_tag: DomainTag
    title: str = Field(min_length=1)
    summary: str | None = None
    body_html: str | None = None
    body_text: str | None = None
    canonical_url: HttpUrl | str | None = None
    published_at: datetime | None = None
    fetched_at: datetime = Field(default_factory=_utc_now)

    model_config = {"extra": "forbid"}


class RawDocument(BaseModel):
    """Normalized, persisted document (JSON artifact + DB row)."""

    id: UUID = Field(default_factory=uuid4)
    content_hash: str = Field(
        min_length=CONTENT_HASH_HEX_LENGTH,
        max_length=CONTENT_HASH_HEX_LENGTH,
    )
    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    domain_tag: DomainTag
    title: str = Field(min_length=1)
    normalized_text: str = Field(min_length=1)
    canonical_url: HttpUrl | None = None
    raw_html: str | None = None
    published_at: datetime | None = None
    ingested_at: datetime = Field(default_factory=_utc_now)

    model_config = {"extra": "forbid"}

    @field_validator("content_hash")
    @classmethod
    def validate_content_hash_hex(cls, value: str) -> str:
        if len(value) != CONTENT_HASH_HEX_LENGTH:
            msg = f"content_hash must be {CONTENT_HASH_HEX_LENGTH} hex characters"
            raise ValueError(msg)
        try:
            int(value, 16)
        except ValueError as exc:
            raise ValueError("content_hash must be hexadecimal") from exc
        return value.lower()

    @classmethod
    def from_normalized(
        cls,
        *,
        source_id: str,
        source_name: str,
        domain_tag: DomainTag,
        title: str,
        normalized_text: str,
        canonical_url: HttpUrl | str | None = None,
        raw_html: str | None = None,
        published_at: datetime | None = None,
        document_id: UUID | None = None,
    ) -> RawDocument:
        """Build a document with computed content_hash."""
        url: str | HttpUrl | None = None
        if canonical_url not in (None, ""):
            url = canonical_url

        return cls(
            id=document_id or uuid4(),
            content_hash=compute_content_hash(normalized_text),
            source_id=source_id,
            source_name=source_name,
            domain_tag=domain_tag,
            title=title,
            normalized_text=normalized_text,
            canonical_url=url,
            raw_html=raw_html,
            published_at=published_at,
        )

    def model_dump_json_artifact(self, **kwargs: Any) -> str:
        """JSON suitable for on-disk raw store (Sprint 1 Step 3+)."""
        return self.model_dump_json(**kwargs)
