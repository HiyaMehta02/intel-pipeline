"""Shared pytest fixtures (expanded in later Sprint 1 steps)."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def repo_root() -> Path:
    """Repository root (parent of tests/)."""
    return Path(__file__).resolve().parent.parent
