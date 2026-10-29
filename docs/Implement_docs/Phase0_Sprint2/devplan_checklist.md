# Dev plan checklist — Phase0_Sprint2 (Ownership & security)

**Initiative:** Phase0-Sprint2 — Ownership & security hardening (Phase 0-core block 0.5)  
**SSOT nghiệp vụ:** [business_requirement.md](business_requirement.md) (Plan #1 chốt 2026-07-25 — accept all Recommended)  
**SSOT kỹ thuật:** file này (bỏ qua `plan_mode_decisions` / gap debate — T1–T8 chốt dưới)  
**Phase map:** [`../../Planing_docs/marketplace_jobmarket_feasibility_phase_plan.md`](../../Planing_docs/marketplace_jobmarket_feasibility_phase_plan.md) §0.B  
**Gate vào:** BR hoàn thiện ✅ + quiz tech ✅  
**Trạng thái:** **CLOSED 2026-07-25** — `scripts/smoke_phase0_sprint2.py` → `ALL_SMOKE_PASS`; Vue production build pass.

---

## Quy ước

- Chỉ tick `[x]` khi có prove-done runtime.
- Hard stop: step hiện tại chưa pass → không sang step sau.
- Guide của step đang làm đọc trước khi sửa source.

---

## Quyết định kỹ thuật đã chốt (T1–T8)

| ID | Quyết định |
|----|------------|
| T1 | Helper ownership dùng chung + `Depends` / gọi tường minh; **403** nếu không phải owner |
| T2 | Siết mọi mutate user-route pin/board/comment còn thiếu ownership (kể cả upload/update) |
| T3 | CORS allowlist từ env (`TRUSTED_ORIGIN`, `FRONTEND_DOMAIN`, …) — không hardcode |
| T4 | TrustedHost siết theo env — bỏ `*` |
| T5 | Double-submit CSRF: cookie CSRF (readable) + header bắt buộc trên POST/PUT/PATCH/DELETE đã login; endpoint phát token |
| T6 | Vue: axios interceptor gửi CSRF header + bootstrap token — không UI mới |
| T7 | Cookie auth: giữ `HttpOnly`; `SameSite=Lax` (không phá Google OAuth); `Secure` khi không DEV / HTTPS |
| T8 | Smoke script kiểu Sprint1 cho AC-01…09 |

**Gap đã khảo sát (baseline)**

| Vấn đề | Path |
|--------|------|
| `DELETE /pins/{id}` lọc theo `user_id` trong SQL nhưng có thể **204 im lặng** khi không phải owner | `app/api/rest/pins/routes.py` |
| `POST /pins/upload/{id}` **không** check owner | cùng file |
| `POST/DELETE board pins` **không** check board thuộc caller | `app/api/rest/boards/routes.py` |
| `PATCH /boards/selected` chưa chắc board thuộc user | cùng file |
| `POST /comments/upload/{id}` **không** check author | `app/api/rest/comments/routes.py` |
| **Không có** `DELETE` comment user-route (AC-03 cần author xóa được) | comments routes |
| CORS / TrustedHost = `*` | `app/middlewares.py` |
| Google OAuth `set_cookie` thiếu flags đồng bộ login | `users_google_auth/routes.py` |
| Vue axios rải `withCredentials` — chưa CSRF header tập trung | `vuejs/src/**` |

**Runtime**

| Mục đích | Lệnh |
|----------|------|
| Up stack | `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d` |
| Migrate (nếu có) | `docker compose ... exec fastapi-app alembic upgrade head` |
| Smoke | `docker compose ... exec -w /fastapi -e PYTHONPATH=/fastapi fastapi-app python scripts/smoke_phase0_sprint2.py` |

---

## P0 — Chuẩn bị

- [x] Đọc BR + bảng T1–T8
- [x] Stack up; FastAPI health OK; Sprint1 role vẫn hoạt động (`GET /users/me/roles`)

+ Prove-done: 2026-07-25 · Docker stack healthy · Alembic `a1b2c3d4e5f6 (head)` · FastAPI health 200.

### Guide

- Không sửa source ở P0.
- Xác nhận `.env` có `TRUSTED_ORIGIN`, `TRUSTED_HOST`, `FRONTEND_DOMAIN`, `DEV_MODE` (sẽ dùng ở P2/P3).

---

## P1 — Ownership helpers + wire mutate (T1, T2) — map AC-01…06

- [x] Module helper `app/api/rest/ownership.py`: `assert_pin_owner`, `assert_board_owner`, `assert_comment_author` — không phải owner → **403**; không tồn tại → **404**
- [x] **Pins**
  - [x] `DELETE /pins/{pin_id}`: check owner → 403
  - [x] `POST /pins/upload/{id}`: chỉ owner
- [x] **Boards**
  - [x] `DELETE /boards/{board_id}`: phân biệt 404 vs 403
  - [x] `POST/DELETE /boards/{board_id}/pins/{pin_id}`: chỉ owner của **board**
  - [x] `PATCH /boards/selected`: board phải thuộc user
- [x] **Comments**
  - [x] `POST /comments/upload/{id}`: chỉ author
  - [x] Thêm `DELETE /comments/{comment_id}` cho author
- [x] **Không** đổi `/admin/*`; admin **không** bypass user-route ownership
- [x] Không đụng `users_mysql` / `users_mongodb` / `users_httpx`

+ Prove-done: 2026-07-25 · smoke AC-01…06 pass.

+ Prove-done tạm: có thể chờ P4 smoke; hoặc curl nhanh cross-user 403.

### Guide

- Tái dùng pattern Sprint1 (`require_roles`) — ownership helper nhận `db`, `user_id`, `resource_id`.
- Saved-pin routes (`user_saved_pins`) là quan hệ user↔pin của **caller**, không phải “xóa pin người khác” — giữ logic hiện có trừ khi phát hiện lỗ hổng cross-user.
- Create pin/board/comment (insert mới gắn `user_id=caller`) không cần ownership check kiểu “của người khác”.

---

## P2 — CORS + TrustedHost (T3, T4) — map AC-07

- [x] Parse allowlist từ env: `TRUSTED_ORIGIN` / `TRUSTED_HOST` (comma-separated)
- [x] `CORSMiddleware`: allowlist, credentials; bỏ origin `*`
- [x] `TrustedHostMiddleware`: hosts từ env; bỏ `*`
- [x] Cập nhật `.env` / `.env.example` format allowlist
- [x] Local Vite/API hosts nằm trong list

+ Prove-done: 2026-07-25 · smoke AC-07 pass (origin lạ không nhận CORS allow-origin).

+ Verify: request Origin không nằm allowlist không được CORS success như trước khi mở `*`.

### Guide

- File chính: `app/middlewares.py` + có thể thêm helper parse list trong `app/config.py`.
- Không hardcode production domain trong code.
- Cẩn thận: `TrustedHost` phải gồm host mà trình duyệt/Docker gọi API (`localhost`, có thể thêm tên service nếu cần).

---

## P3 — Cookie flags + CSRF double-submit (T5, T7) — map AC-08

- [x] Chuẩn hóa `set_cookie` cho `access_token` / `refresh_token` ở login, refresh, Google OAuth:
  - `httponly=True`
  - `samesite="lax"`
  - `secure=False` khi `DEV_MODE` (hoặc HTTP local); `secure=True` khi không DEV / HTTPS
- [x] Cookie CSRF readable, `samesite=lax`, tên `csrf_token`
- [x] Endpoint `GET /users/csrf` + set token khi login/OAuth/refresh
- [x] Middleware yêu cầu `X-CSRF-Token` khớp cookie trên state-changing request đã login
- [x] Exempt login/register hợp lý; không exempt admin/mutate
- [x] Smoke API gửi CSRF header sau login

+ Prove-done: 2026-07-25 · smoke AC-08/09 pass.

### Guide

- Double-submit: giá trị cookie CSRF = giá trị header; so sánh constant-time nếu tiện.
- Không nhúng CSRF vào JWT.
- WebSocket có thể out-of-scope CSRF header lần này nếu không dùng cookie mutate qua WS body — ghi chú nếu skip có chủ đích.
- Giữ Google OAuth redirect + set cookie không gãy vì `SameSite=Lax`.

---

## P4 — Vue tối thiểu (T6) — map AC-09

- [x] Axios interceptor tập trung (`withCredentials: true`)
- [x] Đọc/bootstrap CSRF và gắn `X-CSRF-Token` cho state-changing request
- [x] Login flow set session + CSRF
- [x] **Không** Admin UI / không redesign auth pages

+ Prove-done: 2026-07-25 · `npm run build` trong container → exit 0.

+ Verify: từ UI (hoặc curl giả lập header như browser) create/delete cơ bản không 403 CSRF oan.

### Guide

- Ưu tiên một file kiểu `vuejs/src/api/http.js` rồi dần import; tránh sửa 20 store cùng lúc nếu interceptor global `axios.defaults` đủ.
- Cookie CSRF readable: document.cookie parse; nếu SameSite/path sai sẽ fail sớm — chỉnh path `/`.

---

## P5 — Prove-done tổng (T8)

- [x] Viết `scripts/smoke_phase0_sprint2.py`
- [x] AC-01: user A xóa pin B → 403
- [x] AC-02: user A mutate board B → 403
- [x] AC-03: user A xóa comment B → 403; author xóa được
- [x] AC-04: owner mutate OK
- [x] AC-05: admin `/admin/pin/{id}` → 204
- [x] AC-06: admin qua user-route không bypass → 403
- [x] AC-07: origin lạ không nhận CORS access
- [x] AC-08: thiếu CSRF → 403; đủ CSRF → OK
- [x] AC-09: login + mutate có CSRF thành công
- [x] AC-10: không thêm Job/Marketplace/Admin UI

+ Prove-done: 2026-07-25 · smoke → `ALL_SMOKE_PASS`.
+ Regression: `scripts/smoke_phase0_sprint1.py` (đã thêm CSRF header) → `ALL_SMOKE_PASS`.

+ Prove-done: `ALL_SMOKE_PASS` + ngày.

---

## P6 — Đóng sprint & sync doc

- [x] Tick checklist; cập nhật §0.B phase plan → Sprint2 CLOSED
- [x] Cập nhật `docs/Planing_docs/README.md`
- [x] Scaffold `Phase0_Sprint3` (audit) README tối thiểu
- [x] Không có incident sản phẩm cần ghi; smoke fixture cần `created_at=now()` đã sửa trong test script

---

## Ngoài phạm vi

- Audit log → Phase0-Sprint3
- Job market / Marketplace / payment / watermark
- Admin UI; demo mysql/mongodb/httpx
- Capability matrix; nhúng roles/CSRF vào JWT
