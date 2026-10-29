#!/usr/bin/env bash
# Dump Postgres for local/prod-like drills. Loads repo-root .env. Output: backups/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p backups

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

: "${POSTGRES_USER:=moni}"
: "${POSTGRES_DB:=moni}"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT="backups/moni_${STAMP}.sql"
START="$(date +%s)"

if docker compose ps postgres 2>/dev/null | grep -q "Up\|running"; then
  docker compose exec -T postgres \
    pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$OUT"
elif docker ps --format '{{.Names}}' | grep -qE 'postgres|moni.*pg'; then
  # Fallback: first matching container name
  CID="$(docker ps --format '{{.Names}}' | grep -E 'postgres|moni' | head -1)"
  docker exec -i "$CID" pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$OUT"
else
  echo "No running compose postgres; trying host pg_dump" >&2
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$OUT"
fi

END="$(date +%s)"
BYTES="$(wc -c < "$OUT" | tr -d ' ')"
echo "BACKUP_OK file=$OUT bytes=$BYTES duration_sec=$((END - START))"
