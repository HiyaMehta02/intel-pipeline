"""Database session helpers."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.engine import Connection, Engine

from pipeline.config.settings import Settings, get_settings
from pipeline.db.engine import create_db_engine
from pipeline.db.migrate import apply_migrations


def engine_from_settings(settings: Settings | None = None) -> Engine:
    settings = settings or get_settings()
    engine = create_db_engine(settings.database_url)
    apply_migrations(engine)
    return engine


@contextmanager
def db_connection(settings: Settings | None = None) -> Iterator[Connection]:
    """Yield a connection with migrations applied; commits on success."""
    engine = engine_from_settings(settings)
    with engine.begin() as conn:
        yield conn
