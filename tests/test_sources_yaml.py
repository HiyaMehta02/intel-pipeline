"""configs/sources.yaml loading tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from pipeline.config.sources import load_sources_yaml
from pipeline.models import DomainTag, SourceType


def test_load_project_sources_yaml(repo_root: Path) -> None:
    registry = load_sources_yaml(repo_root / "configs" / "sources.yaml")
    assert registry.version == 1
    assert len(registry.sources) == 3
    enabled = registry.enabled_sources()
    assert len(enabled) == 3

    by_id = {s.id: s for s in registry.sources}
    assert by_id["cyber-thehackernews"].domain_tag == DomainTag.CYBERSECURITY
    assert by_id["cyber-thehackernews"].type == SourceType.RSS
    assert str(by_id["tech-hackernews"].url).startswith("https://")
    assert by_id["tech-hackernews"].domain_tag == DomainTag.AI
    assert by_id["ds-ml-mastery"].domain_tag == DomainTag.DATA_SCIENCE


def test_load_sources_invalid_domain_tag(repo_root: Path, tmp_path: Path) -> None:
    bad = tmp_path / "bad_sources.yaml"
    bad.write_text(
        """
version: 1
sources:
  - id: bad
    name: Bad
    type: rss
    url: https://example.com/feed.xml
    domain_tag: NotARealTag
    enabled: true
""".strip(),
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        load_sources_yaml(bad)


def test_load_sources_missing_file(repo_root: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_sources_yaml(repo_root / "configs" / "does-not-exist.yaml")
