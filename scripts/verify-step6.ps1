# Step 6 verification — run from repo root:
#   .\scripts\verify-step6.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

uv sync --dev
uv run pytest tests/test_cli_ingest.py -v
uv run ruff check src/pipeline/cli src/pipeline/ingest/runner.py src/pipeline/logging

$runId = [guid]::NewGuid().ToString()
uv run pipeline ingest --sources configs/sources.yaml --run-id $runId --fixtures
Write-Host "Manual ingest run_id: $runId"

Write-Host "Step 6 verification finished successfully."
