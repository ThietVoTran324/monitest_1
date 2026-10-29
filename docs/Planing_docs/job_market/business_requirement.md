# Business Requirements — Job Market (system level)

**Mục đích:** SSOT nghiệp vụ cấp **hệ thống** cho Job Market (Phase 1.1–1.6).  
**Mức chi tiết:** ~3/10 (business). Schema/route/file → `Implement_docs/JobMarket_SprintN/` sau khi chốt.  
**Nguồn:** phase map, khảo sát codebase, và chốt nghiệp vụ 2026-07-26 (profile tabs, apply, explore JD, hiring-rights KYC).

> **Trạng thái:** **Gần chốt** 2026-07-26. D1–D16 đã chốt hướng nghiệp vụ. Còn sync `sprint_map.md` rồi mới mở Implement Sprint1. Không thu hẹp năng lực đã ghi khi implement.

---

## 1. Bối cảnh & mục tiêu

### Bối cảnh

- Web gốc đã có user profile đơn trang, pins, chat, updates/SSE, Phase 0-core (role, ownership, CSRF, audit tối thiểu).
- Chưa có domain tuyển dụng đầy đủ.
- `PortfolioView` tĩnh **không** phải Job Market.
- Tab pins hiện có trên profile user **giữ nguyên**; không phải deliverable JM mới.

### Mục tiêu Phase 1

1. **Một profile user** nhiều tab (không tách “profile JM” riêng khỏi profile gốc).  
2. Artist: work exp timeline + education/licensing/awards (**owner CRUD**; không university approve) + CV (tối đa 3, owner-managed).  
3. Employer/company: company profile, JD đang tuyển, quản lý JD + ứng viên, quản lý nhân viên (từ work-exp).  
4. **Explore JD** toàn site + **JD detail + apply**.  
5. **Hiring-rights request** (KYC) để nhận quyền tuyển dụng — không self-claim tùy tiện.  
6. Trust/moderation tối thiểu (company/JD) theo sprint 1.5; audit cho hành động trust.

### Ngoài phạm vi Phase 1

Chi tiết + mã backlog ổn định: [`../deferred_and_out_of_scope_backlog.md`](../deferred_and_out_of_scope_backlog.md).

Tóm tắt:

- Marketplace / thanh toán / watermark / eligibility bán pin  
- Role `university` + luồng approve education (quay Phase 0 — **không làm**)  
- Quản lý status **interview** trong apply pipeline  
- Backfill work-exp khi company đăng ký tài khoản sau (user tự sửa)  
- **Admin UI đầy đủ** (API admin tối thiểu vẫn có thể cần trong phase)  
- Thêm field profile gốc “để sau Phase 1” (ngoài tab JM đã mô tả)  
- Badge verified experience — planning riêng sau; Phase 1 vẫn có status approve từng dòng work-exp  
- Multi-member company self-serve; chat–application bắt buộc; ranking Explore phức tạp 

---

## 2. Actors

| Actor | Vai trò |
|-------|---------|
| Artist / ứng viên | Profile tabs, work exp, CV, explore/apply JD, nhận notify |
| Employer / company (đã có hiring rights) | Company profile, JD, ứng viên, approve work-exp, employee tab |
| User chưa có hiring rights | Có thể **yêu cầu quyền tuyển dụng** (KYC) |
| Admin | Review hiring-rights; moderation; audit; **có thể** CRUD credentials hộ (override) |
| Hệ thống | Notify in-app + email; sort timeline; derive employee list |

Roles Phase 0: `artist`, `employer`, `admin` (`seller` không dùng JM).  
**Hiring rights / employer** chỉ sau khi admin duyệt yêu cầu KYC (xem §7 D1).

---

## 3. Năng lực theo mặt sản phẩm

### 3.A — Profile artist (gộp vào profile user hiện có)

Profile gốc giữ như hiện tại; JM thêm **tab** trong cùng profile:

| Tab | Ai xem | Nội dung |
|-----|--------|----------|
| Profile cơ bản | Công khai theo rule hiện có | Profile user hiện tại; field JM bổ sung **sau Phase 1** nếu cần |
| Work experience | Công khai (dòng + status) | Timeline LinkedIn-like |
| Education / licensing / awards | Công khai đọc; **owner CRUD** | Không luồng approve university; admin override optional |
| CV | **Owner only** (+ employer đọc khi đã được nộp vào JD của họ) | Max **3** CV; chỉ upload + xóa |

