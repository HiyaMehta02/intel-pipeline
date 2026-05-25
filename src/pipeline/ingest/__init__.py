"""Ingestion: adapters, normalization, deduplication."""

from pipeline.ingest.dedup import DedupService
from pipeline.ingest.normalize import NormalizationError, extract_text, normalize_item
from pipeline.ingest.processor import IngestProcessor
from pipeline.ingest.runner import IngestRunner, IngestRunSummary
from pipeline.ingest.results import (
    DedupAction,
    DedupDecision,
    SkippedDocument,
    SourceIngestResult,
    SourceProcessStatus,
)

__all__ = [
    "DedupService",
    "DedupAction",
    "DedupDecision",
    "IngestProcessor",
    "IngestRunner",
    "IngestRunSummary",
    "NormalizationError",
    "SkippedDocument",
    "SourceIngestResult",
    "SourceProcessStatus",
    "extract_text",
    "normalize_item",
]
