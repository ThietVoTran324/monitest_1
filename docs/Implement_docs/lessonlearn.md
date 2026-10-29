# Lesson Learned — Đa dự án (tổng hợp phổ quát)
 
Gom từ `Planning_doc/Lessonlearn.md`, và các issue đã chốt.  
**Mục tiêu:** quy tắc áp dụng được khi **đổi tech stack, domain, cấu trúc repo, spec** — không phụ thuộc một sản phẩm cụ thể.  
**Cách dùng:** bắt đầu từ **mục M** (checklist 1 trang); chi tiết xem các mục A–L; sau mỗi milestone distill thêm vào file này hoặc `issues_history.md` nếu là sự cố.  
**Phạm vi theo loại dự án:** mục **H** (và issue tương ứng §7) chỉ khi có **UI tương tác**; mục **F/G** khi có API hoặc persistence; bỏ qua mục không liên quan (CLI thuần, batch, library).
 
---
 
## A. Tài liệu & nguồn chân lý (single source of truth)
 
### A1. Thứ tự cập nhật khi có quyết định mới
 
Khi chốt quyết định quan trọng, cập nhật *theo thứ tự* (tên file có thể đổi, vai trò giữ nguyên):
 
1. *Hợp đồng nghiệp vụ / spec* (business requirements, API contract, acceptance criteria).
2. *Kế hoạch thực thi* (dev plan, checklist theo step).
3. *Runbook vận hành* (cách chạy, build, migrate, health check).
4. *Lịch sử issue* (sự cố đã gặp + cách phòng).
 
Không để quyết định chỉ nằm trong chat — chat không phải SSOT.
 
### A2. Đồng bộ nhiều bộ tài liệu (mirror policy)
 
Nếu dự án có *nhiều folder doc* (ví dụ: doc sản phẩm + doc demo/training):
 
- Lesson/issue *có giá trị tái sử dụng* nên mirror sang bộ còn lại (có thể thêm tag nguồn).
- Ưu tiên *đầy đủ cho người mới* hơn rút gọn tối đa.
- Khi sửa rule ở một file, *rà soát xung đột* với file cùng vai trò (BR vs lesson vs checklist) trong *cùng phiên*.
 
### A3. Ghi quyết định lớn ngay trong phiên (decision log)
 
Sau *mỗi trao đổi có quyết định nghiệp vụ hoặc kỹ thuật đáng kể* (không phải "ok", xác nhận ngắn):
 
- Ghi vào *decision log* (ví dụ: Promt_History.md, DECISIONS.md): ý user rút gọn, phản hồi AI 1–3 câu, file/area bị ảnh hưởng (không cần paste prompt dài).
- Fix kỹ thuật chi tiết → *issues history*; quy ước tái dùng → *lesson learned* (file này).
 
### A4. Đọc chéo tài liệu trước khi “đóng” milestone
 
Trước khi mark plan completed: *đối chiếu* spec tiêu chí, checklist, lesson (nếu có) code/prompt distill.   
Inconsistency nội bộ là bug khó thấy nhưng phá handoff nặng.
 
### A5. Decision log — không log lặt vặt
 
*Không* ghi decision log cho: “ok”, xác nhận ngắn, reply không đổi spec/hành vi.   
*Có* ghi khi: đổi scope, đổi contract, đổi UX, chốt gate test, chọn giữa phương án A/B.
 
### A6. Distill handoff prompt khi đóng initiative lớn
 
Sau feature/demo/training lớn: rút gọn thành *một file prompt/runbook thực thi* (tên tùy dự án) đủ baseline + step + prove-done để lần sau ~90–95% tái lập *không cần* đọc lại toàn bộ chat.
 
### A7. Phân tầng độ chi tiết: BR vs devplan (tránh “detail → rất detail”)
 
*Vấn đề:* BR ghi quá sâu kỹ thuật (tên field DB, widget UI, cấu trúc file, payload mẫu, snippet code) → devplan chỉ “mở rộng thêm một lớp” → handoff Business → Dev bị lặp, khó đọc, khó chốt nghiệp vụ.
 
*Nguyên tắc tỷ lệ độ chi tiết (hướng dẫn, không cứng nhắc số):*
 
| Tài liệu | Mức chi tiết gợi ý | Nội dung *nên có* | Nội dung *không nên* (chuyển sang devplan) |
|----------|-------------------|---------------------|-----------------------------------------------|
| *Business requirements* | ~*3/10* | Mục tiêu, actor, phạm vi / out of scope, quy tắc nghiệp vụ (ngôn ngữ business), năng lực API ở mức “làm được gì”, acceptance criteria, traceability về spec gốc | Tên cột DB, widget, đường dẫn file, payload đầy đủ, tên class/handler |
| *Dev plan / checklist* | ~*10/10* | Schema/model, constraint, route/endpoint, auth, request/response shape, thứ tự file cấu hình triển khai, prove-done từng step | Định nghĩa lại “vì sao làm feature” (đã có ở BR) |
 
*Luồng derive (một chiều):*
 
1. Spec gốc (requirement_base/) → *BR* (lọc + chốt business, profile Core/Extend).
2. *BR* → *devplan_checklist* (bóc technical; mỗi AC business map ≥1 step prove-done).
3. Implement & test → tick checklist; quyết định lớn → decision log; sự cố → issues.
 
