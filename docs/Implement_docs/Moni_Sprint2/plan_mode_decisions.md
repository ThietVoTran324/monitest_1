# Plan mode decisions — Moni_Sprint2

> **BR:** [business_requirement.md](business_requirement.md)  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **CHỐT 2026-10-27** — T1–T10 **all suggest**

## 0. Meta

| | |
|---|---|
| Baseline | alembic head `b3c4d5e6f7a8` → + Sprint2 migration |
| Target | Stale reject + partial unique 1 OPEN + apply service + tests |

## D* — Core decisions (T1–T10)

| ID | Chủ đề | **CHỐT** |
|----|--------|----------|
| **T1** | Stale compare | `finished_at <= last_checked_at` → skip apply (`=` cũng stale) |
| **T2** | DB unique | Partial unique index `(monitor_id) WHERE status = 'open'` |
| **T3** | Lock | `SELECT monitor … FOR UPDATE` trong txn apply |
| **T4** | Order | Insert `check_run` → lock → stale? → update monitor → open/reuse/close incident |
| **T5** | Observability | Log `stale_check_skipped`; không cột API/`ignored_as_stale` |
| **T6** | Code shape | `apply_check_result` service — unit-testable |
| **T7** | Alert open | `incident_opened` chỉ sau insert OPEN thành công; không sau reuse/conflict |
| **T8** | Prove | Unit/integration script; không bắt 2 Celery process |
| **T9** | Migration data | Đóng OPEN thừa (giữ `opened_at` mới nhất) trước khi tạo index |
| **T10** | Scope files | checks apply path + Incident constraint + Alembic + tests; không Sprint4/6 |

## Alert dispatch

Thu thập alert actions trong apply; **`send_incident_email.delay` sau `commit`** để tránh mail khi rollback.
