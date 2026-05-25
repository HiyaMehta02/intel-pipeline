# Sprint 1 full verification — run from repo root:
#   .\scripts\verify-sprint1.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}

Write-Host "=== Sprint 1 verification ===" -ForegroundColor Cyan

uv sync --dev
uv run ruff check src tests
uv run pytest -v

$runId = [guid]::NewGuid().ToString()
Write-Host "`n=== Fixture ingest (run_id=$runId) ===" -ForegroundColor Cyan
uv run pipeline ingest --sources configs/sources.yaml --run-id $runId --fixtures

if (Test-Path "data/raw") {
    uv run pipeline validate-raw data/raw
}

Write-Host "`nSprint 1 automated verification finished." -ForegroundColor Green
Write-Host "Complete manual checklist: docs/SPRINT_1_SIGNOFF.md"