*Kiểm tra nhanh trước khi approve BR:*
 
- PM/BA đọc BR *không cần biết stack triển khai* vẫn hiểu phạm vi?
- Dev đọc devplan *không cần hỏi lại* field/route/file?
- BR và devplan *không copy-paste* cùng một bảng field?
 
*Ví dụ:* BR ghi chi tiết framework → devplan chỉ nhắc lại → tách BR (business) / devplan (technical).
 
---
 
## B. Kế hoạch & thực thi theo step
 
### B1. Checklist là đơn vị theo dõi tiến độ
 
- Mỗi *step/milestone* kết thúc bằng *prove-done* — chỉ tick khi có *bằng chứng* (build/test/smoke), không tick theo cảm giác.
- *Hard stop:* step hiện tại chưa pass verify → *không chuyển step* tiếp.
- *Gate chuyển step:* còn bất kỳ dòng [ ] trong step hiện tại → *không* sang step sau, *trừ* dòng đó có ghi (Pending: phụ thuộc Step … — …) và lý do còn đúng.
 
### B2. Phân biệt task vs tiêu chí trong checklist
 
- Dòng có *checkbox* [ ] / [x] = task theo dõi tiến độ.
- Dòng *không* checkbox = tiêu chí/validation mô tả dưới task cha (tránh nhầm “chưa làm”).
- Quy ước ký hiệu khuyến nghị: **-** = task; **+** = criteria/spec/validation (không tick riêng).
 
### B3. Cập nhật checklist *cùng lượt* với bằng chứng
 
Mọi lần chạy test/build/smoke pass hoặc fail → phản ánh *ngay* vào checklist.   
“Đã done nhưng chưa tick” = *incident quy trình* — log issue rồi sửa checklist.
 
### B4. Task/step phụ thuộc chưa xong
 
Ghi trên dòng task: (Pending: phụ thuộc Step X — <mô tả>) — không tick done giả.
 
### B5. Phát sinh task ngoài plan
 
Việc làm thêm hoặc phát hiện khi test → *thêm vào checklist* + log issue nếu đáng kể — không để im lặng.
 
### B6. Đóng step đủ bộ
 
Đóng một step chỉ khi đủ (tùy scope đã chốt):
 
1. Code/cấu hình xong và build pass.  
2. Test liên quan pass (automated + manual theo scope).  
3. Checklist + doc đã sync.  
4. Nếu đụng *contract/endpoint dùng chung* → smoke *tất cả consumer* liên quan.
 
### B9. Đóng milestone — “bộ 3” bắt buộc
 
Kết thúc milestone (step lớn):
 
1. *Cập nhật* tài nguyên test (script, manual guide, collection API) cho endpoint/hành vi mới.  
2. *Chạy* test (automated + manual theo scope).  
3. *Tick* checklist và sync doc — trong *cùng phiên*, không để “đã pass nhưng chưa tick”.
 
### B7. Plan trước code (đặc biệt khi làm việc với AI)
 
- *Plan phase:* context-check, regenerate checklist từ spec, trình bày intent + prove-done từng step.  
- Chỉ *implementation* sau khi plan được chốt.  
- Không shortcut “lấy sẵn implementation” bỏ qua checklist đã regenerate.
 
### B8. Council / adversarial review tại mốc lớn
 
*Tối thiểu 3 lần* (điều chỉnh tên mốc theo dự án, giữ đủ 3 vai trò):
 
| # | Mốc (ví dụ) | Trọng tâm review |
|---|-------------|------------------|
| 1 | Sau xong *backend / API* | Contract, validation biên, FK/schema, test assert status/header |
| 2 | Sau xong *frontend / UI* (nếu có) | Accessibility dialog/list, stale async response, giữ hành vi màn cũ, error UX |
| 3 | Trước *đóng plan / handoff* | Spec checklist lesson prompt/runbook; inconsistency nội bộ |
 
- Review *hostile* (adversarial): không chỉ “code chạy”.  
- Critical → fix ngay; major → fix nếu effort thấp; minor → defer có ghi chú trong checklist/issues.
 
### B10. Checkpoint chưa verify được — không tick giả
 
Mục chưa có bằng chứng (thiếu browser, thiếu quyền, chờ dependency) → *giữ* [ ] và ghi ngay trên *cùng dòng*: (Pending: …) hoặc (Chưa verify: …).  
Không tick “tạm” rồi quên.
 
### B11. Step bị block — sync checklist ngay
 
Phát hiện task/step *kẹt*, phụ thuộc chưa xong, hoặc scope đổi giữa step → cập nhật devplan_checklist *trong phiên đó* (annotate Pending / thêm dòng / log issue) — không để trạng thái plan lệch với thực tế.
 
### B12. Gap review trước khi “vá” scope phase 2 / extended
 
Khi có *bản mở rộng* triển khai sau bản core:
 
1. Viết *gap/debate* (spec code UI) — liệt kê: thiếu, thừa, chốt giữ nguyên, làm sau.
2. Stakeholder *chốt từng mục* trước wave fix — tránh implementer tự vá lan.
3. Wave fix theo phase + tick checklist + manual smoke.
 
*Anti-pattern:* Code phase 2 xong rồi mới so spec → refactor lớn (đổi quan hệ entity, migration).
 
### B13. Chốt “giữ nguyên / làm sau” có ghi vào BR hoặc checklist
 
