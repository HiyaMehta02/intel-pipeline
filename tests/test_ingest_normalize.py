"""Normalizer tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.ingest.normalize import NormalizationError, extract_text, normalize_item
from pipeline.models import DomainTag, RawItem
from pipeline.models.hashing import compute_content_hash


def test_extract_text_from_html_fixture(repo_root: Path) -> None:
    html = (repo_root / "tests" / "fixtures" / "html" / "sample_article.html").read_text(
        encoding="utf-8",
    )
    item = RawItem(
        source_id="test",
        source_name="Test",
        domain_tag=DomainTag.AI,
        title="Sample Article",
        body_html=html,
    )
    text = extract_text(item, max_chars=10_000)
    assert "normalizer" in text.lower() or "paragraph" in text.lower()
    assert len(text) >= 20


def test_normalize_item_computes_stable_hash() -> None:
    item = RawItem(
        source_id="ds-ml-mastery",
        source_name="ML Mastery",
        domain_tag=DomainTag.DATA_SCIENCE,
        title="Embedding guide",
        summary="Practical guide to benchmarking embedding quality on domain corpora.",
    )
    doc1 = normalize_item(item)
    doc2 = normalize_item(item)
    assert doc1.content_hash == doc2.content_hash
    assert doc1.content_hash == compute_content_hash(doc1.normalized_text)


def test_normalize_item_raises_when_empty() -> None:
    item = RawItem(
        source_id="test",
        source_name="Test",
        domain_tag=DomainTag.AI,
        title="X",
    )
    with pytest.raises(NormalizationError):
        normalize_item(item)
