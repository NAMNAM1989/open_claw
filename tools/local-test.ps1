# Chay TOAN BO test local truoc deploy
# Usage: powershell -File tools\local-test.ps1 [-SkipDocker]
param(
    [switch]$SkipDocker
)

$ErrorActionPreference = "Continue"
$root = Split-Path $PSScriptRoot -Parent
$fail = 0

function Invoke-Docker([string[]]$DockerArgs) {
    $out = & docker @DockerArgs 2>&1
    return @{ Out = $out; Code = $LASTEXITCODE }
}

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

Step "telegram-bot pytest" {
    Push-Location (Join-Path $root "apps\telegram-bot")
    try {
        python -m pytest tests/ -v --tb=short -q
        if ($LASTEXITCODE -ne 0) { throw "pytest exit $LASTEXITCODE" }
    } finally {
        Pop-Location
    }
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

    Step "telegram-bot Docker build" {
        $botDir = Join-Path $root "apps\telegram-bot"
        Write-Host "   (Playwright image - co the mat vai phut lan dau)" -ForegroundColor DarkGray
        $build = Invoke-Docker @("build", "-t", "namnam-telegram-bot-test", $botDir)
        $build.Out | Select-Object -Last 8 | ForEach-Object { Write-Host "   $_" }
        if ($build.Code -ne 0) { throw "docker build bot exit $($build.Code)" }
    }
} else {
    Write-Host ""
    Write-Host ">> Docker tests skipped (-SkipDocker)" -ForegroundColor DarkYellow
}

Step "Bot check_config (no .env - expected ERROR token)" {
    Push-Location (Join-Path $root "apps\telegram-bot")
    try {
        $env:PYTHONPATH = (Get-Location).Path
        $env:PYTHONIOENCODING = "utf-8"
        python scripts\check_config.py
        # exit 1 expected without TELEGRAM_BOT_TOKEN
        Write-Host "   (expected without TELEGRAM_BOT_TOKEN)" -ForegroundColor DarkYellow
    } finally {
        Pop-Location
    }
    $global:LASTEXITCODE = 0
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
if ($fail -eq 0) {
    Write-Host "  TAT CA TEST TU DONG: PASS" -ForegroundColor Green
    Write-Host ""
    Write-Host "Buoc tiep - test thu cong (can .env):" -ForegroundColor White
    Write-Host "  1. Copy .env.example -> apps\telegram-bot\.env"
    Write-Host "  2. Dien TELEGRAM_BOT_TOKEN, OPENCLAW_*, SUPABASE_*"
    Write-Host "  3. python scripts\check_config.py"
    Write-Host "  4. Terminal A: smoke-gateway"
    Write-Host "  5. Terminal B: cd apps\telegram-bot; python -m bot.main"
    Write-Host "  6. Telegram: /ping /import_gia /bao_gia /booking /ask"
    exit 0
} else {
    Write-Host "  $fail MUC FAIL - xem log tren" -ForegroundColor Red
    exit 1
}
