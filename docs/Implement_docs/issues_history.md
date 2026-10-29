# Issues History

Use this file to record incidents, bugs, and process issues discovered during planning, implementation, or testing. Each entry should include:

- Date
- Summary
- Impact
- Fix applied
- Prevention / lesson learned

*Template entry example:*

- **Date:** YYYY-MM-DD
- **Issue:** [Short summary of the problem]
- **Impact:** [What broke / what was delayed]
- **Fix:** [How it was resolved]
- **Prevention:** [What rule or practice should prevent this next time]

---

- **Date:** 2026-10-27
- **Issue:** Moni_Sprint1 bỏ qua bước trắc nghiệm Plan #1/#2 trên chat — ghi BR/TD rồi implement thẳng.
- **Impact:** Quy trình lessonlearn B7 / bộ 3 bị shortcut; quyết định thiếu vòng chốt stakeholder từng lựa chọn trước docs.
- **Fix:** Giữ code SSRF Sprint1 (đã unit prove-done). Không rollback. Sprint2+ bắt buộc: quiz chat (options + suggest) → user CHỐT → mới ghi docs → mới code.
- **Prevention:** Mỗi Moni sprint: Plan #1 quiz → BR; Plan #2 quiz → `plan_mode_decisions` + checklist; không code trước CHỐT bộ 3.

---

## Wave 2026-10 upgrade + go-live

Chi tiết kỹ thuật đầy đủ (BH-001…BH-013): [`bug_history.md`](bug_history.md).  
Biên niên + artifacts: [`build_history/`](build_history/).

- **Date:** 2026-10-29
- **Issue:** CI GHCR fail vì tag `ghcr.io/ThietVoTran324/...` không lowercase (BH-002/003).
- **Impact:** Không có image để pull; chặn go-live compose.
- **Fix:** Normalize owner lowercase trong `deploy.yml`; rebuild `519f68a`.
- **Prevention:** Mọi tag GHCR phải lowercase; không hard-code SHA lên VPS trước khi Actions xanh.

- **Date:** 2026-10-29
- **Issue:** Migrate `d3e4f5a6b7c8` ENUM tạo trùng + Alembic 1 transaction → DB empty (BH-004/005).
- **Impact:** Schema không lên head sau `compose up`.
- **Fix:** `create_type=False` + `DO $$` idempotent (`937975c`); vá container rồi `upgrade head`.
- **Prevention:** Prove migrate DB trống trong CI; không double-create Postgres ENUM.

- **Date:** 2026-10-29
- **Issue:** CD deploy đỏ / chưa trỏ `VPS_HOST` → `pinvps01` (BH-006); image VPS còn `519f68a` + patch tay (BH-011).
- **Impact:** CI/CD chưa E2E; drift hotfix vs image.
- **Fix:** (Open) Smoke UI → pull `937975c` → retarget secrets → Actions deploy xanh.
- **Prevention:** Gate go-live: smoke trước CD; mọi hotfix phải ship image.
