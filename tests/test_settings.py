"""Settings and environment override tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.config.settings import Settings, get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_settings_defaults(repo_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(repo_root)
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("DATA_DIR", raising=False)
    settings = Settings(_env_file=None)
    assert settings.environment == "local"
    assert settings.enable_near_dedup is False
    assert settings.resolved_sources_path() == repo_root / "configs" / "sources.yaml"


def test_settings_env_override(repo_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("LOG_LEVEL", "debug")
    monkeypatch.setenv("ENABLE_NEAR_DEDUP", "true")
    settings = Settings(_env_file=None)
    assert settings.environment == "staging"
    assert settings.log_level == "DEBUG"
    assert settings.enable_near_dedup is True


def test_resolved_data_dir_relative(repo_root: Path) -> None:
    settings = Settings(_env_file=None, project_root=repo_root, data_dir=Path("./data"))
    assert settings.resolved_data_dir() == repo_root / "data"
