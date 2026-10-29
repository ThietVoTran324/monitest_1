# Job Market — planning chính

> Hệ thống tuyển dụng / hồ sơ artist trong web gốc (profile employer/artist, CV/JD, apply, work exp + approval).  
> **Thứ tự đã chốt:** sau Phase 0-core; trước Marketplace.  
> **Numbering (chốt 2026-07-26):** Job Market = **Phase 1.1 → 1.6** (trước đây ghi 2.x trong bản explore cũ; map cũ 1.1–1.5 đã được thay).  
> Nguồn phase map: [`../marketplace_jobmarket_feasibility_phase_plan.md`](../marketplace_jobmarket_feasibility_phase_plan.md).

## Mục lục thư mục này

| File | Vai trò |
|------|---------|
| [README.md](README.md) | Mục lục, trạng thái, ranh giới với Implement_docs |
| [phase0_handoff_and_block_classification.md](phase0_handoff_and_block_classification.md) | Phase 0 đã ship gì; block giải quyết ngay vs song song sprint |
| [system_survey.md](system_survey.md) | Khảo sát codebase readiness (backend + Vue) |
| [business_requirement.md](business_requirement.md) | BR cấp hệ thống (~3/10) — D1–D16 đã chốt hướng |
| [sprint_map.md](sprint_map.md) | Map Phase **1.1–1.6** → `JobMarket_Sprint1…6` (**synced**) |
| [`../deferred_and_out_of_scope_backlog.md`](../deferred_and_out_of_scope_backlog.md) | Out of scope / admin-later / defer (toàn planning) |
| [`../security_followups_type1_type2.md`](../security_followups_type1_type2.md) | Security Type1 fixed / Type2 defer |
| [SECURITY_FOLLOWUPS.md](SECURITY_FOLLOWUPS.md) | JM-specific Type2 notes |

## Khi nào dùng thư mục này

- Viết / chốt BR cấp **hệ thống** Job market (không phải từng sprint implement).
- Ghi quyết định nghiệp vụ dài hạn (role artist vs employer, verify work exp, …).
- Map phase 1.1 → 1.6 đã sync; Sprint1–6 **CLOSED**.

## Implement

Mỗi sprint Job market → thư mục riêng dưới `docs/Implement_docs/` (ví dụ `JobMarket_Sprint1/`), bám rule bộ 3 trong `docs/Implement_docs/`.

- Sprint1: [`../../Implement_docs/JobMarket_Sprint1/`](../../Implement_docs/JobMarket_Sprint1/) — **CLOSED** (Alembic `c3d4e5f6a7b8`).
- Sprint2: [`../../Implement_docs/JobMarket_Sprint2/`](../../Implement_docs/JobMarket_Sprint2/) — **CLOSED** (Alembic `d4e5f6a7b8c9`).
- Sprint3: [`../../Implement_docs/JobMarket_Sprint3/`](../../Implement_docs/JobMarket_Sprint3/) — **CLOSED** (Alembic `e5f6a7b8c9d0`).
- Sprint4: [`../../Implement_docs/JobMarket_Sprint4/`](../../Implement_docs/JobMarket_Sprint4/) — **CLOSED** (Alembic `f6a7b8c9d0e1`).
- Sprint5: [`../../Implement_docs/JobMarket_Sprint5/`](../../Implement_docs/JobMarket_Sprint5/) — **CLOSED** (Alembic `a7b8c9d0e1f2`).
- Sprint6: [`../../Implement_docs/JobMarket_Sprint6/`](../../Implement_docs/JobMarket_Sprint6/) — **CLOSED** (Alembic `b8c9d0e1f2a3`).

## Trạng thái

- Marketplace: next was Admin — xem [`../admin/`](../admin/).
- Phase 0-core: **CLOSED**.
- Job Market Sprint1–6: **CLOSED** (Phase 1 complete).
- Marketplace Sprint0–5: **CLOSED**.
- Admin Ops: Plan #1 **DRAFT** — [`../admin/`](../admin/).
