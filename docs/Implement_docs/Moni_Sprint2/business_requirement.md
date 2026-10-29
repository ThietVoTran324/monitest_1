# Business Requirements — Moni_Sprint2 (Monitor/incident consistency)

**Mức chi tiết:** ~3/10 (business). Schema/route → Plan #2.  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
**Macro:** [`../../Planing_docs/moni/upgrade_hardening_phase_plan.md`](../../Planing_docs/moni/upgrade_hardening_phase_plan.md)  
**Base:** [base requirement.md](base%20requirement.md)

> **Plan #1 CHỐT 2026-10-27** — Q1–Q10 **all suggest** (chat).

---

## 1. Mục tiêu

| # | Năng lực |
|---|----------|
| 1 | Kết quả check **cũ hơn** trạng thái đã ghi không đè monitor/incident |
| 2 | Mỗi monitor **tối đa 1** incident `OPEN` (logic + DB) |
| 3 | Worker thứ hai khi đã có OPEN → **reuse**, không mở mới / không spam `incident_opened` |
| 4 | Prove bằng unit/integration script (race + stale + unique OPEN) |

---

## 2. Actors

| Actor | Việc |
|-------|------|
| Worker (Celery) | Ghi check_run; cập nhật monitor/incident nếu không stale; mở/đóng/reuse incident |
| User | Xem status/incident nhất quán; không bị 2 OPEN / alert mở trùng vì race |
| Hệ thống | Enforce 1 OPEN; so `finished_at` vs `last_checked_at` |

---

## 3. Quy tắc nghiệp vụ (Q1–Q10 CHỐT)

| ID | Chủ đề | **CHỐT** |
|----|--------|----------|
| **Q1** | Định nghĩa stale | Check có `finished_at` **cũ hơn** `last_checked_at` hiện tại → **không** cập nhật status/incident |
| **Q2** | check_runs khi stale | **Vẫn insert** check_run; chỉ bỏ qua cập nhật monitor/incident |
| **Q3** | Số OPEN | **Tối đa 1** OPEN / monitor (DB enforce + logic) |
| **Q4** | Worker 2 khi đã OPEN | **Reuse** OPEN; cập nhật `last_failed_check`; **không** tạo mới; **không** gửi `incident_opened` lần 2 |
| **Q5** | Song song | Kết quả **muộn hơn theo `finished_at`** thắng; cái apply sau nhưng sớm hơn → stale |
| **Q6** | Alert trùng | **Không** `incident_opened` mới; `still_down` theo cooldown hiện có vẫn được |
| **Q7** | Recovery | Đóng OPEN hiện có; 1 lần `incident_recovered` như semantics hiện tại |
| **Q8** | Prove-done | Unit/integration script đủ; **không** bắt E2E UI / manual 2 terminal |
| **Q9** | Out of scope | Outbox/saga (Sprint6) · freshness UI stale vs DOWN (Sprint4) · multi-region consensus |
| **Q10** | Process debt S1 | Ghi `issues_history`: Plan quiz Sprint1 bị skip; Sprint2+ quiz chat trước docs |

---

## 4. Acceptance criteria

| ID | Tiêu chí |
|----|----------|
| AC1 | Apply check có `finished_at` < monitor.`last_checked_at` → monitor/incident không đổi; check_run vẫn được lưu |
| AC2 | Không tồn tại 2 incident `OPEN` cùng một monitor (DB từ chối hoặc logic + unique) |
| AC3 | Hai lần fail liên tiếp / race mở incident → chỉ 1 OPEN; tối đa một `incident_opened` cho lần mở đầu |
| AC4 | Fail khi đã OPEN → reuse + có thể `still_down` theo policy; không `incident_opened` mới |
| AC5 | UP/SLOW khi đang OPEN → đóng incident + `incident_recovered` một lần |
| AC6 | Automated tests cover stale reject + single OPEN (+ race mô phỏng) |

---

## 5. Out of scope / Chốt giữ

- Email outbox / saga đầy đủ → **Moni_Sprint6**
- Hiển thị freshness stale vs DOWN trên API/UI → **Moni_Sprint4**
- Multi-region consensus (Plan B) → **không làm** (D1 macro)
- Cờ `ignored_stale` trên API public → không bắt buộc Sprint2 (Plan #2 có thể chọn log nội bộ)
- Pin-IP / SSRF T2 → đã xong Sprint1 / defer T2

---

## 6. Traceability

| Quiz | BR |
|------|-----|
| Q1–Q7 | §3 + AC1–AC5 |
| Q8 | AC6 + prove-done |
| Q9 | §5 |
| Q10 | `issues_history.md` |
