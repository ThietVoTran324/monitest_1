# Technical Design — Moni_Sprint1 (SSRF)

**Mức chi tiết:** ~7/10 (kỹ thuật).  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md) · BR: [business_requirement.md](business_requirement.md)

> **Plan #2 CHỐT 2026-10-27** — implement theo checklist.

---

## 1. Vấn đề kỹ thuật hiện tại

| Điểm | File | Gap |
|------|------|-----|
| Validate lúc create | `monitor_service.validate_monitor_url_host` | Không chặn userinfo; scheme mặc định http nếu thiếu |
| Pre-connect | `checks._ensure_public_target` | OK cho host đầu; không cover redirect |
| HTTP client | `checks.run_http_check` | `follow_redirects=True`; `aread()` không giới hạn |

---

## 2. Quyết định thiết kế

| # | Quyết định | Lý do |
|---|------------|-------|
| D1 | Module chung `backend/app/security/ssrf.py` | Một nguồn truth cho create + probe + redirect |
| D2 | `follow_redirects=False`; tự follow tối đa `SSRF_MAX_REDIRECTS` | Re-validate từng Location |
| D3 | Đọc body theo chunk tới `SSRF_MAX_RESPONSE_BYTES` | Tránh OOM |
| D4 | Settings mới trong `config.py` | Tunable không hardcode |
| D5 | Không pin IP socket (T2) | Sprint này đủ redirect+body+URL |

### Settings

| Key | Default | Ý nghĩa |
|-----|---------|---------|
| `SSRF_MAX_REDIRECTS` | `5` | Trần số lần follow Location |
| `SSRF_MAX_RESPONSE_BYTES` | `1048576` (1 MiB) | Trần body đọc vào memory |

---

## 3. Hợp đồng `ssrf.py`

```text
is_blocked_ip(ip: IPv4Address|IPv6Address) -> bool
validate_url_for_ssrf(url: str) -> None   # raise ValueError
assert_host_public(hostname: str) -> None # DNS + is_blocked_ip; raise ValueError
```

`validate_url_for_ssrf`:

1. `urlsplit`; scheme ∈ {http, https}; không cho userinfo; hostname bắt buộc.
2. Nếu hostname là literal IP → `is_blocked_ip`.
3. Không resolve DNS ở bước create (giữ hành vi hiện tại: chỉ block literal private; DNS lúc probe).

`assert_host_public`: resolve A/AAAA; mọi địa chỉ phải public; không có địa chỉ → lỗi.

---

## 4. Thay đổi call sites

| Call site | Thay đổi |
|-----------|----------|
| `monitor_service.validate_monitor_url_host` | Delegate `validate_url_for_ssrf` |
| `checks._ensure_public_target` | Dùng `validate_url_for_ssrf` + `assert_host_public` |
| `checks.run_http_check` | Manual redirect loop; stream/chunk body; cap bytes |

### Probe redirect loop (tóm tắt)

1. `current_url = monitor.url`
2. Lặp tối đa `SSRF_MAX_REDIRECTS + 1` request:
   - Validate URL + assert host public.
   - `client.request(..., follow_redirects=False)`.
   - Nếu status 3xx và có Location: resolve relative URL; `current_url = ...`; continue.
   - Else: đọc body có cap; break.
3. Quá redirects → `CheckResult` DOWN với error chứa `redirect limit` / `ssrf`.

### Body read

- Dùng `response.aiter_bytes()` cộng dồn; vượt cap → DOWN `response body too large`.

### Error taxonomy

- Giữ `error` string có substring nhận diện: `ssrf`, `private`, `blocked`, `redirect`, `body` để test/ops grep.
- Không đổi schema `CheckResult` / DB.

---

## 5. Tests

| Test | Kỳ vọng |
|------|---------|
| Create localhost / 127.0.0.1 / 10.x / userinfo / ftp | 400 |
| `assert_host_public` mock DNS → private | raise |
| Redirect mock: public → `http://127.0.0.1/` | DOWN/blocked, không coi UP |
| Body > cap | DOWN body limit |
| Happy path mock 200 nhỏ | UP (hoặc status theo threshold) |

File ưu tiên: mở rộng `backend/tests/test_ssrf_guards.py`; thêm unit cho `ssrf.py` và redirect/body nếu cần fixture httpx mock.

---

## 6. Rủi ro & mitigation

| Rủi ro | Mitigation |
|--------|------------|
| DNS rebinding giữa resolve và connect | Accept T2; ghi lesson nếu cần |
| Relative Location / `//evil` | `urljoin` chuẩn; validate lại full URL |
| HTTPS redirect sang HTTP | Cho phép nếu URL vẫn pass SSRF (không ép HSTS) |

---

## 7. Done = prove-done

Checklist [implementation_checklist.md](implementation_checklist.md) đủ tick + tests AC pass.
