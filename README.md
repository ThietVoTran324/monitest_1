# MONI

Uptime-style website monitoring: HTTP checks, incidents, email alerts, status pages, SSL/domain expiry — built for correctness on a small shared VPS.

| | |
|--|--|
| **Production** | https://monitoring1.io.vn |
| **API health** | https://monitoring1.io.vn/api/v1/health |
| **Host** | `pinvps01` (`116.118.9.162`), path `/opt/moni` |
| **Coexists with** | `https://monitest.top` → `/opt/pinterest` (do not touch) |
| **Repo** | https://github.com/ThietVoTran324/monitest_1 |

## Current status (2026-10-29)

| Area | Status |
|------|--------|
| HTTPS + Caddy (`monitoring1.io.vn` / www) | **Live** |
| Compose stack (api/worker/beat/frontend/postgres/redis) | **Live** (loopback `8010` / `4173`) |
| Alembic head | `d3e4f5a6b7c8` |
| UI smoke (auth / monitor / check) | **OK** |
| CI `migrate-smoke` + GHCR `build-and-push` | On every push to `main` |
| CD SSH → `/opt/moni` | **Off until enabled** (see [CI/CD](#cicd)) |

Hardening wave log: [`docs/Implement_docs/build_history/`](docs/Implement_docs/build_history/) · bugs: [`docs/Implement_docs/bug_history.md`](docs/Implement_docs/bug_history.md)

## What it does

- Register / login (email+password, verify, Google OAuth)
- HTTP monitors: CRUD, schedule, manual run-check, accepted status codes
- Check history, incidents, email alerts (cooldown / still-down / outbox)
- Status pages (private/public) + maintenance notes
- SSL/domain expiry checks and threshold alerts
- Region catalog + `active_region` (one execution region per cycle — not multi-region fanout)
- Runtime health / queue profile (dashboard non-blocking)

**Out of scope (for now):** TCP/ICMP execution, real multi-location agents, WebSocket, Slack/webhooks, multi-tenant billing.

## Tech stack

- **Frontend:** Vue 3, Vue Router, Vite, TypeScript  
- **API:** FastAPI, SQLAlchemy async, Alembic  
- **Data / jobs:** PostgreSQL, Redis, Celery worker + beat  
- **Auth:** JWT access/refresh, SMTP, Google OAuth  
- **Prod:** Docker Compose + **Caddy** (TLS) on shared VPS  
- **CI/CD:** GitHub Actions → GHCR → optional SSH `deploy/deploy_release.sh`

## Repository layout

| Path | Role |
|------|------|
| `backend/` | API, models, Alembic, Celery |
| `frontend/` | SPA |
| `deploy/deploy_release.sh` | Atomic VPS deploy (pull, backup, migrate, health×2, prune) |
| `docker-compose.prod.yml` | Production stack |
| `.env.prod.example` / `.env.images.example` | Env templates (secrets vs image tags) |
| `docs/Planing_docs/moni/` | Macro plan + sprint map |
| `docs/Implement_docs/Moni_Sprint*/` | Per-sprint BR / decisions / checklist |
| `docs/Implement_docs/build_history/` | Go-live / release chronicle |
| `docs/Implement_docs/bug_history.md` | Wave bugs + prevention |
| `planning-docs/` | Older MVP/runbook docs (see GO-LIVE for current host) |
| `scripts/` | Local restart, smoke, backup/restore drills |
| `.github/workflows/` | `deploy.yml` (migrate + build + optional deploy), `e2e-smoke.yml` |

## Architecture (short)

1. API accepts monitor config and user actions.  
2. Beat enqueues due checks; worker runs HTTP probe in `active_region`.  
3. Results → `check_runs`; status snapshot; open/close incidents; email via outbox.  
4. Caddy terminates TLS and proxies `/api/*` → `127.0.0.1:8010`, else → `127.0.0.1:4173`.

## Runtime modes

| Mode | API | Notes |
|------|-----|--------|
| **local-process** (default) | `127.0.0.1:8011` | uvicorn + celery + vite |
| **local-docker** | `127.0.0.1:8010` | full compose |
| **prod** | `127.0.0.1:8010` behind Caddy | `/opt/moni` on `pinvps01` |

SSOT: [`docs/Planing_docs/moni/RUNTIME_MODES.md`](docs/Planing_docs/moni/RUNTIME_MODES.md)

## Local development

Deps:

```bash
docker compose up -d postgres redis
```

Backend:

```bash
cd backend
py -3 -m pip install -e ".[dev]"
py -3 -m alembic upgrade head
py -3 -m uvicorn app.main:app --host 127.0.0.1 --port 8011
```

Worker / beat (separate terminals):

```bash
cd backend
py -3 -m celery -A app.workers.celery_app worker -P solo -l info
py -3 -m celery -A app.workers.celery_app beat -l info
```

Frontend:

```bash
cd frontend
npm install
npx vite --host 127.0.0.1 --port 5173 --strictPort
```

Guarded Windows restart + smoke:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\restart_full_stack.ps1 -ForceKillPortOwners
powershell -ExecutionPolicy Bypass -File .\scripts\check_celery_runtime.ps1 -Strict -Retries 4 -RetryDelaySeconds 2
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_local_gate.ps1
```

## Production on `pinvps01`

- **Domain:** `monitoring1.io.vn` (+ www)  
- **Dir:** `/opt/moni` (`.env`, `.env.images`, `docker-compose.prod.yml`, `backups/`)  
- **Proxy:** Caddy append site — keep `monitest.top` block unchanged  
- **Images:** `ghcr.io/thietvotran324/moni-backend:<sha>` / `moni-frontend:<sha>` (lowercase owner)  
- **Swap:** 2G recommended before first `compose up` on 3.8 GiB RAM host  

Manual bring-up / verify:

```bash
cd /opt/moni
docker compose --env-file .env --env-file .env.images -f docker-compose.prod.yml ps
curl -fsS http://127.0.0.1:8010/api/v1/health
curl -fsS https://monitoring1.io.vn/api/v1/health
```

Details: [`planning-docs/GO-LIVE-PINVPS01.md`](planning-docs/GO-LIVE-PINVPS01.md) · [`docs/Implement_docs/Moni_Sprint0/dns_caddy_golive.md`](docs/Implement_docs/Moni_Sprint0/dns_caddy_golive.md)

## CI/CD

Workflow: [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)

```text
push main
  → migrate-smoke (empty Postgres + alembic upgrade head)
  → build-and-push (GHCR, lowercase image path)
  → deploy (ONLY if ENABLE_PROD_DEPLOY=true)
```

### Is CD on right now?

**No — not until you flip the gate.**  
Deploy is intentionally skipped unless:

1. Repo **Variables:** `ENABLE_PROD_DEPLOY` = `true`  
2. Repo **Secrets:** `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, `GHCR_USERNAME`, `GHCR_TOKEN` (optional `VPS_PORT`) pointing at **`pinvps01`**

Until then: every `main` push still runs migrate + build/push images; SSH deploy does not run (workflow stays green).

Notes: [`docs/Implement_docs/Moni_Sprint9/CI_CD_HARDEN_NOTES.md`](docs/Implement_docs/Moni_Sprint9/CI_CD_HARDEN_NOTES.md)

After enabling CD, first successful deploy pulls tags into `/opt/moni` via `deploy_release.sh` (backup → migrate → recreate app containers → health×2 → prune).

## Backup / RPO

| | |
|--|--|
| RPO target | ≤ 24h (or spacing between deploy dumps) |
| Scripts | `scripts/backup_pg_dump.*`, `restore_pg_drill.*`, `drill_smoke.ps1` |
| SSOT | [`docs/Implement_docs/Moni_Sprint8/RPO_RTO.md`](docs/Implement_docs/Moni_Sprint8/RPO_RTO.md) |

Restore drills use a **separate** DB name — never overwrite primary. Keep dumps under `backups/` (gitignored); copy off-host for real RPO.

## Docs map

| Start here | |
|------------|--|
| Macro hardening plan | [`docs/Planing_docs/moni/upgrade_hardening_phase_plan.md`](docs/Planing_docs/moni/upgrade_hardening_phase_plan.md) |
| Sprint map | [`docs/Planing_docs/moni/sprint_map.md`](docs/Planing_docs/moni/sprint_map.md) |
| Go-live host | [`planning-docs/GO-LIVE-PINVPS01.md`](planning-docs/GO-LIVE-PINVPS01.md) |
| Build / release history | [`docs/Implement_docs/build_history/`](docs/Implement_docs/build_history/) |
| Bug history | [`docs/Implement_docs/bug_history.md`](docs/Implement_docs/bug_history.md) |
| Lesson rules | [`docs/Implement_docs/lessonlearn.md`](docs/Implement_docs/lessonlearn.md) |
| Env conventions | [`planning-docs/ENV-CONVENTIONS.md`](planning-docs/ENV-CONVENTIONS.md) |
| Smoke checklist | [`planning-docs/SMOKE-CHECKLIST.md`](planning-docs/SMOKE-CHECKLIST.md) |
| Older Nginx runbook | `planning-docs/DEPLOY-RUNBOOK-X3MPHIM.md` (**not** for `pinvps01`) |

## Common pitfalls

1. **JWT_SECRET** too weak in production → API refuses to start.  
2. **Google OAuth** redirect must be exactly `https://monitoring1.io.vn/api/v1/auth/google/callback`.  
3. **GHCR tags** must be lowercase (`thietvotran324/...`).  
4. **Alembic ENUM:** do not double-create Postgres types (fixed in `d3e4f5a6b7c8`).  
5. Celery: API only enqueues; need worker (+ beat for schedule). Prefer `scripts/restart_celery_runtime.ps1` locally.  
6. Shared VPS: never `compose` against `/opt/pinterest`; only `/opt/moni`.  
7. TLS right after new Caddy site: wait for ACME “certificate obtained” before declaring failure.

## License / authorship

Private project repo. Prefer commits **without** Cursor co-author trailers on `main`.
