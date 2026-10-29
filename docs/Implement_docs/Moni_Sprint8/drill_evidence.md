# Drill evidence — Moni_Sprint8

> Template chứng từ (T7). **Không** commit file `.sql`.

## Lần drill: 2026-10-29 (local)

| Field | Value |
|-------|--------|
| Operator | local Windows / Cursor agent |
| Env | `docker compose` Postgres (fresh volume) + Redis sẵn |
| Dump command | `powershell -File .\scripts\backup_pg_dump.ps1` |
| Dump file | `backups/moni_20261029_121627.sql` (gitignored) |
| Dump duration_sec | **1** |
| Dump bytes | **643** (empty schema DB — drill path OK) |
| Restore command | `powershell -File .\scripts\restore_pg_drill.ps1 -DumpFile backups\moni_20261029_121627.sql` |
| Restore DB name | `moni_restore_20261029_121648` |
| Restore duration_sec | **2** |
| Tables count | **0** (fresh empty DB; path proven) |
| Smoke API | Skip full app-on-restore (empty DB); health path via existing `drill_smoke.ps1` when API up |
| E2E FE | Playwright login smoke **1 passed** + CI `e2e-smoke.yml` |
| Off-host copy | Pending on VPS — local dump kept under `backups/` gitignored; prod: scp per RPO_RTO.md |
| RPO note | Mục tiêu ≤24h; CI dump + script tay |
| RTO measured | restore **2s** + dump **1s** (smoke app not timed on empty DB) |

## Off-host checklist

- [x] Dump không commit vào git (`.gitignore` `backups/`)
- [ ] Copy ngoài VPS volume khi chạy prod (Pending go-live)

## Notes

- Primary DB không bị đè.
- Deploy.yml: `source .env` trước `pg_dump` + `test -s` backup file.
