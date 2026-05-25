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

Write-Host "`n=== Lint ===" -ForegroundColor Cyan
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests

Write-Host "`n=== Tests (47 expected) ===" -ForegroundColor Cyan
uv run pytest -v

# Fresh ingest into isolated temp data dir so accepted=3 (not skipped duplicates)
$runId = [guid]::NewGuid().ToString()
$tempData = Join-Path $env:TEMP "intel-pipeline-verify-$runId"
New-Item -ItemType Directory -Path $tempData -Force | Out-Null
$tempDb = Join-Path $tempData "pipeline.db"
$env:DATA_DIR = $tempData
$env:DATABASE_URL = "sqlite:///$($tempDb -replace '\\','/')"

Write-Host "`n=== Fixture ingest (fresh data dir, run_id=$runId) ===" -ForegroundColor Cyan
uv run pipeline ingest --sources configs/sources.yaml --run-id $runId --fixtures

if (Test-Path (Join-Path $tempData "raw")) {
    uv run pipeline validate-raw (Join-Path $tempData "raw")
}

Remove-Item -Recurse -Force $tempData -ErrorAction SilentlyContinue
Remove-Item Env:DATA_DIR -ErrorAction SilentlyContinue
Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue

Write-Host "`nSprint 1 verification finished successfully." -ForegroundColor Green
Write-Host 'Note: Re-running ingest on ./data skips duplicates (accepted=0 skipped=3) - that is correct.'
Write-Host 'Manual checklist: docs/SPRINT_1_SIGNOFF.md'