**Pins:** giữ tab/list pin hiện có — không deliverable JM mới.

#### Work experience

- CRUD tự do các dòng trên timeline.  
- Field: tên công ty; hình thức (full-time, part-time, hybrid, outsourcing, collaborator); start/end (validation thời gian chặt); vị trí/chức vụ; location free-text.  
- **Auto sort** theo `start_date` tăng dần (quá khứ → hiện tại); user không sắp xếp tay.  
- Company input: dropdown gợi ý company đã có trên hệ thống (user/role nhà tuyển dụng–công ty) **hoặc** nhập tên ngoài hệ thống.  
- Status approve:
  - Company **không** trên hệ thống → luôn *chưa approve*.  
  - Company **có** trên hệ thống → *chưa approve* khi mới tạo / chưa duyệt; → *đã approve* khi company duyệt.  
  - Nếu sau này company mới có tài khoản: **không** backfill tự động; user tự cập nhật lại dòng.  
- Khi gắn company trong hệ thống: company nhận **email + in-app notify**, mỗi notify có link tới tab work-exp của artist và UI chỉ hiện nút approve trên **đúng dòng** được nhắc.

#### Education / licensing / awards

- Entity riêng (education / licensing / award); **owner CRUD** trên profile mình.  
- Visitor chỉ đọc công khai.  
- **Không** mở role university / luồng “trường duyệt / verify credential” trong Phase 1 (JM-01). Nội dung credential **không** cần verify bên thứ ba.  
- Admin **có thể** CRUD hộ (override / moderation); Admin UI product = ADM-03 backlog.

#### CV (artist)

- Chỉ **2 API nghiệp vụ chính:** upload, xóa (kèm xóa file storage khi xóa khỏi list).  
- Tối đa **3** CV / user.  
- Tab CV: **hard block** backend — chỉ owner quản lý list.  
- Employer được **đọc / tải** CV chỉ khi ứng viên đã apply CV đó vào JD của company họ.  
- Không public gallery CV.

#### Email bắt buộc cho hành động JM

Email **không** bắt buộc toàn site hiện tại, nhưng **bắt buộc** cho Job Market khi user:

- Upload CV lên hệ thống, hoặc  
- Apply vào JD  

Nếu chưa có email: chặn hành động + thông báo cần gắn email; 2 lựa chọn UI: đi profile thêm email / tạm bỏ qua (không hoàn tất hành động).

---

### 3.B — Explore JD + JD detail + Apply

#### Explore JD (tab lớn ngang profile / settings)

- List mặc định: mọi JD **active** (không rule ranking phức tạp Phase 1).  
- Search text: **title JD** + **tên công ty**.  
- Một nút Filter → popup:
  - Số năm kinh nghiệm yêu cầu  
  - Mức lương / range lương  
  - Vị trí làm việc (search text trên địa chỉ company được gán vào JD)  
- Click item list → **Vue route mới = JD detail** (không chỉ panel tạm).

#### JD detail (public với user đã login theo rule phase)

- Nội dung JD đầy đủ.  
- Cuối trang: nút **Apply**.  
- Route Vue riêng vì còn luồng apply và deep-link từ notify.

#### Apply popup

1. **Thư giới thiệu (file)** — optional upload file đính kèm application (không tính vào quota 3 CV).  
2. **Lời ngỏ / cover note (text)** — free text: giới thiệu bản thân, hiểu biết về công ty, …  
3. **CV:**  
   - Chọn 1 trong tối đa 3 CV đã lưu trên hệ thống, **hoặc**  
   - Upload CV trực tiếp từ máy cho **một lần apply** — **không** tính vào quota 3, **không** tự thêm vào tab CV của artist.  

Sau apply thành công → company nhận **email + in-app**, mỗi thông báo gồm:

- Link **profile artist**  
- Link **Vue route view CV** (riêng) có nút **tải CV về máy**

#### View CV (employer)

