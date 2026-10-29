# Base requirement — Moni_Sprint0

> Input gốc cho **Plan #1**.  
> Macro: [`../../Planing_docs/moni/upgrade_hardening_phase_plan.md`](../../Planing_docs/moni/upgrade_hardening_phase_plan.md) · Phase **H0**.

## Bối cảnh

P0 security/semantics (S1, S10, S4, S2) đã CLOSED. Go-live trên `pinvps01` còn thiếu nền: ba runtime mode (local-process / local-docker / prod) chưa chuẩn hóa; port drift 8000/8010/8011; Redis local phụ thuộc Docker tay; Caddy/swap/`/opt/moni` trên VPS chưa chốt; CI chưa được phép trỏ máy mới.

## Mục tiêu shippable (macro)

1. Chuẩn hóa port/env modes + docs/README khớp.
2. `docker-compose.yml` đủ Postgres **+ Redis** (local-docker / deps).
3. `.env.*.example` đủ knobs (đã bổ sung một phần SSRF/Celery — Sprint0 hoàn thiện & sync).
4. Đọc Caddyfile hiện có trên VPS; ghi swap; scaffold `/opt/moni`.
5. **Không** trỏ GitHub deploy `VPS_HOST` sang `pinvps01` cho đến smoke tay.

## Ngoài phạm vi

- Full docker app build bắt buộc mỗi ngày (local-process vẫn default).
- Hostname public MONI chốt marketing (có thể TBD trong sprint nhưng không block scaffold).
- Sprint8 backup restore drill (sau Sprint0).
