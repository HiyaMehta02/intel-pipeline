"""SQLAlchemy Core metadata, migrations, and repositories."""

from pipeline.db.engine import create_db_engine
from pipeline.db.migrate import apply_migrations
from pipeline.db.repositories import (
    DocumentRepository,
    DuplicateContentHashError,
    IngestEventRecord,
    IngestEventRepository,
    PipelineRunRepository,
    init_database,
)
from pipeline.db.schema import documents, ingest_events, metadata, pipeline_runs
from pipeline.db.session import db_connection, engine_from_settings

__all__ = [
    "create_db_engine",
    "apply_migrations",
    "engine_from_settings",
    "db_connection",
    "init_database",
    "metadata",
    "pipeline_runs",
    "documents",
    "ingest_events",
    "PipelineRunRepository",
    "DocumentRepository",
    "IngestEventRepository",
    "IngestEventRecord",
    "DuplicateContentHashError",
]
