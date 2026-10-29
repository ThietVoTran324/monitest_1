# Business Requirements — Phase0-Sprint1: Role & capability

**Mục đích:** SSOT nghiệp vụ cho sprint nền tảng Phase 0-core block 0.4.  
**Cách dùng:** Điền mục **Nội dung** (base dưới đây) → Plan #1 debate → thay toàn bộ **Nội dung** bằng BR hoàn thiện (giữ block quy tắc).  
**Không** nhồn spec kỹ thuật vào BR — chi tiết tech + step + prove-done → `devplan_checklist.md`.

**Nguồn phase:** `docs/Planing_docs/marketplace_jobmarket_feasibility_phase_plan.md` (§0.A, Phase 0-core).  
**Index bộ 3:** [PLANNING_TRIO.md](PLANNING_TRIO.md)

---

## Quy tắc (cho AI — đọc trước mọi thao tác trên file này)

- File này = *SSOT nghiệp vụ* (~3/10 sau Plan); spec kỹ thuật + step + prove-done → `devplan_checklist.md` (~10/10). *Không* nhồn API/JSON/status/a11y impl/lệnh test vào BR.
- *Hai lần Plan mode* (không gộp một phiên):
  - *Plan #1 (file này):* từ 「Nội dung」base → debate spec *nghiệp vụ* với user → *thay toàn bộ* 「Nội dung」 bằng BR hoàn thiện (giữ block quy tắc đầu file). *Chưa* implement; *chưa* chốt tech.
  - **Plan #2 (`devplan_checklist.md` / `plan_mode_decisions.md`):** sau BR hoàn thiện → chốt spec *tech* → mới được implement.
- Nếu 「Nội dung」 vẫn là base → chỉ được làm *Plan #1*; *cấm* implement / nhét spec tech vào BR.
- *Anti-pattern:* một Plan mode làm cả BR + devplan chi tiết; hoặc implement khi mới có BR base.

---

## Nội dung

> Plan #1 đã chốt 2026-07-25. Nguồn base gốc: [base requirement.md](base%20requirement.md).

### 1. Bối cảnh & mục tiêu

*Bối cảnh*

- Web gốc (Pinterest-like) sắp thêm Job market và Marketplace. Hiện moderation (xóa pin/comment bất kỳ) dựa trên so sánh username cứng — không mở rộng được, không gán/thu hồi có kiểm soát.
- Chưa có khái niệm vai trò trên tài khoản; mọi hệ thống sau đều cần “ai được làm gì”.

*Mục tiêu nghiệp vụ*

- Thay nhận diện admin theo tên bằng **vai trò** gắn tài khoản.
- Dựng nền **multi-role** dùng chung cho Job market / Marketplace sau (catalog sẵn; hành vi nghiệp vụ của employer/seller chưa bật trong sprint này).
- Admin có thể gán/thu hồi role qua kênh tối thiểu (không làm Admin UI trong sprint này).

*Người dùng / actor*

| Actor | Vai trò nghiệp vụ |
|-------|-------------------|
| End-user | Tài khoản thường; mặc định mang role artist |
| Admin | Moderations hiện có + gán/thu hồi role cho user khác |
| Hệ thống | Seed/migrate/backfill role khi đăng ký hoặc nâng cấp dữ liệu cũ |

### 2. Đối tượng nghiệp vụ — Vai trò (role)

Mỗi tài khoản có thể mang **một hoặc nhiều** vai trò trong catalog:

| Vai trò | Ý nghĩa nghiệp vụ | Hành vi bật trong sprint này |
|---------|-------------------|------------------------------|
| `admin` | Quản trị / moderation | Có — xóa pin/comment bất kỳ; gán/thu hồi role |
| `artist` | Người sáng tạo nội dung (pin) | Có — là role mặc định; chưa thêm quyền đặc biệt ngoài nền tảng hiện có |
| `employer` | Nhà tuyển dụng (Job market) | Chỉ tồn tại trong catalog / có thể được gán; **chưa** mở đăng tuyển |
| `seller` | Người bán quyền ảnh (Marketplace) | Chỉ tồn tại trong catalog / có thể được gán; **chưa** mở bán license |

