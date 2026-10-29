# Dev plan checklist — Phase0_Sprint3 (Audit log tối thiểu)

**Initiative:** Phase0-Sprint3 — Audit log tối thiểu (Phase 0-core block 0.6)  
**SSOT nghiệp vụ:** [business_requirement.md](business_requirement.md) (Plan #1 chốt 2026-07-25; Q5=A+B)  
**SSOT kỹ thuật:** file này (bỏ qua `plan_mode_decisions` / gap debate — T1–T7 chốt dưới)  
**Phase map:** [`../../Planing_docs/marketplace_jobmarket_feasibility_phase_plan.md`](../../Planing_docs/marketplace_jobmarket_feasibility_phase_plan.md) §0.B  
**Gate vào:** Sprint1 + Sprint2 CLOSED ✅ · BR hoàn thiện ✅ · quiz tech ✅  
**Trạng thái:** **CLOSED** 2026-07-25 — implement xong, `scripts/smoke_phase0_sprint3.py` = `ALL_SMOKE_PASS`, regression Sprint1/2 pass.

---

## Quy ước

- Chỉ tick `[x]` khi có prove-done runtime.
- Hard stop: step hiện tại chưa pass → không sang step sau.
- Audit và mutation chính dùng **cùng session / transaction**.

---

## Quyết định kỹ thuật đã chốt (T1–T7)

| ID | Quyết định |
|----|------------|
| T1 | Postgres table `audit_logs` + Alembic; không mirror file |
| T2 | `id`, `created_at`, `actor_user_id`, `action`, `target_type`, `target_id`, `metadata` JSONB gọn |
| T3 | Action cố định: `admin_delete_pin`, `admin_delete_comment`, `role_assign`, `role_revoke` |
| T4 | `write_audit(db, ...)` gọi trước `commit`, cùng session với mutation |
| T5 | `GET /admin/audit` (all + filter) và `GET /users/me/audit` (self-related) |
| T6 | Moderation metadata có `owner_user_id`; role event target là user |
| T7 | Smoke tự động: ghi thành công, không ghi 403/404, quyền đọc đúng, atomicity |

**Baseline migration head:** `a1b2c3d4e5f6` → **head sau sprint:** `b2c3d4e5f6a7` (`add audit_logs table`).

---

## P0 — Runtime baseline

- [x] Docker stack healthy; Alembic current = `a1b2c3d4e5f6`
- [x] Sprint1 + Sprint2 regression smoke vẫn pass

### Guide

- Không sửa source ở P0.
- Nếu regression fail, sửa regression trước khi thêm audit.

---

## P1 — Schema + migration (T1–T3)

- [x] Thêm `AuditLogOrm` vào `app/postgresql/models.py`
  - [x] `id` PK; `created_at` timezone UTC
  - [x] `actor_user_id` FK user; `action`; `target_type`; `target_id` nullable; `metadata` JSONB
  - [x] Index tối thiểu: created_at, actor_user_id, target_type + target_id
  - [x] DB/app constraint action chỉ thuộc 4 code T3
- [x] Alembic revision mới (down_revision `a1b2c3d4e5f6`) tạo table/index/check constraint
- [x] `alembic upgrade head` sạch; downgrade có drop table/index

+ Verify: insert/select test row; migration head mới.

### Guide

- Dùng PostgreSQL `JSONB`; metadata mặc định `{}`.
- `actor_user_id` nên giữ lịch sử nếu user bị xóa: FK `ondelete=SET NULL` và nullable; actor ID vẫn có thể null sau deletion.
- Không có model/API update/delete audit.

---

## P2 — Audit helper + schemas

- [x] Module `app/api/rest/audit.py`
  - [x] Constants action T3
  - [x] `write_audit(db, actor_user_id, action, target_type, target_id, metadata=None)`
  - [x] Validate action; chỉ `flush`, **không commit**
- [x] Response/filter schemas gọn (Pydantic)

### Guide

- Helper nhận AsyncSession của route; route mutation + audit → **một** `commit`.
- Không Celery / không swallow exception. Audit insert fail phải làm transaction fail.
- Metadata không chứa token/password/full request.

---

## P3 — Hook admin moderation + role changes (T4, T6)

- [x] `DELETE /admin/pin/{id}`: đọc `owner_user_id` trước delete; delete + audit `admin_delete_pin` + commit
- [x] `DELETE /admin/comment/{id}`: 404 rõ nếu không tồn tại; đọc author trước delete; audit `admin_delete_comment`
- [x] Gán role: audit `role_assign`, target_type=`user`, target_id=user target, metadata role
- [x] Thu hồi role: audit `role_revoke` tương tự
- [x] 403/404 xảy ra **trước write_audit** → không tạo row

+ Verify: mỗi success thêm đúng 1 row; failure count không đổi.

### Guide

- Truyền `admin_user_id` từ `require_roles("admin")` vào cả delete routes (hiện đang dùng `_`).
- Moderation metadata: `{"owner_user_id": <id>}`.
- Role metadata: `{"role": "<role>"}`.
- Gọi `write_audit` sau mutation statement, trước `await db.commit()`.

---

## P4 — Read APIs & authorization (T5, T6)

- [x] `GET /admin/audit` (admin role)
  - [x] Pagination + newest-first
  - [x] Filter optional: actor_user_id, target_type, target_id, action, from/to date
- [x] `GET /users/me/audit` (authenticated)
  - [x] Chỉ rows: actor_user_id = me OR (`target_type=user` + target_id=me) OR metadata.owner_user_id=me
  - [x] Pagination + newest-first
- [x] Không tạo POST/PATCH/DELETE audit endpoints

+ Verify: admin thấy all; user target thấy related; unrelated user không thấy.

### Guide

- Admin route có thể đặt trong `admin/routes.py`; self route trong `users/routes.py`, hoặc router audit riêng được include rõ.
- JSONB owner filter dùng expression PostgreSQL; cast text → integer an toàn.
- Giới hạn page size để tránh dump toàn bộ.

---

## P5 — Prove-done (T7) — AC-01…10

- [x] Viết `scripts/smoke_phase0_sprint3.py`
- [x] AC-01/02: admin delete pin/comment → audit đúng actor/action/target/owner
- [x] AC-03/04: assign/revoke role → audit metadata role
- [x] AC-05: 403/404 → audit count không đổi
- [x] AC-06: OpenAPI không có mutate audit endpoint
- [x] AC-07: admin list/filter thấy đúng rows
- [x] AC-08: user related thấy; unrelated không thấy
- [x] AC-09: test atomicity bằng transaction/helper failure → mutation rollback
- [x] AC-10: không SIEM/UI/Job/Marketplace
- [x] Sprint1 + Sprint2 regression smoke pass

+ Gate: `ALL_SMOKE_PASS`, compile/lint sạch.

---

## P6 — Đóng Phase 0-core

- [x] Tick checklist + BR/README = CLOSED
- [x] Cập nhật §0.B phase plan: Sprint3 CLOSED; **Phase 0-core CLOSED**
- [x] Cập nhật `docs/Planing_docs/README.md`
- [x] Không tự mở Job market implementation; bước kế tiếp là planning chính trong `docs/Planing_docs/job_market/`

---

## Kết quả implement (2026-07-25)

| Hạng mục | Nơi thực hiện |
|----------|---------------|
| Model + constraint + index | `app/postgresql/models.py` (`AuditLogOrm`) |
| Migration | `app/migrations/versions/b2c3d4e5f6a7_add_audit_logs.py` |
| Helper + response schema | `app/api/rest/audit.py` (`write_audit`, `AuditLogOut`) |
| Hook moderation + role | `app/api/rest/admin/routes.py` |
| Read API admin | `GET /admin/audit` (filter actor/action/target/khoảng thời gian, pagination) |
| Read API self-related | `GET /users/me/audit` (`app/api/rest/users/routes.py`) |
| Prove-done | `scripts/smoke_phase0_sprint3.py` → `ALL_SMOKE_PASS` |

---

## Ngoài phạm vi

- SIEM / retention / log shipping / file mirror.
- Admin UI audit.
- Audit mọi mutate owner.
- Audit failed attempts (403/404).
- Job market / Marketplace.
