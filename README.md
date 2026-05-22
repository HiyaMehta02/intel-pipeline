# intel-pipeline

Containerized AI Knowledge Pipeline: ingest technical intelligence (AI, Data Science, Cybersecurity), evaluate with LLMs, synthesize briefing scripts, and generate audio deliverables.

## Status

**Sprint 1 — Steps 1–3 complete:** bootstrap, models/settings, local `StorageBackend` (ADR-001). See [docs/AI_KNOWLEDGE_PIPELINE_BLUEPRINT.md](docs/AI_KNOWLEDGE_PIPELINE_BLUEPRINT.md) for architecture and testing guide.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

## Quick start

```powershell
cd C:\Users\hiyam\Downloads\intel-pipeline-project\intel-pipeline
uv sync --dev
copy .env.example .env
uv run python -c "import pipeline; print(pipeline.__version__)"
uv run ruff check src tests
uv run pytest
.\scripts\verify-step2.ps1
```

## Layout

```
src/pipeline/     Application package (models, ingest, storage, db, cli)
configs/          sources.yaml and future prompt configs
tests/            pytest suite
docs/             Blueprint, ADRs
data/             Runtime artifacts (gitignored; created on first ingest)
```

## Development

- **Lint/format:** `uv run ruff check src tests` / `uv run ruff format src tests`
- **Tests:** `uv run pytest`
- **Pre-commit (optional):** `uv run pre-commit install` after hooks are added

## License

TBD
