# Business Requirements — Admin Ops (system level)

**Mức chi tiết:** ~3/10 (business). Schema/route/widget → Implement sprint Plan #2.  
**Index:** [README.md](README.md) · Survey: [system_survey.md](system_survey.md)  
**Prerequisite:** Phase 0 + Job Market + Marketplace **CLOSED**

> **Plan #1 CHỐT 2026-08-08** — `all suggest` (Q1–Q6 A/B theo bảng dưới).

---

## 1. Bối cảnh & mục tiêu

### Bối cảnh

- Ba phase trước ship **API admin tối thiểu** + ops Swagger/script; **cố ý** không làm Admin UI product (ADM-*).  
- Operator hiện không có màn hình thống nhất để duyệt KYC, moderation JD, copyright, roles, audit.

### Mục tiêu Phase 3 (Admin Ops)

1. Một **Admin shell** (route guard role `admin`, nav theo domain).  
2. **Queue UI** cho các luồng đã có API: KYC, JD report, company suspend, copyright, roles, audit, moderation pin/comment.  
3. Bổ sung API mỏng nơi thiếu cho vận hành (work-exp admin queue; copyright unlist khi resolve).  
4. Không thay nghiệp vụ Domain đã CHỐT (không mở refund in-app; không DRM).

### Ngoài phạm vi MVP (CHỐT)

- ADM-05 multi-claim / dispute product đầy đủ  
- ADM-08 bắt buộc công chứng  
- Payment/chargeback/VNPay admin (SEC-T2-07) — initiative payment sau  
- SIEM / analytics dashboard nặng  
- Thay Swagger (Swagger vẫn dùng cho debug)

---

## 2. Actors

| Actor | Vai trò |
|-------|---------|
| Admin | Vào `/admin`; xử lý queue; gán/thu hồi role; xem audit; moderation nội dung |
| Hệ thống | Giữ `require_roles("admin")` là gate thật; audit mutate quan trọng |
| User thường | Không thấy shell; chỉ luồng report/submit đã có |

---

## 3. Năng lực theo mặt

### 3.A — Core shell & trust

- Đăng nhập user có role `admin` → vào Admin app **trong Vue hiện tại** (`/admin/*`).  
- Nav: Overview (tối thiểu) · Users/Roles · Audit · Content (pin/comment) · JM · MP.  
- FE ẩn nút không đủ; API vẫn từ chối nếu không admin.

### 3.B — Job Market ops

- KYC hiring-rights: list/filter, xem doc, approve / need-more-info / reject.  
- Credentials override UI.  
- JD reports queue + dismiss/actioned; suspend/unsuspend company.  
- Work-exp: admin **list pending** + approve/reject (API list mới + UI — Sprint4 optional / theo map).

### 3.C — Marketplace ops

- Copyright reports queue + resolve/dismiss.  
- **CHỐT:** resolve → **unlist listing** (đổi status report + gỡ listing; **không** revoke `pin_license_access` trong MVP).  
- Rate-limit tạo report (SEC-T2-02) — kèm Admin MP sprint / hardening.  
- Order/payout admin: **out** phase này.

### 3.D — Trace → ADM-*

| ID | MVP |
|----|-----|
| ADM-01 shell + roles + content | **In** |
| ADM-02 KYC UI | **In** |
| ADM-03 credentials UI | **In** |
| ADM-04 JD report + suspend UI | **In** |
| ADM-05 dispute product | **Out** |
| ADM-06 structured need-more UI | **In nhẹ** |
| ADM-07 audit viewer | **In** |
| ADM-08 notarize | **Out** |

---

## 4. Quyết định hệ thống (Q1–Q6 CHỐT)

| ID | Chủ đề | **CHỐT** |
|----|--------|----------|
| **Q1** | Shell | **A** — Vue route `/admin/*` trong app hiện tại |
| **Q2** | Cắt sprint | **A** — Core → JM → MP lần lượt |
| **Q3** | Copyright resolve | **B** — status + **unlist listing** (không revoke license MVP) |
| **Q4** | Work-exp admin | **A** — thêm GET pending list + UI |
| **Q5** | ADM-05 / ADM-08 | **A** — **out MVP** |
| **Q6** | Payment admin | **A** — **out** phase này |

---

## 5. Acceptance hướng hệ thống

| ID | Case | Kỳ vọng |
|----|------|---------|
| A01 | User không admin mở `/admin` | Chặn (redirect / 403) |
| A02 | Admin xem audit filter được | 200, khớp API |
| A03 | Admin duyệt KYC qua UI | Cùng hiệu ứng API hiện có |
| A04 | Admin xử lý JD report + suspend | Cùng API Sprint6 |
| A05 | Admin resolve copyright | Status đổi + listing unlist |
| A06 | Admin gán/thu hồi role | Không self-modify |
| A07 | Non-admin gọi API admin | 403 |

---

## 6. Trace → sprint map

Xem [sprint_map.md](sprint_map.md) (**synced** sau CHỐT).  
Implement: `docs/Implement_docs/Admin_SprintN/`.
