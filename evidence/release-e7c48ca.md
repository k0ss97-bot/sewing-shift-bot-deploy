# RELEASE EVIDENCE — e7c48ca

**Дата:** 2026-08-07

**CI:** GitHub Actions Quality `31168318311` — PASS

**Release:** `/opt/sewing-web/releases/codex-e7c48ca-20260807T100615Z`

**Previous:** `/opt/sewing-web/releases/codex-f7cae4e-20260807T055152Z`

## До переключения

- HEAD = origin/codex/wms-integration = `e7c48ca6f6447f38d5bdb1fdeb759853d2d0819e`.
- SQLite и PostgreSQL backup one-shots: `Result=success`, `ExecMainStatus=0`.
- Release archive SHA-256: `76f9882572004a868b3aef220a62a73f9128ac6d2570e2faeb82950277afc9cb`.
- Compile: 68 Python-файлов; isolated Web smoke: PASS.

## После переключения

- `/opt/sewing-web/current` и `COMMIT` указывают на `e7c48ca`.
- SHA-256 `miniapp_assets.py`, monitor и reconciliation совпадают с локальным кандидатом.
- `sewing-web.service`, monitor timer и reconciliation timer active.
- Post-deploy monitor и reconciliation one-shots: `Result=success`, `ExecMainStatus=0`.
- Local и public `/health`: ready; SQLite, marketplace PostgreSQL и supplies ready.
- Public HTTPS: CSP, HSTS, Permissions-Policy и no-cache присутствуют.
- Invalid Origin login: HTTP 403 `invalid_origin`; unauthenticated admin mutation: HTTP 401 `unauthorized`.
- Штатный `sewing-marketplaces-sync.service` запущен после релиза и завершился `Result=success`, `ExecMainStatus=0`; повторный public health остался ready.

Авторизованные A–G и физический TSD этим протоколом не закрыты.
