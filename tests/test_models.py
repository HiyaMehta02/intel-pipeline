"""Domain model validation tests."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from pipeline.models import (
    DomainTag,
    PipelineRun,
    RawDocument,
    RawItem,
    RunStatus,
    SourceConfig,
    SourceRegistry,
    SourceType,
    StageName,
    StageResult,
    compute_content_hash,
)


def test_raw_document_from_normalized_computes_hash() -> None:
    doc = RawDocument.from_normalized(
        source_id="cyber-thehackernews",
        source_name="The Hacker News",
        domain_tag=DomainTag.CYBERSECURITY,
        title="Test headline",
        normalized_text="Body text for hashing.",
        canonical_url="https://example.com/article",
    )
    assert doc.content_hash == compute_content_hash("Body text for hashing.")
    assert doc.domain_tag == DomainTag.CYBERSECURITY
    assert isinstance(doc.id, UUID)


def test_raw_document_rejects_invalid_hash() -> None:
    with pytest.raises(ValidationError):
        RawDocument(
            content_hash="not-a-valid-hash",
            source_id="x",
            source_name="X",
            domain_tag=DomainTag.AI,
            title="T",
            normalized_text="body",
        )


def test_pipeline_run_id_must_be_uuid() -> None:
    with pytest.raises(ValidationError):
        PipelineRun(run_id="not-a-uuid")


def test_source_registry_unique_ids() -> None:
    with pytest.raises(ValidationError):
        SourceRegistry(
            version=1,
            sources=[
                SourceConfig(
                    id="dup",
                    name="A",
                    type=SourceType.RSS,
                    url="https://example.com/a.xml",
                    domain_tag=DomainTag.AI,
                ),
                SourceConfig(
                    id="dup",
                    name="B",
                    type=SourceType.RSS,
                    url="https://example.com/b.xml",
                    domain_tag=DomainTag.AI,
                ),
            ],
        )


def test_raw_item_and_stage_result() -> None:
    item = RawItem(
        source_id="tech-hackernews",
        source_name="Hacker News",
        domain_tag=DomainTag.AI,
        title="Show HN",
    )
    assert item.domain_tag == DomainTag.AI

    stage = StageResult(
        stage=StageName.INGEST,
        status=RunStatus.RUNNING,
        finished_at=datetime.now(UTC),
    )
    assert stage.stage == StageName.INGEST
