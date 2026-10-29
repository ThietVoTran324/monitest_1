# Dev plan checklist — Moni_Sprint6

**SSOT:** [business_requirement.md](business_requirement.md) · [plan_mode_decisions.md](plan_mode_decisions.md)  
**Trạng thái:** **CLOSED 2026-10-29** (chạy `alembic upgrade` + seed admin trên môi trường)

## P0 — Baseline

- [x] notify/apply/AlertEvent + User model

## P1 — Implement

- [x] Migration `d3e4f5a6b7c8` — outbox, `is_admin`, monitor overrides
- [x] Settings global backoff/max
- [x] Insert pending apply/expiry + `process_email_outbox` beat
- [x] Admin API outbox/retry/override + grant-admin (tag `admin-internal`)
- [x] FE `/admin/email-outbox`
- [x] `scripts/seed_admin.sql`
- [x] Unit tests outbox (3 passed)

## P2 — Prove-done

- [x] Tests pass
- [x] Sync trio / sprint_map / macro
- [ ] Ops: `alembic upgrade head` + seed first admin
