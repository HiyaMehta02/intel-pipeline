"""SQLAlchemy Core table definitions (portable to Postgres)."""

from __future__ import annotations

from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Table,
    Text,
    UniqueConstraint,
)

metadata = MetaData()

pipeline_runs = Table(
    "pipeline_runs",
    metadata,
    Column("run_id", Text, primary_key=True),
    Column("status", Text, nullable=False),
    Column("started_at", Text, nullable=False),
    Column("finished_at", Text, nullable=True),
    Column("stages_json", Text, nullable=True),
    Column("artifact_uris_json", Text, nullable=True),
)

documents = Table(
    "documents",
    metadata,
    Column("id", Text, primary_key=True),
    Column("content_hash", Text, nullable=False),
    Column("source_id", Text, nullable=False),
    Column("source_name", Text, nullable=False),
    Column("domain_tag", Text, nullable=False),
    Column("title", Text, nullable=False),
    Column("normalized_text", Text, nullable=False),
    Column("canonical_url", Text, nullable=True),
    Column("raw_artifact_key", Text, nullable=True),
    Column("raw_artifact_uri", Text, nullable=True),
    Column("ingested_at", Text, nullable=False),
    Column("published_at", Text, nullable=True),
    Column("created_at", Text, nullable=False),
    UniqueConstraint("content_hash", name="uq_documents_content_hash"),
)

ingest_events = Table(
    "ingest_events",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("run_id", Text, ForeignKey("pipeline_runs.run_id"), nullable=False),
    Column("source_id", Text, nullable=False),
    Column("status", Text, nullable=False),
    Column("documents_ingested", Integer, nullable=False, default=0),
    Column("error_message", Text, nullable=True),
    Column("created_at", Text, nullable=False),
    Index("ix_ingest_events_run_id", "run_id"),
)
