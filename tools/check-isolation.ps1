# Kiem tra tach biet open_claw khoi project bot cu (telegram_bot)
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
Write-Host "open_claw isolation check"
Write-Host ""

$hits = @()
Get-ChildItem -Path $root -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\\.git\\' } |
    ForEach-Object {
        if (Select-String -Path $_.FullName -Pattern 'C:\\Project\\telegram_bot|C:/Project/telegram_bot' -Quiet) {
            $hits += $_.FullName.Replace($root + '\', '')
        }
    }
Ok "repo khong tro den C:\Project\telegram_bot" ($hits.Count -eq 0) $(if ($hits.Count) { ($hits -join ", ") } else { "" })

$oldDir = "C:\Project\telegram_bot"
if (Test-Path $oldDir) {
    Warn "thu muc bot cu van ton tai tren disk" $oldDir
} else {
    Ok "thu muc bot cu da xoa" $true
}

$localPath = Join-Path $env:USERPROFILE ".openclaw\openclaw.json"
if (Test-Path $localPath) {
    try {
        $local = Get-Content $localPath -Raw | ConvertFrom-Json
        if ($local.channels.telegram.enabled) {
            Warn "local openclaw: channels.telegram DANG BAT" "tat neu khong can Telegram local"
        } else {
            Ok "local channels.telegram disabled" $true
        }
        $ws = @($local.agents.defaults.workspace) + @($local.agents.list | ForEach-Object { $_.workspace })
        $badWs = $ws | Where-Object { $_ -match 'telegram_bot' }
        if ($badWs.Count) {
            Warn "local workspace tro den telegram_bot" "chay: node tools\restore-cursor-agent-config.mjs"
        } else {
            Ok "local workspace OK" $true
        }
    } catch {
        Warn "khong doc duoc local openclaw.json" $_.Exception.Message
    }
}

Write-Host ""
if ($fail -eq 0) {
    Write-Host "Isolation: OK"
    exit 0
} else {
    Write-Host "$fail muc FAIL"
    exit 1
}
