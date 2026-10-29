# Bối cảnh VPS — `pinvps01`

Số đo dưới đây lấy lúc **17:39 ngày 26/10/2026 (UTC+7)**. Đây là máy đang chạy dự án chính (`monitest.top`). MONI chưa được đưa lên máy này.

Tài liệu viết cho người chưa từng đăng nhập máy. Mỗi tên kỹ thuật được giải thích ngay tại chỗ.

## Máy là gì

Một máy Linux trên mạng, tên `pinvps01`. Người quản trị đăng nhập bằng tài khoản `root` (tài khoản quyền cao nhất của máy).

| Hạng mục | Giá trị đo được |
|---|---|
| Nhân CPU | 2 (`nproc`) |
| Tải CPU lúc đo | 0,06 / 0,07 / 0,02 (máy gần như không làm gì) |
| RAM tổng | 3,8 GiB |
| RAM `used` | 1,9 GiB (chương trình đang giữ) |
| RAM `free` | 298 MiB (trống hoàn toàn) |
| RAM `buff/cache` | 1,9 GiB (hệ điều hành mượn tạm để đọc đĩa cho nhanh, nhường lại được) |
| RAM `available` | **1,9 GiB** (lượng thật sự còn nhận thêm chương trình) |
| Swap | **0**. Hết RAM thì Linux tắt process, không đẩy sang đĩa |
| Ổ `/` | `/dev/vda1`, 50 GB, đã dùng 29 GB, còn 19 GB (61%) |
| Thời gian máy đã chạy | 27 ngày tại lúc đo |

`available` mới là số dùng để quyết định có bật thêm dịch vụ hay không. `free` thấp vì phần RAM trống đang nằm trong cache.

## Trang web đang sống

- Địa chỉ: `https://monitest.top`
- Mã nguồn trên máy: `/opt/pinterest`
- Lệnh xem container đang chạy: `cd /opt/pinterest && docker compose -f docker-compose.prod.yml ps`

Khách không nói chuyện thẳng với ứng dụng. Đường đi:

1. Trình duyệt mở `https://monitest.top`.
2. **Caddy** (chương trình trên máy chủ, đang `active`) giữ cổng công cộng và chứng chỉ HTTPS.
3. Caddy chuyển tiếp vào container giao diện. Container đó xuất cổng **8080** của máy chủ ra cổng 80 bên trong.
4. Nginx trong container phục vụ giao diện Vue. Request bắt đầu bằng `/api` được chuyển tiếp sang API, cổng 8000, chỉ trong mạng Docker.

File cấu hình Caddy là `/etc/caddy/Caddyfile`, 72 byte, sửa lần cuối 29/09. Nội dung file chưa được đọc. Thư mục `/var/log/caddy` **trống** (không có access log trên đĩa).

`remote_ip` trong log là IP công cộng của đường mạng khách đang dùng (WiFi nhà, mạng di động). Không phải địa chỉ riêng của từng laptop hay điện thoại. Ba máy cùng một WiFi thành một IP. Một máy đổi từ WiFi sang 4G thành hai IP.

## Chín container đang chạy

Container là một chương trình được đóng hộp, có RAM và mạng riêng. Cả chín cái đang lên liên tục 2–3 tuần. API báo `healthy`. Lúc đo, CPU từng cái đều dưới 1%. RAM cộng lại khoảng **775 MiB**.

| Container | Image | Việc | RAM | Cổng |
|---|---|---|---|---|
| `fastapi-container` | `fastapi-image:latest` | API Python (FastAPI) | 270 MiB | 8000, chỉ trong Docker |
| `celery-worker-container` | `fastapi-image:latest` | Việc nền: ảnh, email, thống kê | 157 MiB | 8000, chỉ trong Docker |
| `rabbitmq` | `rabbitmq:3-management` | Hàng đợi để sẵn. Luồng chính của app không dùng | 112 MiB | chỉ trong Docker |
| `celery-beat-container` | `fastapi-image:latest` | Đồng hồ gọi việc định kỳ (đơn hết hạn) | 87 MiB | 8000, chỉ trong Docker |
| `mongodb` | `mongo:6` | Database để sẵn. Không phải database của app | 73 MiB | chỉ trong Docker |
| `postgres` | `postgres:15` | Database thật của app. Tên service là `postgres`, không phải `db` | 61 MiB | chỉ trong Docker |
| `vuejs-container` | `vuejs-image:latest` | Giao diện | 5 MiB | `0.0.0.0:8080` → cổng 80 trong container |
| `mailhog` | `mailhog/mailhog:v1.0.1` | Hộp thư giả để xem email | 5 MiB | `0.0.0.0:8025` |
| `redis` | `redis:7` | Phiên đăng nhập, cache, hàng đợi Celery | 4 MiB | chỉ trong Docker |

