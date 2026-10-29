# MONI — planning chính (hardening + go-live)

> Stream **MONI** trong cùng khung `Planing_docs` / `Implement_docs` của repo docs.  
> **Không** trộn với marketplace / job_market / admin (các stream CLOSED của dự án khác).

## Mục lục

| File | Vai trò |
|------|---------|
| [README.md](README.md) | Index |
| [upgrade_hardening_phase_plan.md](upgrade_hardening_phase_plan.md) | **SSOT vĩ mô** — context, survey, phase/sprint map, DoD |
| [RUNTIME_MODES.md](RUNTIME_MODES.md) | Ports / 3 runtime modes (Sprint0 SSOT) |
| [sprint_map.md](sprint_map.md) | Bảng sprint + dependency |
| [deferred_and_out_of_scope_backlog.md](deferred_and_out_of_scope_backlog.md) | OUT / defer / chốt giữ |
| [security_followups_type1_type2.md](security_followups_type1_type2.md) | Security T1/T2 |

## Implement_docs

| Folder | Phase | Plan status |
|--------|-------|-------------|
| [`../../Implement_docs/Moni_Sprint0/`](../../Implement_docs/Moni_Sprint0/) | H0 Foundation | **DONE** 2026-10-29 (VPS Pending) |
| [`../../Implement_docs/Moni_Sprint1/`](../../Implement_docs/Moni_Sprint1/) | H1 SSRF | **DONE** 2026-10-27 |
| [`../../Implement_docs/Moni_Sprint2/`](../../Implement_docs/Moni_Sprint2/) | H1 Consistency | **DONE** 2026-10-27 |
| [`../../Implement_docs/Moni_Sprint3/`](../../Implement_docs/Moni_Sprint3/) | H2 Load prove | Plan #1 **OPEN** |
| [`../../Implement_docs/Moni_Sprint4/`](../../Implement_docs/Moni_Sprint4/) | H1 Stale | **DONE** 2026-10-28 |
| [`../../Implement_docs/Moni_Sprint5/`](../../Implement_docs/Moni_Sprint5/) | H1 Region honesty | Plan #1 **OPEN** |
| [`../../Implement_docs/Moni_Sprint6/`](../../Implement_docs/Moni_Sprint6/) | H1 Email outbox | **DONE** 2026-10-29 |
| [`../../Implement_docs/Moni_Sprint7/`](../../Implement_docs/Moni_Sprint7/) | H2 Retention | Plan #1 **OPEN** |
| [`../../Implement_docs/Moni_Sprint8/`](../../Implement_docs/Moni_Sprint8/) | H0 Backup | **DONE** 2026-10-29 |
| [`../../Implement_docs/Moni_Sprint9/`](../../Implement_docs/Moni_Sprint9/) | H2 Release | Plan #1 **OPEN** |
| [`../../Implement_docs/Moni_Sprint10/`](../../Implement_docs/Moni_Sprint10/) | H1 Status privacy | **DONE** 2026-10-27 |
| [`../../Implement_docs/Moni_Sprint11/`](../../Implement_docs/Moni_Sprint11/) | H1 SSL clarity | Plan #1 **OPEN** |
| [`../../Implement_docs/Moni_Sprint12/`](../../Implement_docs/Moni_Sprint12/) | H1 Quota | Plan #1 **OPEN** |

Mỗi folder: `PLANNING_TRIO.md` · `base requirement.md` · `business_requirement.md` · `plan_mode_decisions.md` · `devplan_checklist.md`.

## Rules

- [`../../Implement_docs/lessonlearn.md`](../../Implement_docs/lessonlearn.md) — áp dụng hết  
- [`../../Implement_docs/issues_history.md`](../../Implement_docs/issues_history.md) — log sự cố  

## Quyết định hệ thống (rút)

Xem macro plan §6 (D1–D10). Tóm: GL = 1 region thật + S5 honesty; multi-region target = **Lambda** (plumbing sẵn, env bật sau); Caddy `pinvps01`; P0 H1 một phần DONE.

## Trạng thái

| Hạng mục | Status |
|----------|--------|
| Macro plan | **LIVE** — §2.0 status 2026-10-29 |
| Sprint scaffold 0–12 | **DONE** 2026-10-27 |
| DONE | S0, S1, S2, S4, S6, S8, S10 |
| Next | **Go-live gate** (VPS) rồi Plan #1 **Moni_Sprint12** |
