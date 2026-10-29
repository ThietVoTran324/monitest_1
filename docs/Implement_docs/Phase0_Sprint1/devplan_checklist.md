# Dev plan checklist — Phase0_Sprint1 (Role & capability)

**Initiative:** Phase0-Sprint1 — Role & capability (Phase 0-core block 0.4)  
**SSOT nghiệp vụ:** [business_requirement.md](business_requirement.md) (BR hoàn thiện, Plan #1 chốt 2026-07-25)  
**SSOT kỹ thuật:** file này (đã thống nhất **bỏ qua** `plan_mode_decisions.md` / `requirement_gap_debate.md` cho sprint này — quyết định tech T1–T12 ghi ngay dưới)  
**Phase map:** [`../../Planing_docs/marketplace_jobmarket_feasibility_phase_plan.md`](../../Planing_docs/marketplace_jobmarket_feasibility_phase_plan.md) §0.B  
**Gate vào:** BR hoàn thiện ✅ + quiz tech Plan #2 đã chốt ✅  
**Trạng thái:** **CLOSED** — implement + prove-done 2026-07-25 (`scripts/smoke_phase0_sprint1.py` → `ALL_SMOKE_PASS`; alembic head `a1b2c3d4e5f6`).

---

## Quy ước

- Chỉ tick `[x]` khi có **prove-done runtime** (migrate/smoke/curl), không tick theo cảm giác.
- **Hard stop:** step hiện tại chưa pass verify → không sang step sau.
- Dòng `[ ]` / `[x]` = task; dòng `+` = tiêu chí/validation (không tick riêng).
- Guide của step đang làm phải đọc trước khi sửa source.

---

## Quyết định kỹ thuật đã chốt (Plan #2 quiz)

| ID | Quyết định |
|----|------------|
| T1 | Bảng nối `user_roles(user_id, role)`, `role` là string cố định (`admin\|artist\|employer\|seller`), unique/PK `(user_id, role)` |
| T2 | Role mặc định gắn ở **mọi** đường tạo user Postgres chính (register, Google OAuth, `create-user-entity`) qua helper `ensure_default_roles(db, user_id)` |
| T3 | **Một** Alembic revision: tạo bảng + backfill toàn bộ user → `artist` + gán `admin` cho bootstrap username (idempotent-ish) |
| T4 | Bootstrap admin lấy từ env `BOOTSTRAP_ADMIN_USERNAME` (default `danya` cho local); **route không đọc username** |
| T5 | Helper `require_roles(...)` dạng FastAPI `Depends`, đặt trong `app/api/rest/dependencies.py` (hoặc module nhỏ import vào đó) |
| T6 | Xóa hẳn so sánh `username != "danya"` trong admin routes; thay bằng `require_roles("admin")` |
| T7 | `POST /admin/users/{id}/roles` (body `{"role": "..."}`) + `DELETE /admin/users/{id}/roles/{role}`; **chặn self-modify role** (caller ≠ target) |
| T8 | `GET /users/me/roles` nhẹ để debug/AC (không UI) |
| T9 | **Không** nhúng roles vào JWT — query DB mỗi lần cần (giữ token/login như hiện tại) |
| T10 | **Không sửa frontend Vue** trong sprint này |
| T11 | Thứ tự step: runtime → model+migration → helper → default role → wire admin → API role → me/roles → prove-done → đóng doc |
| T12 | Prove-done = migrate up sạch + smoke curl theo AC-01…10 + grep sạch hardcode |

**Delivered paths**

| Vùng | Path |
|------|------|
| Model | `app/postgresql/models.py` → `UserRolesOrm` |
| Migration | `app/migrations/versions/a1b2c3d4e5f6_add_user_roles.py` |
| Helpers | `app/api/rest/roles.py` |
| Depends | `app/api/rest/dependencies.py` → `require_roles` |
| Admin | `app/api/rest/admin/routes.py` |
| Register / me/roles | `app/api/rest/users/routes.py` |
| Google OAuth | `app/api/rest/users_google_auth/routes.py` |
| Env | `BOOTSTRAP_ADMIN_USERNAME` in `app/config.py`, `.env`, `.env.example` |
| Smoke | `scripts/smoke_phase0_sprint1.py` |

---

## P0 — Chuẩn bị / xác nhận runtime

- [x] Đọc BR hoàn thiện + bảng T1–T12 ở trên
- [x] Stack dev up được; baseline trước migrate = `d948933f5835`
- [x] Ghi lại số user hiện có trong DB trước backfill (= 1)

+ Prove-done: 2026-07-25 · `alembic current` trước upgrade = `d948933f5835`; Docker stack up; FastAPI health 200.

---

## P1 — Model + Alembic revision (T1, T3, T4)

- [x] Thêm model `UserRolesOrm` vào `app/postgresql/models.py`
- [x] Thêm `BOOTSTRAP_ADMIN_USERNAME` vào `app/config.py` + `.env` + `.env.example`
- [x] Revision `a1b2c3d4e5f6` (down_revision = `d948933f5835`): create table + backfill `artist` + bootstrap `admin`
- [x] `alembic upgrade head` chạy sạch

+ Prove-done: 2026-07-25 · `alembic upgrade head` → `a1b2c3d4e5f6 (head)`; `scripts/check_user_roles.py` → users=1, roles=[('artist', 1)] (không có user `danya` local nên không có admin bootstrap — đúng T4).

---

## P2 — Helper role: đọc + require (T5, T9)

- [x] `get_user_roles` / `ensure_default_roles` / `assign_role` / `revoke_role` trong `app/api/rest/roles.py`
- [x] `require_roles(...)` trong `app/api/rest/dependencies.py`
- [x] Hằng `VALID_ROLES`

+ Prove-done: 2026-07-25 · import + FastAPI startup complete; smoke dùng helper qua API.

---

## P3 — Gán role mặc định khi tạo user (T2)

- [x] `ensure_default_roles` trong `register_user` (cả 2 nhánh)
- [x] `ensure_default_roles` trong `create_user_entity`
- [x] `ensure_default_roles` trong Google OAuth khi tạo user mới

+ Prove-done: 2026-07-25 · smoke AC-01: register → `GET /users/me/roles` = `["artist"]`.

---

## P4 — Wire admin moderation theo role (T6)

- [x] Xóa hardcode `username != "danya"` ở cả 2 admin delete routes
- [x] Thêm `Depends(require_roles("admin"))`
- [x] `rg "danya" app/api/rest/` → không còn (bootstrap chỉ còn env/config/migration)

+ Prove-done: 2026-07-25 · smoke AC-04 403 / AC-05 204; grep sạch trong `app/api/rest/`.

---

## P5 — API tối thiểu gán / thu hồi role (T7)

- [x] `POST /admin/users/{target_user_id}/roles`
- [x] `DELETE /admin/users/{target_user_id}/roles/{role}`
- [x] Validate role + 404 user + chặn self-modify + idempotent assign

+ Prove-done: 2026-07-25 · smoke AC-07 / AC-08 / AC-09 + REVOKE PASS.

---

## P6 — Endpoint đọc role của chính mình (T8)

- [x] `GET /users/me/roles`

+ Prove-done: 2026-07-25 · smoke trả `roles` cho user vừa đăng ký và admin.

---

## P7 — Prove-done tổng (T12)

- [x] Migrate `alembic upgrade head` sạch
- [x] Smoke AC-01…AC-10 (+ revoke) qua `scripts/smoke_phase0_sprint1.py`
- [x] Grep hardcode quyền sạch trong `app/api/rest/`

+ Prove-done: 2026-07-25 · `docker compose ... exec -w /fastapi -e PYTHONPATH=/fastapi fastapi-app python scripts/smoke_phase0_sprint1.py` → `ALL_SMOKE_PASS`.

---

## P8 — Đóng sprint & sync doc

- [x] Cập nhật §0.B phase plan: Phase0-Sprint1 → đóng
- [x] Cập nhật `docs/Planing_docs/README.md` bảng sprint đang chạy
- [x] Scaffold `Phase0_Sprint2` (README tối thiểu)
- [x] Không ghi lesson/issue (không sự cố đáng nhớ ngoài: local không có user bootstrap `danya` — admin smoke dùng promote SQL trong script)

---

## Ngoài phạm vi (không làm trong sprint này)

- Admin UI quản trị role (feature riêng sau toàn bộ).
- Ownership hardening toàn mutate, CORS/TrustedHost, cookie/CSRF → Phase0-Sprint2.
- Audit log → Phase0-Sprint3.
- Capability matrix tách khỏi role.
- Job market / Marketplace features; `users_mysql` / `users_mongodb` / `users_httpx` demo paths.
- Sửa frontend Vue.
