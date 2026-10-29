# Base requirement — Moni_Sprint10

> Input gốc cho **Plan #1**.  
> Macro: [`../../Planing_docs/moni/upgrade_hardening_phase_plan.md`](../../Planing_docs/moni/upgrade_hardening_phase_plan.md) · Phase **H1**.

## Bối cảnh

`GET /api/v1/public/status-pages/{slug}` không auth nhưng trả `url` monitor (và incident reason có thể chứa URL). Ownership mutate đã có; private → 404 đã có.

## Mục tiêu shippable

1. Public DTO không lộ `url` monitor.
2. FE public không hiển thị/không type `url`.
3. Public incident reason được bỏ hoặc redact.
4. Rate limit endpoint public.
5. Automated tests ownership + privacy + rate limit; manual hit public slug.

## Ngoài phạm vi

CAPTCHA · signed links · viewer auth · Sprint4 freshness · Sprint12 quota.
