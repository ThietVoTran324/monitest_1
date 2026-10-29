# Job Market — system survey (codebase readiness)

> **Ngày:** 2026-07-26  
> **Phạm vi:** Backend + Vue readiness trước Phase 1.1–1.6.  
> **Không** thay BR hệ thống — chỉ inventory tái dùng / thiếu / rủi ro.

---

## 1. Verdict

| Layer | Ready? | Ghi chú |
|-------|--------|---------|
| Auth / CSRF / CORS | Yes | Phase 0.5 |
| Multi-role catalog + admin assign | Yes | `employer` dormant — chưa gắn JD routes |
| Ownership helper pattern | Yes | Extend cho entity mới |
| Audit helper + txn discipline | Yes | Widen allowlist per sprint |
| Pagination / Celery email / chat / SSE skeleton | Yes | Có gap auth/PII |
| Job domain schema + APIs | **No** | Zero remnant |
| Vue shell / FormData / list / detail patterns | Yes | Zero JM UI; chưa hydrate roles |
| System BR / Implement sprint folders | Drafting | BR draft trong repo; Implement **chưa** tạo |

---

## 2. Backend — có sẵn

### Auth & roles

- Cookie JWT + Redis revoke: `app/api/rest/dependencies.py`
- `require_roles(*required)` — **AND** semantics (`required_set.issubset(roles)`)
- `VALID_ROLES = {admin, artist, employer, seller}`; default `artist` via `ensure_default_roles`
- Admin: `POST/DELETE /admin/users/{id}/roles`; self: `GET /users/me/roles`
- Không có self-service “become employer”; không có DB CHECK trên `user_roles.role`

### Ownership & security

- `assert_pin_owner` / `assert_board_owner` / `assert_comment_author` — 404 missing / 403 wrong owner
- CSRF middleware khi có `access_token`; cookie helpers trong `security.py`
- CORS / TrustedHost từ `TRUSTED_ORIGIN` / `TRUSTED_HOST`

### Audit

- `write_audit` flush-only; caller `commit`
- Actions hiện tại: `admin_delete_pin`, `admin_delete_comment`, `role_assign`, `role_revoke`
- DB constraint `ck_audit_logs_action` khớp allowlist — **đổi action = cần migration**

### Profile / media / notify / search / chat

| Thành phần | Path | Ghi chú JM |
|------------|------|-----------|
| `UsersOrm` | `postgresql/models.py` | image, banner, description, socials — chưa skills/company |
| Pin media pipeline | `pins/routes.py`, `utils.save_file` | Pattern FormData; allowlist image/video |
| User avatar/banner | `users/routes.py` | **Thiếu auth/ownership** trên upload by `{id}` |
| `UpdatesOrm` + list API | `updates/routes.py` | Chưa có FK job/application; mark-read thiếu ownership |
| SSE updates | `sse/routes.py` | Stream theo `user_id` — **thiếu auth** |
| Search history | `search/routes.py` | Không phải content search JD |
| Pin `ilike` title/description | `pins/routes.py` | Pattern gần nhất cho JD text search |
| Chat / messages | `chats`, `messages` | Chưa có `application_id` |
| Email tokens | `utils.create_url_safe_token` | Tái dùng work-exp email nếu chọn |

### Domain Job Market — **thiếu hoàn toàn**

Không có model / migration / route cho:

- `company_profiles`
- `artist_profiles` (hoặc cột skills trên users)
- `job_posts`
- `cv_documents`
- `applications`
- `work_experiences` (+ verification tokens)

Demo MySQL/Mongo/httpx **không** phải SSOT sản phẩm.

---

## 3. Frontend — có sẵn

### Shell

- Router: `vuejs/src/router/index.js` — home, create-pin, pin, user, messages, recommendations. **Không** Jobs route / `meta.roles` / `beforeEach`.
- Auth gate: `App.vue` (cookie `access_token` → Auth vs NotAuth).
- Layout: `Auth.vue` + `Aside.vue` — chưa có mục Jobs.
- `/portfolio` mount `PortfolioView` **ngoài** router — **không** dùng làm nền JM.

### Stores & CSRF

- `authUserStore` — gần như chỉ username; **không** roles/id đầy đủ
- CSRF: interceptor global trong `main.js` (`withCredentials` + `X-CSRF-Token`) — mọi axios mutation JM hưởng sẵn
- Unread messages/updates stores — tái dùng notify apply / work-exp

### Patterns tái dùng

| Pattern | Source | Dùng cho |
|---------|--------|----------|
| Profile edit + avatar/banner | `UserView.vue` | Artist/company profile |
| FormData create entity | `CreatePinView.vue` | JD create, CV upload |
| Infinite list + masonry | `HomeView`, `CreatedPins`, … | JD list, applications inbox |
| Detail by id | `PinView.vue` | JD detail + apply CTA |
| Search bar UX | `SearchBar.vue` | Skeleton filter JD (API mới) |
| Chat / SSE updates | `MessagesView`, `Aside` EventSource | Apply pipeline notify |

### Gaps FE

1. Không gọi `GET /api/users/me/roles`
2. `CommentSection.vue` vẫn so `authUsername == 'danya'` cho admin delete
3. Không có shared form/list library — copy pattern, không component hóa bắt buộc
4. `PortfolioView.vue` = dead-end sản phẩm JM

---

## 4. Map sơ bộ Phase → phụ thuộc kỹ thuật

| Phase | Backend mới | FE chính | Hygiene song song |
|-------|-------------|----------|-------------------|
| 1.1 Profiles | `company_profiles` (+ artist shape); employer gates | Roles hydrate; UserView tabs; company CRUD; Aside Jobs; bỏ `danya` hardcode | Fix user upload auth/ownership |
| 1.2 JD & CV | `job_posts`, `cv_documents`; PDF allowlist; search API | JD form/list/detail; CV upload | — |
| 1.3 Apply | `applications` state machine; update types | Apply CTA; my apps; employer inbox | SSE/auth + updates ownership |
| 1.4 Work exp | `work_experiences` + approve (+ email token?) | Exp CRUD; approve UI; verified badge | Audit actions mới |
| 1.5 Moderation | Company review; JD report; CV harden | Queue tối thiểu | `require_roles` OR helper nếu cần |

---

## 5. Rủi ro bảo mật đáng chú ý trước PII (CV / applications)

1. Avatar/banner upload by arbitrary id — không auth  
2. SSE notification stream — không auth  
3. Mark update read — không ownership  
4. (Thấp hơn cho JM ngắn hạn) pin original served to any logged-in user — Marketplace blocker  

Chi tiết phân loại block: [`phase0_handoff_and_block_classification.md`](phase0_handoff_and_block_classification.md).
