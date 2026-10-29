# Base requirement — Phase0-Sprint2 (Ownership & security)

> Input gốc Plan #1. SSOT nghiệp vụ sau chốt: [business_requirement.md](business_requirement.md).

## Quyết định đã chốt (Plan #1 — accept all Recommended)

- Ownership: **pin + board + comment** (app chính); không đụng demo mysql/mongodb/httpx.
- Owner mutate resource mình; admin “xóa bất kỳ” chỉ `/admin/*`; admin **không** bypass mọi user-route.
- Không phải owner → **forbidden** rõ.
- CORS/TrustedHost: chỉ origin/host tin cậy (frontend + API cấu hình); không còn `*`.
- Cookie flags + **một** lớp CSRF tối thiểu; Vue chỉnh tối thiểu để không gãy login/API.
- Out of scope: Sprint3 audit; Job/Marketplace; Admin UI; watermark/payment; full redesign auth.

## Ngoài phạm vi sprint này

- Audit log → Phase0-Sprint3.
- Job market / Marketplace / payment / watermark.
- Admin UI; demo DB stacks ngoài app chính.
