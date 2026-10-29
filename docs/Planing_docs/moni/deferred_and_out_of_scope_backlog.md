# MONI — deferred / out of scope backlog

> Pull từ macro plan D* và survey. Khi một mục được làm, **kéo** sang sprint BR và đánh dấu DONE ở đây.

## A. Out of scope (đợt hardening này)

| ID | Mục | Ghi chú |
|----|-----|---------|
| OUT-01 | TCP/ICMP monitoring đầy đủ | Schema only |
| OUT-02 | Multi-region consensus / N-way fanout | Plan B — rejected |
| OUT-03 | Kafka / WebSocket live updates | Polling |
| OUT-04 | Slack / webhook / PagerDuty | Email only |
| OUT-05 | Org/team RBAC + billing plans | — |
| OUT-06 | Postgres partitioning ngay | Sau retention + số liệu |
| OUT-07 | Claim capacity 1000 monitors không đo | Sprint3 chỉ N khớp VPS |
| OUT-08 | Celery pool **gevent/eventlet** làm hướng chính | Xung đột stack hiện tại `asyncio`+`httpx.AsyncClient`+SQLAlchemy async; ROI thấp vs prefork/concurrency + Lambda (D10) |

## B. Type2 / làm sau (có thể gắn sprint sau GL)

| ID | Mục | Gắn gợi ý |
|----|-----|-----------|
| DEF-01 | SSRF pin-IP + custom transport + egress firewall | Post-Sprint1 |
| DEF-02 | Alert admin replay UI / dead-letter console | Post-Sprint6 |
| DEF-03 | External watchdog (UptimeRobot check MONI API) | Ops |
| DEF-04 | Deploy bỏ phụ thuộc tag `latest` hoàn toàn | Sprint9 |
| DEF-05 | Redis object-cache / CDN | Không liên quan core |
| DEF-REGION | **Multi-region = AWS Lambda** per region (D10). Ship plumbing 100% (chỉ cần setup env/deploy function là active). GL chỉ 1 region `direct`. Cấm public free list; CF/Render không path chính | Sau S5 honesty; bật khi có AWS/thẻ; macro §2.3 |

## C. Quyết định “chốt giữ” (không làm dù ai hỏi lại)

| ID | Giữ nguyên |
|----|------------|
| KEEP-01 | Celery decoupled khỏi API process |
| KEEP-02 | Local API port 8011 vs compose 8010 |
| KEEP-03 | `active_region` single execution |
| KEEP-04 | Alert channel = email MVP |
