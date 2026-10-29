# Base requirement — Moni_Sprint9

> Input gốc cho **Plan #1**.  
> Macro: [`../../Planing_docs/moni/upgrade_hardening_phase_plan.md`](../../Planing_docs/moni/upgrade_hardening_phase_plan.md) · Phase **H2**.

## Bối cảnh

Deploy hiện tại: GH Actions build → GHCR → SSH pull/restart; có `pg_dump` trước migrate + curl health tức thì.  
Hở đã chốt sẽ lấp (không dual-stack nặng trên VPS 3.8G): false-healthy, disk image, SSH nửa vời, `sed` `.env`, thiếu rollback drill / SHA discipline.

DNS/Caddy go-live: [`../Moni_Sprint0/dns_caddy_golive.md`](../Moni_Sprint0/dns_caddy_golive.md) — làm **trước/ops** song song; Sprint9 = harden pipeline sau (hoặc ngay khi GL ổn).

## Mục tiêu shippable

1. Health check deploy: chờ / sleep + curl lại (tránh false positive).  
2. Prune image sau deploy thành công.  
3. Script deploy atomic trên VPS (một lần chạy qua SSH).  
4. Giảm ghi đè `.env` (image tag tách file hoặc cơ chế an toàn hơn).  
5. Rollback drill theo SHA (không phụ thuộc chỉ `latest`).  
6. Blue-green **nhẹ** optional — không giữ 2 full stack lâu.  
7. Ghi chú expand-contract cho migrate phá schema.

## Ngoài phạm vi

- Full enterprise blue-green / k8s  
- Build trên VPS prod  
- Đổi hostname / DNS (ops GL riêng)
