# DNS + Caddy go-live — MONI trên `pinvps01` (song song `monitest.top`)

> CI/CD harden (health wait, prune, atomic script, ít đụng `.env`, blue-green nhẹ) → **Moni_Sprint9** / sau smoke tay.  
> **FQDN CHỐT:** `monitoring1.io.vn`

## 0) Thứ tự an toàn

1. Biết **IP public** của `pinvps01`  
2. Tạo **DNS** trỏ về IP đó (có thể trước khi Caddy có site)  
3. Swap + `/opt/moni` + `.env` + `compose up` (chỉ loopback)  
4. **Thêm block Caddy** (không xóa `monitest.top`)  
5. Caddy xin TLS tự động  
6. OAuth redirect + smoke  
7. Đổi GitHub `VPS_HOST` (sau cùng)

## 1) DNS records (registrar / Cloudflare / …)

Giả sử domain apex + www (bỏ www nếu không dùng):

| Type | Name | Value | TTL |
|------|------|--------|-----|
| **A** | `@` (hoặc `<MONI_DOMAIN>`) | `<VPS_PUBLIC_IP>` | 300–3600 |
| **A** | `www` | `<VPS_PUBLIC_IP>` | 300–3600 |
| **AAAA** | chỉ nếu VPS có IPv6 ổn | `<VPS_IPV6>` | — |

**Không** trỏ MONI vào IP/app của `monitest.top` khác máy.  
**Không** dùng CNAME vòng về nhau gây conflict với apex (trừ khi DNS provider hỗ trợ CNAME flattening).

Kiểm tra:

```bash
dig +short <MONI_DOMAIN> A
dig +short www.<MONI_DOMAIN> A
# phải ra đúng IP VPS
```

## 2) Caddy site (append — không replace file)

Sau khi API/FE đã listen `127.0.0.1:8010` và `127.0.0.1:4173`:

```caddyfile
# --- MONI (keep monitest.top block above unchanged) ---
<MONI_DOMAIN>, www.<MONI_DOMAIN> {
	encode gzip

	handle /api/* {
		reverse_proxy 127.0.0.1:8010
	}

	handle {
		reverse_proxy 127.0.0.1:4173
	}
}
```

```bash
sudo cp -a /etc/caddy/Caddyfile /etc/caddy/Caddyfile.bak.$(date +%Y%m%d)
# edit append block...
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

TLS: Caddy tự ACME — cần DNS đã trỏ đúng + port 80/443 mở tới Caddy.

## 3) `.env` prod (khớp domain)

```env
APP_ENV=production
APP_BASE_URL=https://<MONI_DOMAIN>
API_PUBLIC_URL=https://<MONI_DOMAIN>
GOOGLE_OAUTH_REDIRECT_URI=https://<MONI_DOMAIN>/api/v1/auth/google/callback
```

Google Cloud Console: thêm đúng redirect URI trên.

## 4) CI/CD harden (đã chốt hướng — làm Sprint9, không phình RAM 24/7)

- [ ] Health: sleep + curl lại / đợi container healthy  
- [ ] `docker image prune` sau deploy thành công  
- [ ] Script deploy atomic trên VPS (một lần SSH)  
- [ ] Giảm ghi `.env` (chỉ image tag qua file riêng hoặc env compose)  
- [ ] Blue-green **nhẹ** (optional; tránh dual full stack lâu trên 3.8G)  
- [ ] Backup trước migrate (đã có) + quy ước expand-contract cho migrate phá

## 5) Tick

- [x] FQDN chốt: `monitoring1.io.vn`  
- [x] A record OK (`dig` khớp IP VPS)  
- [ ] Stack loopback health OK  
- [ ] Caddy block + HTTPS OK  
- [ ] OAuth OK  
- [ ] Smoke prod OK  
- [ ] `VPS_HOST` → `pinvps01`
