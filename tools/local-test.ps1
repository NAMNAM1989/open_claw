# Chay TOAN BO test local truoc deploy
# Usage: powershell -File tools\local-test.ps1 [-SkipDocker]
param(
    [switch]$SkipDocker
)

$ErrorActionPreference = "Continue"
$root = Split-Path $PSScriptRoot -Parent
$fail = 0

function Step($name, [scriptblock]$action) {
    Write-Host ""
    Write-Host ">> $name" -ForegroundColor Cyan
    try {
        & $action
        if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw "exit $LASTEXITCODE" }
        Write-Host "   OK" -ForegroundColor Green
    } catch {
        Write-Host "   FAIL: $_" -ForegroundColor Red
        $script:fail++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  open_claw - LOCAL TEST (pre-deploy)" -ForegroundColor Yellow
Write-Host "========================================"

Step "Platform scaffold" {
    & "$PSScriptRoot\check-platform.ps1"
    if ($LASTEXITCODE -ne 0) { throw "check-platform exit $LASTEXITCODE" }
}

Step "cursor-agent npm test" {
    Push-Location (Join-Path $root "plugins\cursor-agent")
    try {
        npm test -- --run 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "npm test exit $LASTEXITCODE" }
    } finally {
        Pop-Location
    }
}

if (-not $SkipDocker) {
    Step "Gateway Docker smoke" {
        & "$PSScriptRoot\smoke-gateway.ps1"
        if ($LASTEXITCODE -ne 0) { throw "smoke-gateway exit $LASTEXITCODE" }
    }
} else {
    Write-Host ""
    Write-Host ">> Docker tests skipped (-SkipDocker)" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
if ($fail -eq 0) {
    Write-Host "  TAT CA TEST TU DONG: PASS" -ForegroundColor Green
    Write-Host ""
    Write-Host "Buoc tiep:" -ForegroundColor White
    Write-Host "  1. Copy .env.example -> .env.secrets; dien GEMINI + OPENCLAW_GATEWAY_TOKEN"
    Write-Host "  2. powershell -File tools\set-railway-secrets.ps1"
    Write-Host "  3. powershell -File tools\smoke-gateway.ps1"
    exit 0
} else {
    Write-Host "  $fail MUC FAIL - xem log tren" -ForegroundColor Red
    exit 1
}
