# Set Railway secrets from local file (values never printed)
# Usage:
#   1. Copy .env.example -> .env.secrets (gitignored)
#   2. Fill: GEMINI_API_KEY, OPENCLAW_GATEWAY_TOKEN
#   3. powershell -File tools\set-railway-secrets.ps1
# Optional: -IncludeTelegramBot when telegram-bot service exists on Railway

param(
    [switch]$IncludeTelegramBot
)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$secrets = Join-Path $root ".env.secrets"

if (-not (Test-Path $secrets)) {
    Write-Host "Missing $secrets"
    Write-Host "Copy .env.example -> .env.secrets and fill secrets, then rerun."
    exit 1
}

function Read-EnvFile($path) {
    $map = @{}
    Get-Content $path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#")) { return }
        if ($line -match '^([^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            if ($value -match '^([^#]+)') { $value = $matches[1].Trim() }
            if ($value) { $map[$key] = $value }
        }
    }
    return $map
}

$envMap = Read-EnvFile $secrets
$gemini = $envMap["GEMINI_API_KEY"]
if (-not $gemini) { $gemini = $envMap["GOOGLE_API_KEY"] }
if (-not $gemini) {
    Write-Host "Missing GEMINI_API_KEY (or GOOGLE_API_KEY) in .env.secrets"
    exit 1
}
if (-not $envMap["OPENCLAW_GATEWAY_TOKEN"]) {
    Write-Host "Missing OPENCLAW_GATEWAY_TOKEN in .env.secrets"
    exit 1
}

$google = if ($envMap["GOOGLE_API_KEY"]) { $envMap["GOOGLE_API_KEY"] } else { $gemini }
$port = if ($envMap["PORT"]) { $envMap["PORT"] } else { "18789" }
$token = $envMap["OPENCLAW_GATEWAY_TOKEN"]

Push-Location $root
try {
    Write-Host "Setting openclaw-gateway (GEMINI, GOOGLE, TOKEN, PORT)..."
    railway variable set `
        "GEMINI_API_KEY=$gemini" `
        "GOOGLE_API_KEY=$google" `
        "OPENCLAW_GATEWAY_TOKEN=$token" `
        "PORT=$port" `
        --service openclaw-gateway `
        --environment production `
        --json | Out-Null
    railway service redeploy --service openclaw-gateway --environment production --yes 2>&1 | Out-Null

    if ($IncludeTelegramBot) {
        $botRequired = @("TELEGRAM_BOT_TOKEN", "SUPABASE_SERVICE_ROLE_KEY")
        $missing = $botRequired | Where-Object { -not $envMap[$_] }
        if ($missing.Count) {
            Write-Host "Missing keys for telegram-bot: $($missing -join ', ')"
            exit 1
        }
        Write-Host "Setting telegram-bot (TELEGRAM + SUPABASE_SERVICE_ROLE_KEY)..."
        railway variable set `
            "TELEGRAM_BOT_TOKEN=$($envMap['TELEGRAM_BOT_TOKEN'])" `
            "SUPABASE_SERVICE_ROLE_KEY=$($envMap['SUPABASE_SERVICE_ROLE_KEY'])" `
            --service telegram-bot `
            --environment production `
            --json | Out-Null
        railway service redeploy --service telegram-bot --environment production --yes 2>&1 | Out-Null
    }

    Write-Host "Done. Check: railway service status --json"
} finally {
    Pop-Location
}
