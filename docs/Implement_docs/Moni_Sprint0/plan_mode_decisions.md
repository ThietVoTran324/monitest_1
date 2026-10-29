# Plan mode decisions — Moni_Sprint0

> **BR:** [business_requirement.md](business_requirement.md)  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **CHỐT 2026-10-29** — T1 A, T2 A, **T3 A+C**, T4–T10 A

## 0. Meta

| | |
|---|---|
| Target | Modes/port/docs/compose Redis/env examples/scripts + VPS checklist (swap, `/opt/moni`, Caddy note); không GH deploy; không đổi logic app |

## D* — Core

| ID | **CHỐT** |
|----|----------|
| **T1** | Thêm `redis` (+ volume) vào `docker-compose.yml`; giữ Postgres |
| **T2** | Sửa `.env.example` + `.env.prod.example`: hết `8000` sai mode; note 8011/8010; giữ knobs SSRF/Celery/freshness |
| **T3** | **A+C:** bảng modes trong README **và** file `docs/.../RUNTIME_MODES.md` (SSOT chi tiết; README link ngắn) |
| **T4** | Scripts restart/smoke: default local **8011**; ghi chú docker **8010** |
| **T5** | Checklist ops trong Implement Sprint0: swap, `mkdir /opt/moni`, paste/tóm Caddyfile; chạy tay, không CI SSH |
| **T6** | Chỉ ghi nhận Caddy + draft note site MONI; **không** enable live |
| **T7** | **Không** đổi `VPS_HOST` / workflow → `pinvps01` |
| **T8** | local-process default; compose = deps Postgres+Redis; app image optional |
| **T9** | Prove: Redis compose OK; docs/scripts không API default 8000; checklist VPS có mục rõ |
| **T10** | Không đổi monitor/Celery/region/Lambda/FE |

### T3 — Docs layout

```text
README.md          → bảng modes ngắn + link RUNTIME_MODES.md
RUNTIME_MODES.md   → SSOT: ports, env files, compose vs process, prod loopback
```

Đường dẫn file: `docs/Planing_docs/moni/RUNTIME_MODES.md` (cùng stream planning MONI) **hoặc** `docs/Implement_docs/Moni_Sprint0/RUNTIME_MODES.md` nếu muốn gắn sprint — **chọn:** `docs/Planing_docs/moni/RUNTIME_MODES.md` + link từ README + Planing README index.
