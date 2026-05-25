# intel-pipeline

Containerized AI Knowledge Pipeline: ingest technical intelligence (AI, Data Science, Cybersecurity), evaluate with LLMs, synthesize briefing scripts, and generate audio deliverables.

## Status

**Sprint 1 complete** — local ingest pipeline (RSS → normalize → dedup → JSON + SQLite).  
Next: **Sprint 2** (LLM evaluation & curation) after [Sprint 1 sign-off](docs/SPRINT_1_SIGNOFF.md).

Architecture: [docs/AI_KNOWLEDGE_PIPELINE_BLUEPRINT.md](docs/AI_KNOWLEDGE_PIPELINE_BLUEPRINT.md)

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Quick start

```powershell
cd C:\Users\hiyam\Downloads\intel-pipeline-project\intel-pipeline

# Install uv (once): irm https://astral.sh/uv/install.ps1 | iex
# Then add to PATH:  $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"

uv sync --dev
copy .env.example .env

$runId = [guid]::NewGuid().ToString()
uv run pipeline ingest --sources configs/sources.yaml --run-id $runId --fixtures
```

Expected output:

```text
run_id=... status=completed accepted=3 skipped=0 sources_failed=0
```

## CLI commands (Sprint 1)

| Command | Description |
|---------|-------------|
| `uv run pipeline ingest --fixtures` | Ingest from test RSS fixtures (no network) |
| `uv run pipeline ingest` | Ingest from live feeds in `configs/sources.yaml` |
| `uv run pipeline validate-raw data/raw` | Validate stored JSON against schema |

## Verify Sprint 1

```powershell
.\scripts\verify-sprint1.ps1
```

Manual checklist: [docs/SPRINT_1_SIGNOFF.md](docs/SPRINT_1_SIGNOFF.md)

## Layout

```
src/pipeline/     Application package (models, ingest, storage, db, cli)
configs/          sources.yaml
tests/            pytest + fixtures/feeds
docs/             Blueprint, ADRs, sign-off
data/             Runtime artifacts (gitignored)
```

## Development

```powershell
uv run ruff check src tests
uv run pytest -v
```

## License

TBD
