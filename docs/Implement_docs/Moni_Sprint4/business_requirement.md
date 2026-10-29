# Business Requirements — Moni_Sprint4 (Stale vs DOWN freshness)

**Mức chi tiết:** ~3/10 (business). Schema/route → Plan #2.  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
**Macro:** [`../../Planing_docs/moni/upgrade_hardening_phase_plan.md`](../../Planing_docs/moni/upgrade_hardening_phase_plan.md)  
**Base:** [base requirement.md](base%20requirement.md)

> **Plan #1 CHỐT 2026-10-28** — Q1–Q10 **all suggest** (chat).

---

## 1. Mục tiêu

| # | Năng lực |
|---|----------|
| 1 | Biết monitor nào **stale** (check không còn tươi theo interval) |
| 2 | **Không** đổi `current_status` UP→DOWN chỉ vì pipeline/worker chết |
| 3 | UI/API owner phân biệt stale vs website DOWN |
| 4 | Runtime degraded vẫn rõ: hệ thống yếu ≠ site down |
| 5 | Không mở incident / down-alert chỉ vì stale |

---

## 2. Actors

| Actor | Việc |
|-------|------|
| Owner | Thấy list/detail/dashboard: status gốc + tín hiệu freshness |
| Hệ thống | Derive stale từ `last_checked_at` + interval; không tự DOWN vì stale |
| Visitor (public) | Không bắt buộc stale đầy đủ Sprint4 (owner surfaces trước) |

---

## 3. Quy tắc nghiệp vụ (Q1–Q10 CHỐT)

| ID | Chủ đề | **CHỐT** |
|----|--------|----------|
| **Q1** | Định nghĩa stale | Quá hạn theo `interval * factor + min_buffer` (Plan #2); lần đầu `last_checked_at` null → không stale |
| **Q2** | `current_status` | **Giữ nguyên**; thêm field freshness (`is_stale` / `freshness`) |
| **Q3** | Paused / null | Paused: không stale vận hành; null: unknown/chưa fresh — không nhãn “stale quá hạn” như đã UP |
| **Q4** | API surfaces | List + detail + dashboard (tối thiểu) |
| **Q5** | UI | Badge/cảnh báo Stale rõ, **khác** DOWN; vẫn hiện status gốc |
| **Q6** | Runtime degraded | Giữ banner; copy rõ pipeline ≠ site down; stale vẫn theo Q1 từng monitor |
| **Q7** | Alert | **Không** incident / down-alert chỉ vì stale |
| **Q8** | Public status | Owner trước; public stale = optional nếu fit Plan #2 |
| **Q9** | Prove-done | Unit/API derive + không UP→DOWN; FE/manual badge; runtime banner |
| **Q10** | Out | Enum DB `stale` · watchdog SaaS · rewrite scheduler · Sprint3/6 |

---

## 4. Acceptance criteria

| ID | Tiêu chí |
|----|----------|
| AC1 | Monitor đã check, vượt ngưỡng freshness → API đánh dấu stale; `current_status` không bị đổi thành down vì lý do đó |
| AC2 | Monitor paused không hiện stale “quá hạn vận hành” |
| AC3 | Monitor chưa từng check: không dùng cùng nhãn stale-overdue như monitor đã có check |
| AC4 | List + detail + dashboard có tín hiệu freshness |
| AC5 | UI badge/cảnh báo stale phân biệt được với DOWN |
| AC6 | Runtime degraded banner/copy không đồng nhất với “website down” |
| AC7 | Stale alone không tạo incident / không enqueue down alert |
| AC8 | Automated tests cover derive + non-mutation status; manual thấy badge |

---

## 5. Out of scope / Chốt giữ

- Migration enum DB `stale`
- External watchdog SaaS
- Chaos kill worker formal (Sprint3)
- Email outbox (Sprint6)
- Bắt buộc public status freshness đầy đủ (optional Plan #2)

---

## 6. Traceability

| Quiz | BR |
|------|-----|
| Q1–Q3 | §3 + AC1–AC3 |
| Q4–Q6 | AC4–AC6 |
| Q7 | AC7 |
| Q8 | §5 |
| Q9 | AC8 |
| Q10 | §5 |
