# Business Requirements — Moni_Sprint6 (Email outbox)

**Mức chi tiết:** ~3/10 (business). Schema/API admin → Plan #2.  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
**Macro:** [`../../Planing_docs/moni/upgrade_hardening_phase_plan.md`](../../Planing_docs/moni/upgrade_hardening_phase_plan.md)  
**Base:** [base requirement.md](base%20requirement.md)

> **Plan #1 CHỐT 2026-10-29** — Q1=A (C SMTP-sync **OUT** vì Q3/D6); Q2=B; Q3–Q7/Q9–Q10=A; **Q8=A+B** (admin UI mỏng bắt đầu).

---

## 1. Mục tiêu

| # | Năng lực |
|---|----------|
| 1 | Quyết định alert → ghi **outbox pending** bền (bảng riêng) trong txn, **không** SMTP sync |
| 2 | Celery claim pending → gửi email → `sent` / `failed` |
| 3 | Retry/backoff mỏng + max attempts |
| 4 | Cover đủ loại event hiện có (open/recover/still-down/ssl/domain) |
| 5 | **Admin UI mỏng**: xem/điều khiển outbox (pending/failed/retry) — quyền **admin**, user thường **không** thấy |

---

## 2. Actors

| Actor | Việc |
|-------|------|
| Hệ thống | Insert pending; worker send/retry |
| Owner (user) | Nhận email; **không** quản lý outbox |
| Admin | UI/API kiểm soát outbox (list, retry, xem lỗi) — bề mặt user không có |

---

## 3. Quy tắc nghiệp vụ (Q* CHỐT)

| ID | Chủ đề | **CHỐT** |
|----|--------|----------|
| **Q1** | Shippable | Pending-in-txn + worker + retry mỏng + prove. **Không** SMTP đồng bộ trong apply (Q1-C từ chối) |
| **Q2** | Storage | Bảng **`email_outbox`** (hoặc tên tương đương) **tách** khỏi `alert_events` audit |
| **Q3** | Apply txn | Chỉ ghi pending (+ enqueue best-effort); không chờ SMTP |
| **Q4** | Sender | Celery task claim pending rồi send |
| **Q5** | Retry | Backoff mỏng + max attempts (row và/hoặc Celery bound) |
| **Q6** | Events | Đủ loại hiện có qua outbox |
| **Q7** | Prove | Test pending không SMTP; worker cập nhật status; reclaim/retry path |
| **Q8** | UI | User surfaces không bắt buộc đổi lớn; **thêm Admin UI mỏng** quản outbox (A+B) |
| **Q9** | Out | Multi-channel; admin replay **enterprise** đầy đủ; GL hostname; region; S12 |
| **Q10** | Actor | Hệ thống + owner nhận mail; admin điều khiển outbox |

---

## 4. Acceptance criteria

| ID | Tiêu chí |
|----|----------|
| AC1 | Khi cần alert: có row outbox `pending` commit cùng quyết định (trước/không phụ thuộc SMTP success) |
| AC2 | Worker gửi thành công → status `sent` (và audit `alert_events` nếu vẫn giữ) |
| AC3 | Gửi fail → `failed` + error; retry đến max rồi dừng có kiểm soát |
| AC4 | Apply check path không gọi SMTP sync |
| AC5 | Mất `.delay()` giả lập: pending vẫn còn để worker/reclaim xử lý |
| AC6 | Admin (không phải user thường) list pending/failed + trigger retry |
| AC7 | User thường **không** gọi được admin outbox API (403) |

---

## 5. Out of scope / Chốt giữ

- SMTP trong apply check txn
- Slack/webhook/PagerDuty
- Admin dead-letter console “đầy đủ” kiểu ops platform (chỉ **mỏng** Sprint6)
- Đổi SMTP per-monitor cho user
- Go-live hostname / region Lambda

---

## 6. Traceability

| Quiz | BR |
|------|-----|
| Q1–Q3 | §1 + AC1 + AC4 |
| Q4–Q5 | AC2–AC3 |
| Q6–Q7 | AC5 + §3 |
| Q8 | AC6–AC7 |
| Q9–Q10 | §2 + §5 |
