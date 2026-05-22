# Step 4 verification — run from repo root:
#   .\scripts\verify-step4.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

uv sync --dev
uv run pytest tests/test_db.py -v
uv run ruff check src/pipeline/db tests/test_db.py

Write-Host "Step 4 verification finished successfully."
