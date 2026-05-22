# ADR-001: Storage abstraction and object key layout

**Status:** Accepted  
**Date:** 2026-05-21  
**Sprint:** 1 (Step 3)

## Context

Raw documents and future briefing artifacts must persist locally during development and map directly to S3/GCS in Sprint 4 without changing ingest or orchestration code.

## Decision

1. **`StorageBackend` protocol** with operations:
   - `write_raw_document(RawDocument) -> StoredArtifact`
   - `raw_document_exists(content_hash) -> bool`
   - `read_raw_document(content_hash) -> RawDocument | None`
2. **Sprint 1 implementation:** `LocalFilesystemBackend` rooted at `Settings.resolved_data_dir()`.
3. **Object key layout (portable to S3):**
   - Raw document: `raw/{yyyy-mm-dd}/{content_hash}.json`
   - Date prefix uses UTC from `RawDocument.ingested_at`.
4. **Idempotent writes:** If any `raw/**/{content_hash}.json` exists, return that artifact with `created=False` (no second file for the same hash).
5. **URI format:** `Path.as_uri()` locally (`file://...`); S3 backend will use `s3://bucket/key` later.

## Consequences

- Ingest (Step 6) depends only on `StorageBackend`, not `open()` calls.
- Sprint 4 `S3Backend` reuses `raw_document_key()` from `pipeline.storage.paths`.
- Dedup (Step 5) can call `raw_document_exists` before normalize/write.
- Run manifests store `artifact.uri` and `artifact.key` for traceability.

## Implementation

- `pipeline.storage.protocol.StorageBackend`
- `pipeline.storage.local.LocalFilesystemBackend`
- `pipeline.storage.paths.raw_document_key`
