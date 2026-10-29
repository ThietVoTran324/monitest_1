# MONI security follow-ups — Type 1 vs Type 2

> Nguồn: survey trong [`upgrade_hardening_phase_plan.md`](upgrade_hardening_phase_plan.md) §2.  
> **Type 1** = lỗ/debt trên code đã ship → sửa trong sprint gắn ID (hoặc hotfix).  
> **Type 2** = làm kèm sau / initiative tiếp theo → note backlog.

---

## Type 1 — OPEN (chưa fixed)

| ID | Issue | Sprint |
|----|-------|--------|

Khi fixed: chuyển xuống bảng FIXED kèm ngày + PR/commit.

---

## Type 1 — FIXED

| ID | Issue | Fix | Date |
|----|-------|-----|------|
| T1-M01 | Redirect SSRF — manual follow + re-validate mỗi hop | Moni_Sprint1 (`app/security/ssrf.py`, `checks._http_get_ssrf_safe`) | 2026-10-27 |
| T1-M02 | Public status page lộ `url` / incident reason | Moni_Sprint10 (public DTO + rate limit + FE) | 2026-10-27 |
| T1-M03 | Monitor UP khi check đã cũ / không phân biệt stale vs DOWN | Moni_Sprint4 (`freshness_service` + API/UI badge) | 2026-10-28 |
| T1-M04 | Race/stale overwrite + unique 1 OPEN incident | Moni_Sprint2 (`check_apply_service`, partial unique index) | 2026-10-27 |
| T1-M05 | Probe body unlimited — capped `SSRF_MAX_RESPONSE_BYTES` | Moni_Sprint1 | 2026-10-27 |

---

## Type 2 — DEFER

| ID | Issue | Gắn vào |
|----|-------|---------|
| T2-M01 | Pin resolved IP to TCP connect + keep TLS SNI | Post-Sprint1 |
| T2-M02 | Host egress firewall deny RFC1918 từ worker | Ops VPS |
| T2-M03 | Alert outbox admin replay / poison queue UI | Post-Sprint6 |
| T2-M04 | Separate signing secret for any future signed public links | When needed |
| T2-M05 | Public status page CAPTCHA / bot score | After abuse seen |

Chi tiết OUT lớn: [`deferred_and_out_of_scope_backlog.md`](deferred_and_out_of_scope_backlog.md).
