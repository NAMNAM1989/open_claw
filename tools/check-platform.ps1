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
    "apps\telegram-bot\bot\main.py",
    "apps\telegram-bot\requirements.txt",
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
Ok "primary model Gemini" ($json.agents.defaults.model.primary -eq "google/gemini-3.5-flash")
Ok "plugin google enabled" ($json.plugins.entries.google.enabled -eq $true)
$openaiOn = $json.plugins.entries.openai.enabled -eq $true
$deepseekOn = $json.plugins.entries.deepseek.enabled -eq $true
Ok "openai (ChatGPT) enabled" $openaiOn
Ok "deepseek fallback enabled" $deepseekOn
$fb = @($json.agents.defaults.model.fallbacks)
Ok "fallback[0] gpt-4o-mini" ($fb.Count -ge 1 -and $fb[0] -eq "openai/gpt-4o-mini")
Ok "fallback[1] deepseek" ($fb.Count -ge 2 -and $fb[1] -eq "deepseek/deepseek-v4-flash")
Ok "Gemini->GPT->DeepSeek chain" ($fb -contains "openai/gpt-4o-mini" -and $fb -contains "deepseek/deepseek-v4-flash")
$webDenied = $json.tools.deny -contains "group:web"
Ok "web_search disabled" $webDenied

$botDir = Join-Path $root "apps\telegram-bot"
if (Test-Path $botDir) {
    Push-Location $botDir
    try {
        python -m pytest tests/ -q --tb=no 2>$null
        Ok "telegram-bot v2 pytest" ($LASTEXITCODE -eq 0)
    } catch {
        Ok "telegram-bot v2 pytest" $false
    } finally {
        Pop-Location
    }
}

Write-Host ""
if ($fail -eq 0) {
    Write-Host "Tat ca kiem tra file/config: OK"
    exit 0
} else {
    Write-Host "$fail muc FAIL"
    exit 1
}
