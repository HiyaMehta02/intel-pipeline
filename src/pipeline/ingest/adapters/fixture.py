"""Fixture-based RSS adapter for CI (no network)."""

from __future__ import annotations

from pathlib import Path

import feedparser

from pipeline.ingest.adapters.base import SourceAdapter
from pipeline.ingest.adapters.rss import entries_to_raw_items
from pipeline.models import RawItem, SourceConfig


class FixtureAdapter(SourceAdapter):
    """Load RSS XML from tests/fixtures/feeds/{source_id}.xml."""

    def __init__(self, fixtures_dir: Path) -> None:
        self._fixtures_dir = fixtures_dir.resolve()

    def fetch(self, source: SourceConfig) -> list[RawItem]:
        fixture_path = self._fixtures_dir / f"{source.id}.xml"
        if not fixture_path.is_file():
            msg = f"Fixture feed not found for source {source.id}: {fixture_path}"
            raise FileNotFoundError(msg)

        parsed = feedparser.parse(fixture_path.read_text(encoding="utf-8"))
        return entries_to_raw_items(
            source,
            list(parsed.entries),
            _null_client(),
            fetch_linked_pages=False,
        )


def _null_client() -> object:
    """Placeholder client; fixture mode never follows links."""

    class _Null:
        def get(self, *_args: object, **_kwargs: object) -> None:
            raise RuntimeError("FixtureAdapter must not perform HTTP GET")

    return _Null()
