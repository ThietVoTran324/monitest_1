# VPS prep checklist — Moni_Sprint0 (T5–T7)

> Chạy **tay** trên `pinvps01`. Không SSH/CI tự động trong Sprint0.  
> **T7:** không đổi GitHub secret `VPS_HOST` → máy này cho đến smoke tay + go-live gate.

## 1) Swap (bắt buộc trước khi `up -d` MONI)

Máy ~3.8 GiB RAM, no swap (macro §2.1). Ví dụ:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h
```

- [ ] `free -h` shows swap > 0  
- [ ] Persist across reboot (`/etc/fstab`)

## 2) Scaffold `/opt/moni`

```bash
sudo mkdir -p /opt/moni/backups
sudo chown -R "$USER":"$USER" /opt/moni   # hoặc user deploy
ls -la /opt/moni
```

- [ ] `/opt/moni` exists  
- [ ] `/opt/moni/backups` exists  

## 3) Caddyfile hiện trạng (chỉ ghi nhận — T6)

**Không** enable site MONI / DNS trong Sprint0.

```bash
# Ví dụ đường dẫn — chỉnh theo máy thật:
ls /etc/caddy/
sudo caddy validate --config /etc/caddy/Caddyfile   # nếu binary có
```

Dán tóm tắt vào đây sau khi đọc (ops):

```text
# Caddyfile summary (paste):
# - sites hiện có: …
# - monitest.top → /opt/pinterest (không đụng)
# - draft MONI site (chưa enable): host TBD → 127.0.0.1:8010 / 4173
```

- [ ] Đã đọc Caddyfile  
- [ ] Ghi summary ở trên  
- [ ] **Chưa** bật hostname MONI live  

## 4) GitHub deploy host (T7)

- [ ] Xác nhận workflow/`VPS_HOST` **chưa** trỏ `pinvps01` vì Sprint0  
- [ ] Gate: chỉ đổi sau smoke `curl http://127.0.0.1:8010/api/v1/health` trên máy mới  

## 5) Ports dự kiến (khi deploy sau này)

| Bind | Service |
|------|---------|
| `127.0.0.1:8010` | API |
| `127.0.0.1:4173` | Frontend static |

Không mở `0.0.0.0` cho API. Chi tiết modes: [`../../Planing_docs/moni/RUNTIME_MODES.md`](../../Planing_docs/moni/RUNTIME_MODES.md).
