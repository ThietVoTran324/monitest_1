# Base requirement — Moni_Sprint6

> Input gốc cho **Plan #1**.  
> Macro: [`../../Planing_docs/moni/upgrade_hardening_phase_plan.md`](../../Planing_docs/moni/upgrade_hardening_phase_plan.md) · Phase **H1**.

## Bối cảnh

Sau Sprint2: incident/check apply nhất quán; email vẫn `.delay()` **sau** khi xử lý — nếu worker chết / Redis mất task **trước khi gửi**, **không còn hàng đợi bền** trong DB. `AlertEvent` hiện chủ yếu ghi **sau** send (audit), chưa phải outbox `pending` trong cùng txn với quyết định alert.

Macro D6: outbox mỏng; **không** block monitor txn bằng SMTP đồng bộ.

Go-live gate (VPS) có thể Pending song song — Sprint6 là code reliability, không phụ thuộc hostname live.

## Mục tiêu shippable

1. Khi cần gửi alert: ghi `alert_events` (hoặc tương đương) trạng thái **pending** trong txn quyết định.
2. Worker/task lấy pending → SMTP send → cập nhật sent/failed.
3. Retry/backoff mỏng cho lỗi tạm.
4. Prove: mất enqueue giả lập vẫn còn pending để gửi lại; không SMTP trong critical path apply check.

## Ngoài phạm vi

- Admin replay UI đầy đủ / dead-letter console (DEF / Type2)
- Multi-channel (Slack, webhook, PagerDuty)
- Đổi copy marketing email / template lớn
- Go-live Caddy/hostname (GL gate riêng)
