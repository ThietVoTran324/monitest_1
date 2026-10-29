# Dump Postgres for local drills. Loads repo-root .env. Output: backups/
Param(
  [string]$ComposeFile = "docker-compose.yml"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
New-Item -ItemType Directory -Force -Path (Join-Path $Root "backups") | Out-Null

$envFile = Join-Path $Root ".env"
$pgUser = "moni"
$pgDb = "moni"
if (Test-Path $envFile) {
  Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*POSTGRES_USER=(.*)$') { $pgUser = $Matches[1].Trim().Trim('"') }
    if ($_ -match '^\s*POSTGRES_DB=(.*)$') { $pgDb = $Matches[1].Trim().Trim('"') }
  }
}

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$out = Join-Path $Root "backups\moni_$stamp.sql"
$start = Get-Date

$composeOk = $false
try {
  $ps = docker compose -f $ComposeFile ps postgres 2>$null | Out-String
  if ($ps -match "running|Up") { $composeOk = $true }
} catch { }

if ($composeOk) {
  cmd /c "docker compose -f `"$ComposeFile`" exec -T postgres pg_dump -U $pgUser $pgDb > `"$out`""
} else {
  $names = docker ps --format "{{.Names}}"
  $cid = ($names | Where-Object { $_ -match "postgres" } | Select-Object -First 1)
  if (-not $cid) { throw "No postgres container running. Start: docker compose up -d postgres" }
  cmd /c "docker exec -i $cid pg_dump -U $pgUser $pgDb > `"$out`""
}

$secs = [int]((Get-Date) - $start).TotalSeconds
$len = (Get-Item $out).Length
Write-Host "BACKUP_OK file=$out bytes=$len duration_sec=$secs"
