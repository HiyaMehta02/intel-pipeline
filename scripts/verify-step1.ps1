# Step 1 verification — run from repo root in PowerShell:
#   .\scripts\verify-step1.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "Repo: $Root"
Write-Host ""

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "uv is not installed. Install: https://docs.astral.sh/uv/getting-started/installation/"
}

uv --version
uv sync --dev
uv run python -c "import pipeline; print('version:', pipeline.__version__)"
uv run ruff check src tests
uv run pytest -v

Write-Host ""
Write-Host "Step 1 verification finished successfully."
