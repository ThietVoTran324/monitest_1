# Business Requirements — Moni_Sprint0 (Foundation)

**Mức chi tiết:** ~3/10 (business). Schema/route/ops chi tiết → Plan #2.  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
**Macro:** [`../../Planing_docs/moni/upgrade_hardening_phase_plan.md`](../../Planing_docs/moni/upgrade_hardening_phase_plan.md)  
**Base:** [base requirement.md](base%20requirement.md)

> **Plan #1 CHỐT 2026-10-29** — Q1–Q10 **all suggest** (chat). Format quiz = nhiều đáp án, 1 đáp án **Suggest**.

---

## 1. Mục tiêu

| # | Năng lực |
|---|----------|
| 1 | Ba runtime mode rõ: local-process / local-docker / prod |
| 2 | Port + env + README/scripts **không drift** (8011 vs 8010; hết 8000 như API MONI) |
| 3 | Local deps: Postgres + **Redis** qua compose |
| 4 | `.env.*.example` đủ knobs (SSRF/Celery/freshness/mode notes) |
| 5 | VPS prep: ghi Caddyfile hiện có, **swap**, scaffold `/opt/moni` |
| 6 | **Không** trỏ GitHub `VPS_HOST` → `pinvps01` trong sprint này |

---

## 2. Actors

| Actor | Việc |
|-------|------|
| Dev local | Chạy local-process (default) hoặc local-docker theo docs |
| Ops `pinvps01` | Swap + `/opt/moni` + đọc Caddy; chưa go-live Caddy hostname |
| End-user | Không đổi UX trong Sprint0 |

---

## 3. Quy tắc nghiệp vụ (Q1–Q10 CHỐT)

| ID | Chủ đề | **CHỐT** |
|----|--------|----------|
| **Q1** | Shippable | Modes + port/docs; compose Redis; env examples; VPS Caddy note + swap + `/opt/moni`; không đổi GH deploy host |
| **Q2** | Default local | **local-process**, API **8011** |
| **Q3** | Port SSOT | Map rõ 8011 (local-process) / 8010 (docker & prod loopback); cấm sót 8000 = API MONI trong README/script chính |
| **Q4** | Redis | Compose (local-docker/deps) có Redis (+ Postgres); local-process trỏ Redis như docs |
| **Q5** | Env examples | Sync knobs hiện có + note mode/port; không bắt buộc rewrite hết `.env` máy dev |
| **Q6** | VPS trong S0 | Đọc/ghi Caddyfile hiện có; document/bật swap; scaffold `/opt/moni`; chưa Caddy live MONI; chưa CI deploy |
| **Q7** | Hostname public | TBD OK; không block scaffold; không claim go-live xong |
| **Q8** | Prove-done | README mode table khớp; compose Redis OK; checklist VPS có chứng từ; restart scripts đúng port |
| **Q9** | Out | Full docker app mỗi ngày; Sprint8 backup; GH deploy; Lambda multi-region; đổi region UI |
| **Q10** | Actor | Dev + ops; không UX end-user |

---

## 4. Acceptance criteria

| ID | Tiêu chí |
|----|----------|
| AC1 | README (hoặc doc mode) mô tả 3 mode + port đúng 8011/8010 |
| AC2 | Không còn hướng dẫn chính trỏ API local mặc định `8000` |
| AC3 | `docker-compose.yml` (deps/local-docker) có Redis usable |
| AC4 | `.env.example` / `.env.prod.example` đồng bộ knobs + note port/mode |
| AC5 | Tài liệu/checklist VPS: swap + `/opt/moni` + ghi chú Caddyfile hiện trạng |
| AC6 | Không đổi secret/CI `VPS_HOST` sang máy mới trong Sprint0 |
| AC7 | Scripts restart/smoke local khớp port mode default |

---

## 5. Out of scope / Chốt giữ

- Bắt buộc docker full app mỗi ngày (local-process default — macro D2)
- Sprint8 backup/restore drill
- Go-live Caddy hostname + trỏ GitHub deploy
- DEF-REGION / Lambda active (D10 — plumbing sau)
- S5 region UI honesty (sprint riêng)

---

## 6. Traceability

| Quiz | BR |
|------|-----|
| Q1–Q2 | §1 + §3 |
| Q3–Q5 | AC1–AC4 |
| Q6–Q7 | AC5–AC6 |
| Q8 | AC7 + prove |
| Q9–Q10 | §2 + §5 |
