"""Bootstrap smoke tests for Step 1."""

from __future__ import annotations

import pipeline


def test_package_version() -> None:
    assert pipeline.__version__ == "0.1.0"


def test_package_import() -> None:
    assert pipeline.__doc__ is not None
