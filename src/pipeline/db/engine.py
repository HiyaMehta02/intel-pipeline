"""Database engine factory."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import Connection


def create_db_engine(database_url: str) -> Engine:
    """
    Create SQLAlchemy engine and ensure SQLite parent directory exists.
    """
    _ensure_sqlite_parent_dir(database_url)
    engine = create_engine(database_url, future=True)

    if database_url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _sqlite_pragma(dbapi_connection: object, _connection_record: object) -> None:
            cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def _ensure_sqlite_parent_dir(database_url: str) -> None:
    if not database_url.startswith("sqlite"):
        return
    # sqlite:///./data/pipeline.db or sqlite:////absolute/path.db
    path_part = database_url.removeprefix("sqlite:///")
    if path_part == database_url:
        path_part = database_url.removeprefix("sqlite://")
    if path_part in (":memory:", "/:memory:"):
        return
    db_path = Path(path_part)
    if not db_path.is_absolute():
        db_path = Path.cwd() / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)


def connection(engine: Engine) -> Connection:
    """Open a connection (caller manages commit/close)."""
    return engine.connect()