Quyết định *không làm* (i18n, tùy chọn UI, tham số API phụ, …) phải ghi rõ trong BR/checklist *Out of scope / Chốt giữ* — tránh bị hỏi lại mỗi milestone.
 
---
 
## C. Cấu hình & môi trường
 
### C1. Phân lớp cấu hình (tránh hiểu nhầm)
 
- File .env / .env.example thường là *tài liệu tham chiếu cho team*, không phải runtime tự đọc (trừ khi stack đã cấu hình load).
- Runtime đọc: biến môi trường hệ thống, file config framework, secrets manager — *ghi rõ* trong README.
- Mọi thay đổi biến môi trường → cập nhật *đồng thời*: .env.example, README, lesson (nếu có lệnh vận hành).
 
### C2. Chuẩn hóa giữa stack / công cụ
 
Khi team dùng *nhiều stack* (ví dụ URL DB kiểu A vs connection string kiểu B): document *mapping tương đương* ngay từ đầu — tránh mỗi người tự map.
 
### C3. Runbook lệnh — format cố định
 
- Mỗi lệnh vận hành: **mục đích: lệnh** (copy một dòng được).
- Nhóm tối thiểu: start/stop service, build, migrate/schema, health check, dọn port/process.
- Cập nhật runbook *ngay khi chốt step lớn* có lệnh mới.
 
### C4. URL client server phải khớp runbook
 
Base URL API / cổng service trong *config client* và *runbook* phải *cùng một nguồn chân lý*.  
Đổi cổng server → cập nhật client config + runbook + (nếu có) CORS/allowed origins *cùng lượt*.
 
### C5. Dependency khai báo ≠ đã cài trên runtime thật
 
Package manifest / lockfile / requirements.txt khai báo thư viện ≠ môi trường chạy server/test đã cài.
 
- Ghi trong manifest *và* runbook: lệnh cài dep trên *đúng* interpreter/process.
- Build/upgrade fail “not found” → cài dependency, chạy lại — *không* sửa code nghiệp vụ trước.
 
### C6. Script vận hành vs snippet shell
 
Script trong scripts/ phải *tự bootstrap* (đọc config, kết nối DB, context app) — không chỉ vài dòng giả định REPL/shell đã có sẵn biến.
 
Snippet tương tác → README/runbook; file .py`/.sh` → chạy độc lập được.
 
---
 
## D. Vận hành local & session
 
### D1. Một phiên service rõ ràng
 
- Tránh *nhiều process* cùng chiếm một port → address already in use, build bị lock file.
- Trước build/migrate: *dừng* service đang giữ file/port (nếu stack tạo file lock khi chạy).
 
### D2. Thứ tự thao tác khi đổi schema
 
1. Kiểm tra process đang chạy.  
2. Dừng service cũ.  
3. Migration / schema update.  
4. Build.  
5. Start lại service.  
6. Health check + một endpoint dữ liệu.
 
### D3. Port hygiene
 
Trước khi spawn dev server mới: *kiểm tra port* đã bận chưa.  
Nếu đã có instance → *tái sử dụng*, tránh lệnh *interactive* (hỏi đổi port) trong automation/CI.
 
### D4. Tín hiệu shell ≠ tín hiệu service
 
Task/script background *fail* không đồng nghĩa app down.  
Quyết định tiếp theo dựa trên *health endpoint / smoke thật*, không chỉ exit code của wrapper.
 
### D5. Runtime gate trước khi debug nghiệp vụ
 
Khi “UI/API không có data”:
 
1. Client/UI process up?  
2. Server/API up?  
3. Health check OK?  
4. Ít nhất *một endpoint dữ liệu* trả success?  
 
Chỉ khi pass 4 bước mới đào filter/business logic.
 
### D6. Build ≠ dev server (frontend)
 
build tạo artifact; *dev server* mới phục vụ trình duyệt — cần cả hai tùy mục đích verify.
 
### D7. Phối hợp phiên khi nhiều terminal
 
Trước migrate/build trong môi trường có service nền: xác định process đang giữ port/file lock → dừng *một* instance rõ ràng → thao tác → start lại → health. Tránh nhiều người/agent spawn trùng mà không ai “own” việc dừng.
 
### D8. Mất context terminal / session cũ
 
Task/terminal cũ fail hoặc mất kết nối → *không* kết luận từ exit code cũ.  
Luôn xác nhận lại: health + ít nhất một endpoint dữ liệu trước khi tiếp tục step.
 
---
 
## E. Kiểm thử
 
### E1. Tài nguyên test tập trung, không tản
 
- Script automated, hướng dẫn manual, collection API test → *một nơi* theo module/milestone.
- *Một collection* API dùng chung (Postman/Insomnia/OpenAPI runner) — thêm folder/request theo feature, *không* tách file collection mới mỗi step (trừ yêu cầu đặc biệt).
- *Hai luồng song song (khuyến nghị):* script trong repo (agent/CI) + collection/curl ngoài (dev thử tay) — cùng URL/body; đóng step phải *đồng bộ cả hai*.
 
### E2. Ba kênh bổ sung cho API (khuyến nghị mạnh)
 
Mỗi step có API mới, xác nhận bằng *ba kênh* (bổ sung, không thay thế):
 
