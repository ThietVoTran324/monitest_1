# CI/CD harden notes (wave go-live)

Ship in repo (2026-10-29):

| Gap | Mitigation |
|-----|------------|
| Build on VPS | Still GitHub-hosted build → GHCR only |
| sed full `.env` | Tags → `.env.images`; secrets stay in `.env` |
| SSH half-applied | Single `deploy/deploy_release.sh` via `script_path` |
| False health | Sleep + health curl loop **twice** |
| Disk full images | `docker image prune -f` after success |
| Backup before migrate | Unchanged (`pg_dump` + `test -s`) |
| GHCR mixed-case owner | Lowercase `repository_owner` before tag (BH-002) |
| Migrate ENUM on empty DB | `migrate-smoke` job + Alembic ENUM fix (BH-004) |
| Deploy đỏ khi chưa sẵn sàng | Job `deploy` chỉ chạy nếu `vars.ENABLE_PROD_DEPLOY=true` |
| Deploy thiếu secret | Step “Require deploy secrets” fail rõ trước SSH |

## Bật CD lên `pinvps01` (sau smoke UI)

1. Repo **Settings → Secrets**: `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, `GHCR_USERNAME`, `GHCR_TOKEN` (+ optional `VPS_PORT`).  
2. Repo **Settings → Variables**: `ENABLE_PROD_DEPLOY` = `true`.  
3. Chạy **Actions → Deploy Production** (workflow_dispatch) hoặc push `main`.  
4. Kỳ vọng: `migrate-smoke` → `build-and-push` → `deploy` đều xanh.

Trên VPS trước lần CD đầu: `/opt/moni` đã có `.env`, `docker-compose.prod.yml`, `deploy_release.sh` (đã có từ go-live tay).

## Vẫn optional / sau

Light blue-green, expand-contract migrate policy, formal SHA rollback drill (Sprint9 Plan).
