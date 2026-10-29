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

Still later / optional: light blue-green, expand-contract migrate policy, formal SHA rollback drill.
