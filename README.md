# MONI

**Live demo:** https://monitoring1.io.vn

Uptime-style website monitoring: HTTP checks, incidents, email alerts, status pages, SSL/domain expiry — built for correctness on a small shared VPS.

## Current status

| Area | Status |
|------|--------|
| HTTPS + Caddy (`monitoring1.io.vn` / www) | **Live** |
| Compose stack (api/worker/beat/frontend/postgres/redis) | **Live** (loopback `8010` / `4173`) |
| Alembic head | `d3e4f5a6b7c8` |
| UI smoke (auth / monitor / check) | **OK** |
| CI `migrate-smoke` + GHCR `build-and-push` | On every push to `main` |
| CD SSH → `/opt/moni` | Gated by `ENABLE_PROD_DEPLOY` + deploy secrets |

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

## CI/CD

Workflow: [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)

```text
push main
  → migrate-smoke (empty Postgres + alembic upgrade head)
  → build-and-push (GHCR, lowercase image path)
  → deploy (if ENABLE_PROD_DEPLOY=true and secrets set)
```

Notes: [`docs/Implement_docs/Moni_Sprint9/CI_CD_HARDEN_NOTES.md`](docs/Implement_docs/Moni_Sprint9/CI_CD_HARDEN_NOTES.md) · go-live: [`planning-docs/GO-LIVE-PINVPS01.md`](planning-docs/GO-LIVE-PINVPS01.md)

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
