# Phase0_Sprint2 — Ownership & security hardening

> Block **0.5** trong Phase 0-core.  
> Phase map: [`../../Planing_docs/marketplace_jobmarket_feasibility_phase_plan.md`](../../Planing_docs/marketplace_jobmarket_feasibility_phase_plan.md) §0.B  
> Phụ thuộc: Phase0-Sprint1 **CLOSED** (role model sẵn).

## Mục tiêu (từ phase plan)

- Ownership check khi mutate pin/board (và tài nguyên liên quan) — user A không sửa/xóa của B.
- Siết CORS / TrustedHost (không còn `*`).
- Cookie flags + chiến lược CSRF cho cookie auth.

## Trạng thái

**CLOSED 2026-07-25** — ownership + CORS/TrustedHost + cookie/CSRF + Vue interceptor đã prove-done (`ALL_SMOKE_PASS`, Vue build pass).

## Ngoài phạm vi

- Audit log → Phase0-Sprint3.
- Job market / Marketplace features.
- Admin UI.
