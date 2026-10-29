# Plan mode decisions — Phase0_Sprint1 (TEMPLATE scaffold)

> **Initiative:** Phase0-Sprint1 — Role & capability  
> **Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
> **Trạng thái:** Chưa điền — chỉ được điền sau Plan #1 (BR hoàn thiện) + Plan #2 tech.  
> **Cấm** implement khi file này còn placeholder.

---

## 0. Meta

| | |
|---|---|
| Initiative | Phase0-Sprint1 — Role & capability (block 0.4) |
| Profile Core | Role model + thay hardcode admin + seed/migrate admin cũ |
| Profile Extend | (TBD Plan #1) UI quản trị role đầy đủ? |
| Stack | FastAPI + SQLAlchemy + Alembic + Postgres + Vue (nếu có UI) |
| Nguồn | `business_requirement.md` + phase plan §0.A |
| BR | `business_requirement.md` |
| Devplan | `devplan_checklist.md` |

---

## P0 — Chiến lược

| ID | Quyết định |
|----|------------|
| P0-1 | *(chờ Plan #2)* Gate đóng Core khi… |
| P0-2 | *(chờ)* Runtime / migrate / seed |

---

## D* — Core technical (chờ Plan #2)

| ID | Quyết định |
|----|------------|
| D1 | Schema role — *(TBD: bảng `user_roles` vs `roles`+`user_roles`)* |
| D2 | Danh sách role code — *(TBD)* |
| D3 | Dependency FastAPI `require_role` / `require_capability` — *(TBD)* |
| D4 | Thay `username != "danya"` trong `app/api/rest/admin/routes.py` — *(TBD)* |
| D5 | Seed/migrate admin — *(TBD)* |

---

## Out of scope (đã biết từ phase plan)

- CORS / TrustedHost / CSRF / cookie → Phase0-Sprint2
- Ownership pin/board → Phase0-Sprint2
- Audit log → Phase0-Sprint3
- Job market / Marketplace features
