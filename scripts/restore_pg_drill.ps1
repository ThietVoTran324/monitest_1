# Restore dump into NEW database moni_restore_<ts> (does not overwrite primary).
Param(
  [Parameter(Mandatory = $true)][string]$DumpFile,
  [string]$ComposeFile = "docker-compose.yml"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path $DumpFile)) {
  throw "Dump not found: $DumpFile"
}

$pgUser = "moni"
if (Test-Path (Join-Path $Root ".env")) {
  Get-Content (Join-Path $Root ".env") | ForEach-Object {
    if ($_ -match '^\s*POSTGRES_USER=(.*)$') { $pgUser = $Matches[1].Trim().Trim('"') }
  }
}

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$newDb = "moni_restore_$stamp"
$start = Get-Date

function Invoke-Pg {
  param([string[]]$SqlArgs)
  & docker compose -f $ComposeFile exec -T postgres psql -U $pgUser -d postgres @SqlArgs
}

Invoke-Pg @("-v", "ON_ERROR_STOP=1", "-c", "DROP DATABASE IF EXISTS $newDb;")
Invoke-Pg @("-v", "ON_ERROR_STOP=1", "-c", "CREATE DATABASE $newDb;")

Get-Content -Raw $DumpFile | docker compose -f $ComposeFile exec -T postgres `
  psql -U $pgUser -d $newDb -v ON_ERROR_STOP=1

$secs = [int]((Get-Date) - $start).TotalSeconds
$tables = docker compose -f $ComposeFile exec -T postgres `
  psql -U $pgUser -d $newDb -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';"
$tables = ($tables | Out-String).Trim()

Write-Host "RESTORE_OK db=$newDb tables=$tables duration_sec=$secs dump=$DumpFile"
Write-Host "NOTE: Point throwaway API at DATABASE_URL=.../$newDb for smoke; do not use as primary."
