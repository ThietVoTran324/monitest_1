# MONI go-live — shared VPS `pinvps01`

Status date: **2026-10-29** (host wiring largely done). Machine facts originally from `server-context.md` (2026-10-26).

**Live now:** FQDN `monitoring1.io.vn` on `pinvps01`, Caddy + TLS, compose `/opt/moni`, loopback `8010`/`4173`.  
**Still open:** UI smoke, pull image with migration fix, retarget GitHub `VPS_HOST`.  
**Wave docs:** `docs/Implement_docs/build_history/`, `docs/Implement_docs/bug_history.md`.

This file remains the host go-live plan. Older runbooks still describe a different host and proxy:

- `planning-docs/DEPLOY-RUNBOOK-X3MPHIM.md` targets `x3mphim.click` behind **host Nginx + Certbot**, and tells the operator not to touch `myauction.fun`.
- A previous MONI deploy (April 2026) used another VPS path (`/opt/moni/monitest_1`) and host Nginx.
- Neither of those layouts is the machine in `server-context.md`.

## 1) What the codebase already is

Product code for the upgrade cycle is implemented. Go-live work is host wiring, not a new feature phase.

Shipped and covered by migrations, API, worker, and UI:

- Auth: email/password, email verify, Google OAuth, JWT access/refresh.
- HTTP monitors: create/edit/pause/delete, manual run-check, scheduled checks.
- Check history, uptime window, incidents, email alerts.
- Per-monitor `accepted_status_codes`.
- Alert policy: cooldown, still-down reminder, max reminders, dedupe.
- Status pages: private/public, monitor mapping, maintenance notes.
- SSL and domain expiry checks, summary, threshold alerts at 30/14/7/1 days.
- Region catalog (`probe_regions`), mapping (`monitor_regions`), one `active_region` per check cycle.
- Runtime health and queue profile, dashboard does not block on them.
- Production compose: `postgres`, `redis`, `api`, `worker`, `beat`, `frontend`.
- GitHub Actions builds GHCR images and deploys over SSH to `/opt/moni`, then runs Alembic inside the live `api` container.

Explicitly not in this go-live:

- TCP and ICMP checks (schema exists, HTTP is the shipped type).
- Real multi-location probe agents. Extra regions are configuration; only `active_region` runs.
- WebSocket updates. UI polls.
- Slack/webhook alerts. Email only.

Local vs production ports stay split on purpose:

- Local API default: `127.0.0.1:8011` (Windows dev stability).
- Compose API: `127.0.0.1:8010`.
- Compose frontend: `127.0.0.1:4173`.

## 2) Target machine

| Item | Value |
|---|---|
| Host | `pinvps01`, login `root` |
| CPU | 2 |
| RAM | 3.8 GiB, **no swap** |
| RAM available at measure time | **1.9 GiB** |
| Disk `/` | 50 GB, about 19 GB free |
| Public proxy | **Caddy** (`/etc/caddy/Caddyfile`, 72 bytes, not read yet) |
| Site already on this host | `https://monitest.top` and `www.monitest.top` |
| That site's code | `/opt/pinterest` (not MONI) |
| Containers already up | API, Celery worker, Celery beat, Postgres 15, Redis, Vue, plus unused RabbitMQ, MongoDB, Mailhog |
| Host ports already published | `8080` (that app's UI), `8025` (Mailhog) |

`monitest.top` on this VPS is the other product. MONI is not running here. Do not deploy MONI into `/opt/pinterest`, and do not reuse that compose project, database, or Redis.

## 3) Fit on a shared box

MONI production is six containers, bound only to loopback:

- `127.0.0.1:8010` API
- `127.0.0.1:4173` frontend

Those ports do not clash with `8080` or `8025`. Postgres, Redis, worker, and beat stay on the Docker network.

Rough memory, from `server-context.md`, for the current app with about 10 users plus MONI watching about 10 URLs:

- Existing containers idle about 775 MiB, about 1.0–1.2 GiB with light use.
- MONI idle about 0.6–0.8 GiB. RAM sits in the always-on processes, not in the URL count.
- Together about 2.5–3.0 GiB of 3.8 GiB, leaving about 1.1–1.3 GiB available.
- Ten healthy HTTP checks per minute are about 1–5% of one CPU. Worker concurrency follows `nproc` (2). Prefetch is already `1`.

Disk is enough for a first image pull and a small Postgres volume. It is not enough to keep unlimited backups.

Risk that blocks a careless cutover: **no swap**. One memory spike kills a process. Add a small swapfile before the first MONI start, and do not raise Celery concurrency.

## 4) Decisions still open

1. **MONI public hostname.** Not chosen. It cannot be `monitest.top` on this machine. OAuth redirect, `APP_BASE_URL`, `API_PUBLIC_URL`, and the Caddy site block all wait on this name.
2. **Caddyfile contents.** Still unread. Read it before adding a site. Do not replace the file.
3. **How deploy reaches this host.** `.github/workflows/deploy.yml` SSHs to `secrets.VPS_HOST` and `cd /opt/moni`. Those secrets may still point at the April VPS. Do not push a deploy until secrets and `/opt/moni/.env` exist on `pinvps01`.

## 5) Go-live sequence

Do these in order. Stop if a step would restart Caddy, touch `/opt/pinterest`, or publish a port other than loopback.

1. Read the live proxy config and confirm the existing site block:
   - `cat /etc/caddy/Caddyfile`
2. Add 1–2 GiB swap. Confirm `free -h` shows swap before starting MONI.
3. Create `/opt/moni` and `/opt/moni/backups` only.
4. Place `docker-compose.prod.yml` and a filled `.env` from `.env.prod.example`:
   - `APP_ENV=production`
   - `APP_BASE_URL` and `API_PUBLIC_URL` = `https://<moni-domain>`
   - `GOOGLE_OAUTH_REDIRECT_URI` = `https://<moni-domain>/api/v1/auth/google/callback`
   - strong `JWT_SECRET`
   - SMTP credentials
   - `BACKEND_IMAGE` / `FRONTEND_IMAGE` GHCR tags
   - DB and Redis URLs stay on the compose service names (`postgres`, `redis`), not the other project's containers
5. `docker compose --env-file .env -f docker-compose.prod.yml up -d`
6. `docker compose ... exec -T api alembic upgrade head`
7. Confirm loopback only:
   - `curl -fsS http://127.0.0.1:8010/api/v1/health`
   - frontend answers on `127.0.0.1:4173`
   - `ss` shows `8010` and `4173` on `127.0.0.1`, not `0.0.0.0`
8. Append one Caddy site for `<moni-domain>`:
   - `/api/*` → `127.0.0.1:8010`
   - everything else → `127.0.0.1:4173`
   - leave the `monitest.top` block unchanged
   - `caddy validate` then reload
9. Point DNS at this VPS. Let Caddy obtain the certificate. Do not run Certbot/Nginx for MONI on this host.
10. Register the Google OAuth redirect for the new domain.
11. Smoke: register or login, create one HTTP monitor, confirm a check row, open dashboard, open a private status page, hit public slug only when `is_public=true`.
12. Only after the manual path is green, point GitHub `VPS_HOST` / SSH key at `pinvps01` so later `main` pushes update `/opt/moni`.

## 6) What not to do

- Do not stop RabbitMQ, MongoDB, or Mailhog as part of the MONI cutover. They are unused by the other app's request path, but removing them is a separate cleanup.
- Do not bind MONI Postgres or Redis to a host port.
- Do not set Celery `--concurrency` above 2 on this box.
- Do not treat `planning-docs/DEPLOY-RUNBOOK-X3MPHIM.md` as the procedure for `pinvps01`.
