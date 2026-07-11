# Kiem tra cau hinh local open_claw
# Usage: powershell -File tools\check-isolation.ps1
$ErrorActionPreference = "Continue"
$root = Split-Path $PSScriptRoot -Parent
$fail = 0

function Ok($name, $good, [string]$detail = "") {
    if (-not $good) { $script:fail++ }
    $mark = if ($good) { "OK" } else { "FAIL" }
    $extra = if ($detail) { " - $detail" } else { "" }
    Write-Host "  [$mark] $name$extra"
}
function Warn($name, [string]$detail = "") {
    Write-Host "  [WARN] $name$(if ($detail) { " - $detail" })"
}

Write-Host ""
Write-Host "open_claw local config check"
Write-Host ""

$localPath = Join-Path $env:USERPROFILE ".openclaw\openclaw.json"
if (Test-Path $localPath) {
    try {
        $local = Get-Content $localPath -Raw | ConvertFrom-Json
        if ($local.channels.telegram.enabled) {
            Warn "channels.telegram dang bat tren gateway local" "tat neu chi dung apps/telegram-bot"
        } else {
            Ok "channels.telegram disabled" $true
        }
        $ws = @($local.agents.defaults.workspace) + @($local.agents.list | ForEach-Object { $_.workspace })
        $openClawWs = $ws | Where-Object { $_ -match 'open_claw' }
        if ($openClawWs.Count -gt 0 -or $ws.Count -eq 0) {
            Ok "local workspace" $true
        } else {
            Warn "workspace local khong tro open_claw" "chay: node tools\restore-cursor-agent-config.mjs"
        }
    } catch {
        Warn "khong doc duoc local openclaw.json" $_.Exception.Message
    }
} else {
    Ok "khong co ~/.openclaw/openclaw.json (OK neu chua dev gateway local)" $true
}

Write-Host ""
if ($fail -eq 0) {
    Write-Host "Config: OK"
    exit 0
} else {
    Write-Host "$fail muc FAIL"
    exit 1
}
