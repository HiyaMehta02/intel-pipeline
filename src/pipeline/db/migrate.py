"""Apply SQL migrations and ensure schema exists."""

from __future__ import annotations

import re
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


def _strip_sql_comments(script: str) -> str:
    """Remove full-line -- comments so semicolons inside comments are ignored."""
    lines: list[str] = []
    for line in script.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        lines.append(line)
    return "\n".join(lines)


def _split_sql_statements(script: str) -> list[str]:
    """Split on semicolons outside of comments."""
    cleaned = _strip_sql_comments(script)
    parts = re.split(r";\s*", cleaned)
    return [part.strip() for part in parts if part.strip()]


def _execute_sql_script(conn: Connection, script: str) -> None:
    for statement in _split_sql_statements(script):
        conn.execute(text(statement))


def list_migration_files() -> list[str]:
    return sorted(path.name for path in migrations_dir().glob("*.sql"))
