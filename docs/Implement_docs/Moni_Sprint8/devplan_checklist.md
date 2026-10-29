# Dev plan checklist — Moni_Sprint8

**SSOT:** [business_requirement.md](business_requirement.md) · [plan_mode_decisions.md](plan_mode_decisions.md)  
**Trạng thái:** **CLOSED 2026-10-29**

## P0 — Baseline

- [x] `deploy.yml` dump + compose Postgres + gitignore

## P1 — Implement

- [x] **T1** `RPO_RTO.md` + README mục backup/RPO
- [x] **T2** `scripts/backup_pg_dump.sh` + `.ps1`
- [x] **T3** `scripts/restore_pg_drill.sh` + `.ps1`
- [x] **T4** `drill_smoke.ps1` + Playwright e2e + `e2e-smoke.yml` (**1 passed**)
- [x] **T5** off-host trong RPO_RTO + evidence
- [x] **T6** optimize `deploy.yml`
- [x] **T7** `drill_evidence.md` điền
- [x] **T9** gitignore `backups/`
- [x] **T8/T10** dump+restore local OK

## P2 — Prove-done

- [x] Evidence dump 1s / restore 2s
- [x] Playwright login smoke passed
- [x] Sync trio + sprint_map + macro §2.0
