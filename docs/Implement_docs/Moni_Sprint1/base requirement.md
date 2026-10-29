# Base requirement — Moni_Sprint1

> Input gốc cho **Plan #1**.  
> Macro: [`../../Planing_docs/moni/upgrade_hardening_phase_plan.md`](../../Planing_docs/moni/upgrade_hardening_phase_plan.md) · Phase **H1**.

## Bối cảnh

MONI gửi HTTP request tới URL do user cung cấp. Hiện đã chặn localhost/IP private lúc create và DNS resolve trước probe, nhưng:

- Client `follow_redirects=True` có thể đi theo redirect tới đích nội bộ.
- Response body được đọc hết (`aread`) không giới hạn.
- URL có userinfo / scheme lạ chưa bị từ chối tường minh.

## Mục tiêu shippable

1. Chỉ cho phép `http`/`https`; từ chối userinfo trong URL.
2. Mỗi bước redirect được kiểm tra lại URL + DNS/IP cấm.
3. Giới hạn số redirect và kích thước body đọc được.
4. Website công khai hợp lệ vẫn probe bình thường.
5. Test tự động cover các tình huống SSRF chính.

## Ngoài phạm vi

- Pin IP đã duyệt vào socket connect + custom TLS transport.
- Egress firewall trên VPS.
- Thay đổi UX create monitor ngoài message lỗi validation.
