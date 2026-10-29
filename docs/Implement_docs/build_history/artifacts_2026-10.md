# Artifacts — wave 2026-10

> Snapshot vận hành / release. Cập nhật khi đổi SHA đang chạy hoặc đóng CD gate.

## GitHub

| Item | Value |
|------|--------|
| Repo | `https://github.com/ThietVoTran324/monitest_1` |
| Default branch | `main` |
| Remote owner (display) | `ThietVoTran324` |
| GHCR path (lowercase) | `ghcr.io/thietvotran324/...` |

### Commits liên quan go-live / CI

| SHA (short) | Ý nghĩa |
|-------------|---------|
| `16a8ef8` | Harden go-live (SSRF, freshness, outbox, deploy script, docs) — **build fail** BH-002 |
| `519f68a` | Fix GHCR lowercase tags — **first successful image push** |
| `937975c` | Fix email_outbox ENUM migration — **in repo; VPS pull Pending** |

Author trên remote (yêu cầu): không có `Co-authored-by: Cursor` (BH-009).

## Container images (GHCR)

| Service | Tag đã chạy trên VPS (2026-10-29) | Tag mục tiêu sau smoke |
|---------|-----------------------------------|-------------------------|
| backend | `ghcr.io/thietvotran324/moni-backend:519f68ae2be2ad9d1b39569a67c2b1981ae88584` | `…:937975cd4d7ebda020c7b85d629f944f6ae99fef` hoặc `:latest` sau build xanh |
| frontend | `ghcr.io/thietvotran324/moni-frontend:519f68ae2be2ad9d1b39569a67c2b1981ae88584` | cùng policy |

Workflow: `.github/workflows/deploy.yml`  
Script VPS: `/opt/moni/deploy_release.sh` ← `deploy/deploy_release.sh`

## Host `pinvps01`

| Item | Value |
|------|--------|
| Public IP | `116.118.9.162` |
| MONI dir | `/opt/moni` |
| Backups | `/opt/moni/backups` |
| Compose | `docker-compose.prod.yml` + `.env` + `.env.images` |
| API bind | `127.0.0.1:8010` |
| FE bind | `127.0.0.1:4173` |
| Swap | `/swapfile` 2G |
| Caddyfile | `/etc/caddy/Caddyfile` (+ `.bak.*`) |
| Cert storage | `/var/lib/caddy/.local/share/caddy/certificates/.../monitoring1.io.vn` |

### Coexist

| App | Path | Public | Upstream |
|-----|------|--------|----------|
| monitest.top | `/opt/pinterest` | `monitest.top` | `127.0.0.1:8080` |
| MONI | `/opt/moni` | `monitoring1.io.vn` | `8010` / `4173` |

## DB

| Item | Value |
|------|--------|
| Engine | Postgres 16 (compose `moni-postgres-1`) |
| Alembic head (prove) | `d3e4f5a6b7c8` |
| Volume | `moni_moni_pgdata` |

## GitHub Actions secrets (gate)

| Secret | Mục đích | Trạng thái 2026-10-29 |
|--------|----------|------------------------|
| `VPS_HOST` | SSH deploy target | **Chưa** trỏ `pinvps01` (BH-006) |
| `VPS_USER` / `VPS_PORT` / `VPS_SSH_KEY` | SSH | Kiểm tra lại khi retarget |
| `GHCR_USERNAME` / `GHCR_TOKEN` | `docker login` trên VPS trong deploy script | Cần có khi bật CD |

## OAuth / SMTP (prod env trên VPS)

| Item | Ghi chú |
|------|---------|
| `APP_BASE_URL` / `API_PUBLIC_URL` | `https://monitoring1.io.vn` |
| Google redirect | `https://monitoring1.io.vn/api/v1/auth/google/callback` |
| SMTP | Gmail app password trong `/opt/moni/.env` (không commit) |
