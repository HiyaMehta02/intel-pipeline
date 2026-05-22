"""Object key conventions (ADR-001); shared by local and S3 backends."""

from __future__ import annotations

from datetime import datetime


def format_date_prefix(when: datetime) -> str:
    """UTC date folder segment: yyyy-mm-dd."""
    return when.strftime("%Y-%m-%d")


def raw_document_key(content_hash: str, ingested_at: datetime) -> str:
    """
    Storage key for a raw document artifact.

    Layout: raw/{yyyy-mm-dd}/{content_hash}.json
    """
    return f"raw/{format_date_prefix(ingested_at)}/{content_hash}.json"
