"""Migration runner regression tests."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import inspect

from pipeline.db import apply_migrations, create_db_engine
from pipeline.db.migrate import _split_sql_statements


def test_split_sql_ignores_semicolons_in_comments() -> None:
    script = """
    -- Comment with semicolon; should not split here
    CREATE TABLE IF NOT EXISTS demo (id TEXT PRIMARY KEY);
    """
    statements = _split_sql_statements(script)
    assert len(statements) == 1
    assert "CREATE TABLE" in statements[0]


def test_migrations_apply_on_fresh_db(tmp_path: Path) -> None:
    engine = create_db_engine(f"sqlite:///{tmp_path / 'fresh.db'}")
    apply_migrations(engine)
    tables = set(inspect(engine).get_table_names())
    assert tables >= {"pipeline_runs", "documents", "ingest_events"}
    engine.dispose()
