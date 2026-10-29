# Dev plan checklist — Moni_Sprint10

**SSOT:** [business_requirement.md](business_requirement.md) · [plan_mode_decisions.md](plan_mode_decisions.md)  
**Trạng thái:** **CLOSED** 2026-10-27 — unit + manual pass

## P0

- [x] Plan #1+#2 CHỐT

## P1 — Implement

- [x] Schemas: public monitor/incident tách; owner giữ url
- [x] Public router: rate limit IP 60/60s; public DTO
- [x] Settings `public_status_rate_limit_*`
- [x] FE public types + view bỏ URL/reason
- [x] Ownership cross-user tests
- [x] Exception handler giữ `Retry-After` trên 429

## P2 — Prove-done

- [x] `py -3 -m pytest tests/test_status_pages_api.py -q` → 3 passed
- [x] Manual public slug — no URL (stakeholder 2026-10-27)
- [x] Sync sprint_map / macro / T1-M02 FIXED
