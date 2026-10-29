# Business Requirements — Moni_Sprint1 (SSRF hardening)

**Mức chi tiết:** ~3/10 (business). Schema/route → Plan #2.  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
**Macro:** [`../../Planing_docs/moni/upgrade_hardening_phase_plan.md`](../../Planing_docs/moni/upgrade_hardening_phase_plan.md)

> **Plan #1 CHỐT 2026-10-27** — stakeholder: bắt đầu implement Sprint 1.

---

## 1. Mục tiêu

Ngăn người dùng dùng MONI như proxy để với tới mạng nội bộ / metadata / loopback, **mà không làm hỏng** việc kiểm tra website công khai hợp lệ.

| # | Năng lực |
|---|----------|
| 1 | Từ chối URL không phải http/https hoặc có thông tin đăng nhập nhúng |
| 2 | Từ chối đích loopback / private / đặc biệt lúc lưu monitor và lúc probe |
| 3 | Redirect không được mở đường tới đích cấm |
| 4 | Probe không tải body vô hạn; timeout/redirect có trần |
| 5 | Kết quả bị chặn ghi nhận là thất bại kiểm tra có lý do rõ (blocked), không coi là “website down mơ hồ” nếu có thể |

---

## 2. Actors

| Actor | Việc |
|-------|------|
| User (owner) | Tạo/sửa monitor với URL; nhận lỗi validation khi URL cấm |
| Worker | Probe URL; follow redirect an toàn; ghi check_run |
| Attacker (cùng là user) | Cố đưa URL/redirect nội bộ — phải bị chặn |

---

## 3. Quy tắc nghiệp vụ

1. Chỉ `http` và `https` được chấp nhận khi tạo/sửa monitor.  
2. URL chứa `user:pass@host` bị từ chối.  
3. Hostname/IP loopback, private, link-local, multicast, reserved, unspecified bị từ chối.  
4. Hostname công khai nhưng DNS ra IP cấm → probe bị chặn.  
5. Mỗi redirect: áp dụng lại cùng quy tắc URL + DNS/IP; vượt số redirect tối đa → thất bại kiểm tra.  
6. Body response chỉ đọc trong giới hạn đã cấu hình; vượt → thất bại kiểm tra (không làm cạn RAM).  
7. Website HTTPS công khai bình thường vẫn UP/SLOW theo policy hiện có.

---

## 4. Acceptance criteria

| ID | Tiêu chí |
|----|----------|
| AC1 | Create monitor `http://localhost...` / private IP / `http://user:pass@host/` / `ftp://...` → 400 |
| AC2 | Probe hostname resolve về IP private → bị chặn (không kết nối thành công như đích hợp lệ) |
| AC3 | URL công khai redirect về localhost/private → bị chặn ở bước redirect |
| AC4 | Response body vượt giới hạn → không đọc hết không kiểm soát; check kết thúc với lỗi giới hạn |
| AC5 | URL `https://example.com` (hoặc mock tương đương hợp lệ) vẫn probe được |
| AC6 | Automated tests cover AC1–AC4 tối thiểu |

---

## 5. Out of scope / Chốt giữ

- Pin IP vào TCP connect (T2-M01).  
- Firewall egress VPS (T2-M02).  
- Đổi interval/quota (Sprint12).  
- Đổi status page public DTO (Sprint10).
