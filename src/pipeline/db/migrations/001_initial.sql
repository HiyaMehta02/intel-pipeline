-- Sprint 1 initial schema (SQLite; Postgres-compatible types as TEXT/INTEGER)

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    stages_json TEXT,
    artifact_uris_json TEXT
);

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    content_hash TEXT NOT NULL,
    source_id TEXT NOT NULL,
    source_name TEXT NOT NULL,
    domain_tag TEXT NOT NULL,
    title TEXT NOT NULL,
    normalized_text TEXT NOT NULL,
    canonical_url TEXT,
    raw_artifact_key TEXT,
    raw_artifact_uri TEXT,
    ingested_at TEXT NOT NULL,
    published_at TEXT,
    created_at TEXT NOT NULL,
    CONSTRAINT uq_documents_content_hash UNIQUE (content_hash)
);

CREATE TABLE IF NOT EXISTS ingest_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES pipeline_runs (run_id),
    source_id TEXT NOT NULL,
    status TEXT NOT NULL,
    documents_ingested INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_ingest_events_run_id ON ingest_events (run_id);
