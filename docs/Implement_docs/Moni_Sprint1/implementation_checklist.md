# Implementation Checklist — Moni_Sprint1

**Theo:** [technical_design.md](technical_design.md) · BR: [business_requirement.md](business_requirement.md)

> Tick khi đã prove-done (code + test hoặc bằng chứng).

## Docs

- [x] Plan #1 BR CHỐT
- [x] Plan #2 TD CHỐT
- [x] Sync `sprint_map.md` + macro status sau khi code xong

## Code

- [x] `backend/app/security/ssrf.py` (validate URL, blocked IP, assert_host_public)
- [x] Settings `SSRF_MAX_REDIRECTS`, `SSRF_MAX_RESPONSE_BYTES`
- [x] `monitor_service` delegate validate
- [x] `checks.run_http_check` manual redirect + body cap
- [x] `_ensure_public_target` dùng module chung

## Tests

- [x] Create: localhost / private / userinfo / bad scheme → 400/422
- [x] DNS private → blocked
- [x] Redirect → private blocked
- [x] Body over cap blocked
- [x] Happy path still works

## Close

- [x] Checklist tick đủ
- [x] Macro / sprint_map: Sprint1 = done

**Prove-done:** `py -3 -m pytest tests/test_ssrf_guards.py tests/test_checks_logic.py -q` → 24 passed (2026-10-27).
