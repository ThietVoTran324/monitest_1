# Business Requirements — Phase0-Sprint3: Audit log tối thiểu

**Mục đích:** SSOT nghiệp vụ cho sprint Phase 0-core block 0.6.  
**Cách dùng:** Plan #1 đã chốt → file này là BR hoàn thiện. Tech + step + prove-done → `devplan_checklist.md`.  
**Không** nhồn spec kỹ thuật vào BR.

**Nguồn phase:** `docs/Planing_docs/marketplace_jobmarket_feasibility_phase_plan.md` (§0.B Phase0-Sprint3).  
**Phụ thuộc:** Phase0-Sprint1 + Sprint2 CLOSED.

---

## Quy tắc (cho AI — đọc trước mọi thao tác trên file này)

- File này = *SSOT nghiệp vụ* (~3/10 sau Plan); tech + step + prove-done → `devplan_checklist.md`.
- Sprint này thống nhất **bỏ qua** `plan_mode_decisions` / `requirement_gap_debate` (giống Sprint1–2); sau BR → quiz tech trực tiếp vào `devplan_checklist.md` rồi mới code.
- *Anti-pattern:* implement khi chưa có checklist tech đã chốt; nhét tên cột/schema vào BR.

---

## Nội dung

> Plan #1 đã chốt 2026-07-25 — Recommended toàn bộ, **Q5 = A+B** (admin xem tất cả; user xem audit liên quan mình). Nguồn base: [base requirement.md](base%20requirement.md).

### 1. Bối cảnh & mục tiêu

*Bối cảnh*

- Sprint1–2 đã có role và ownership/CSRF. Hành động quyền lực (admin xóa nội dung bất kỳ, admin gán/thu hồi role) hiện **không để lại dấu vết nghiệp vụ**.
- Log hiện có chỉ là request/error file — không đủ để tranh chấp / đối chiếu.

*Mục tiêu nghiệp vụ*

- Có nhật ký **chỉ ghi thêm** cho hành động quan trọng.
- Mỗi bản ghi trả lời: ai (actor), làm gì (action), trên đối tượng nào (target), khi nào, kèm bối cảnh gọn nếu cần.
- Đọc lại được qua kênh tối thiểu (API), không cần UI.

*Actor*

| Actor | Vai trò |
|-------|---------|
| Admin | Thực hiện moderation / đổi role; xem **toàn bộ** audit |
| End-user | Xem audit **liên quan tới mình** (là actor hoặc là đối tượng bị tác động) |
| Hệ thống | Ghi sự kiện khi hành động thành công |

### 2. Sự kiện audit

Mỗi bản ghi gồm (mức nghiệp vụ):

| Thuộc tính | Ý nghĩa |
|------------|---------|
| Actor | Ai thực hiện |
| Action | Loại hành động (vd xóa pin, gán role) |
| Target type + target id | Đối tượng bị tác động |
| Thời điểm | Khi xảy ra |
| Bối cảnh gọn | Thông tin bổ sung ngắn (vd role được gán/gỡ) — không lưu full payload nhạy cảm |

*Append-only*

- Không cung cấp đường sửa/xóa bản ghi audit qua API.
- Nghiệp vụ cấm chỉnh sửa/xóa lịch sử.

### 3. Phạm vi hành động được ghi (sprint này)

| Hành động | Ghi khi |
|-----------|---------|
| Admin xóa pin bất kỳ (`/admin/pin/...`) | Thành công |
| Admin xóa comment bất kỳ (`/admin/comment/...`) | Thành công |
| Admin gán role cho user khác | Thành công |
| Admin thu hồi role của user khác | Thành công |

- **Chỉ ghi hành động thành công** — không ghi nỗ lực bị 403/404 trong sprint này.
- **Nhất quán giao dịch:** hành động thành công thì bản ghi audit phải tồn tại cùng lúc (không best-effort bỏ qua khi lỗi ghi).

### 4. Đọc lại audit

- Endpoint **tối thiểu** (không UI):
  - **Admin:** xem tất cả; lọc cơ bản theo actor / loại đối tượng / khoảng thời gian (mức đủ dùng, không dashboard).
  - **User thường:** chỉ xem bản ghi **liên quan tới mình** (mình là actor **hoặc** mình là target bị tác động — vd bị gỡ/gán role, hoặc nội dung của mình bị admin xóa nếu target gắn được với user).
- Không public.

### 5. Phạm vi

*In scope*

- Nhật ký append-only + helper ghi dùng chung.
- Hook moderation admin + đổi role.
- API đọc tối thiểu (admin all + self-related).
- Prove-done: sau hành động thành công có bản ghi đọc lại được đúng quyền.

*Out of scope*

- SIEM / retention / log shipping.
- Admin UI xem audit.
- Audit mọi mutate của user thường (pin/board/comment owner).
- Job market / Marketplace / payment / watermark.
- Lưu full request payload.

### 6. Acceptance criteria (business)

| ID | Tiêu chí |
|----|----------|
| AC-01 | Admin xóa pin thành công → có bản ghi audit với actor = admin, action xóa pin, target = pin đó. |
| AC-02 | Admin xóa comment thành công → có bản ghi audit tương ứng. |
| AC-03 | Admin gán role thành công → có bản ghi (kèm role được gán trong bối cảnh). |
| AC-04 | Admin thu hồi role thành công → có bản ghi (kèm role bị gỡ). |
| AC-05 | Hành động bị từ chối (403/404) → **không** tạo bản ghi audit (sprint này). |
| AC-06 | Không có API sửa/xóa bản ghi audit. |
| AC-07 | Admin đọc được toàn bộ audit (lọc cơ bản hoạt động ở mức tối thiểu). |
| AC-08 | User thường chỉ đọc được audit liên quan tới mình; không đọc được audit của người khác không liên quan. |
| AC-09 | Nếu ghi audit thất bại thì hành động chính không được coi là hoàn tất thành công (không “thành công im lặng mất dấu”). |
| AC-10 | Không mở SIEM/UI audit/Job/Marketplace trong sprint này. |

---

> **Trạng thái:** **CLOSED** 2026-07-25 — implement xong theo [devplan_checklist.md](devplan_checklist.md); AC-01…AC-10 pass qua `scripts/smoke_phase0_sprint3.py`, regression Sprint1/2 pass.
