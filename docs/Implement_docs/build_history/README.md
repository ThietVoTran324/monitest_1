# Build History — MONI

> **Vai trò:** Bộ tài liệu **lịch sử build / deploy / go-live** theo wave, bổ sung cho sprint folders (`Moni_SprintN/`) và macro plan (`Planing_docs/moni/`).  
> **Rule:** [`../lessonlearn.md`](../lessonlearn.md) A1–A3, J5 — quyết định & sự cố không chỉ nằm trong chat.  
> **Bug SSOT wave này:** [`../bug_history.md`](../bug_history.md)

## Mục lục

| File | Nội dung |
|------|----------|
| [README.md](README.md) | Index (file này) |
| [wave_2026-10_upgrade_golive.md](wave_2026-10_upgrade_golive.md) | Biên niên upgrade hardening + go-live `pinvps01` / `monitoring1.io.vn` |
| [artifacts_2026-10.md](artifacts_2026-10.md) | Commit SHA, image tags, host paths, secrets gate |

## Nguồn SSOT liên quan

| Layer | Path |
|-------|------|
| Macro plan | [`../../Planing_docs/moni/upgrade_hardening_phase_plan.md`](../../Planing_docs/moni/upgrade_hardening_phase_plan.md) |
| Sprint map | [`../../Planing_docs/moni/sprint_map.md`](../../Planing_docs/moni/sprint_map.md) |
| Runtime modes | [`../../Planing_docs/moni/RUNTIME_MODES.md`](../../Planing_docs/moni/RUNTIME_MODES.md) |
| Go-live host plan | [`../../../planning-docs/GO-LIVE-PINVPS01.md`](../../../planning-docs/GO-LIVE-PINVPS01.md) |
| DNS/Caddy ticks | [`../Moni_Sprint0/dns_caddy_golive.md`](../Moni_Sprint0/dns_caddy_golive.md) |
| CI harden notes | [`../Moni_Sprint9/CI_CD_HARDEN_NOTES.md`](../Moni_Sprint9/CI_CD_HARDEN_NOTES.md) |
| Issues (process) | [`../issues_history.md`](../issues_history.md) |
| Server facts | [`../../../server-context.md`](../../../server-context.md) |

## Cách thêm wave sau

1. Copy `wave_YYYY-MM_<name>.md` + `artifacts_YYYY-MM.md`.  
2. Ghi bug vào [`../bug_history.md`](../bug_history.md) (ID mới).  
3. Link từ [`../../Planing_docs/moni/README.md`](../../Planing_docs/moni/README.md) và Planing_docs index.
