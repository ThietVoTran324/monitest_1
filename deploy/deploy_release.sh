#!/usr/bin/env bash
# Atomic production deploy on VPS (/opt/moni). Invoked once via CI SSH.
# Required env: BACKEND_IMAGE FRONTEND_IMAGE GHCR_USERNAME GHCR_TOKEN
set -euo pipefail

ROOT="${DEPLOY_ROOT:-/opt/moni}"
cd "$ROOT"

: "${BACKEND_IMAGE:?BACKEND_IMAGE required}"
: "${FRONTEND_IMAGE:?FRONTEND_IMAGE required}"
: "${GHCR_USERNAME:?GHCR_USERNAME required}"
: "${GHCR_TOKEN:?GHCR_TOKEN required}"

COMPOSE=(docker compose --env-file .env --env-file .env.images -f docker-compose.prod.yml)

# Image tags only — do not rewrite secrets in .env
umask 077
cat > .env.images <<EOF
BACKEND_IMAGE=${BACKEND_IMAGE}
FRONTEND_IMAGE=${FRONTEND_IMAGE}
EOF

set -a
# shellcheck disable=SC1091
source .env
set +a
: "${POSTGRES_USER:?POSTGRES_USER missing in ${ROOT}/.env}"
: "${POSTGRES_DB:?POSTGRES_DB missing in ${ROOT}/.env}"

echo "DEPLOY_START backend=${BACKEND_IMAGE} frontend=${FRONTEND_IMAGE}"

echo "${GHCR_TOKEN}" | docker login ghcr.io -u "${GHCR_USERNAME}" --password-stdin

"${COMPOSE[@]}" pull
"${COMPOSE[@]}" up -d postgres redis

mkdir -p "${ROOT}/backups"
BACKUP_FILE="${ROOT}/backups/moni_$(date +%Y%m%d_%H%M%S).sql"
"${COMPOSE[@]}" exec -T postgres \
  pg_dump -U "${POSTGRES_USER}" "${POSTGRES_DB}" > "${BACKUP_FILE}"
test -s "${BACKUP_FILE}"
echo "BACKUP_OK file=${BACKUP_FILE} bytes=$(wc -c < "${BACKUP_FILE}")"

"${COMPOSE[@]}" up -d api
"${COMPOSE[@]}" exec -T api alembic upgrade head
# Recreate app containers so they pick the pulled image tags from .env.images
"${COMPOSE[@]}" up -d --force-recreate --no-deps api worker beat frontend

wait_health() {
  local url="$1"
  local tries="${2:-18}"
  local i
  for i in $(seq 1 "${tries}"); do
    if curl -fsS "${url}" >/dev/null; then
      echo "HEALTH_OK url=${url} attempt=${i}"
      return 0
    fi
    sleep 5
  done
  echo "HEALTH_FAIL url=${url}" >&2
  return 1
}

# Avoid false-positive: require health twice with a gap
sleep 8
wait_health "http://127.0.0.1:8010/api/v1/health" 18
sleep 8
wait_health "http://127.0.0.1:8010/api/v1/health" 6

# Disk hygiene (dangling/unused images only — keeps named tags)
docker image prune -f

echo "DEPLOY_OK"