| Kênh | Nội dung |
|------|----------|
| *Automated* | Unit/integration + script smoke trong repo |
| *Collection runner* | Postman/Newman/CI API test với assert status/shape |
| *Manual* | REST client/curl/GUI — edge case, header, UX lỗi |
 
Gate đóng step API: cả ba *pass* hoặc có chứng từ ngắn trong checklist/issues.
 
### E3. Test theo step — scope rõ
 
Khi team chốt “test như các step trước”, mặc định thường là:
 
- build/compile pass,  
- test automated theo step,  
- manual smoke hành vi vừa sửa.  
 
*Không* tự thêm loại test mới (ví dụ unit test UI) nếu chưa được yêu cầu — tránh nhiễu scope.
 
### E4. Integration test gần production
 
- Ưu tiên *provider/runtime thật* cho test end-to-end contract — tránh trộn provider giả + thật gây fail giả.
- *Không* dựa dataset seed/shared chung cho assert tổng hợp — tạo dữ liệu test *scope hẹp* (prefix/GUID/tenant/time-window).
 
### E5. Test export / file machine-readable
 
- Assert *parser-level* (parse CSV/JSON, đếm cột/dòng), không chỉ “có chuỗi header”.
- Số và datetime trong export: *format cố định* (ISO-8601, dấu thập phân chuẩn), *không* phụ thuộc locale máy host.
 
### E6. Đối chiếu đa nguồn (reconciliation)
 
Khi cùng một chỉ số hiển thị ở *nhiều nơi* (chart, list, export):
 
- Chốt *cùng semantics filter* (cùng mốc thời gian, cùng trạng thái entity) *trước* khi viết test.  
- Có test *đối chiếu chéo* (tổng khớp nhau trên cùng bộ filter) trước khi tick done.
 
### E7. Gate hiệu năng cho feature filter/list
 
Step có filter/query trên dữ liệu lớn → có mục *index/perf gate* (hoặc review query plan) trước khi coi done — tránh nợ perf.
 
### E8. Smoke khi không có trình duyệt
 
Có thể thay một phần manual UI bằng: dev server up + HTTP 200 + response có *điểm mount client* (root element / bundle) — *không* kỳ vọng nội dung render đầy đủ trong HTML tĩnh.
 
### E9. Chế độ “test mù context” (tùy chọn team AI)
 
Trigger (ví dụ "bắt đầu test"): agent chỉ dùng file workspace hiện tại, không viện meta phiên trước.  
Trigger thoát (ví dụ "kết thúc test"): làm việc bình thường.
 
### E10. Cấu trúc test theo milestone/step
 
Mỗi step/milestone có tối thiểu (tên folder tùy dự án):
 
- manual-test.md — checklist thao tác tay.  
- Script smoke/API tự chạy được (step-NN-*.ps1, *.sh, pytest file, …).  
- (Khuyến nghị) file REST .http / tương đương trong repo — cùng URL/body với script.
 
### E11. Index test — cập nhật khi thêm script
 
Khi thêm script/collection mới → cập nhật *README/index* test (bảng: step | lệnh chạy | pass criteria) — tránh script “mồ côi” không ai biết chạy.
 
### E12. Chốt chiến lược test *trước* khi viết test code
 
Trước implement test suite, chốt bằng văn bản (không chỉ chat):
 
| Hạng mục | Cần chốt |
|----------|----------|
| Phạm vi automated | Unit / persistence / integration / HTTP / E2E — cái nào có, cái nào không |
| Phạm vi manual | Collection runner (Postman/Insomnia/…), smoke UI |
| Database test | DB riêng vs DB dev chung; quy tắc prefix + cleanup |
| SSOT endpoint | *Code hiện tại*, không chỉ số lượng trong spec gốc (spec hay lệch sau triển khai) |
| CI | Có hay chưa; kênh nào bắt buộc pass để đóng milestone |
 
*Anti-pattern:* Test chỉ cover subset spec ban đầu trong khi implementation đã thêm capability.
 
*Gate verify:* File chốt liệt kê đủ endpoint/hành vi + các kênh (automated + manual collection).
 
### E13. Ba kênh test API — vai trò khác nhau, không thay thế
 
| Kênh | Mục đích | Ai chạy |
|------|----------|---------|
| *Automated trong repo* | Regression, CI, prove-done checklist | Agent / dev / pipeline |
| *Collection import* | Thử tay, demo, debug session | Dev / BA |
| *Script vận hành* (ngoài test) | Sửa quyền, state, schema kẹt — *không* phải test | Dev khi incident |
 
Đóng milestone API: automated pass *và* collection cập nhật *cùng* contract (URL, body, auth/session).
 
### E14. Test code ở repo root vs test trong package chính thức (bridge)
 
Khi test runner *chỉ discover* test trong package/module chính thức của framework:
 
- *Logic test* có thể đặt ở thư mục gốc repo (test/, tests/) để quản lý đa module.
- *Bắt buộc* bridge mỏng trong package chính thức: import logic + class tên Test* với __module__ = package đó.
- Entry package test (ví dụ tests/__init__, index.ts, assembly) phải *đăng ký* submodule test_* — loader thường **không** quét file chưa được import/khai báo.
- *Không* để class case gốc (FooCases) trong namespace bridge — runner có thể load *mọi* subclass → chạy đôi.
- Tạo subclass qua type('TestFoo', (FooCases,), {'__module__': __name__}) nếu tên gốc không bắt đầu bằng Test.
 
