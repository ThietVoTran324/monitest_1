# System survey — Admin Ops (codebase 2026-08-08)

> Mục đích: chân trời kỹ thuật trước Plan #1 BR. Không thay BR.

---

## 1. Tóm tắt

| | |
|--|--|
| Admin-gated APIs | **22** |
| Vue admin product | **Gần 0** (chỉ xóa comment inline khi `hasRole('admin')`) |
| Router `/admin*` | **Không** |
| Ops hiện tại | Swagger + `grant_admin.py` + smoke scripts |

---

## 2. API đã ship (admin)

### Core — `app/api/rest/admin/routes.py` (`/admin`)

| Method | Path |
|--------|------|
| DELETE | `/admin/pin/{pin_id}` |
| DELETE | `/admin/comment/{comment_id}` |
| POST | `/admin/users/{id}/roles` |
| DELETE | `/admin/users/{id}/roles/{role}` |
| GET | `/admin/audit` |
| GET | `/admin/copyright-reports` |
| PATCH | `/admin/copyright-reports/{id}` |

### Job Market — `/job-market/admin/...`

| Area | Endpoints | File |
|------|-----------|------|
| Credentials | POST/PATCH/DELETE `.../users/{id}/credentials` | `job_market/routes.py` |
| KYC | GET queue; approve / need-more-info / reject; GET doc file | `sprint2_routes.py` |
| Work-exp | POST approve / reject **by id** (không list pending admin) | `sprint5_routes.py` |
| Moderation | GET job-reports; dismiss / actioned; company suspend / unsuspend | `sprint6_routes.py` |

### Marketplace

- User: `POST /marketplace/pins/{id}/copyright-reports`  
- Admin decide: qua `/admin/copyright-reports*` (không prefix marketplace)  
- **Không** có admin order / payout / SePay force-pay

---

## 3. UI hiện có

| Surface | Status |
|---------|--------|
| `CommentSection.vue` | Admin xóa comment |
| Settings / PinView / JobDetail | User-facing (KYC submit, copyright report, JD report) — **không** admin |
| Admin shell / queues | **Missing** |

---

## 4. Scripts / smoke

`grant_admin.py` · `check_user_roles.py` · `seed_role_sheet_api.py`  
Smoke: Phase0 S1–3 · JM S1–2, S5–6 · MP S5 (copyright patch)

---

## 5. Gap matrix

| Gap | Loại | Map backlog |
|-----|------|-------------|
| Admin shell + router + nav | MISSING UI | ADM-01 |
| Roles manager UI | MISSING UI | ADM-01 |
| Audit viewer UI | MISSING UI | ADM-07 |
| Pin delete UI | MISSING UI | ADM-01 |
| KYC queue + doc viewer UI | MISSING UI | ADM-02, ADM-06 |
| Credentials override UI | MISSING UI | ADM-03 |
| JD report + suspend UI | MISSING UI | ADM-04 |
| Copyright queue UI | MISSING UI | ADM-01 / SEC-T2-08 |
| Work-exp **admin pending list** API | MISSING API | JM harden |
| Copyright resolve → unlist / revoke | MISSING API | SEC-T2-01 |
| Payment / order admin | MISSING API | SEC-T2-07 |
| Company dispute workflow | MISSING product | ADM-05 |
| Notarized KYC | Policy later | ADM-08 |

---

## 6. Nhóm domain gợi ý (→ sprint_map)

| Group | Nội dung |
|-------|----------|
| **Core** | Shell, roles, audit, pin/comment moderation |
| **JM** | KYC, credentials, JD reports, suspend, work-exp queue (+ list API) |
| **MP** | Copyright queue; optional unlist/revoke; payment admin = later |
| **Later** | ADM-05, ADM-08, VNPay/chargeback admin, analytics |

---

## 7. Rủi ro kỹ thuật khi làm UI

- PII: admin xem full company/KYC docs — không lộ qua public `CompanyPublicOut`.  
- CSRF + cookie session giữ nguyên; mọi mutate admin cần CSRF.  
- Role `admin` DB-backed (`require_roles`) — FE chỉ ẩn UI; API vẫn là gate.  
- Copyright resolve hiện **không** đổi listing/access — product phải chốt có/không auto-unlist (SEC-T2-01).
