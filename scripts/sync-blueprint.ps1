# Copy the full blueprint from the Cursor project docs into this repo.
$Source = "C:\Users\hiyam\.cursor\projects\empty-window\docs\AI_KNOWLEDGE_PIPELINE_BLUEPRINT.md"
$Dest = Join-Path (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)) "docs\AI_KNOWLEDGE_PIPELINE_BLUEPRINT.md"

if (-not (Test-Path $Source)) {
    Write-Error "Source blueprint not found: $Source"
}
Copy-Item -Path $Source -Destination $Dest -Force
Write-Host "Synced blueprint to $Dest"
