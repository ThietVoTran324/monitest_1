# Dev plan checklist — Moni_Sprint0

**SSOT:** [business_requirement.md](business_requirement.md) · [plan_mode_decisions.md](plan_mode_decisions.md)  
**Trạng thái:** **CLOSED 2026-10-29** — repo done; VPS ticks = **Pending** (ops tay, không block mở S8)

## P0 — Baseline

- [x] Xác nhận baseline scripts/port (restart đã 8011; drift ở example/README)

## P1 — Implement (T*)

- [x] **T1** Redis (+ volume) trong `docker-compose.yml`
- [x] **T2** `.env.example` + `.env.prod.example` port/mode + knobs
- [x] **T3** `docs/Planing_docs/moni/RUNTIME_MODES.md` + bảng README + Planing index
- [x] **T4** Scripts comment + default 8011; smoke đã 8011
- [x] **T5–T7** [`vps_prep_checklist.md`](vps_prep_checklist.md) shipped; ops tick trên VPS = **Pending**
- [x] **T8/T10** Không đụng logic app / Lambda / region FE

## P2 — Prove-done

- [x] Redis usable (existing `moni-redis` PONG; compose ready)
- [x] Không còn API default `8000` trong README / `.env.example` / `scripts/`
- [x] Sync trio + sprint_map + macro §2.0 (**CLOSED**; VPS Pending ghi rõ)
- [ ] ~~Ops tick hết trên `pinvps01`~~ → **Pending** (go-live gate vẫn cần)
