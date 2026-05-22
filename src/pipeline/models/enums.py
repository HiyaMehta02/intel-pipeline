"""Domain enumerations for pipeline contracts."""

from __future__ import annotations

from enum import StrEnum


class DomainTag(StrEnum):
    """Intelligence domain lane for filtering and briefing segmentation."""

    AI = "AI"
    DATA_SCIENCE = "DataScience"
    CYBERSECURITY = "Cybersecurity"


class SourceType(StrEnum):
    """Ingestion adapter type (Sprint 1: rss + fixture; rest in later steps)."""

    RSS = "rss"
    FIXTURE = "fixture"
    REST = "rest"


class RunStatus(StrEnum):
    """Pipeline run lifecycle status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"


class StageName(StrEnum):
    """Named pipeline stages."""

    INGEST = "ingest"
    EVALUATE = "evaluate"
    CURATE = "curate"
    SYNTHESIZE = "synthesize"
    TTS = "tts"
