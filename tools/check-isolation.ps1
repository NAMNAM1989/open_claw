# Kiem tra tach biet open_claw khoi project bot cu (telegram_bot)
# Usage: powershell -File tools\check-isolation.ps1
$ErrorActionPreference = "Continue"
$root = Split-Path $PSScriptRoot -Parent
$fail = 0
$warn = 0

function Ok($name, $good, [string]$detail = "") {
    if (-not $good) { $script:fail++ }
    $mark = if ($good) { "OK" } else { "FAIL" }
    $extra = if ($detail) { " - $detail" } else { "" }
    Write-Host "  [$mark] $name$extra"
}

function Warn($name, [string]$detail = "") {
    $script:warn++
    $extra = if ($detail) { " - $detail" } else { "" }
    Write-Host "  [WARN] $name$extra" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "open_claw isolation check"
Write-Host ""

# 1. Repo khong tham chieu duong dan cu
$oldPathPattern = "C:\\Project\\telegram_bot|C:/Project/telegram_bot"
$hits = @()
Get-ChildItem $root -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $rel = $_.FullName.Substring($root.Length + 1)
        $rel -notmatch '^(docs\\|tools\\check-isolation\.ps1)' -and
        $_.FullName -notmatch '\\node_modules\\|\\\.git\\|\\__pycache__\\|\\dist\\' -and
        $_.Extension -match '\.(mjs|js|ts|py|md|json|yml|yaml|ps1|sh|toml)$'
    } |
    ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -and $content -match $oldPathPattern) {
            $hits += $_.FullName.Substring($root.Length + 1)
        }
    }

Ok "repo khong tro den C:\Project\telegram_bot" ($hits.Count -eq 0) $(if ($hits.Count) { ($hits -join ", ") } else { "" })

# 2. Gateway production template: telegram channel OFF
$tpl = Join-Path $root "apps\gateway\openclaw.template.json"
$json = Get-Content $tpl -Raw | ConvertFrom-Json
Ok "gateway template: channels.telegram disabled" ($json.channels.telegram.enabled -eq $false)

# 3. Bot code self-contained
$req = Test-Path (Join-Path $root "apps\telegram-bot\requirements.txt")
$main = Test-Path (Join-Path $root "apps\telegram-bot\bot\main.py")
Ok "apps/telegram-bot greenfield co day du" ($req -and $main)

# 4. Thu muc cu khong ton tai tren may
$oldDir = "C:\Project\telegram_bot"
Ok "thu muc cu khong ton tai ($oldDir)" (-not (Test-Path $oldDir))

# 5. Local OpenClaw config (neu co)
$localCfg = Join-Path $env:USERPROFILE ".openclaw\openclaw.json"
if (Test-Path $localCfg) {
    $local = Get-Content $localCfg -Raw | ConvertFrom-Json
    if ($local.channels.telegram.enabled -eq $true) {
        Warn "local openclaw: channels.telegram DANG BAT" "tat truoc khi chay apps/telegram-bot"
    } else {
        Ok "local openclaw: channels.telegram disabled" $true
    }
    $ws = @($local.agents.defaults.workspace) + @($local.agents.list | ForEach-Object { $_.workspace })
    $badWs = $ws | Where-Object { $_ -match 'telegram_bot' }
    if ($badWs.Count -gt 0) {
        Warn "local openclaw workspace tro den telegram_bot" "doi thanh apps\telegram-bot"
    } else {
        Ok "local openclaw workspace" $true
    }
    $proj = $local.plugins.entries.'cursor-agent'.config.projects.'telegram-bot'
    if ($proj -match 'telegram_bot') {
        Warn "cursor-agent project map tro den telegram_bot" "chay: node tools\restore-cursor-agent-config.mjs"
    } else {
        Ok "cursor-agent project map" $true
    }
} else {
    Write-Host "  [SKIP] khong co $localCfg"
}

Write-Host ""
if ($fail -eq 0 -and $warn -eq 0) {
    Write-Host "Isolation: OK - san sang deploy doc lap"
    exit 0
} elseif ($fail -eq 0) {
    Write-Host "Isolation: $warn canh bao - xem docs/DEPLOY.md muc Tach biet"
    exit 0
} else {
    Write-Host "Isolation: $fail FAIL - sua truoc khi deploy"
    exit 1
}
