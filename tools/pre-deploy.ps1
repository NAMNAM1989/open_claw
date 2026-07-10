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
Write-Host "=== San sang deploy ===" -ForegroundColor Green
Write-Host "Checklist: docs\DEPLOY.md"
Write-Host ""
Write-Host "Thu tu:"
Write-Host "  1. supabase db push (neu co migration moi)"
Write-Host "  2. powershell -File tools\set-railway-secrets.ps1"
Write-Host "  3. cd apps\gateway; railway up --environment production"
Write-Host ""
