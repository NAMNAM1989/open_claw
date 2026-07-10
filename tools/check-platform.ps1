# Kiem tra scaffold open_claw truoc deploy
# Usage: powershell -File tools\check-platform.ps1
$ErrorActionPreference = "Continue"
$root = Split-Path $PSScriptRoot -Parent
$fail = 0

function Ok($name, $good, [string]$detail = "") {
    if (-not $good) { $script:fail++ }
    $mark = if ($good) { "OK" } else { "FAIL" }
    $extra = if ($detail) { " - $detail" } else { "" }
    Write-Host "  [$mark] $name$extra"
}

Write-Host ""
Write-Host "open_claw platform check"
Write-Host ""

$tpl = Join-Path $root "apps\gateway\openclaw.template.json"
try {
    Get-Content $tpl -Raw | ConvertFrom-Json | Out-Null
    Ok "openclaw.template.json" $true
} catch {
    Ok "openclaw.template.json" $false $_.Exception.Message
}

@(
    "apps\gateway\Dockerfile",
    "apps\gateway\docker-entrypoint.sh",
    "apps\gateway\railway.toml",
    "apps\gateway\workspace\IDENTITY.md",
    "apps\gateway\workspace\SOUL.md",
    "supabase\migrations\20260709100000_initial.sql",
    "supabase\migrations\20260709110000_storage.sql",
    "docs\PLATFORM.md",
    ".env.example"
) | ForEach-Object {
    $p = Join-Path $root $_
    Ok $_ (Test-Path $p)
}

Ok "plugins/cursor-agent/dist" (Test-Path (Join-Path $root "plugins\cursor-agent\dist\index.js"))

Get-ChildItem (Join-Path $root ".github\workflows\*.yml") -ErrorAction SilentlyContinue | ForEach-Object {
    Ok "workflow $($_.Name)" $true
}

$json = Get-Content $tpl -Raw | ConvertFrom-Json
Ok "telegram channel disabled" ($json.channels.telegram.enabled -eq $false)
Ok "primary model Gemini" ($json.agents.defaults.model.primary -eq "google/gemini-2.5-flash")
Ok "plugin google enabled" ($json.plugins.entries.google.enabled -eq $true)
$openaiOff = -not $json.plugins.entries.openai -or $json.plugins.entries.openai.enabled -eq $false
$deepseekOff = -not $json.plugins.entries.deepseek -or $json.plugins.entries.deepseek.enabled -eq $false
Ok "openai disabled" $openaiOff
Ok "deepseek disabled" $deepseekOff

$botMigrated = Test-Path (Join-Path $root "apps\telegram-bot\requirements.txt")
if ($botMigrated) {
    Ok "telegram-bot present" $true
    $pytest = Join-Path $root "apps\telegram-bot"
    Push-Location $pytest
    try {
        python -m pytest tests/ -q --tb=no 2>$null
        Ok "telegram-bot pytest" ($LASTEXITCODE -eq 0)
    } catch {
        Ok "telegram-bot pytest" $false "python/pytest unavailable"
    } finally {
        Pop-Location
    }
} else {
    Write-Host "  [WARN] apps/telegram-bot chua co requirements.txt"
}

Write-Host ""
if ($fail -eq 0) {
    Write-Host "Tat ca kiem tra file/config: OK"
    exit 0
} else {
    Write-Host "$fail muc FAIL"
    exit 1
}
