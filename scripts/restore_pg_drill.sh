#!/usr/bin/env bash
# Restore a dump into a NEW database moni_restore_<ts> (does not overwrite primary DB).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DUMP="${1:-}"
if [[ -z "$DUMP" || ! -f "$DUMP" ]]; then
  echo "Usage: $0 backups/moni_YYYYMMDD_HHMMSS.sql" >&2
  exit 1
fi

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

: "${POSTGRES_USER:=moni}"
: "${POSTGRES_DB:=moni}"
STAMP="$(date +%Y%m%d_%H%M%S)"
NEW_DB="moni_restore_${STAMP}"
START="$(date +%s)"

run_psql() {
  docker compose exec -T postgres psql -U "$POSTGRES_USER" -d postgres "$@"
}

run_psql -v ON_ERROR_STOP=1 -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${NEW_DB}' AND pid <> pg_backend_pid();" || true
run_psql -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS ${NEW_DB};"
run_psql -v ON_ERROR_STOP=1 -c "CREATE DATABASE ${NEW_DB};"

docker compose exec -T postgres \
  psql -U "$POSTGRES_USER" -d "$NEW_DB" -v ON_ERROR_STOP=1 < "$DUMP"

END="$(date +%s)"
TABLES="$(docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$NEW_DB" -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';")"
echo "RESTORE_OK db=${NEW_DB} tables=${TABLES} duration_sec=$((END - START)) dump=${DUMP}"
echo "NOTE: Point a throwaway API at DATABASE_URL=.../${NEW_DB} for smoke; do not use as primary."