*Gate verify:* Lệnh test chính thức báo đúng số case, không duplicate suite / metadata thiếu.
 
### E15. Test trên DB dùng chung — prefix + cleanup *commit*
 
Khi automated test chạy trên DB dev/production-like (không DB throwaway riêng):
 
1. *Prefix/GUID* cho mọi entity test (tuân rule validation nghiệp vụ nếu có).
2. *Không* xóa toàn bảng / delete all.
3. *Rollback* sau mỗi test method *không đủ* nếu HTTP layer commit hoặc cleanup cùng transaction bị rollback.
4. Cleanup đầu/cuối suite: connection *riêng* + **commit** — chỉ domain prefix.
 
*Anti-pattern:* tearDown() xóa rồi rollback → lần chạy sau duplicate key / data rác.
 
### E16. HTTP/API test — tạo dữ liệu cùng “tầng” với request
 
Integration test gọi HTTP trong khi setup bằng persistence trực tiếp (repository/SQL/ORM):
 
- Dữ liệu trong transaction test có thể *không hiện* với request HTTP (session/connection khác) dù đã flush.
- *Ưu tiên:* setup qua *cùng API* mà test gọi; hoặc document + verify chế độ test của framework.
 
*Gate verify:* Test “create → read detail” ổn định, không flaky empty/not found.
 
### E17. HTTP client test — tắt proxy hệ thống cho localhost
 
Proxy corporate/captive portal có thể chặn http://localhost:<port> → response *403 HTML*, không phải lỗi app.
 
Trong setup HTTP test: tắt proxy env / NO_PROXY cho localhost; áp dụng *sau* bước tạo lại HTTP client (login thường tạo client mới).
 
---
 
## F. API & contract (nguyên tắc đa stack)
 
### F1. Mở rộng endpoint đã có nhiều consumer
 
- *Backward-compatible:* hành vi/ shape cũ giữ nguyên cho caller không đổi.  
- Shape mới chỉ khi caller *chủ động* gửi param/version/header mới.  
- Trade-off: polymorphism có thể “xấu” — chấp nhận có chủ đích hoặc tách endpoint/version riêng khi scale.
 
### F2. Đổi contract → rollout đồng bộ
 
Checklist khi đổi response/error shape:
 
- Server/controller + *tất cả client consumer* + script test + collection API.  
- Smoke từng màn hình/ service phụ thuộc.  
- Chỉ “done” khi render/hành vi khớp thực tế.
 
### F3. Error contract thống nhất
 
- Format lỗi *một kiểu* (code + message user-facing).  
- Đổi format → cập nhật *cả* server và client parser + smoke các nhánh lỗi chính (400/404/409/timeout).
 
### F4. Validation filter range đối xứng
 
Filter có min`/max` hoặc from`/to`:
 
- Validate **min ≤ max** (hoặc from ≤ to) → *400* với code rõ — *không* trả empty im lặng (user không biết filter sai hay không có data).
 
### F5. Status code có ý nghĩa trạng thái
 
Ví dụ: thao tác hợp lệ nhưng *trạng thái resource không cho phép* → *409 Conflict* (không nhầm với 400 validation hay 404 not found). Document lý do trong spec.
 
### F6. Test assert khớp contract, không chỉ body
 
Happy path POST: assert cả *status*, *body*, và *header* quan trọng (ví dụ Location) nếu spec yêu cầu.
 
### F7. Validation filter đối xứng trong cùng module
 
Endpoint/list/filter *mới* có range (min/max, from/to, pageSize, …) → áp dụng *cùng pattern* với endpoint cũ trong module (400 + code lỗi, clamp biên, không silent empty).
 
### F8. Phân biệt lỗi mạng/timeout vs validation
 
Client parser và message user-facing *tách bạch*:
 
- Timeout / connection / server down → message runtime (không giống validation).  
- 400/404/409 → code + message từ contract.  
Đổi một nhánh → smoke cả hai loại.
 
### F9. List API — giới hạn phân trang (biên)
 
page, pageSize, limit → validate/clamp theo spec (ví dụ pageSize max 100); test assert biên vượt ngưỡng.
 
### F10. SSOT số lượng capability API = inventory code hiện tại
 
Sau phase implement (đặc biệt bản mở rộng):
 
- Lập *bảng endpoint thực tế* từ code (grep route decorator / OpenAPI / router table).
- So với spec gốc → ghi *delta* (thêm/bỏ/đổi) vào planning hoặc README API.
- Test automated + collection manual cover *inventory*, không chỉ subset spec ban đầu.
 
---
 
## G. Toàn vẹn dữ liệu & side effects
 
### G1. Quan hệ tham chiếu: app check + DB constraint
 
Entity bị tham chiếu bởi bản ghi khác:
 
- *Application check* trước delete (409 có message rõ).  
- *DB FK* ON DELETE RESTRICT (defense-in-depth chống race).  
- Catch lỗi DB khi save/delete → map về *cùng* error contract user-facing, không lộ stack trace.
 
### G2. Cập nhật trạng thái trung gian (non-terminal)
 
