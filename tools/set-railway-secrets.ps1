# Set Railway secrets from local file (values never printed)
# Usage:
#   1. Copy .env.example -> .env.secrets (gitignored)
#   2. Fill GEMINI_API_KEY, OPENCLAW_GATEWAY_TOKEN, TELEGRAM_BOT_TOKEN
#   3. powershell -File tools\set-railway-secrets.ps1
# Optional: -SkipTelegramBot if only updating gateway

param(
    [switch]$SkipTelegramBot
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
    $gwVars = @(
        "GEMINI_API_KEY=$gemini",
        "GOOGLE_API_KEY=$google",
        "OPENCLAW_GATEWAY_TOKEN=$token",
        "PORT=$port"
    )
    if ($envMap["OPENAI_API_KEY"]) {
        $gwVars += "OPENAI_API_KEY=$($envMap['OPENAI_API_KEY'])"
    }
    if ($envMap["DEEPSEEK_API_KEY"]) {
        $gwVars += "DEEPSEEK_API_KEY=$($envMap['DEEPSEEK_API_KEY'])"
    }
    railway variable set @gwVars `
        --service openclaw-gateway `
        --environment production `
        --json | Out-Null
    railway service redeploy --service openclaw-gateway --environment production --yes 2>&1 | Out-Null

    if (-not $SkipTelegramBot) {
        if (-not $envMap["TELEGRAM_BOT_TOKEN"]) {
            Write-Host "Missing TELEGRAM_BOT_TOKEN in .env.secrets"
            exit 1
        }
        $botVars = @(
            "TELEGRAM_BOT_TOKEN=$($envMap['TELEGRAM_BOT_TOKEN'])",
            "OPENCLAW_GATEWAY_TOKEN=$token",
            "OPENCLAW_BASE_URL=http://openclaw-gateway.railway.internal:18789/v1"
        )
        if ($envMap["ALLOWED_CHAT_IDS"]) {
            $botVars += "ALLOWED_CHAT_IDS=$($envMap['ALLOWED_CHAT_IDS'])"
        }
        Write-Host "Setting telegram-bot..."
        railway variable set @botVars `
            --service telegram-bot `
            --environment production `
            --json | Out-Null
        railway service redeploy --service telegram-bot --environment production --yes 2>&1 | Out-Null
    }

    Write-Host "Done. Check: railway service status --json"
} finally {
    Pop-Location
}
