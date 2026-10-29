# Business Requirements — Moni_Sprint10 (Status page privacy)

**Mức chi tiết:** ~3/10 (business). Schema/route → Plan #2.  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
**Macro:** [`../../Planing_docs/moni/upgrade_hardening_phase_plan.md`](../../Planing_docs/moni/upgrade_hardening_phase_plan.md)  
**Base:** [base requirement.md](base%20requirement.md)

> **Plan #1 CHỐT 2026-10-27** — Q1–Q9: A,A,A,B,A,A,A,A,A (chat).

---

## 1. Mục tiêu

| # | Năng lực |
|---|----------|
| 1 | Public status page **không** trả / hiện URL monitor |
| 2 | Owner (login) vẫn thấy URL trên API/UI quản lý status page |
| 3 | Public incident: **không** lộ reason thô (bỏ hoặc redact) |
| 4 | Rate limit gọi public status page |
| 5 | Private / unknown slug → 404 giống nhau; ownership mutate được prove bằng test |

---

## 2. Actors

| Actor | Việc |
|-------|------|
| Visitor (không login) | Xem page `is_public=true` qua slug — chỉ tên dịch vụ + trạng thái (+ metadata an toàn) |
| Owner (login) | CRUD status page; gắn monitor của mình; xem đủ URL |
| Attacker | Quét slug / đọc URL nội bộ / spam public API — phải bị chặn hoặc không thu được URL |

---

## 3. Quy tắc nghiệp vụ (Q1–Q9 CHỐT)

| ID | Chủ đề | **CHỐT** |
|----|--------|----------|
| **Q1** | Public monitor fields | `name` + `current_status` (+ thời gian/latency nếu hữu ích); **không** `url` |
| **Q2** | Owner API | **Vẫn trả `url`** trên endpoint authenticated |
| **Q3** | FE public | Không hiển thị URL; type public không còn `url` |
| **Q4** | Public incidents | **Bỏ reason hoặc sanitize/redact** — không để reason thô (có thể chứa URL) |
| **Q5** | Rate limit | Có — theo IP (hoặc tương đương); vượt → 429 |
| **Q6** | Private / missing | **404** giống nhau |
| **Q7** | Ownership | Giữ logic hiện có; **siết test**; vá nếu thiếu |
| **Q8** | Prove-done | Automated API + manual hit public slug local |
| **Q9** | Out | CAPTCHA · signed links · viewer auth · Sprint4/12 |

---

## 4. Acceptance criteria

| ID | Tiêu chí |
|----|----------|
| AC1 | `GET /public/status-pages/{slug}` JSON monitors **không** chứa key/value `url` |
| AC2 | Owner `GET/POST/PATCH` status-pages (auth) vẫn có `url` trên monitor items |
| AC3 | FE trang public không render URL monitor |
| AC4 | Public incidents không trả `open_reason`/`close_reason` thô (null hoặc đã redact) |
| AC5 | Vượt rate limit public → 429 |
| AC6 | `is_public=false` hoặc slug lạ → 404 |
| AC7 | User A không patch/delete / gắn monitor page của user B |
| AC8 | Automated tests cover AC1–AC7 tối thiểu; manual một lần public slug OK |

---

## 5. Out of scope / Chốt giữ

- CAPTCHA / bot score (T2-M05)
- Signed / expiring public links
- Auth bắt buộc để xem public page
- Freshness stale UI (Sprint4)
- Quota monitors (Sprint12)
- Đổi slug policy / SEO

---

## 6. Traceability

| Quiz | BR |
|------|-----|
| Q1–Q3 | §3 + AC1–AC3 |
| Q4 | AC4 |
| Q5 | AC5 |
| Q6–Q7 | AC6–AC7 |
| Q8 | AC8 |
| Q9 | §5 |
