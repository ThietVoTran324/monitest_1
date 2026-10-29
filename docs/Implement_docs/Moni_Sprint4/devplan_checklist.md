# Dev plan checklist — Moni_Sprint4

**SSOT:** [business_requirement.md](business_requirement.md) · [plan_mode_decisions.md](plan_mode_decisions.md)  
**Trạng thái:** **CLOSED** 2026-10-29 — unit + manual pass

## P0

- [x] Plan #1+#2 CHỐT (T1 = factor + min buffer + first-run)

## P1

- [x] Settings `monitor_stale_factor` + `monitor_stale_min_buffer_seconds`
- [x] `evaluate_monitor_freshness` helper
- [x] Schemas list/detail + dashboard `stale` count
- [x] Wire monitors + dashboard routers
- [x] FE types + badge list/detail/dashboard
- [x] Runtime degraded copy tweak

## P2

- [x] `py -3 -m pytest tests/test_freshness_service.py -q` pass
- [x] Manual freshness / stale badge (stakeholder 2026-10-29)
- [x] Sync sprint_map / macro / T1-M03 FIXED