App thật chỉ cần API, worker, beat, Postgres, Redis và Vue. RabbitMQ, MongoDB và Mailhog đang bật nhưng không nằm trên đường khách xem trang.

Cổng mở ra internet của các container chỉ có **8080** (giao diện) và **8025** (Mailhog). Postgres, Redis, MongoDB, RabbitMQ và API không công bố cổng ra máy chủ.

Ảnh người dùng nằm trên đĩa trong thư mục `media` của `/opt/pinterest`. Database chỉ lưu đường dẫn file.

## Log truy cập

- Access log có IP khách từng nằm trong journal của Caddy (`journalctl -u caddy`), không nằm trong `/var/log/caddy`.
- Khoảng sau ngày 10/10/2026, request thành công không còn được ghi vào journal.
- Ngày 18–20/10 journal chỉ còn việc gia hạn chứng chỉ (`monitest.top`, `www.monitest.top`) và dọn bộ nhớ chứng chỉ. Không có `remote_ip`.
- Ngày 21/10 chỉ còn các kết nối bị Caddy cắt giữa chừng (`aborting with incomplete response`). Các IP đó gắn với hai tài khoản của chủ máy: `USER01` (user id 2) và `fs01` (user id 29).

Việc chỉ xem feed hoặc danh sách job **không** ghi một dòng nào trong database. Bấm một chỗ cần đăng nhập chỉ mở form trên trình duyệt (`openAuthModal`), không gửi request lên server. Dấu duy nhất của lần xem đó là access log, và access log thành công những ngày sau 10/10 không còn.

## Tài khoản và SSH

- Tài khoản Linux chỉ có `root`. Không thấy user hệ thống lạ.
- SSH đăng nhập thành công chỉ từ mạng của chủ máy. Các dòng `lastb` là bot thử mật khẩu cổng 22 và bị từ chối (`ssh:notty`, thời lượng `00:00`).
- Trong phần log còn đọc được, không có tài khoản app lạ để lại pin, comment, like hay view. `fs01` là tài khoản chủ máy tự tạo, không có trong script seed của repo.

## Chỗ trống nếu đưa MONI lên cùng máy

MONI chưa chạy ở đây. Bản production của nó là sáu container riêng (API, worker Celery, beat, Postgres, Redis, Nginx), cổng `127.0.0.1:8010` và `127.0.0.1:4173`. Không trùng cổng đang mở.

Ước lượng khi app hiện tại có khoảng 10 người đang dùng và MONI theo dõi khoảng 10 URL:

- Container hiện tại từ ~775 MiB lên khoảng 1,0–1,2 GiB.
- MONI lúc idle thêm khoảng 0,6–0,8 GiB.
- Tổng chương trình khoảng 2,5–3,0 GiB trên 3,8 GiB. `available` sau khi bật còn khoảng 1,1–1,3 GiB.
- 19 GB đĩa trống đủ cho image và database MONI lúc đầu.
- Không có swap: một đợt vượt RAM sẽ bị Linux tắt process.

Check của MONI không giữ kết nối thường trực. Mỗi URL, mỗi 60 giây, worker phân giải DNS, mở TCP, bắt tay TLS, tải nội dung HTTP, rồi đóng. Mười URL khỏe mạnh tốn khoảng 1–5% của một nhân CPU. RAM của MONI nằm ở sáu process luôn chạy, không nằm ở số URL.

Worker production **không** đặt số process. Celery lấy số nhân máy, tức **2 process** trên VPS này. Hệ số lấy task trước (`worker_prefetch_multiplier`) đã đặt thành **1** trong `backend/app/core/config.py`. Default của Celery là 4, nên default sẽ xin về khoảng `2 × 4 = 8` task rồi chỉ chạy 2. Cấu hình hiện tại xin về 2 và chạy 2. Việc hạ hệ số này không làm check nhanh hơn trên một container. Phần giảm số việc thật là mỗi monitor chỉ check một region đang active.

## Lệnh đã dùng để lấy số này

```bash
free -h
df -h /
nproc
uptime
cd /opt/pinterest && docker compose -f docker-compose.prod.yml ps
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
systemctl is-active caddy
ls -l /etc/caddy /var/log/caddy
```

Chưa đọc nội dung `/etc/caddy/Caddyfile`. Muốn xem đúng một đoạn chuyển tiếp:

```bash
cat /etc/caddy/Caddyfile
```
