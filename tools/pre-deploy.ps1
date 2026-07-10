# Pre-deploy — chay truoc khi len Railway
# Usage: powershell -File tools\pre-deploy.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent

Write-Host ""
Write-Host "=== open_claw pre-deploy ===" -ForegroundColor Cyan
Write-Host ""

& "$PSScriptRoot\check-platform.ps1"
if ($LASTEXITCODE -ne 0) { throw "check-platform failed" }

Write-Host ""
Write-Host "pytest telegram-bot..." -ForegroundColor Cyan
Push-Location (Join-Path $root "apps\telegram-bot")
try {
    python -m pytest tests/ -q
    if ($LASTEXITCODE -ne 0) { throw "pytest failed" }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "=== San sang deploy ===" -ForegroundColor Green
Write-Host "Checklist: docs\DEPLOY.md"
Write-Host ""
Write-Host "Thu tu:"
Write-Host "  1. supabase db push"
Write-Host "  2. powershell -File tools\set-railway-secrets.ps1"
Write-Host "  3. (Tuy chon) Smoke test bot local — xem docs\DEPLOY.md muc 0"
Write-Host ""