- Mọi trạng thái *không terminal* phải có đường xử lý chính thức trên UI hoặc API vận hành — tránh can thiệp DB tay.
- Update trạng thái trung gian: định nghĩa *field bất biến* (immutable boundaries).  
- Side effects (trừ điểm, trừ tiền, v.v.): *hoàn tác cũ → áp mới* để số dư nhất quán.
 
### G3. Tiền / số nguyên business
 
- Tiền: *integer* trong domain model khi có thể — tránh float và truncate ngầm.  
- Validate *reject* input thập phân nếu domain chỉ cho phép số nguyên.  
- Client + server cùng validate.
 
### G4. Lỗi delete/conflict tại điểm thao tác
 
409 / conflict / validation trên thao tác xóa/sửa → hiển thị *inline* trong dialog/form đang mở; *giữ* dialog mở.  
Tránh chỉ toast/global rồi đóng dialog — user mất ngữ cảnh.
 
---
 
## H. UI/UX & accessibility (khi dự án có UI tương tác)
 
Nguyên tắc **không** gắn framework. Triển khai web thường map sang WAI-ARIA; desktop/mobile map sang API accessibility của nền tảng.
 
### H1. Modal / dialog
 
- Khai báo *semantic modal* theo chuẩn nền tảng (tiêu đề, mô tả khi cần).  
- *Focus trap* đủ vòng Tab (kể cả vùng focus “ảo” trên shell dialog).  
- Esc / backdrop đóng; click trong dialog không đóng nhầm qua backdrop.  
- *Scroll lock* khi mở; *khôi phục* trạng thái scroll/overflow đã lưu khi đóng.  
- *Return focus* về control đã mở dialog.  
- Helper focus/scroll *tách theo feature* — không share state giữa picker / form / confirm.  
- Schedule initial focus *một lần* sau render — tránh chuỗi delay lồng nhau gây race.
 
### H2. Dialog hành động nguy hiểm (destructive)
 
- Focus mặc định trên *Hủy/Cancel*, không phải Xóa/Confirm.  
- Mô tả rõ *entity* đang bị tác động (title/body), không chỉ “Xác nhận xóa?”.  
- Lỗi server (409, 404): *giữ dialog*, lỗi *inline* — không toast rồi đóng ngầm.
 
### H3. Thông báo lỗi & hành động có ngữ cảnh
 
- Lỗi field/dialog: dùng *live region / announcement* theo mức độ (polite vs assertive trên web).  
- Nút trong bảng/dòng: nhãn accessible = *động từ + tên bản ghi*, không chỉ “Sửa” / “Xóa”.
 
### H4. Submit in-flight
 
Khi request đang chạy: *disable* input và nút (không chỉ nút Submit) — tránh state drift khi mạng chậm.
 
### H5. Danh sách async — stale response & tìm kiếm trễ
 
- Request list: *sequence id / cancel / ignore outdated* — response cũ không ghi đè kết quả mới.  
- Tìm kiếm/lọc có *delay*: lấy giá trị từ *sự kiện/input mới nhất* trước khi gọi API — không phụ thuộc blur hoặc binding hai chiều lệch timing.  
- Ô lọc *số* gõ nhanh: cùng pattern delay/guard như text — tránh flood API.
 
### H6. Filter min/max trên client
 
Trước khi gọi API: *guard* min ≤ max (hoặc from ≤ to) — tránh gửi range tạm khi user đang gõ → lỗi list chung chung.
 
---
 
## I. Git & phân tách phạm vi (nguyên tắc)
 
### I1. Boundary module / package
 
- Code feature nằm trong *boundary rõ* (folder/package/service riêng).  
- *Không* import/phụ thuộc build trực tiếp vào legacy ngoài boundary (trừ tham khảo ý tưởng).  
- Monorepo có thể chứa doc chung nhưng *build & điều tra* gói trong boundary.
 
### I2. Branch & baseline (feature lớn / demo)
 
- Feature/demo trên *branch riêng*; tag/baseline trước khi tách để rollback.  
- `main`/protected branch: không WIP feature; doc có thể cherry-pick riêng code feature.
 
### I3. Commit tách code và doc
 
Commit *code* và commit *doc* riêng khi cần cherry-pick doc không kéo feature.
 
### I4. Feature lớn / demo trên branch riêng
 
Implementation thử nghiệm hoặc demo trên *branch riêng*; tag/baseline trước khi tách để rollback. Branch bảo vệ (main) không chứa WIP feature — doc định hướng có thể merge/cherry-pick riêng code feature.
 
### I5. Tag baseline trước khi tách branch
 
Trước branch feature/demo lớn: tạo *tag* (hoặc commit marker) trên nhánh bảo vệ = điểm rollback an toàn nếu nhánh thử nghiệm bị bỏ.
 
---
 
## J. Làm việc với AI / pair programming
 
### J1. Spec + checklist là input chính
 
AI regenerate plan từ *business requirements*, không copy checklist cũ cho nhanh (anti-cheat / anti-drift).  
Khi viết BR: tuân *A7* (~3/10 business); khi viết devplan: derive technical (~10/10) — không nhồn kỹ thuật vào BR rồi nhân đôi ở checklist.
 
### J2. Log issue & lesson — không trì hoãn
 