*Quan hệ*

- Role gắn với user; không thay thế login/JWT hiện tại.
- Sprint này kiểm quyền theo **role-only** (không tách ma trận capability).

### 3. Luồng & quy tắc nghiệp vụ

**Đăng ký / user mới**

- User mới nhận role mặc định **`artist`**.

**User đã tồn tại (backfill)**

- Mọi user cũ nhận backfill **`artist`** nếu chưa có role mặc định.
- User từng được coi là admin qua hardcode username (`danya`), nếu còn trong hệ thống, nhận thêm role **`admin`** (có thể vừa `artist` vừa `admin`).

**Moderation (xóa pin / comment bất kỳ)**

- Chỉ user có role **`admin`** được thực hiện thao tác moderation “xóa bất kỳ”.
- Username cứng **không còn** là nguồn quyền.
- **Ngoại lệ nghiệp vụ (không mở moderation cho mọi người):** owner vẫn được xóa pin/comment **của mình** qua luồng user hiện có. Sprint này không siết ownership toàn hệ thống (để Phase0-Sprint2).

**Gán / thu hồi role**

- Chỉ **admin** được gán hoặc thu hồi role cho **user khác**.
- User **không** được tự nâng mình lên `admin` (cấm self-elevate).
- Kênh: seed/migrate + **API tối thiểu**. **Admin UI** là feature riêng sau khi hoàn thành các phần lớn hơn — **không** nằm trong sprint này / không nằm Phase 0.

**Catalog vs hành vi**

- Bốn role trên tồn tại ngay; sprint này **chỉ bật hành vi admin** (moderation + quản lý role). Job posting / bán license / eligibility seller = out of scope.

### 4. Phạm vi

*In scope*

- Mô hình multi-role với catalog `admin`, `artist`, `employer`, `seller`.
- Default + backfill `artist`; migrate bootstrap admin.
- Kiểm quyền moderation hiện có theo role `admin`.
- API tối thiểu để admin gán/thu hồi role (không UI).
- Giữ nguyên login / phiên đăng nhập hiện tại về mặt nghiệp vụ (không đổi cách user đăng nhập).

*Out of scope*

- Admin UI quản trị role (feature riêng, sau này).
- Phase0-Sprint2: ownership hardening toàn mutate, CORS/TrustedHost, cookie/CSRF.
- Phase0-Sprint3: audit log.
- Job market (JD/CV/apply/work exp) và Marketplace (license/payment/watermark).
- Ma trận capability tách khỏi role.

### 5. Acceptance criteria (business)

| ID | Tiêu chí |
|----|----------|
| AC-01 | User đăng ký mới có role `artist`. |
| AC-02 | User cũ được backfill `artist` (không mất tài khoản / không phải đăng ký lại). |
| AC-03 | User bootstrap admin cũ (nếu còn) có role `admin`; moderation không còn phụ thuộc đúng một username cứng. |
| AC-04 | User không có role `admin` gọi thao tác moderation “xóa bất kỳ” → bị từ chối. |
| AC-05 | User có role `admin` thực hiện được moderation “xóa bất kỳ” như trước về mặt nghiệp vụ. |
| AC-06 | Owner vẫn xóa được pin/comment của mình qua luồng user (không bị hiểu nhầm là “chỉ admin mới xóa được mọi thứ của mình”). |
| AC-07 | Admin gán/thu hồi được role cho user khác qua kênh API tối thiểu. |
| AC-08 | User không tự gán cho mình role `admin`. |
| AC-09 | Có thể gán `employer` / `seller` ở mức dữ liệu, nhưng không mở tính năng Job market / Marketplace trong sprint này. |
| AC-10 | Đăng nhập / phiên hiện tại vẫn dùng được sau thay đổi (không ép user đổi cách đăng nhập). |

---

> **Trạng thái:** BR **hoàn thiện** — Plan #1 xong. **Implement CLOSED** 2026-07-25 (xem `devplan_checklist.md` prove-done).
