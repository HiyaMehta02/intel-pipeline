# Step 2 verification — run from repo root:
#   .\scripts\verify-step2.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

uv sync --dev
uv run pytest tests/test_content_hash.py tests/test_models.py tests/test_settings.py tests/test_sources_yaml.py -v
uv run ruff check src tests

Write-Host "Step 2 verification finished successfully."
