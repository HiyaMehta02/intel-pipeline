"""Resolve SourceConfig to concrete adapters."""

from __future__ import annotations

from pipeline.config.settings import Settings
from pipeline.ingest.adapters.base import SourceAdapter
from pipeline.ingest.adapters.fixture import FixtureAdapter
from pipeline.ingest.adapters.rss import RssAdapter
from pipeline.models.enums import SourceType


def build_adapter(
    source_type: SourceType,
    *,
    settings: Settings,
    use_fixtures: bool = False,
) -> SourceAdapter:
    if use_fixtures:
        if source_type != SourceType.RSS:
            msg = f"Fixture mode only supports RSS sources, got {source_type}"
            raise ValueError(msg)
        return FixtureAdapter(
            settings.resolved_ingest_fixtures_dir(),
            fetch_linked_pages=False,
        )

    if source_type == SourceType.RSS:
        return RssAdapter(
            timeout=settings.ingest_http_timeout,
            fetch_linked_pages=settings.ingest_fetch_linked_pages,
        )

    msg = f"Unsupported source type for Sprint 1: {source_type}"
    raise ValueError(msg)


def adapter_for_source(
    source: object,
    *,
    settings: Settings,
    use_fixtures: bool = False,
) -> SourceAdapter:
    from pipeline.models import SourceConfig

    if not isinstance(source, SourceConfig):
        raise TypeError("source must be SourceConfig")
    return build_adapter(source.type, settings=settings, use_fixtures=use_fixtures)