- **Vue route** riêng (không chỉ modal tạm), vì có nút tải về và deep-link từ notify / quản lý JD.  
- Hard ACL: chỉ employer của JD đã nhận application đó (và owner nếu cần xem lại bản đã nộp — chi tiết sprint).

#### Trạng thái application (đơn giản hóa — **không** có interview)

| Status | Khi nào |
|--------|---------|
| Đã gửi (submitted) | Vừa apply |
| Đã xem (viewed) | Employer **mở view CV** lần đầu |
| Từ chối (rejected) | Employer chọn từ chối |
| Thông qua (passed / shortlisted) | Employer chọn thông qua |

Ở `đã xem`, `từ chối`, `thông qua`: gửi **email + in-app** cho ứng viên, kèm link **JD detail** tương ứng.

**Không** quản lý status interview.

---

### 3.C — Site công ty / nhà tuyển dụng

#### Tab 1 — Company profile

- Tên  
- Địa chỉ: có thể nhiều line / chi nhánh  
- Ngành nghề chính  
- Mô tả  
- Size: min–max số người (input min và max)  

#### Tab 2 — Đang tuyển (JD active trong thời gian tuyển)

- Hiển thị các JD đang mở / đang tuyển (view phía public/company — chi tiết UI ở sprint).

#### Tab 3 — Quản lý JD (**owner-only**, hard block API)

- CRUD JD.  
- Field JD:
  - **Title** (bắt buộc)  
  - **Số năm kinh nghiệm yêu cầu** (bắt buộc)  
  - Mô tả công việc, yêu cầu ứng viên, quyền lợi — free text  
  - Lương “thường” / ghi chú lương free text nếu cần  
  - **Salary mode (bắt buộc chọn đúng một):**  
    - Không rõ ràng → UI hiển thị kiểu *you'll love it*  
    - Rõ ràng → min và/hoặc max (from–to / tối thiểu / up to) có validation  
  - **Địa điểm làm việc:** bắt buộc chọn từ địa chỉ/chi nhánh đã nhập ở company profile; **được chọn nhiều**  
- Employer **đóng JD chủ động** bất kỳ lúc nào; không phụ thuộc end time.  
- Vào **detail JD trong quản lý**: phần trên = detail; phần dưới = **list ứng viên đã apply**. Từ đây: mở profile ứng viên, mở view CV, đổi status xét CV (đã gửi → đã xem tự động khi mở CV → từ chối / thông qua).

#### Tab 4 — Quản lý nhân viên

- Owner cấu hình tab **public / private** ngay trong tab (chỉ owner đổi setting).  
  - Public: người khác xem được list theo rule hiển thị.  
  - Private: **chỉ owner**; hard block API với mọi user khác.  
- List **tự động**: artist có work-exp gắn company này với khoảng thời gian **từ quá khứ đến present** (đang làm). Sort mặc định theo thời điểm gia nhập (theo timeline artist). Không filter phức tạp Phase 1.  
- Khối **head** (lãnh đạo/HR/…): đưa lên đầu các cá nhân quan trọng — điều kiện: có tài khoản hệ thống **và** đang làm tại company. Không entity phức tạp: lưu thông tin thường (vị trí trong công ty, liên hệ free-text), free CRUD bởi owner.

#### Approve work-exp

- Company nhận notify khi bị gắn vào timeline; approve/reject đúng dòng; deep-link như §3.A.

---

### 3.D — Yêu cầu quyền tuyển dụng (Hiring rights / KYC)

**Vị trí UX:** trong **Cài đặt** tài khoản → nút “Yêu cầu quyền tuyển dụng” → mở tab/flow mới → điền/upload → submit.

#### Mục đích xác minh

1. Doanh nghiệp tồn tại thật.  
2. Người gửi liên quan và có quyền đại diện.  
3. Đăng tuyển cho **chính** doanh nghiệp — không phải headhunter đăng thay bên thứ ba.  
4. Doanh nghiệp chưa bị tài khoản khác chiếm quyền quản lý trên hệ thống.

#### Điều kiện trước khi mở form (thiếu thì báo rõ)

- Đã đăng nhập  
- Email tài khoản đã xác minh  
- Chưa có quyền tuyển dụng đang hoạt động  
- Tài khoản không bị khóa / hạn chế  

