"""Apply SQL migrations and ensure schema exists."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import Engine, text
from sqlalchemy.engine import Connection

from pipeline.db.schema import metadata


def migrations_dir() -> Path:
    return Path(__file__).resolve().parent / "migrations"


def apply_migrations(engine: Engine) -> None:
    """
    Create tables from SQL files, then ensure SQLAlchemy metadata is in sync.

    Safe to call on every startup (IF NOT EXISTS).
    """
    with engine.begin() as conn:
        for sql_file in sorted(migrations_dir().glob("*.sql")):
            _execute_sql_script(conn, sql_file.read_text(encoding="utf-8"))
        metadata.create_all(conn)


def _execute_sql_script(conn: Connection, script: str) -> None:
    # Split on semicolons; skip empty / comment-only fragments.
    statements = [s.strip() for s in script.split(";") if s.strip()]
    for statement in statements:
        if statement.startswith("--"):
            continue
        conn.execute(text(statement))


def list_migration_files() -> list[str]:
    return sorted(path.name for path in migrations_dir().glob("*.sql"))
