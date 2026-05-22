"""UTC datetime serialization for SQLite TEXT columns."""

from __future__ import annotations

from datetime import UTC, datetime


def to_iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).isoformat()


def utc_now_iso() -> str:
    return to_iso(datetime.now(UTC))
