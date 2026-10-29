# Phase0_Sprint3 — Audit log tối thiểu

> Block **0.6** trong Phase 0-core.  
> Phụ thuộc: Phase0-Sprint2 **CLOSED**.

## Mục tiêu từ phase plan

- Audit log append-only tối thiểu.
- Helper ghi sự kiện dùng chung.
- Gắn audit vào mutation quan trọng đầu tiên: đổi role và admin delete.

## Trạng thái

**CLOSED** 2026-07-25 — audit log đã chạy: bảng `audit_logs` (migration `b2c3d4e5f6a7`), helper `write_audit`, hook admin moderation + đổi role, `GET /admin/audit` và `GET /users/me/audit`. Prove-done: `scripts/smoke_phase0_sprint3.py` → `ALL_SMOKE_PASS` cùng regression Sprint1/2.

Sprint này đóng lại **Phase 0-core**. Bước kế tiếp là planning Job market trong `docs/Planing_docs/job_market/`.

## Ngoài phạm vi

- SIEM / retention phức tạp / Admin UI audit.
- Job market / Marketplace.
