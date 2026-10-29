# Business Requirements — Moni_Sprint8 (Backup / restore drill)

**Mức chi tiết:** ~3/10 (business). Script/CI chi tiết → Plan #2.  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
**Macro:** [`../../Planing_docs/moni/upgrade_hardening_phase_plan.md`](../../Planing_docs/moni/upgrade_hardening_phase_plan.md)  
**Base:** [base requirement.md](base%20requirement.md)

> **Plan #1 CHỐT 2026-10-29** — Q2/3/5/7–10 = A; **Q1 = A** (C HA = OUT vì Q9); **Q4 = A+C**; **Q6 = A** (+ C best-case, không block).

---

## 1. Mục tiêu

| # | Năng lực |
|---|----------|
| 1 | RPO/RTO mục tiêu **ghi và đo** được trên drill |
| 2 | Restore vào **DB riêng** (không đè prod) |
| 3 | Smoke sau restore: health + (login/schema) **và** e2e FE khi stack lên được |
| 4 | Backup **off-host** có policy + ít nhất 1 chứng từ |
| 5 | Script dump/restore/verify + checklist chứng từ |

---

## 2. Actors

| Actor | Việc |
|-------|------|
| Ops / Dev | Chạy dump, restore drill, smoke, ghi chứng từ |
| End-user | Không đổi UX; không self-serve backup UI |

---

## 3. Quy tắc nghiệp vụ (Q* CHỐT)

| ID | Chủ đề | **CHỐT** |
|----|--------|----------|
| **Q1** | Shippable | RPO/RTO + restore DB riêng + smoke + off-host chứng từ. **Không** Postgres HA multi-region (Q1-C từ chối vì Q9/macro) |
| **Q2** | RPO/RTO | Doc số thực tế (vd. RPO gắn chu kỳ dump; RTO = thời gian restore+smoke đo được) |
| **Q3** | Restore target | DB/container **riêng** |
| **Q4** | Smoke | Health + login/schema **và** full e2e FE khi stack available (A+C) |
| **Q5** | Off-host | Document + lệnh/copy ra ngoài volume app; ≥1 chứng từ |
| **Q6** | Script | Chuẩn hóa dump+restore+verify + checklist (**A**). Viết lại toàn bộ deploy pipeline = **best-case only**, không block CLOSED |
| **Q7** | Env drill | Ưu tiên local-docker / Postgres compose riêng; không bắt buộc đè `pinvps01` prod |
| **Q8** | Prove-done | File chứng từ thời gian dump/restore/smoke; RPO/RTO điền; checklist tick |
| **Q9** | Out | HA multi-AZ; đổi `VPS_HOST`; Caddy live hostname; Lambda/region; retention S7; không gộp S9/S5 |
| **Q10** | Actor | Ops/dev; không UX backup |

---

## 4. Acceptance criteria

| ID | Tiêu chí |
|----|----------|
| AC1 | Doc RPO/RTO có số (mục tiêu và/hoặc đo từ drill) |
| AC2 | Có lệnh/script restore vào database riêng thành công |
| AC3 | Smoke health (+ login hoặc schema check) trên data restore |
| AC4 | E2E FE smoke (login → dashboard/monitors tối thiểu) khi API+FE lên được sau restore |
| AC5 | Off-host: mô tả + bằng chứng copy/backup ngoài volume app |
| AC6 | Checklist chứng từ trong Implement Sprint8 được tick |
| AC7 | Không đụng HA DB / GH `VPS_HOST` / region Lambda |

---

## 5. Out of scope / Chốt giữ

- Postgres HA / multi-region DB
- Go-live Caddy hostname + retarget CI host
- DEF-REGION / Lambda
- Sprint7 retention; Sprint9 rollback (trừ khi best-case đụng nhẹ deploy backup steps)
- Full rewrite deploy pipeline (Q6-C) trừ khi làm kèm tự nhiên và không block

---

## 6. Traceability

| Quiz | BR |
|------|-----|
| Q1–Q2 | §1 + AC1 |
| Q3–Q4 | AC2–AC4 |
| Q5–Q6 | AC5–AC6 |
| Q7–Q10 | §2 + §5 |
