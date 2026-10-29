# Base requirement — Moni_Sprint4

> Input gốc cho **Plan #1**.  
> Macro: [`../../Planing_docs/moni/upgrade_hardening_phase_plan.md`](../../Planing_docs/moni/upgrade_hardening_phase_plan.md) · Phase **H1**.

## Bối cảnh

Runtime API đã có `ok | degraded` (beat/worker heartbeat). Monitor vẫn hiện `UP` khi `last_checked_at` đã quá hạn so với interval — user tưởng website sống trong khi hệ thống không còn chứng cứ check mới.

## Mục tiêu shippable (macro)

1. Freshness / stale trên API + UI.
2. **Không** đổi `current_status` UP→DOWN chỉ vì worker chết.
3. Gắn tín hiệu runtime degraded với hiểu biết stale ở monitor/list/dashboard.

## Ngoài phạm vi

- Enum DB bắt buộc nếu derive đủ ở API.
- External watchdog SaaS.
