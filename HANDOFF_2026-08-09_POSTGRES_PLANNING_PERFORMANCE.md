# Handoff · PostgreSQL planning and performance · 2026-08-09

## Production status

- Active release: `/opt/sewing-web/releases/codex-beaa606-84b33884-20260809T111912Z`.
- Production code commit: `beaa60689c2bbe1d4ddf8175be74ee57ebac46af`.
- Site: `https://www.shagaemfabrika.ru/app`.
- PostgreSQL: 16.14; `schema_migrations` contains 18 migrations, latest is `018_operational_migration_control.sql`.
- Post-deploy `/health`: ready; SQLite and marketplace PostgreSQL are ready.
- Production→WMS reconciliation and production monitor completed successfully after deployment.
- Rollback release: `/opt/sewing-web/releases/codex-5c7a68d-20260808T135044Z`.

## What was completed

- Added protected admin planning endpoints:
  - `POST /api/admin/planning/overview`;
  - `POST /api/admin/planning/calculate`.
- Added the admin screen `Админ → Планирование` with MRP, capacity/skills, OEE,
  unit economics, demand forecast and WMS slotting calculators.
- Applied migrations 013–018 for BOM/MRP, capacity, QMS/OEE, WMS optimization,
  costing/forecasting and operational migration control.
- Fixed migration 016: picking waves now keep the immutable external SQLite shipment id
  instead of an impossible cross-database foreign key.
- Fixed article-first WMS identity for materials and semi-finished components. Different
  articles no longer merge even when their names, colour and other descriptions match.
- Split/cacheable frontend assets, short-lived authenticated session restore cache,
  analytics read-model cache, request metrics and bounded graceful HTTP shutdown are active.
- Product images are normalized and served through controlled thumbnail routes.
- Added conservative production load smoke and isolated backup restore verification tools.

## Verification

- PostgreSQL 16 full suite: 358 discovered, 358 executed, 358 passed, 0 failed,
  0 skipped; all migrations 001–018 applied on a clean database.
- Python compile, JavaScript syntax, `git diff --check`: PASS.
- Offline web smoke on the final production candidate: PASS.
- Production load smoke, 60 GET requests / concurrency 6: 0 failures,
  23.52 requests/s, p50 220.62 ms, p95 463.60 ms, max 748.62 ms.
- Pre-deploy baseline: 9.15 requests/s and p95 1682.61 ms.
- SQLite production backup restore: PASS, 73 application tables.
- PostgreSQL critical restore: PARTIAL_PASS, 12 restored migrations, 15 zones,
  0 negative or over-reserved balances.
- Production after migration: 18 migrations and 0 invalid warehouse balances.

## Infrastructure action still required

The production WMS database is 14 GB while the only server filesystem has 12 GB free.
A full second PostgreSQL restore cannot fit on that server. No old backup was deleted to
manufacture free space. Increase the disk so that at least 25–30 GB remains free after the
live database and backups, or restore regularly on a separate recovery host. After that,
run `scripts/verify_production_restore.py` without `--critical-only` and require `PASS`.

## Repository

- Working branch: `codex/article-first-wms`.
- The release manifest records the source worktree and the 358/358 PostgreSQL gate.
- No `.env`, database, backup, export or log file belongs in Git.
