# Bug History — MONI upgrade + go-live wave

> **Vai trò:** Nhật ký lỗi / sự cố kỹ thuật & quy trình trong đợt **hardening + go-live** (2026-10).  
> **Template entry:** Date · Issue · Impact · Fix · Prevention (cùng shape [`issues_history.md`](issues_history.md)).  
> **Phạm vi:** không chỉ CI/CD — gồm plan shortcut, migrate, GHCR, VPS shared, Caddy/TLS, commit hygiene.  
> **Companion:** [`build_history/`](build_history/) (timeline + artifacts).

---

## Index

| ID | Date | Area | Severity | Status |
|----|------|------|----------|--------|
| BH-001 | 2026-10-27 | Process | Med | Closed |
| BH-002 | 2026-10-29 | CI / GHCR | High | Closed |
| BH-003 | 2026-10-29 | CI / pull | High | Closed (follow BH-002) |
| BH-004 | 2026-10-29 | Migrate | High | Closed |
| BH-005 | 2026-10-29 | Migrate / Alembic | High | Closed (by design awareness) |
| BH-006 | 2026-10-29 | CD / secrets | Med | Open (gate) |
| BH-007 | 2026-10-29 | TLS / ACME | Med | Closed |
| BH-008 | 2026-10-29 | VPS ops | High | Closed |
| BH-009 | 2026-10-29 | Git hygiene | Med | Mitigated |
| BH-010 | 2026-10-29 | Shell / Windows | Low | Closed |
| BH-011 | 2026-10-29 | Release drift | Med | Open |
| BH-012 | 2026-10-29 | DNS / LE secondary | Low | Closed |
| BH-013 | 2026-10-29 | Ops UX | Low | Closed |

---

## Entries

### BH-001 — Skip Plan #1/#2 quiz (Sprint1)

- **Date:** 2026-10-27
- **Issue:** Moni_Sprint1 bỏ quiz Plan #1/#2 trên chat; ghi BR/TD rồi implement thẳng.
- **Impact:** Shortcut lessonlearn B7 / bộ 3; thiếu vòng CHỐT stakeholder trước code.
- **Fix:** Giữ code SSRF (unit prove-done). Không rollback. Sprint2+ bắt buộc quiz → CHỐT → docs → code.
- **Prevention:** Mỗi Moni sprint: Plan #1 quiz → BR; Plan #2 quiz → `plan_mode_decisions` + checklist; không code trước CHỐT bộ 3.
- **Also logged:** [`issues_history.md`](issues_history.md) (2026-10-27).

### BH-002 — GHCR tag mixed-case owner

- **Date:** 2026-10-29
- **Issue:** Actions `build-and-push` fail: `invalid tag "ghcr.io/ThietVoTran324/moni-backend:…": repository name must be lowercase`.
- **Impact:** Không push được image; VPS `docker pull` 404; job deploy bị skip/đỏ phụ thuộc.
- **Fix:** Lowercase `github.repository_owner` trong `.github/workflows/deploy.yml` trước khi tag (`tr '[:upper:]' '[:lower:]'`). Commit `519f68a`.
- **Prevention:** Mọi workflow GHCR: luôn normalize owner/path về lowercase; thêm step assert tag `grep -E '^[a-z0-9._/-]+$'` trước buildx push.

### BH-003 — Pull SHA không tồn tại trên GHCR

- **Date:** 2026-10-29
- **Issue:** VPS pull `…:16a8ef85…` → `not found` vì build trước đó (BH-002) chưa bao giờ push tag.
- **Impact:** `compose up` fail; go-live bị chặn cho đến khi có image thật.
- **Fix:** Đợi build xanh sau BH-002; pull SHA `519f68a` (hoặc `:latest`).
- **Prevention:** Không hard-code SHA lên VPS trước khi Actions `build-and-push` = success; prefer `latest` chỉ sau khi xác nhận run xanh, hoặc copy tag từ job output.

