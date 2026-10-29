# RPO / RTO — MONI (Sprint8)

> SSOT số liệu mục tiêu + đo từ drill. README root chỉ tóm + link file này.

## Mục tiêu (ban đầu)

| Metric | Mục tiêu | Cơ sở |
|--------|----------|--------|
| **RPO** | ≤ **24h** (hoặc ≤ khoảng cách giữa 2 lần dump gần nhất nếu deploy dày hơn) | `pg_dump` trước migrate trong CI deploy + dump tay/script |
| **RTO** | **Đo từ drill** (restore DB riêng + smoke); mục tiêu mềm **≤ 60 phút** ops quen máy | Không claim 5 phút khi chưa đo |

Cập nhật hàng “Đo lần gần nhất” trong [drill_evidence.md](drill_evidence.md) sau mỗi drill.

## Off-host

Backup trên cùng VPS (`/opt/moni/backups`) **không** đủ off-host.

Tối thiểu mỗi chu kỳ drill/prod:

```bash
# Ví dụ: copy ra máy ops (không commit git)
scp user@vps:/opt/moni/backups/moni_YYYYMMDD_HHMMSS.sql ./offhost-backups/
# hoặc rsync / USB / object storage khi có
```

Ghi đường đích + ngày vào `drill_evidence.md`.

## Lệnh nhanh

```bash
# Dump (repo root, .env loaded by script)
./scripts/backup_pg_dump.sh
# Windows:
powershell -File .\scripts\backup_pg_dump.ps1

# Restore drill → DB riêng
./scripts/restore_pg_drill.sh backups/moni_....sql
powershell -File .\scripts\restore_pg_drill.ps1 -DumpFile backups\moni_....sql

# Smoke API (sau khi trỏ app vào DB restore — optional)
powershell -File .\scripts\drill_smoke.ps1
```

## Related

- CI: `.github/workflows/deploy.yml` (dump trước migrate; đã tối ưu load `.env`)
- E2E FE: `.github/workflows/e2e-smoke.yml` + Playwright login smoke