#### Nhóm field (bắt buộc / theo điều kiện / bổ sung khi admin yêu cầu)

Chi tiết field (quốc gia, loại hình DN, tên pháp lý, mã đăng ký, MST/VAT tách riêng, ngày thành lập không future, trạng thái hoạt động, địa chỉ pháp lý, website/email domain, social optional, lý do không có website/domain email ≤1000 chars, v.v.) — **bắt buộc theo bảng đã mô tả trong phiên chốt**; implement không được bỏ nhóm bắt buộc.

Lưu pháp nhân **tách field**, không gộp một `company_code`:

- `registration_number` (+ raw / normalized)  
- `tax_id` (optional theo quốc gia)  
- `vat_number` (optional theo quốc gia)  

**Ngôn ngữ review KYC mặc định: English.**  
`document_translation` bắt buộc khi tài liệu **không phải tiếng Anh** (hoặc admin không đọc được ngôn ngữ đó). Phase 1 chấp nhận bản dịch thường; admin có thể yêu cầu bản rõ hơn.

**Giấy tờ (upload):**

| Field | Khi nào |
|-------|---------|
| `business_registration_document` | Bắt buộc mọi hồ sơ (≥1 loại giấy tờ DN hợp lệ) |
| `tax_registration_document` | Khi MST không có trên giấy ĐK / quốc gia tách / admin không verify được |
| `authorization_evidence` | Khi người gửi không phải chủ/đại diện pháp luật |
| `identity_document` | Khi admin/rule nghi ngờ / không có email domain / cần đối chiếu — cho phép che PII không cần thiết |
| `document_translation` | Khi tài liệu ngoài **English** (ngôn ngữ review mặc định) |

**Kỹ thuật file Phase 1:** PDF/JPG/JPEG/PNG; max 15MB/file; max 5 file/nhóm; max 15 file/request; PDF ≤30 trang; cấm ZIP/RAR/exe/Drive-link/password-PDF/DOCX pháp lý; backend validate MIME + signature + size + readable + không mã hóa; **private storage** — chỉ owner request + admin review.

**Cam kết + chữ ký điện tử:** các checkbox cam kết đã liệt kê + nhập lại họ tên đầy đủ; lưu họ tên, thời gian, IP, user agent, phiên bản điều khoản.

**Email công ty:** phải khớp email tài khoản; gửi mail tự động tới email công ty với hành động **Xác nhận**.

#### Chống chiếm company — khóa pháp nhân (bắt buộc)

**Không** dùng làm hard unique: tên công ty, website domain, `tax_id` đơn lẻ toàn cầu, `registration_number` đơn lẻ không kèm quốc gia.

**Khóa pháp nhân chuẩn (hard unique cho company đang hoạt động):**

```text
UNIQUE(
  registration_country,
  registration_authority,   -- vùng/cơ quan nếu cần; VN Phase 1 có thể đơn giản hóa
  registration_type,
  registration_number_normalized
)
```

Ví dụ nhận diện:

- `VN` + (authority đơn giản) + `ENTERPRISE_REGISTRATION_NUMBER` + `0101234567`  
- `DE` + `Amtsgericht Berlin-Charlottenburg` + `HRB` + `123456`  
- `US` + `US-DE` + `STATE_FILE_NUMBER` + `1234567`  

**Normalize trước khi so trùng:** trim; uppercase; bỏ space / `-` / `.` / `/` nếu format cho phép; bỏ prefix thừa; **giữ leading zero**; không cast integer.  
Lưu cả `registration_number_raw` (đúng giấy tờ / admin đọc) và `registration_number_normalized` (so trùng).

**Cảnh báo (không hard block):** trùng tên gần giống; trùng website domain — admin review.

**Rule phụ (cảnh báo hoặc unique mềm theo quốc gia khi có rule rõ):** `country + normalized_tax_id`, `country + normalized_vat_number` — không thay khóa pháp nhân chính.

#### Tách `companies` và `company_verification_requests`

- **Không** mỗi lần submit KYC lại tạo một Company hoàn chỉnh mới.  
- Một pháp nhân = một `companies` record; nhiều `company_verification_requests` theo thời gian (rejected → need_more_info → approved).  