- *Mọi* sai lầm / phát hiện lỗi (user hoặc AI) → ghi *ngay* vào issues_history (hoặc issues_history.md ở dự án mới): triệu chứng, tác động, cách xử lý, rule phòng lần sau.  
- Sau *mỗi step hoặc nhóm function* đóng: distill quy ước tái dùng vào lessonlearn / lessonlearn.md — không để chỉ nằm trong chat.  
- Sau khi AI tự fix: sync checklist step liên quan; quyết định lớn → decision log (Promt_History.md, DECISIONS.md, …).
 
### J3. Vòng lặp quyết định (a→b→c→a)
 
Dừng lặp; ghi issue; đưa user *2–3 lựa chọn* có cách verify; quay về spec hoặc spike nhỏ một giả thuyết.
 
### J4. Không mở rộng scope test/UI khi user chưa yêu cầu
 
Rollback nếu đã thêm test/refactor ngoài scope.
 
### J5. Bắt buộc tự log (agent / dev) — gặp lỗi & sau khi xử lý
 
*Không chờ user nhắc.* Trong *cùng phiên* làm việc:
 
| Sự kiện | Hành động bắt buộc |
|---------|-------------------|
| Phát hiện bug / sai spec / drift checklist | Ghi entry **issues_history** (template issues_history.md) |
| Đã fix xong | Cập nhật entry issue: *cách xử lý* + *rule phòng lần sau* |
| Rút ra quy ước tái dùng | Thêm/bổ sung **lessonlearn** (hoặc file multi-project) |
| Quyết định scope/contract/UX | **decision log** (A3, A5) |
| Liên quan step đang chạy | Sync **devplan_checklist** (`[x]`/`[ ]`/Pending) |
 
*Phân tách:* issue = sự cố cụ thể; lesson = pattern; decision log = chốt hướng đi.
 
### J6. Distill sau milestone lớn (trước “học tiếp”)
 
Khi đóng initiative / yêu cầu tổng kết:
 
1. Quét checklist, gap doc, chat quyết định.
2. Log *cụ thể* → file initiative (issues_log.md hoặc tương đương).
3. Rút *pattern phổ quát* → lessonlearn + mục § phù hợp trong issues_history — *bỏ* tên product/path/stack.
4. (Tùy chọn) Index milestone một trang trong folder initiative — *không* nhồi vào file multi-project.
 
---
 
## K. Known limitations — nên ghi thẳng trong spec
 
- Search pattern đặc biệt (wildcard SQL/LIKE) — document nếu không escape.  
- Không optimistic concurrency — last writer wins.  
- Test tạo dữ liệu không cleanup được qua API — chấp nhận prefix/GUID hoặc fixture cleanup.  
- Catch DB exception gộp nhiều nguyên nhân → chấp nhận trong demo, tách map ở production nếu cần.
- List search wildcard (LIKE`/contains`) không escape %
_
\ — document nếu admin-facing.
- Pagination chỉ clamp pageSize — document hành vi khi page vượt tổng trang.
 
---
 
## M. Workflow tối thiểu — checklist 1 trang (copy cho dự án mới)
 
Gom rule workflow từ mục A–J. Dùng làm **gate hàng ngày**; chi tiết kỹ thuật xem mục tương ứng hoặc `issues_history.md`.
 
### M0. File tối thiểu nên có
 
| Vai trò | Tên gợi ý | Ghi chú |
|---------|-----------|---------|
| Spec / BR | business_requirements.md | SSOT nghiệp vụ + acceptance |
| Kế hoạch | devplan_checklist.md | Step, [ ]`/`[x], prove-done |
| Vận hành | README / runbook | Format *mục đích: lệnh* |
| Sự cố | issues_history.md | Template entry đầu file |
| Bài học | lessonlearn.md hoặc copy lessonlearn.md | Quy tắc tái dùng |
| Quyết định | DECISIONS.md / Promt_History.md | Sau exchange có quyết định |
 
---
 
### M1. Trước khi code feature mới
 
- [ ] Đọc spec/BR; ghi *baseline assumption* (repo phải có gì trước khi bắt đầu).
- [ ] *Plan phase:* context-check (2 câu hỏi xác nhận hiểu đúng scope) → regenerate checklist từ spec — *không* copy checklist cũ cho nhanh.
- [ ] User/lead *chốt plan* trước khi implementation.
- [ ] Runbook: biết lệnh start/stop, build, migrate, health.
 
---
 
### M2. Trong mỗi step (lặp đến hết plan)
 
- [ ] Chỉ làm việc *step hiện tại*; không shortcut sang implementation “tương đương” ngoài checklist.
- [ ] Còn [ ] trong step → *không* chuyển step, trừ dòng có (Pending: phụ thuộc Step …).
- [ ] Mọi test/build/smoke pass hoặc fail → *cập nhật checklist cùng phiên* (không “done mà chưa tick”).
- [ ] Phát sinh việc khi test → thêm dòng checklist + log issue nếu đáng kể.
- [ ] Step kẹt / đổi scope → sync checklist + Pending ngay (B11).
- [ ] Chưa verify được → giữ [ ] + ghi (Pending: …) trên dòng (B10).
- [ ] Quy ước dòng: **-** = task có checkbox; **+** = tiêu chí/validation (không tick riêng).
 
*Đóng step — bộ 3:*
 
- [ ] (1) Cập nhật tài nguyên test (script, manual, collection API) cho hành vi mới.
- [ ] (2) Chạy test theo scope step (automated + manual).
- [ ] (3) Tick checklist + sync doc liên quan.
 
