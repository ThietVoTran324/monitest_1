# Post-restore API smoke (health + optional authenticated checks via smoke-check.ps1).
Param(
  [string]$ApiBase = "http://127.0.0.1:8011",
  [string]$FrontendBase = "http://127.0.0.1:5173",
  [string]$AccessToken = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "[drill_smoke] API health $ApiBase/api/v1/health"
$health = Invoke-RestMethod -Uri "$ApiBase/api/v1/health" -TimeoutSec 15
if (-not $health) { throw "empty health" }
Write-Host "[drill_smoke] health OK"

Write-Host "[drill_smoke] Frontend reachability $FrontendBase"
try {
  $fe = Invoke-WebRequest -UseBasicParsing -Uri $FrontendBase -TimeoutSec 15
  if ($fe.StatusCode -ge 400) { throw "FE status $($fe.StatusCode)" }
  Write-Host "[drill_smoke] frontend OK"
} catch {
  Write-Warning "[drill_smoke] frontend not up (run vite for AC4 e2e): $($_.Exception.Message)"
}

& (Join-Path $Root "scripts\smoke-check.ps1") -ApiBase $ApiBase -FrontendBase $FrontendBase -AccessToken $AccessToken
Write-Host "[drill_smoke] DONE — also run: npm run e2e:smoke (Playwright) when FE is up"
