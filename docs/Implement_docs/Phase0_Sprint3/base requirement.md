# Base requirement — Phase0-Sprint3 (Audit log tối thiểu)

> Input gốc Plan #1. SSOT nghiệp vụ sau chốt: [business_requirement.md](business_requirement.md).

## Quyết định đã chốt (Plan #1)

- Phạm vi ghi: **admin moderation** (xóa pin/comment) + **thay đổi role** (gán/thu hồi).
- Bản ghi: actor + action + target type/id + thời điểm + bối cảnh gọn (không full payload).
- Append-only: không API sửa/xóa.
- Đọc lại: endpoint admin-only cho **toàn bộ** + user xem **audit liên quan mình** (actor hoặc target) — không UI.
- Chỉ ghi hành động **thành công**.
- Audit cùng giao dịch với hành động (thành công ⇒ phải có bản ghi).
- Out of scope: SIEM/retention/UI; audit mọi mutate user; Job/Marketplace.

## Ngoài phạm vi sprint này

- SIEM / retention / log shipping.
- Admin UI audit.
- Audit mọi mutate user thường.
- Job market / Marketplace / payment / watermark.
