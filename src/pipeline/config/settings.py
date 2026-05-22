"""Application settings (environment + .env)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

EnvironmentName = Literal["local", "staging", "prod"]


class Settings(BaseSettings):
    """Runtime configuration; inject via get_settings()."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: EnvironmentName = "local"
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[3],
    )
    data_dir: Path = Field(default=Path("./data"))
    database_url: str = "sqlite:///./data/pipeline.db"
    log_level: str = "INFO"
    sources_path: Path | None = None
    enable_near_dedup: bool = False
    max_normalized_chars: int = Field(default=50_000, ge=1000)

    @field_validator("project_root", "data_dir", "sources_path", mode="before")
    @classmethod
    def resolve_paths(cls, value: Path | str | None) -> Path | None:
        if value is None:
            return None
        return Path(value).expanduser().resolve()

    @field_validator("log_level")
    @classmethod
    def uppercase_log_level(cls, value: str) -> str:
        return value.upper()

    def resolved_sources_path(self) -> Path:
        if self.sources_path is not None:
            return self.sources_path
        return self.project_root / "configs" / "sources.yaml"

    def resolved_data_dir(self) -> Path:
        if self.data_dir.is_absolute():
            return self.data_dir
        return (self.project_root / self.data_dir).resolve()


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
