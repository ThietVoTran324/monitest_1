# MONI — runtime modes (SSOT ports / env)

> Linked from root `README.md`. Sprint0 Plan #2 **T3 A+C**.

## Mode table

| Mode | Processes | DB / Redis hostnames | API port | When |
|------|-----------|----------------------|----------|------|
| **local-process** (default) | uvicorn + celery worker/beat + vite on host | `localhost` (compose deps OK) | **8011** | Day-to-day Windows/macOS/Linux dev |
| **local-docker** | optional full app compose | `postgres` / `redis` service names | **8010** | Prove gần prod khi cần |
| **prod** | `docker-compose.prod.yml` on VPS | `postgres` / `redis` | **127.0.0.1:8010** + Caddy | Go-live `pinvps01` |

**Không** dùng `8000` làm API MONI trong docs/example/script chính (tránh drift với stack cũ / app khác).

## Env files

| File | Role |
|------|------|
| `.env` | Local secrets (gitignored); copy from `.env.example` |
| `.env.example` | Local-process template — `API_PUBLIC_URL` / OAuth → **8011** |
| `.env.prod.example` | Prod template — public URL = domain; container Redis `redis://redis:6379/0` |

Keep `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` aligned.

## Local deps compose

```bash
docker compose up -d postgres redis
docker compose ps
docker compose exec redis redis-cli ping   # → PONG
```

If `Bind for 0.0.0.0:6379 failed: port is already allocated`, another Redis (e.g. legacy `moni-redis`) already serves local-process — keep it, or stop/remove it then re-run compose. Prove: `redis-cli -h 127.0.0.1 ping` → `PONG`.

App code still runs on the host in **local-process** (macro D2). Full app images are optional.

## Scripts (local-process)

| Script | Default API |
|--------|-------------|
| `scripts/restart_full_stack.ps1` | `-BackendPort 8011` (override if needed) |
| `scripts/smoke_local_gate.ps1` | `http://127.0.0.1:8011` |
| `scripts/restart_celery_runtime.ps1` | (no HTTP port; uses same `.env` Redis) |

Docker/prod health checks use **8010** (`docker-compose.prod.yml`, deploy workflow).

## Prod host notes (Sprint0)

- Target VPS: `pinvps01` — see `server-context.md`, `planning-docs/GO-LIVE-PINVPS01.md`
- Prep checklist: [`../../Implement_docs/Moni_Sprint0/vps_prep_checklist.md`](../../Implement_docs/Moni_Sprint0/vps_prep_checklist.md)
- **Do not** retarget GitHub `VPS_HOST` until smoke-on-host passes
- Proxy on this VPS is **Caddy** (not host Nginx from older runbooks)

## Related

- Macro: [upgrade_hardening_phase_plan.md](upgrade_hardening_phase_plan.md)
- Keep: local **8011** vs compose **8010** ([deferred KEEP-02](deferred_and_out_of_scope_backlog.md))
