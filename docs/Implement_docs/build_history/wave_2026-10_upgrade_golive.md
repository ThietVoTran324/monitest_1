# Wave 2026-10 — Upgrade hardening + go-live

> **Status (2026-10-29):** HTTPS + smoke UI OK trên `monitoring1.io.vn`. CD: bật `ENABLE_PROD_DEPLOY` + secrets `pinvps01` (Pending). Pull image mới sau Actions xanh.  
> **Host:** `pinvps01` (shared với `monitest.top` @ `/opt/pinterest`).  
> **Bugs:** [`../bug_history.md`](../bug_history.md) · **Artifacts:** [`artifacts_2026-10.md`](artifacts_2026-10.md)

---

## 1) Mục tiêu wave

Hoàn thiện MONI theo macro [`upgrade_hardening_phase_plan.md`](../../Planing_docs/moni/upgrade_hardening_phase_plan.md): security probe, consistency, freshness, email outbox, backup drill, CI harden — rồi **ship production** trên VPS dùng chung, **không** đụng app `monitest.top`.

### OUT (giữ)

- TCP/ICMP execution, multi-region consensus, WebSocket, Slack/webhook  
- Claim scale 1000 monitor không đo máy thật  
- Đổi `VPS_HOST` trước smoke tay  

---

## 2) Sprint / deliverable đã chốt trong wave

| Sprint | Ship | Status |
|--------|------|--------|
| S0 | Runtime modes + VPS prep docs | DONE (VPS ops → GL) |
| S1 | SSRF redirect/body/DNS | DONE |
| S2 | Consistency + 1 open incident | DONE |
| S4 | Freshness stale vs DOWN | DONE |
| S6 | Email outbox + admin mỏng | DONE |
| S8 | Backup/restore scripts + drill local | DONE |
| S10 | Status privacy | DONE |
| S9 (partial) | `deploy_release.sh`, `.env.images`, health×2, prune | Code shipped; CD E2E Pending |
| GL | `/opt/moni` + Caddy `monitoring1.io.vn` + TLS | **HTTPS OK**; smoke Pending |

**Chuỗi còn lại (macro):** smoke → CD secrets → S12 → S11 → S5 → S3/S7/S9 formal.

---

## 3) Biên niên go-live (2026-10-29)

### 3.1 Prep

1. Chốt FQDN **`monitoring1.io.vn`** (+ www).  
2. DNS A → `116.118.9.162` (`dig` OK).  
3. Đọc Caddyfile: chỉ `monitest.top` → `127.0.0.1:8080`.  
4. Cổng `8010`/`4173` trống; không đụng `8080`/`80`/`443`.  
5. Swap 2G + `mkdir /opt/moni/backups` (BH-008).  
6. Curl `docker-compose.prod.yml` + `deploy_release.sh` từ GitHub `ThietVoTran324/monitest_1`.

### 3.2 Secrets / images

7. `.env` prod (JWT, Postgres, SMTP Gmail app password, Google OAuth client).  
8. `.env.images` trỏ GHCR `thietvotran324/moni-*`.  
9. Lần 1: pull SHA `16a8ef8` **fail** (BH-002/003) — Actions chưa push được vì tag mixed-case.  
10. Fix workflow lowercase → commit `519f68a` → build xanh → pull OK.  
11. `compose up -d` → 6 service MONI (`moni-*-1`); pinterest containers vẫn Up.

### 3.3 Migrate

12. `alembic upgrade head` fail ở `d3e4f5a6b7c8` ENUM trùng (BH-004).  
13. Transactional env → DB empty (BH-005).  
14. Patch migration trong container + upgrade lại → **`d3e4f5a6b7c8 (head)`**.  
15. Fix tương đương commit `937975c` trên repo (image pull Pending — BH-011).

### 3.4 Proxy / TLS

16. Append Caddy block `/api/*` → `:8010`, else → `:4173`; **không** xóa `monitest.top`.  
17. ACME: tls-alpn secondary DNS SERVFAIL rồi http-01 OK (BH-012).  
18. Cert LE cho `monitoring1.io.vn` + www; curl HTTPS FE 200 + health `{"status":"ok"}`; `monitest.top` vẫn 200 (BH-007 timing).  
19. `caddy fmt --overwrite` + reload.

### 3.5 CI/CD trạng thái lúc đóng phần host

| Job | Kết quả | Ghi chú |
|-----|---------|---------|
| build-and-push | Xanh (sau `519f68a`) | Images trên GHCR lowercase path |
| deploy | Đỏ / chưa retarget | BH-006 — đợi smoke |

### 3.6 Còn mở

- [x] Smoke UI (register / OAuth / monitor / check)  
- [ ] Pull image sau build (SHA mới / `:latest`) trên VPS  
- [ ] GitHub: secrets → `pinvps01` + `ENABLE_PROD_DEPLOY=true` + deploy xanh  
- [ ] Formal Sprint9 rollback drill  

---

## 4) Quyết định kỹ thuật chốt trong wave (rút)

| ID | Quyết định |
|----|------------|
| D-GL-1 | Domain prod = `monitoring1.io.vn` |
| D-GL-2 | Caddy append dual-site; MONI loopback only |
| D-GL-3 | Image tags chỉ qua `.env.images`; không sed secrets `.env` |
| D-GL-4 | Deploy atomic = `deploy/deploy_release.sh` một SSH |
| D-GL-5 | GHCR owner path lowercase bắt buộc |
| D-GL-6 | Không đổi `VPS_HOST` trước smoke HTTPS + UI |
| D-GL-7 | Region honesty / Lambda = defer (S5 / DEF-REGION); GL 1 egress |

Chi tiết D1–D10 macro: phase plan §6.

---

## 5) Prove-done host (đã đạt)

```text
curl -fsS http://127.0.0.1:8010/api/v1/health     → {"status":"ok"}
curl -fsSI http://127.0.0.1:4173/                 → 200
ss: 127.0.0.1:8010 + 127.0.0.1:4173
alembic current                                   → d3e4f5a6b7c8 (head)
curl -fsS https://monitoring1.io.vn/api/v1/health → {"status":"ok"}
curl -fsSI https://monitoring1.io.vn/             → 200
curl -fsSI https://monitest.top/                  → 200 (unchanged)
free -h                                           → Swap 2G
```

---

## 6) Liên kết sprint implement

Toàn bộ bộ 3 sprint: `docs/Implement_docs/Moni_Sprint{0..12}/`  
Planning cũ (MVP): `planning-docs/PROJECT-PLAN.md`, `SMOKE-CHECKLIST.md`, `GO-LIVE-PINVPS01.md`.
