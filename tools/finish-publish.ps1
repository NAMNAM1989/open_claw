# OPTIONAL: full public publish (npm + ClawHub + GitHub).
# Not required for local plugin development.
# Prefer local load path; see README.md and plugins/cursor-agent/PUBLISH.md.
#
# Run in a normal PowerShell (with browser) only when you want to ship publicly:
#   powershell -ExecutionPolicy Bypass -File C:\Project\open_claw\tools\finish-publish.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
$Plugin = Join-Path $Root "plugins\cursor-agent"

$Gh = $null
$ghCmd = Get-Command gh -ErrorAction SilentlyContinue
if ($ghCmd) { $Gh = $ghCmd.Source }
if (-not $Gh) {
  $candidates = @(
    "$env:LOCALAPPDATA\gh-cli\bin\gh.exe",
    "$env:LOCALAPPDATA\gh-cli\gh_2.74.1_windows_amd64\bin\gh.exe"
  )
  foreach ($c in $candidates) {
    if (Test-Path $c) { $Gh = $c; break }
  }
}

function Need($cmd) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    throw "Missing command: $cmd"
  }
}

Need npm
Need clawhub
Need git
if (-not $Gh) {
  throw "Missing gh.exe - install GitHub CLI first"
}

Write-Host ""
Write-Host "=== 1) npm login ===" -ForegroundColor Cyan
$npmUser = $null
try { $npmUser = npm whoami 2>$null } catch { }
if ($npmUser) {
  Write-Host "npm: already logged in as $npmUser"
} else {
  Write-Host "Opening npm login (browser/web)..."
  npm login --auth-type=web
  npm whoami
}

Write-Host ""
Write-Host "=== 2) clawhub login ===" -ForegroundColor Cyan
$clawOk = $false
try {
  clawhub whoami | Out-Null
  if ($LASTEXITCODE -eq 0) { $clawOk = $true }
} catch { }
if ($clawOk) {
  Write-Host "clawhub: already logged in"
} else {
  Write-Host "Starting clawhub device login..."
  clawhub login
  clawhub whoami
}

Write-Host ""
Write-Host "=== 3) GitHub auth + remote ===" -ForegroundColor Cyan
Push-Location $Root
try {
  & $Gh auth status 2>$null
  if ($LASTEXITCODE -ne 0) {
    & $Gh auth login -p https -w
  }

  $remote = git remote get-url origin 2>$null
  if (-not $remote) {
    $repoName = "open_claw"
    Write-Host "Creating GitHub repo $repoName ..."
    & $Gh repo create $repoName --public --source=. --remote=origin --push
  } else {
    Write-Host "Remote exists: $remote"
    git push -u origin HEAD
  }
  $remote = git remote get-url origin
  $commit = git rev-parse HEAD
  Write-Host "Pushed $commit to $remote"
} finally {
  Pop-Location
}

Write-Host ""
Write-Host "=== 4) Publish plugin ===" -ForegroundColor Cyan
Push-Location $Plugin
try {
  & .\scripts\publish.ps1
} finally {
  Pop-Location
}

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Green
Write-Host "Install:"
Write-Host "  openclaw plugins install npm:openclaw-cursor-agent"
Write-Host "  openclaw plugins install clawhub:openclaw-cursor-agent"
