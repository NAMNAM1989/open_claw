# Smoke test OpenClaw gateway Docker image
# Usage: powershell -File tools\smoke-gateway.ps1
param(
    [string]$Token = "smoke-test-token-123456",
    [int]$Port = 0
)

$ErrorActionPreference = "Continue"
$root = Split-Path $PSScriptRoot -Parent
$image = "openclaw-gateway-test"
$name = "openclaw-gw-smoke"
$gatewayDir = Join-Path $root "apps\gateway"

function Invoke-Docker([string[]]$DockerArgs) {
    $out = & docker @DockerArgs 2>&1
    $code = $LASTEXITCODE
    return @{ Out = $out; Code = $code }
}

Write-Host "Building gateway image..."
$build = Invoke-Docker @("build", "-t", $image, $gatewayDir)
if ($build.Code -ne 0) {
    $build.Out | Select-Object -Last 15
    throw "docker build failed"
}

Invoke-Docker @("rm", "-f", $name) | Out-Null

if ($Port -le 0) {
    $Port = 18792
}
$ports = @($Port, 18793, 18794, 18795)
$started = $false

foreach ($p in $ports) {
    $run = Invoke-Docker @(
        "run", "-d", "--name", $name,
        "-p", "${p}:18789",
        "-e", "OPENCLAW_GATEWAY_TOKEN=$Token",
        "-e", "GEMINI_API_KEY=placeholder",
        $image
    )
    if ($run.Code -eq 0) {
        $Port = $p
        $started = $true
        break
    }
    $run.Out | ForEach-Object { Write-Host $_ }
    Invoke-Docker @("rm", "-f", $name) | Out-Null
}

if (-not $started) {
    throw "docker run failed on ports $($ports -join ', ')"
}

Write-Host "Gateway on port $Port - waiting 25s..."
Start-Sleep -Seconds 25

$status = (Invoke-Docker @("ps", "-a", "--filter", "name=$name", "--format", "{{.Status}}")).Out
if ($status -notmatch "^Up") {
    Write-Host "Container status: $status"
    (Invoke-Docker @("logs", $name)).Out | Select-Object -Last 20
    Invoke-Docker @("rm", "-f", $name) | Out-Null
    throw "gateway container not running"
}

$health = curl.exe -sS "http://127.0.0.1:${Port}/health"
Write-Host "health: $health"
if ($health -notmatch '"ok":true') {
    Invoke-Docker @("rm", "-f", $name) | Out-Null
    throw "health check failed"
}

$models = curl.exe -sS "http://127.0.0.1:${Port}/v1/models" -H "Authorization: Bearer $Token"
if (-not $models) {
    Invoke-Docker @("rm", "-f", $name) | Out-Null
    throw "models endpoint empty"
}
Write-Host "models: $($models.Substring(0, [Math]::Min(120, $models.Length)))..."
if ($models -notmatch "openclaw") {
    Invoke-Docker @("rm", "-f", $name) | Out-Null
    throw "models auth failed"
}

Write-Host "OK - gateway smoke passed (port $Port)"
Invoke-Docker @("rm", "-f", $name) | Out-Null
exit 0
