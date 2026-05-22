# ADR-002: Document identity and content hashing

**Status:** Accepted  
**Date:** 2026-05-21  
**Sprint:** 1 (Step 2)

## Context

The pipeline must deduplicate ingested intelligence, join evaluations in Sprint 2, and store immutable raw JSON artifacts without collision or silent drift.

## Decision

1. **Primary key for deduplication:** `content_hash` — lowercase SHA-256 hex (64 characters) of UTF-8 bytes of `normalized_text.strip()`.
2. **Document UUID:** `RawDocument.id` — UUID4 generated at document creation; stable in DB and manifests.
3. **Run identifier:** `PipelineRun.run_id` — UUID4 string; propagated in logs and stage results.
4. **Composite provenance:** `source_id` + `content_hash` identifies a document lane; same URL with changed body yields a **new** hash and **new** document (no in-place update in Sprint 1).
5. **Near-duplicate detection:** Out of scope for Sprint 1 (`ENABLE_NEAR_DEDUP=false`); SimHash deferred to Sprint 2 golden-set tuning.

## Consequences

- Normalization quality directly affects hash stability; HTML noise must be stripped before hashing (Step 5).
- Changing the hash algorithm requires re-ingest and invalidates Sprint 2 evaluation joins.
- SQLite `documents.content_hash` will use a UNIQUE constraint (Step 4).
- S3 object keys will include `{content_hash}` under `raw/{date}/` (Step 3, ADR-001).

## Implementation

- `pipeline.models.hashing.compute_content_hash`
- `pipeline.models.document.RawDocument.from_normalized`
