# Plan mode decisions — Moni_Sprint4

> **BR:** [business_requirement.md](business_requirement.md)  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **CHỐT 2026-10-28** — T2–T10 all suggest; **T1** chốt thêm min buffer + first-run

## 0. Meta

| | |
|---|---|
| Target | Derive freshness trên list/detail/dashboard; FE badge; không mutate status; không public |

## D* — Core

| ID | **CHỐT** |
|----|----------|
| **T1** | `threshold = interval_seconds * factor + min_buffer_seconds`. Default `factor=2.0`, `min_buffer=60`. **First run** (`last_checked_at is None`) → không stale. |
| **T2** | `is_stale: bool` + `freshness: "fresh" \| "stale" \| "unknown"` (derive, không cột DB) |
| **T3** | Helper thuần `evaluate_monitor_freshness(...)` + unit tests |
| **T4** | Paused / null → `freshness=unknown`, `is_stale=false` |
| **T5** | Wire `MonitorListItem`, `MonitorDetailResponse`, dashboard items (+ optional `stale` count summary) |
| **T6** | Skip public status freshness |
| **T7** | FE badge Stale, tone khác DOWN |
| **T8** | Tweaks copy runtime degraded banner |
| **T9** | Settings `MONITOR_STALE_FACTOR`, `MONITOR_STALE_MIN_BUFFER_SECONDS` |
| **T10** | Unit helper + API fields; manual badge |

### T1 công thức (chi tiết)

```text
if paused or last_checked_at is None:
    freshness = unknown; is_stale = false
else:
    threshold = interval_seconds * factor + min_buffer_seconds
    age = now - last_checked_at
    is_stale = age > threshold
    freshness = stale | fresh
```

**Vì sao min buffer:** interval ngắn (30–60s) với chỉ `× factor` vẫn dễ false-stale khi beat/worker trễ nhẹ; buffer cố định 60s tạo sàn an toàn. Interval dài vẫn chủ yếu theo `× factor`.
