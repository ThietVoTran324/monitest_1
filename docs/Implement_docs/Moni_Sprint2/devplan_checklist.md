# Dev plan checklist — Moni_Sprint2

**SSOT:** [business_requirement.md](business_requirement.md) · [plan_mode_decisions.md](plan_mode_decisions.md)  
**Trạng thái:** **DONE** 2026-10-27

## P0 — Baseline

- [x] Plan #1+#2 CHỐT (all suggest)
- [x] Baseline alembic head `b3c4d5e6f7a8` → `c2d3e4f5a6b7`

## P1 — Implement

- [x] Migration: close duplicate OPEN + partial unique index
- [x] `Incident` model `__table_args__` index
- [x] `apply_check_result` service (FOR UPDATE, stale `<=`, open/reuse/close)
- [x] Wire `_check_http_monitor_async` — alerts after commit
- [x] Log `stale_check_skipped`

## P2 — Prove-done

- [x] Unit/IT: stale skip; equal timestamp stale; open/reuse/recover; unique index
- [x] `py -3 -m pytest tests/test_check_apply_service.py tests/test_checks_logic.py tests/test_ssrf_guards.py -q` pass
- [x] Sync trio + sprint_map + macro + T1-M04 FIXED
