# Base requirement — Moni_Sprint2

> Input gốc cho **Plan #1**.  
> Macro: [`../../Planing_docs/moni/upgrade_hardening_phase_plan.md`](../../Planing_docs/moni/upgrade_hardening_phase_plan.md) · Phase **H1**.

## Bối cảnh

Worker Celery có thể chạy chồng / retry. Hiện:

- Cập nhật monitor theo kết quả mới nhất **không** so `finished_at` vs `last_checked_at` → kết quả cũ có thể đè trạng thái mới hơn.
- Incident OPEN chỉ lọc bằng query; **không** unique partial → race có thể tạo 2 OPEN.
- Alert `incident_opened` gắn với tạo incident mới → spam nếu race.

## Mục tiêu shippable

1. Reject stale overwrite (theo `finished_at`).
2. Tối đa 1 OPEN incident / monitor (logic + DB).
3. Reuse OPEN khi fail tiếp; recovery đóng 1 OPEN.
4. Test tự động race/stale/unique.

## Ngoài phạm vi

Outbox email (Sprint6) · freshness UI (Sprint4) · consensus đa region.
