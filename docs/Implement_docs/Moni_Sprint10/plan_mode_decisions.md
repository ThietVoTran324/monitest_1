# Plan mode decisions — Moni_Sprint10

> **BR:** [business_requirement.md](business_requirement.md)  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **CHỐT 2026-10-27** — T1–T8 **all suggest**

## 0. Meta

| | |
|---|---|
| Baseline | Sprint1/2 DONE; local API public status-pages |
| Target | Public DTO no url/reasons · rate limit · FE · ownership tests |

## D* — Core (T1–T8)

| ID | **CHỐT** |
|----|----------|
| **T1** | `PublicStatusPageMonitorItem` không `url`; owner giữ `StatusPageMonitorItem` có `url` |
| **T2** | Public incident DTO **không** `open_reason`/`close_reason` |
| **T3** | `InMemoryRateLimiter` key `public_status:{ip}`; settings `PUBLIC_STATUS_RATE_LIMIT_*` |
| **T4** | Default **60 / 60s / IP**; 429 + `Retry-After` |
| **T5** | FE type public không `url`; view public không bind URL |
| **T6** | Audit ownership + pytest cross-user |
| **T7** | Giữ `monitor.id` trên public |
| **T8** | API automated + manual curl/browser slug |
