"""Load and validate configs/sources.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from pipeline.models import SourceRegistry


def load_sources_yaml(path: Path | str) -> SourceRegistry:
    """
    Parse sources registry with PyYAML safe_load and Pydantic validation.

    Raises:
        FileNotFoundError: missing file
        ValidationError: invalid shape or enum values
        yaml.YAMLError: malformed YAML
    """
    file_path = Path(path).resolve()
    if not file_path.is_file():
        msg = f"Sources config not found: {file_path}"
        raise FileNotFoundError(msg)

    with file_path.open(encoding="utf-8") as handle:
        raw: Any = yaml.safe_load(handle)

    if raw is None:
        msg = "Sources config is empty"
        raise ValueError(msg)

    return SourceRegistry.model_validate(raw)
