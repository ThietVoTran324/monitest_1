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
