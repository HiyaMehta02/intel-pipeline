"""Source adapters."""

from pipeline.ingest.adapters.base import SourceAdapter
from pipeline.ingest.adapters.fixture import FixtureAdapter
from pipeline.ingest.adapters.registry import adapter_for_source, build_adapter
from pipeline.ingest.adapters.rss import RssAdapter

__all__ = [
    "SourceAdapter",
    "RssAdapter",
    "FixtureAdapter",
    "build_adapter",
    "adapter_for_source",
]
