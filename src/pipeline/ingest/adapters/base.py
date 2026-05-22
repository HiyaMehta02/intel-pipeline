"""Source adapter contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pipeline.models import RawItem, SourceConfig


class SourceAdapter(ABC):
    """Fetch raw items from a configured source."""

    @abstractmethod
    def fetch(self, source: SourceConfig) -> list[RawItem]:
        """Return zero or more items; raise on unrecoverable fetch failure."""
        ...
