# One-shot publish for openclaw-cursor-agent
# Prerequisites: npm login  AND/OR  clawhub login
param(
  [switch]$SkipNpm,
  [switch]$SkipClawhub,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "==> typecheck / test / build"
npm run typecheck
npm test
npm run build

$pkg = Get-Content package.json -Raw | ConvertFrom-Json
$tgz = "$($pkg.name)-$($pkg.version).tgz"
if (Test-Path $tgz) { Remove-Item $tgz }
npm pack
if (-not (Test-Path $tgz)) { throw "Missing $tgz after npm pack" }

if (-not $SkipNpm) {
  Write-Host "==> npm publish"
  try {
    npm whoami | Out-Null
  } catch {
    Write-Warning "Not logged in to npm. Run: npm login"
    throw
  }
  if ($DryRun) {
    npm publish --access public --dry-run
  } else {
    npm publish --access public
  }
}

if (-not $SkipClawhub) {
  Write-Host "==> clawhub package publish"
  if (-not (Get-Command clawhub -ErrorAction SilentlyContinue)) {
    Write-Warning "clawhub CLI missing. Run: npm i -g clawhub"
    throw "clawhub not found"
  }

  $repoRoot = Resolve-Path (Join-Path (Get-Location) "..\..")
  Push-Location $repoRoot
  try {
    $remote = (git remote get-url origin 2>$null)
    $commit = (git rev-parse HEAD 2>$null)
    $ref = (git rev-parse --abbrev-ref HEAD 2>$null)
  } finally {
    Pop-Location
  }

  if (-not $remote -or -not $commit) {
    throw "ClawHub code-plugin publish requires git remote + commit. Push this repo to GitHub first."
  }

  # Normalize git@github.com:owner/repo.git → owner/repo
  $sourceRepo = $remote
  if ($sourceRepo -match 'github\.com[:/](.+?)(?:\.git)?$') {
    $sourceRepo = $Matches[1]
  }

  $cliArgs = @(
    "package", "publish", ".\$tgz",
    "--family", "code-plugin",
    "--source-repo", $sourceRepo,
    "--source-commit", $commit,
    "--source-ref", $ref,
    "--source-path", "plugins/cursor-agent",
    "--changelog", "v$($pkg.version) publish-ready release"
  )
  if ($DryRun) { $cliArgs += "--dry-run" }
  & clawhub @cliArgs
}

Write-Host "Done. Install with:"
Write-Host "  openclaw plugins install npm:$($pkg.name)"
Write-Host "  openclaw plugins install clawhub:$($pkg.name)"
