# Phase 0 handoff & block classification — Job Market

> **Ngày:** 2026-07-26  
> **Mục đích:** Chốt những gì Phase 0-core đã ship, cái gì **không** cần làm trước Job Market, và cái gì làm **song song** từng sprint.  
> **SSOT phase map:** [`../marketplace_jobmarket_feasibility_phase_plan.md`](../marketplace_jobmarket_feasibility_phase_plan.md)

---

## 1. Phase 0-core — đã DONE

Manual API test + smoke Sprint1–3 pass. Alembic head: `b2c3d4e5f6a7`.

| Block | Deliverable | Path chính |
|-------|-------------|------------|
| 0.4 Roles | `user_roles`, `VALID_ROLES` gồm `admin/artist/employer/seller`, `require_roles`, admin assign/revoke, `GET /users/me/roles` | `app/api/rest/roles.py`, `dependencies.py`, `admin/routes.py`, migration `a1b2c3d4e5f6` |
| 0.5 Ownership + security | `assert_pin/board/comment_*`, CORS/TrustedHost allowlist, CSRF double-submit + Vue interceptor | `ownership.py`, `security.py`, `middlewares.py`, `vuejs/src/main.js` |
| 0.6 Audit | `audit_logs`, `write_audit` cùng transaction, `GET /admin/audit`, `GET /users/me/audit` | `audit.py`, migration `b2c3d4e5f6a7` |

### Primitive tái dùng cho Job Market

- Gate route: `Depends(require_roles("employer"))` / `"admin"` — role **không** nhét JWT → revoke có hiệu lực request sau.
- Ownership pattern: copy `assert_*` cho company / JD / CV / application / work-exp.
- Audit: gọi `write_audit` trước `commit`; **mọi action mới** cần mở rộng `VALID_ACTIONS` **và** DB check constraint (migration).
- Notify: `UpdatesOrm` + Celery + SSE skeleton.
- Media/local save: `save_file` / FormData patterns từ pin/user upload.
- Email token: `create_url_safe_token` / `decode_url_safe_token` (verify/reset) — tái dùng cho work-exp email nếu chọn phương án đó.

---

## 2. Block **không** giải quyết ngay (Marketplace / Phase 2)

| Block | Lý do hoãn |
|-------|------------|
| `pins.created_at` | Chỉ phục vụ eligibility bán license |
| `pin_stats` (view bền vững) | Chỉ Marketplace |
| Unique `likes` / `subscriptions` | Chống gian lận follower cho bán hàng |
| Watermark / original ACL / payment | Domain Marketplace |

> Không mở lại Phase 0-core để làm các mục trên.

---

## 3. Block phải chốt **trước code** Sprint 1 (planning)

Đây là quyết định nghiệp vụ / model — ghi trong BR hệ thống, **không** phải code platform mới:

1. Employer onboarding: chỉ admin gán `employer`, hay user tự claim?
2. Company verification bar cho MVP (unverified được post JD không?).
3. Artist profile: cột mới trên `users` vs bảng `artist_profiles`.
4. Work-exp verify: chỉ company in-app vs + email token ngoài hệ thống (ảnh hưởng schema từ 1.1/1.4).

Chi tiết open decisions: [`business_requirement.md`](business_requirement.md).

---

## 4. Block làm **song song** với từng sprint (hygiene)

Không chặn viết BR; nên gắn vào sprint gần nhất khi domain đụng PII/media/role UI.

| Gap | Rủi ro | Sprint tự nhiên |
|-----|--------|-----------------|
| Vue chưa gọi `/users/me/roles`; `CommentSection` còn hardcode `danya` | Role-aware UI sai | JobMarket Sprint1 (Phase 1.1) |
| `POST /users/upload/{id}` và banner upload **không auth / không ownership** | Ai cũng ghi đè avatar/banner | Sprint1 (logo/company) hoặc trước CV |
| `PUT /updates/read/{id}` thiếu auth/ownership; SSE updates stream thiếu auth | Lộ / sửa notify người khác | Trước hoặc kèm Sprint3 (apply notify) |
| Messages upload/read thiếu participant check | Trung bình | Khi gắn chat–application (1.3) |
| `require_roles` chỉ **AND** (issubset) | Khó “employer OR admin” | Khi moderation (1.5) hoặc sớm hơn nếu cần |
| Audit action allowlist cứng (Python + DB CHECK) | Mỗi action JM cần migration | Mỗi sprint có mutation nhạy cảm |
| Ownership helpers cho entity JM | Copy pattern hiện có | Mỗi sprint domain |
| `POST /users/create-user-entity` unauthenticated | Tạo user thật không qua register | Hygiene sớm (không thuộc JM domain nhưng nên vá) |

---

## 5. Kết luận handoff

| Câu hỏi | Trả lời |
|---------|---------|
| Phase 0 đủ để bắt đầu Job Market? | **Có** — auth/role/ownership/CSRF/audit tối thiểu đã có |
| Còn block platform bắt buộc trước Sprint1? | **Không** — chỉ còn chốt BR + open decisions |
| Marketplace data gaps chặn JM? | **Không** |
| Việc đầu tiên sau handoff? | Plan #1 chốt BR hệ thống → `Implement_docs/JobMarket_Sprint1/` |

Xem thêm khảo sát chi tiết: [`system_survey.md`](system_survey.md).
