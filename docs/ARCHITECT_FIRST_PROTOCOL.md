# Architect-First Protocol

Every implementation step requires approval before code is written.

## Required justification block

1. **Proposed technologies/libraries** — What is used for this micro-task?
2. **Technical "why"** — Why this choice over alternatives?
3. **System impact** — How does this affect downstream steps?

## Gate

After the justification block, work **STOPS** until the owner replies **"Proceed"** (optionally scoped, e.g. `Proceed Step 2 only`).

## Sprint 1 implementation order

| Step | Scope | Status |
|------|--------|--------|
| 1 | Bootstrap + layout | **Complete** (2026-05-21) |
| 2 | Models + Settings | **Complete** (2026-05-21) |
| 3 | Storage protocol + local backend | **Complete** (2026-05-21) |
| 4 | DB schema + repository | **Complete** (2026-05-21) |
| 5 | Adapters + normalize + dedup | **Complete** (2026-05-21) |
| 6 | Ingest service + CLI | Pending |
| 7 | Integration tests + Sprint 1 sign-off | Pending |
