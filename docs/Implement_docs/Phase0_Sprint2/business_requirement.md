# Business Requirements — Phase0-Sprint2: Ownership & security hardening

**Mục đích:** SSOT nghiệp vụ cho sprint Phase 0-core block 0.5.  
**Cách dùng:** Plan #1 đã chốt → file này là BR hoàn thiện. Tech + step + prove-done → `devplan_checklist.md`.  
**Không** nhồn spec kỹ thuật vào BR.

**Nguồn phase:** `docs/Planing_docs/marketplace_jobmarket_feasibility_phase_plan.md` (§0.B Phase0-Sprint2).  
**Phụ thuộc:** Phase0-Sprint1 CLOSED.

---

## Quy tắc (cho AI — đọc trước mọi thao tác trên file này)

- File này = *SSOT nghiệp vụ* (~3/10 sau Plan); tech + step + prove-done → `devplan_checklist.md`.
- Sprint này thống nhất **bỏ qua** `plan_mode_decisions` / `requirement_gap_debate` (giống Sprint1); sau BR → quiz tech trực tiếp vào `devplan_checklist.md` rồi mới code.
- *Anti-pattern:* implement khi chưa có checklist tech đã chốt; nhét schema/header CSRF chi tiết vào BR.

---

## Nội dung

> Plan #1 đã chốt 2026-07-25 — **accept all Recommended** (Q1-B … Q7-A). Nguồn base: [base requirement.md](base%20requirement.md).

### 1. Bối cảnh & mục tiêu

*Bối cảnh*

- Phase0-Sprint1 đã thay hardcode admin bằng role; moderation “xóa bất kỳ” chỉ qua `/admin/*` với role `admin`.
- Cookie auth đang dùng; CORS/TrustedHost đang mở (`*`). Ownership trên các luồng mutate pin/board/comment chưa đồng nhất — chưa đủ an toàn trước Job market / Marketplace.

*Mục tiêu nghiệp vụ*

- Owner chỉ được sửa/xóa tài nguyên của mình (trừ moderation admin đã có).
- Chỉ origin/host tin cậy được phục vụ API từ trình duyệt (không còn “mọi origin”).
- Có lớp chống CSRF tối thiểu cho thao tác đổi trạng thái dùng cookie — đủ local và chuẩn bị VPS.

*Actor*

| Actor | Vai trò |
|-------|---------|
| End-user (owner) | Mutate tài nguyên mình sở hữu |
| Admin | Moderation “xóa bất kỳ” qua `/admin/*` (đã có Sprint1); **không** tự động bypass mọi mutate user-route |
| Hệ thống / cấu hình | Giới hạn origin/host tin cậy; áp CSRF tối thiểu + cookie flags |

### 2. Phạm vi ownership

Áp dụng cho app chính (Postgres / FastAPI / Vue hiện tại):

| Tài nguyên | Quy tắc |
|------------|---------|
| Pin | Chỉ owner được sửa/xóa pin của mình (luồng user) |
| Board | Chỉ owner được sửa/xóa board của mình; thao tác gắn/gỡ pin trên board thuộc owner |
| Comment | Chỉ author được sửa/xóa comment của mình (luồng user) |

*Admin vs owner (đã chốt)*

- Owner mutate resource mình qua user-route.
- Admin “xóa bất kỳ” **chỉ** qua `/admin/*` (Sprint1).
- Admin **không** tự động bypass ownership trên mọi mutate user-route.

*Khi không phải owner*

- Từ chối rõ (**forbidden**) — không “im lặng thành công”, không cố tình trả not-found để giấu tồn tại (trừ khi endpoint vốn đã 404 vì không tìm thấy).

### 3. Trusted surface (CORS / TrustedHost — mức nghiệp vụ)

- Chỉ cho phép origin/host của frontend + API đã cấu hình (local: frontend localhost; VPS đổi qua cấu hình môi trường).
- **Không** còn chính sách “mọi origin / mọi host”.

### 4. CSRF & cookie (mức nghiệp vụ)

- Cookie auth cần cookie flags phù hợp + **một** lớp CSRF tối thiểu cho request đổi trạng thái.
- Đủ dùng local và chuẩn bị VPS; chi tiết kỹ thuật (header/token/SameSite…) chốt ở quiz `devplan_checklist`.
- Frontend Vue: chỉnh **tối thiểu** để login/API hiện tại không gãy vì CORS/CSRF — **không** Admin UI / không redesign auth.

### 5. Phạm vi

*In scope*

- Ownership đồng nhất cho pin, board, comment (user-route mutate).
- Siết CORS/TrustedHost theo cấu hình tin cậy.
- Cookie flags + CSRF tối thiểu; Vue chỉnh tối thiểu nếu cần.
- Giữ moderation admin Sprint1 không bị phá.

*Out of scope*

- Audit log → Phase0-Sprint3.
- Job market / Marketplace / payment / watermark.
- Admin UI.
- Demo stacks (`users_mysql` / `users_mongodb` / `users_httpx`) nếu không thuộc app chính.
- Full CSRF + đổi toàn bộ form UI ngoài mức tối thiểu để app chạy được.

### 6. Acceptance criteria (business)

| ID | Tiêu chí |
|----|----------|
| AC-01 | User A không xóa/sửa được pin của user B qua luồng user → bị từ chối (forbidden). |
| AC-02 | User A không xóa/sửa được board của user B → forbidden. |
| AC-03 | User A không xóa/sửa được comment của user B → forbidden. |
| AC-04 | Owner vẫn xóa/sửa được tài nguyên của mình như trước về mặt nghiệp vụ. |
| AC-05 | Admin vẫn xóa được pin/comment bất kỳ qua `/admin/*` (role admin). |
| AC-06 | Admin không được hiểu là “mọi user-route mutate đều bypass ownership”. |
| AC-07 | Trình duyệt từ origin không tin cậy không dùng được API như origin mở `*`. |
| AC-08 | Request đổi trạng thái từ cookie auth có lớp chống CSRF tối thiểu (không còn “chỉ cookie là đủ”). |
| AC-09 | Luồng login / gọi API chính từ frontend cấu hình vẫn hoạt động sau khi siết. |
| AC-10 | Không mở Job market / Marketplace / Admin UI / audit trong sprint này. |

---

> **Trạng thái:** **CLOSED 2026-07-25** — BR + implement + prove-done hoàn tất. Xem `devplan_checklist.md` và `scripts/smoke_phase0_sprint2.py`.
