# Step 3 verification — run from repo root:
#   .\scripts\verify-step3.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

uv sync --dev
uv run pytest tests/test_storage_local.py -v
uv run ruff check src/pipeline/storage tests/test_storage_local.py

Write-Host "Step 3 verification finished successfully."
