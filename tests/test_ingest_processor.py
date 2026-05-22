"""Ingest processor integration tests (fixture mode, no network)."""

from __future__ import annotations

from pathlib import Path

from pipeline.config.settings import Settings
from pipeline.config.sources import load_sources_yaml
from pipeline.ingest import DedupService, IngestProcessor
from pipeline.ingest.results import SourceProcessStatus
from pipeline.models import DomainTag, SourceConfig, SourceType


def _settings(repo_root: Path) -> Settings:
    return Settings(
        _env_file=None,
        project_root=repo_root,
        ingest_fixtures_dir=repo_root / "tests" / "fixtures" / "feeds",
    )


def test_process_all_fixture_sources(repo_root: Path) -> None:
    registry = load_sources_yaml(repo_root / "configs" / "sources.yaml")
    processor = IngestProcessor(_settings(repo_root), DedupService(), use_fixtures=True)
    results = processor.process_sources(registry.enabled_sources())

    assert len(results) == 3
    for result in results:
        assert result.status in (SourceProcessStatus.SUCCESS, SourceProcessStatus.PARTIAL)
        assert len(result.accepted) >= 1
        assert result.items_fetched >= 1


def test_dedup_skips_duplicate_in_same_run(repo_root: Path) -> None:
    source = SourceConfig(
        id="cyber-thehackernews",
        name="THN",
        type=SourceType.RSS,
        url="https://example.com/feed.xml",
        domain_tag=DomainTag.CYBERSECURITY,
    )
    dedup = DedupService()
    processor = IngestProcessor(_settings(repo_root), dedup, use_fixtures=True)
    first = processor.process_source(source)
    second = processor.process_source(source)

    assert len(first.accepted) == 1
    assert len(second.skipped) == 1
    assert len(second.accepted) == 0


def test_failure_isolation_bad_fixture_dir(repo_root: Path) -> None:
    good_source = SourceConfig(
        id="cyber-thehackernews",
        name="THN",
        type=SourceType.RSS,
        url="https://example.com/feed.xml",
        domain_tag=DomainTag.CYBERSECURITY,
    )
    good_processor = IngestProcessor(_settings(repo_root), DedupService(), use_fixtures=True)
    bad_processor = IngestProcessor(
        Settings(
            _env_file=None,
            project_root=repo_root,
            ingest_fixtures_dir=repo_root / "nonexistent-feeds",
        ),
        DedupService(),
        use_fixtures=True,
    )

    assert good_processor.process_source(good_source).status == SourceProcessStatus.SUCCESS
    bad_result = bad_processor.process_source(good_source)
    assert bad_result.status == SourceProcessStatus.FAILED
    assert bad_result.errors