*Nếu step có API mới — thêm (khuyến nghị mạnh):*
 
- [ ] Kênh 1: lệnh test chính thức của repo / CI (npm test, pytest, mvn test, …).
- [ ] Kênh 2: collection runner (Postman, Newman, REST Client, …) — assert status/shape.
- [ ] Kênh 3: manual (curl/REST Client) — edge case, header, UX lỗi.
 
*Nếu đổi contract endpoint dùng chung:*
 
- [ ] Checklist “đổi *toàn bộ* consumer” + smoke từng màn/script phụ thuộc.
 
---
 
### M3. Sau mỗi exchange có quyết định (đặc biệt khi dùng AI)
 
- [ ] Ghi *decision log* (ý user + phản hồi 1–3 câu + file bị ảnh hưởng) — *không* log “ok” / xác nhận ngắn.
- [ ] Quyết định đổi spec → cập nhật theo thứ tự: *spec → checklist → runbook → issues*.
- [ ] Nhiều folder doc → mirror lesson/issue có giá trị; *rà chéo* BR checklist lesson trong *cùng phiên*.
 
---
 
### M4. Khi gặp lỗi / incident
 
- [ ] *Runtime gate* trước khi debug nghiệp vụ: client up → server up → health → 1 endpoint data.
- [ ] Ghi *ngay* entry issues_history (dùng template trong issues_history.md).
- [ ] Sau khi fix: cập nhật issue (xử lý + phòng ngừa) + lesson nếu có pattern mới (*J5*).
- [ ] AI/dev tự sửa → sync checklist + issue + lesson + decision log (nếu có quyết định) — *không chờ user nhắc*.
- [ ] Vòng quyết định lặp (a→b→c→a) → dừng; ghi issue; đưa 2–3 option có cách verify.
 
---
 
### M5. Council — 3 mốc bắt buộc
 
- [ ] *Council 1* — sau backend/API (contract, FK, validation, test vs spec).
- [ ] *Council 2* — sau frontend/UI (accessibility, stale list, consumer cũ, error inline).
- [ ] *Council 3* — trước đóng plan (docs khớp nhau; prompt/runbook đủ baseline).
 
---
 
### M6. Trước khi mark plan / milestone completed
 
- [ ] Đối chiếu: spec checklist lesson code (và prompt distill nếu có).
- [ ] Mọi số giới hạn (max length, status code) *trích từ schema/spec*, không copy từ bản cũ.
- [ ] Distill lesson mới vào lessonlearn (hoặc bổ sung lessonlearn.md).
- [ ] Distill *handoff prompt* / runbook thực thi nếu initiative lớn (A6).
- [ ] Feature thử nghiệm: tag baseline + branch riêng; tách commit *code* vs *doc* (I5, I3).
 
---
 
### M7. Tùy chọn — chế độ test mù context (training AI)
 
- [ ] User nói *“bắt đầu test”* → agent chỉ dùng file workspace, không viện meta phiên trước.
- [ ] User nói *“kết thúc test”* → làm việc bình thường.
 
---
 
### M8. Chỉ mục nhanh → mục chi tiết
 
| Checklist M | Chi tiết |
|-------------|----------|
| M1 Plan | B7, A1, C3 |
| M2 Step / bộ 3 / 3 kênh | B1–B9, E1–E2, E12–E17, F2, F10 |
| M3 Decision / SSOT | A1–A3 |
| M4 Incident | D5, J2, *J5*, J3, issues_history.md |
| M5 Council | B8 |
| M6 Đóng plan | A4, A6, I3–I5 |
| M7 Test mù | E9 |
 
---
 
## N. Template index milestone (đặt trong folder initiative — không trong file này)
 
Copy sang `planing_doc/<initiative>/MILESTONE_INDEX.md` khi đóng sprint. File `lessonlearn.md` / `issues_history.md` **không** chứa tên product cụ thể.
 
| Phase | Việc chính | Artefact gợi ý |
|-------|------------|----------------|
| Plan | BR + devplan + decision log | business_requirement.md, devplan_checklist.md |
| Core build | Feature tối thiểu shippable | source module/service |
| Extended | Phase 2 theo spec mở rộng | module/package phụ |
| Gap | Spec code UI + chốt giữ/làm sau | *_gap_debate.md |
| Verify | Automated + manual smoke | test README, collection API |
| Distill | Pattern → file multi-project | lessonlearn, issues_history §1–8 |
 
*Ba kênh test (mẫu chốt):* (1) automated persistence/domain, (2) automated HTTP/contract, (3) manual collection — xem E12–E13.
 
---
 
## L. Template thêm lesson mới
 
text
## [Mã] Tiêu đề ngắn
- Bối cảnh: (khi nào áp dụng)
- Quy tắc: (làm gì)
- Anti-pattern: (tránh gì)
- Gate verify: (chứng minh xong)
- Nguồn: (tùy chọn — ghi trong log initiative, không bắt buộc trong file multi-project)
 
---
 
Nguồn tổng hợp: Planning_doc/Lessonlearn.md, Planning_doc/issues_history.md, Planning_doc_demo (mirror). Cập nhật: 2026-05-21 — chuẩn hóa đa dự án: bỏ log/stack cụ thể; tổng quát hóa mục H (UI/a11y), A7, E8/E14/E16, M2; gộp lesson H1–H10 → H1–H6.
