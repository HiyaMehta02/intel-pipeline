# Step 5 verification — run from repo root:
#   .\scripts\verify-step5.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

uv sync --dev
uv run pytest tests/test_ingest_normalize.py tests/test_ingest_dedup.py tests/test_ingest_processor.py tests/test_ingest_adapters.py -v
uv run ruff check src/pipeline/ingest tests/test_ingest_normalize.py tests/test_ingest_dedup.py tests/test_ingest_processor.py tests/test_ingest_adapters.py

Write-Host "Step 5 verification finished successfully."
