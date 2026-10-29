# Plan mode decisions — Moni_Sprint8

> **BR:** [business_requirement.md](business_requirement.md)  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **CHỐT 2026-10-29** — T1 A+C; T2 A; T3 A; T4 A+C; T5 A; **T6 A+B (optimize, không rewrite hết)**; T7–T10 A

## 0. Meta

| | |
|---|---|
| Target | Dump/restore drill scripts; RPO/RTO docs (sprint + README); smoke + Playwright CI; off-host; evidence; gitignore; deploy.yml tối ưu tránh drift |

## D* — Core

| ID | **CHỐT** |
|----|----------|
| **T1** | **A+C song song:** `Moni_Sprint8/RPO_RTO.md` **và** mục ngắn trong root `README.md` (link chi tiết) |
| **T2** | `scripts/backup_pg_dump.sh` (+ `.ps1` Windows) đọc `.env` → `backups/` |
| **T3** | `scripts/restore_pg_drill.sh` (+ `.ps1`): DB `moni_restore_<ts>`, restore, đo thời gian |
| **T4** | **A+C:** smoke drill (health/login/schema) **và** Playwright (hoặc gate tương đương) trong CI / script e2e tối thiểu |
| **T5** | Doc + lệnh off-host copy; template chứng từ |
| **T6** | **A+B optimize:** giữ `pg_dump` trước migrate; chỉnh `deploy.yml` gọn, tránh drift env/path/backup — **không** viết lại toàn bộ pipeline |
| **T7** | `drill_evidence.md` template + 1 lần điền sau chạy |
| **T8** | Drill mặc định local `docker compose` Postgres; DB name riêng |
| **T9** | `backups/*.sql` (và compressed) trong `.gitignore` |
| **T10** | 1 drill local + evidence + scripts trong repo = prove tối thiểu |

### T6 — Deploy optimize (không rewrite)

Giữ flow hiện tại; chỉ siết:
- Backup path/`POSTGRES_*` từ `.env` rõ ràng
- Comment trỏ Sprint8 drill docs
- Tránh hardcode lệch compose file / env-file
- Không đổi `VPS_HOST` / không thêm HA
