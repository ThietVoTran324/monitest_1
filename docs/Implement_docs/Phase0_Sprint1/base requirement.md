# Base requirement — Phase0-Sprint1 (Role & capability)

> Input gốc cho Plan #1. Sau Plan #1, SSOT nghiệp vụ là [business_requirement.md](business_requirement.md) (đã hoàn thiện). File này giữ tóm tắt khớp quyết định đã chốt — không supersede BR.

## Bối cảnh

App hiện có route admin (xóa pin/comment bất kỳ) nhưng quyền admin đang **hardcode username**. Không có model role. Sắp tới Job market cần `employer` / `artist`, Marketplace cần `seller`, moderation cần `admin`.

## Quyết định đã chốt (Plan #1)

- Multi-role; catalog: `admin`, `artist`, `employer`, `seller`.
- Mặc định + backfill user cũ: **`artist`**.
- Bootstrap admin cũ → thêm role **`admin`**; bỏ hardcode username làm nguồn quyền.
- Sprint này chỉ **bật hành vi admin** (moderation + gán/thu hồi role); employer/seller chỉ tồn tại trong catalog.
- Admin gán/thu hồi role cho user khác qua **API tối thiểu**; **cấm** self-elevate `admin`.
- **Admin UI** = feature riêng sau — out of scope sprint này / Phase 0.
- Kiểm quyền **role-only** (không capability matrix).
- Owner vẫn xóa object của mình qua luồng user; moderation “xóa bất kỳ” chỉ `admin`.
- Out of scope: Sprint2 (ownership/CORS/CSRF), Sprint3 (audit), Job market / Marketplace features.

## Ngoài phạm vi sprint này

- CSRF / CORS / TrustedHost / cookie flags → Phase0-Sprint2.
- Ownership check toàn hệ thống → Phase0-Sprint2.
- Audit log → Phase0-Sprint3.
- Eligibility seller / payment / job posting UI → stream Job market / Marketplace.
- Admin UI quản trị role → feature riêng sau.