#### Khi mã pháp nhân đã tồn tại

| Trạng thái Company | Hành vi |
|--------------------|---------|
| Active + verified | **Không** tạo mới. Message: doanh nghiệp đã tồn tại — yêu cầu quyền quản lý / liên hệ hỗ trợ. Phase 1 chưa multi-member → ticket admin, tranh chấp thủ công. |
| Pending verification | **Cho phép nhiều request pending** cùng key; admin **chọn** một. Không lộ danh tính requester cho nhau. Không spawn `companies` mới. |
| Rejected trước đó | Cho request mới nhưng **liên kết** candidate/company cũ — không spawn Company mới mỗi lần reject. |
| Suspended | Không cho chiếm. Message: đang bị hạn chế — liên hệ hỗ trợ. |
| Soft-deleted / fraud / dissolved / merged | **Không** giải phóng unique key chỉ vì soft delete; phân biệt lý do trước khi tái sử dụng mã. |

Sau admin duyệt request → cấp hiring rights / gắn ownership đúng một pháp nhân đã verify; **account chuyển identity hiển thị sang tổ chức** — bề mặt profile chính **thay** profile cá nhân/artist trước đó (chốt JobMarket_Sprint2 Plan #1).

---

### 3.E — Trust & moderation (Phase 1.5)

- Theo BR: duyệt/flag company; report JD; harden CV allowlist.  
- Spec chi tiết khi vào sprint moderation — **không bỏ** khỏi phase.

### 3.F — Audit

- Đồng ý: hành động trust (duyệt hiring-rights, approve work-exp, moderation, và các mutate nhạy cảm khác khi sprint chốt) ghi audit append-only khi thành công.

---

## 4. Quy tắc chung

1. Role / hiring-rights gate mọi mutate employer.  
2. Ownership hard block API (JD manage, CV list, employee private, KYC docs).  
3. CSRF + cookie auth như Phase 0.  
4. Notify: **in-app + email** cho các sự kiện đã liệt kê (work-exp gắn company, apply mới, đổi status ứng viên, KYC email confirm).  
5. PII/CV private theo §3.A.  
6. Không dùng PortfolioView làm SSOT hồ sơ JM.  
7. Không hardcode username admin trên FE.

---

## 5. Acceptance criteria cấp hệ thống

| ID | Tiêu chí |
|----|----------|
| SAC-01 | Profile user có tab Work exp / Education-licensing / CV (owner) bên cạnh profile cơ bản; pins giữ nguyên. |
| SAC-02 | Work-exp CRUD + auto sort + company suggest/free-text + approve in-app khi company tồn tại; notify company đủ link/nút đúng dòng. |
| SAC-03 | Education/licensing/awards: **owner CRUD**; visitor chỉ đọc; không university approve. |
| SAC-04 | CV max 3 trên tab owner; apply upload từ máy **không** tính quota 3; employer chỉ đọc/tải CV đã nộp vào JD của họ; xóa list CV ⇒ xóa file đã lưu. |
| SAC-05 | Explore JD list active + search/filter; JD bắt buộc title + years experience. |
| SAC-06 | JD detail + apply (cover **file** optional + lời ngỏ **text** + CV chọn/lưu hoặc one-shot từ máy); chặn nếu chưa email; view CV là **Vue route** có nút tải. |
| SAC-07 | Application statuses: đã gửi / đã xem / từ chối / thông qua; không interview; đóng JD chủ động được. |
| SAC-08 | Company nhận notify apply (profile + view CV route); ứng viên nhận notify khi viewed/rejected/passed kèm link JD detail route. |
| SAC-09 | Company tabs: profile (branches, size min–max), đang tuyển, quản lý JD+ứng viên (owner), nhân viên auto + head CRUD + public/private. |
| SAC-10 | Hiring-rights KYC; `companies` tách `company_verification_requests`; unique pháp nhân theo country+authority+type+normalized number; không unique theo tên/domain; luồng trùng mã theo §3.D; review language **English**. |
| SAC-11 | Không ship Marketplace; không university approve; không backfill work-exp khi company xuất hiện sau. |
| SAC-12 | Audit tối thiểu cho trust actions đã chốt từng sprint. |

---

## 6. Quyết định đã chốt (thay open decisions cũ)

| ID | Chủ đề | Chốt |
|----|--------|------|
| D1 | Employer onboarding | **Self-request KYC** trong Settings → admin duyệt; không self-claim tùy tiện; không chỉ admin gán im lặng (admin vẫn có thể hỗ trợ vận hành) |
| D2 | Verified / hiring rights bar | Chỉ tài khoản **đã được cấp hiring rights** mới quản lý company/JD như employer |
| D3 | Artist profile shape | **Gộp tabs vào profile user hiện có**; không tách product profile; field gốc bổ sung sau Phase 1; pins không phải deliverable JM |
| D4 | Work-exp ngoài hệ thống | Free-text company ngoài hệ thống = luôn chưa approve; **không** email-token approve ngoài; **không** auto-link khi company đăng ký sau |
| D5 | Apply ↔ chat | **Chưa bắt buộc** trong chốt mới; apply + notify + profile/CV links là đủ Phase 1 trừ khi sprint bổ sung |
| D6 | Audit | Có cho trust actions; chi tiết action code theo sprint |
| D7 | CV visibility | Owner manage; employer read chỉ khi nhận apply |
| D8 | Apply status model | submitted → viewed → rejected \| passed; **bỏ interview** |
| D9 | Email | Bắt buộc trước upload CV hoặc apply; UX: tới profile gắn email / bỏ qua |
| D10 | Education | **Owner CRUD**; không university role / approve; admin có thể override |
| D11 | Verified badge tổng | Defer sâu khi planning riêng; status từng dòng work-exp vẫn có |
| D12 | Apply CV từ máy | **Không** tính vào quota 3; không tự thêm tab CV; đính kèm one-shot application |
| D13 | Cover letter | File upload (optional) **và** lời ngỏ text free-form — tách biệt |
| D14 | JD detail / view CV UX | **Vue routes** riêng (có nút tải CV + deep-link notify) |
| D15 | Chống chiếm company | Unique pháp nhân `country + authority + type + normalized_registration_number`; tách `registration_number` / `tax_id` / `vat_number`; raw+normalized; không unique name/domain; tách `companies` vs `company_verification_requests`; xử lý trùng theo trạng thái active/pending/rejected/suspended/deleted như §3.D |
| D16 | Ngôn ngữ review KYC | **English**; bản dịch bắt buộc khi tài liệu không phải English |

---

## 7. Traceability → sprint

SSOT cắt sprint: [`sprint_map.md`](sprint_map.md) (**synced 2026-07-26**, 6 sprint).

| Phase | Sprint | Gói năng lực |
|-------|--------|--------------|
| 1.1 | JobMarket_Sprint1 | Artist tabs + work-exp CRUD + CV owner + credentials owner CRUD |
| 1.2 | JobMarket_Sprint2 | Company + hiring-rights KYC + legal-entity unique |
| 1.3 | JobMarket_Sprint3 | Explore JD + JD detail + quản lý JD |
| 1.4 | JobMarket_Sprint4 | Apply + statuses + notify + view-CV route |
| 1.5 | JobMarket_Sprint5 | Work-exp approve + employee tab |
| 1.6 | JobMarket_Sprint6 | Trust & moderation tối thiểu |

Out of scope / admin-later: [`../deferred_and_out_of_scope_backlog.md`](../deferred_and_out_of_scope_backlog.md).

---

## 8. Gap mỏng

**Đã đóng** (2026-07-26): D12–D16. Sprint map đã sync.

---

## 9. Gate

- [x] Bổ sung apply + explore JD + CV visibility + hiring KYC vào BR hệ thống  
- [x] Đóng 5 gap mỏng (quota CV apply, cover file+text, Vue routes, legal-entity unique, review English)  
- [x] Ghi out-of-scope / admin-later / defer → [`../deferred_and_out_of_scope_backlog.md`](../deferred_and_out_of_scope_backlog.md)  
- [x] Đồng bộ `sprint_map.md` (6 sprint: 1.1–1.6)  
- [x] Mở `docs/Implement_docs/JobMarket_Sprint1/` (base + PLANNING_TRIO; BR sprint = Plan #1)  

---

*Cập nhật 2026-07-26 — sprint map synced.*
