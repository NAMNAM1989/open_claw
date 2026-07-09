# OPTIONAL: login npm -> clawhub -> GitHub for public publish only.
# Not required for local plugin development (0 login).
# Chay trong PowerShell thuong (co browser) chi khi muon publish:
#   powershell -ExecutionPolicy Bypass -File C:\Project\open_claw\tools\login-all.ps1

$ErrorActionPreference = "Stop"

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

function Pause-Step([string]$msg) {
  Write-Host ""
  Write-Host $msg -ForegroundColor Yellow
  Read-Host "Nhan Enter de tiep tuc"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LOGIN 1/3: npmjs.com" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ban can co tai khoan https://www.npmjs.com/signup (mien phi)."
Write-Host "Khi npm in ra URL:"
Write-Host "  1) Nhan Enter de mo browser (hoac copy URL vao Chrome)"
Write-Host "  2) Dang nhap npm tren web"
Write-Host "  3) Bam Authorize / Allow cho CLI"
Write-Host "  4) Quay lai terminal - KHONG go username/password o day"
Write-Host ""

$npmUser = $null
try { $npmUser = npm whoami 2>$null } catch { }
if ($npmUser) {
  Write-Host "Da login npm: $npmUser" -ForegroundColor Green
} else {
  Pause-Step "San sang login npm?"
  npm login --auth-type=web
  $npmUser = npm whoami
  Write-Host "OK npm: $npmUser" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LOGIN 2/3: ClawHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "clawhub se in ma + URL. Tren browser:"
Write-Host "  1) Mo URL"
Write-Host "  2) Dang nhap ClawHub / OpenClaw"
Write-Host "  3) Nhap ma device neu duoc hoi"
Write-Host ""

$clawOk = $false
try {
  clawhub whoami | Out-Null
  if ($LASTEXITCODE -eq 0) { $clawOk = $true }
} catch { }
if ($clawOk) {
  Write-Host "Da login clawhub" -ForegroundColor Green
  clawhub whoami
} else {
  Pause-Step "San sang login ClawHub?"
  clawhub login
  clawhub whoami
  Write-Host "OK clawhub" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LOGIN 3/3: GitHub (gh)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
if (-not $Gh) { throw "Thieu gh.exe" }

& $Gh auth status 2>$null
if ($LASTEXITCODE -eq 0) {
  Write-Host "Da login GitHub" -ForegroundColor Green
} else {
  Write-Host "Chon: GitHub.com -> HTTPS -> Login with a web browser"
  Write-Host "Copy one-time code, Enter de mo browser, paste code, Authorize."
  Write-Host ""
  Pause-Step "San sang login GitHub?"
  & $Gh auth login -p https -w -h github.com
  & $Gh auth status
  Write-Host "OK GitHub" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== TAT CA LOGIN XONG ===" -ForegroundColor Green
Write-Host "Chay tiep publish:"
Write-Host "  powershell -ExecutionPolicy Bypass -File C:\Project\open_claw\tools\finish-publish.ps1"
