# Plan mode decisions — Moni_Sprint6

> **BR:** [business_requirement.md](business_requirement.md)  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **CHỐT 2026-10-29** — T1–T4/T6–T10 = A; **T5** = A + per-monitor backoff override (admin)

## 0. Meta / Roles

| | |
|---|---|
| Roles | **Chỉ 2:** `user` (mặc định) và `admin` (`users.is_admin`). **Không** RBAC đầy đủ. |
| Bootstrap | Seed admin **trực tiếp DB** (script/SQL). |
| Thêm admin | Chỉ admin hiện có gọi **endpoint không công khai** (không list trong docs public / không link marketing) để cấp `is_admin` cho user khác. |

## D* — Core

| ID | **CHỐT** |
|----|----------|
| **T1** | Bảng `email_outbox` cột tối thiểu như Suggest A |
| **T2** | Outbox = gửi; sau sent/failed vẫn ghi `alert_events` audit |
| **T3** | Insert pending trong apply/expiry; bỏ phụ thuộc chỉ `.delay()` fire-and-forget |
| **T4** | `process_email_outbox` + SKIP LOCKED / claim đến hạn |
| **T5** | Settings hệ thống `max_attempts` + backoff schedule; **admin có thể override backoff/max theo monitor** (local); không set → dùng global |
| **T6** | `users.is_admin` boolean default false |
| **T7** | Admin API outbox + **endpoint cấp admin** (non-public OpenAPI tag / hidden) |
| **T8** | FE `/admin/email-outbox` (+ UI cấp admin tối thiểu nếu fit) |
| **T9** | Tests: pending, process mock mail, 403 non-admin, reclaim |
| **T10** | Alembic outbox + `is_admin`; giữ `alert_events` |

### T5 — Backoff

```text
effective = monitor.alert_backoff_override ?? settings.global_backoff
effective_max = monitor.alert_max_attempts_override ?? settings.global_max_attempts
```

Admin UI: chỉnh override trên monitor (nullable = inherit system).
