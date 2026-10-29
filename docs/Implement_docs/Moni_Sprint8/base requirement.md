# Base requirement — Moni_Sprint8

> Input gốc cho **Plan #1**.  
> Macro: [`../../Planing_docs/moni/upgrade_hardening_phase_plan.md`](../../Planing_docs/moni/upgrade_hardening_phase_plan.md) · Phase **H0**.

## Bối cảnh

CI deploy đã `pg_dump` trước migrate. Chưa có **restore drill** có chứng từ (RPO/RTO), restore vào DB riêng, smoke trên data restore, backup **off-host**. Sprint0 CLOSED (VPS ticks Pending).

## Mục tiêu shippable

1. Ghi RPO/RTO mục tiêu (thực tế, không marketing).
2. Ít nhất 1 lần restore drill → DB riêng (không đè prod).
3. Smoke health/login (hoặc tối thiểu health + schema) trên DB restore.
4. Chính sách/backup off-host (copy ra ngoài volume app) — document + lệnh/script nếu thiếu.
5. Chứng từ thời gian dump/restore trong Implement docs.

## Ngoài phạm vi

- HA multi-region DB
- Đổi CI `VPS_HOST` / go-live Caddy hostname (GL gate)
- Lambda / multi-region egress (DEF-REGION — sau proxy talk; **không** trong chuỗi pre-proxy)
- Retention purge (Sprint7)
