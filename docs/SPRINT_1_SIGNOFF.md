# Sprint 1 Sign-Off Checklist

> **Goal:** Prove the local ingest foundation is production-ready before Sprint 2 (LLM evaluation).

## Automated verification

```powershell
cd C:\Users\hiyam\Downloads\intel-pipeline-project\intel-pipeline
$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
.\scripts\verify-sprint1.ps1
```

Expected: `pytest` green, fixture ingest exits 0.

## Blueprint Tests 1.1–1.6

| # | Test | Command / check | Pass |
|---|------|-----------------|------|
| 1.1 | Unit + integration pytest | `uv run pytest -v` | ☐ |
| 1.2 | CLI ingest (fixtures) | `uv run pipeline ingest --sources configs/sources.yaml --run-id <uuid> --fixtures` | ☐ |
| 1.3 | Idempotency | Re-run ingest; `skipped=3`, `accepted=0`, raw file count unchanged | ☐ |
| 1.4 | Schema spot-check | `uv run pipeline validate-raw data/raw` | ☐ |
| 1.5 | Failure isolation | One bad source still allows others (see `test_integration_failure_isolation`) | ☐ |
| 1.6 | Clean machine / README | Another dev can follow README quick start | ☐ |

## Artifacts produced

| Artifact | Location |
|----------|----------|
| Raw documents | `data/raw/<yyyy-mm-dd>/<content_hash>.json` |
| SQLite metadata | `data/pipeline.db` |
| ADR-001 Storage | `docs/adr/ADR-001-storage-abstraction.md` |
| ADR-002 Identity | `docs/adr/ADR-002-document-identity.md` |

## Optional: live ingest smoke

```powershell
$runId = [guid]::NewGuid().ToString()
uv run pipeline ingest --sources configs/sources.yaml --run-id $runId
```

Requires network access to configured RSS URLs.

## Sprint 1 Definition of Done (from blueprint)

- [ ] `pipeline ingest` on ≥3 sources (fixtures or live)
- [ ] ≥95% valid `RawDocument` schema on disk
- [ ] Dedup on re-run (0 duplicate raw files)
- [ ] CI/default pytest passes without network
- [ ] README + ADRs complete

## Sign-off record

| Field | Value |
|-------|-------|
| **Sprint** | 1 |
| **Status** | Ready for Sprint 2 planning after all boxes checked |
| **Date** | |
| **Tester** | |
| **Notes** | |

---

When all items are checked, reply **"Sprint 1 approved"** to begin Sprint 2 (LLM evaluation) under Architect-First protocol.