### BH-004 — Alembic ENUM `email_outbox_status` tạo trùng

- **Date:** 2026-10-29
- **Issue:** Revision `d3e4f5a6b7c8` gọi `Enum.create()` rồi `create_table` với cùng `sa.Enum` (`create_type` mặc định) → `DuplicateObjectError: type "email_outbox_status" already exists`.
- **Impact:** Migrate fail trên DB trống; stack compose đã up nhưng schema không head.
- **Fix:** `create_type=False` + `DO $$ … CREATE TYPE … EXCEPTION WHEN duplicate_object … $$`. Commit `937975c`. Vá tay file trong container đang chạy để unblock trước khi image mới về.
- **Prevention:** Postgres + SQLAlchemy Enum: hoặc explicit create + `create_type=False`, hoặc chỉ để `create_table` tạo type — không cả hai. Prove migrate trên DB trống trong CI trước go-live.

### BH-005 — Một transaction Alembic → fail cuối = rollback toàn bộ

- **Date:** 2026-10-29
- **Issue:** `alembic/env.py` bọc `run_migrations()` trong một `begin_transaction()`. Fail BH-004 làm biến mất cả chuỗi bảng + `alembic_version` (“Did not find any relations”).
- **Impact:** Nhầm tưởng DB “nửa chừng”; thực tế empty — phải chạy lại full upgrade sau khi vá.
- **Fix:** Nhận ra empty DB là expected; patch migration + `alembic upgrade head` lại → `d3e4f5a6b7c8 (head)`.
- **Prevention:** Document hành vi transactional DDL; optional: tách transaction per revision (trade-off). Sau fail migrate luôn `\dt` + `alembic current` trước khi “stamp tay”.

### BH-006 — Deploy job đỏ: `VPS_HOST` chưa trỏ `pinvps01`

- **Date:** 2026-10-29
- **Issue:** `build-and-push` xanh nhưng `deploy` đỏ/skip path SSH (secrets vẫn máy cũ hoặc thiếu; gate cố ý chưa đổi).
- **Impact:** CI/CD chưa end-to-end; go-live phải compose tay trên VPS.
- **Fix:** Smoke UI OK 2026-10-29. Workflow: `deploy` chỉ chạy khi `vars.ENABLE_PROD_DEPLOY=true` + secrets đủ; operator set `VPS_*`/`GHCR_*` rồi bật biến.
- **Prevention:** Checklist go-live: không đổi secret deploy trước loopback health + HTTPS + smoke; sau gate bật `ENABLE_PROD_DEPLOY`.

### BH-007 — HTTPS `tlsv1 alert internal error` trước khi có cert

- **Date:** 2026-10-29
- **Issue:** Ngay sau `systemctl reload caddy`, `curl https://monitoring1.io.vn` fail TLS trong lúc ACME còn chạy.
- **Impact:** False alarm “Caddy hỏng”; `monitest.top` vẫn 200.
- **Fix:** Đợi `certificate obtained successfully` trong journal; retry → HTTP/2 200 + `/api/v1/health` ok.
- **Prevention:** Sau thêm site mới: `journalctl -u caddy -f` đến khi obtain OK rồi mới smoke HTTPS; phân biệt lỗi cert vs reverse_proxy.

### BH-008 — VPS không có swap trước khi `compose up`

- **Date:** 2026-10-29 (phát hiện / xử lý trước up)
- **Issue:** `pinvps01` 3.8 GiB RAM, `Swap: 0` trong khi đã chạy full stack `monitest.top`.
- **Impact:** Risk OOM kill khi thêm 6 container MONI (~0.6–0.8 GiB).
- **Fix:** `fallocate` 2G `/swapfile` + fstab trước `compose up`. Không đụng `/opt/pinterest`.
- **Prevention:** Go-live shared box: swap (hoặc memory reservation) là hard gate trước MONI up — ghi trong Sprint0 checklist.

### BH-009 — Commit bị inject `Co-authored-by: Cursor`

- **Date:** 2026-10-29
- **Issue:** `git commit` / amend (kể cả `--no-verify`) vẫn gắn trailer Cursor; user yêu cầu không xuất hiện Cursor trên GitHub.
- **Impact:** Phải rewrite HEAD bằng `commit-tree` + `reset --soft` trước push.
- **Fix:** Tạo commit object sạch qua `git commit-tree` (Python/`py` bypass wrapper khi cần); verify message không match `Cursor|cursoragent` trước `push`.
- **Prevention:** Pre-push check local: `git log -1 --format=%B` reject nếu có Cursor; document quy trình commit sạch cho operator.

### BH-010 — PowerShell nuốt `HEAD^{tree}` / `{tree}`

- **Date:** 2026-10-29
- **Issue:** Trong PowerShell, `{tree}` bị coi scriptblock → `git rev-parse HEAD^{tree}` vỡ (`could not read 'ree'`).
- **Impact:** Lệnh rewrite commit fail lần đầu.
- **Fix:** Quote `"HEAD^{tree}"` / `"HEAD^"`; hoặc lấy tree qua Python subprocess.
- **Prevention:** Trên Windows PS: luôn quote refspec có `{}` / `^`; ưu tiên script nhỏ thay one-liner phức tạp.

### BH-011 — Drift: image chạy `519f68a` + patch migrate tay vs repo `937975c`

- **Date:** 2026-10-29
- **Issue:** Unblock go-live bằng patch file trong container; image tag trên VPS chưa phải SHA có fix ENUM.
- **Impact:** Recreate container từ image cũ mất patch; CD sau này có thể “lạ” nếu không pull SHA mới.
- **Fix:** (Pending) Pull `937975c` (hoặc `:latest` sau build) + `up -d`; `alembic current` vẫn head — không re-run revision đã stamp.
- **Prevention:** Mọi hotfix runtime phải có commit + image tag; ghi SHA đang chạy trong build_history artifacts.

### BH-012 — Let’s Encrypt secondary validation DNS SERVFAIL rồi HTTP-01 OK

- **Date:** 2026-10-29
- **Issue:** Challenge `tls-alpn-01` fail: `SERVFAIL looking up A for monitoring1.io.vn` (secondary). Fallback `http-01` thành công; cert vẫn cấp.
- **Impact:** Delay ~1 phút; log error gây nhiễu.
- **Fix:** Không cần hành động thêm sau khi obtain success. DNS A từ VPS/`dig` đã đúng `116.118.9.162`.
- **Prevention:** Domain NS ổn định trước go-live; chấp nhận LE retry; tránh panic reload Caddy liên tục khi đang obtain.

### BH-013 — Heredoc Caddyfile bị tab-completion xen dòng

- **Date:** 2026-10-29
- **Issue:** Khi `cat >> Caddyfile <<'EOF'`, shell gợi ý tên file (`backups/`, `.env`…) xen vào stdin nhìn rối — nội dung cuối vẫn đúng.
- **Impact:** Noise khi review; rủi ro paste nhầm nếu không `cat` kiểm.
- **Fix:** `cat /etc/caddy/Caddyfile` verify; `caddy validate`; `caddy fmt --overwrite`.
- **Prevention:** Viết Caddyfile bằng `tee`/`nano` hoặc file scp; luôn validate trước reload.

---

## Patterns rút (→ lessonlearn khi distill)

1. **GHCR path = lowercase** luôn.  
2. **Enum Postgres:** một đường tạo type.  
3. **Transactional Alembic:** fail = có thể empty DB.  
4. **Shared VPS:** swap + project compose riêng + Caddy append.  
5. **ACME:** đợi cert trước khi kết luận TLS hỏng.  
6. **CD gate:** smoke trước khi đổi `VPS_HOST`.  
7. **Hotfix container ≠ release** — phải ship image.
