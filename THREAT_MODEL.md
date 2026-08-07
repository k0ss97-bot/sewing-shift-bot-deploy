# THREAT MODEL — «Шагаем вместе»

**Версия:** 2026-08-07

## Активы

- учётные записи, роли, смены и история действий сотрудников;
- производственные задания, раскрой, брак, маршруты и зарплатные показатели;
- адресные остатки WMS и движения товара;
- marketplace catalog, продажи, остатки, поставки и финансовая аналитика;
- Telegram, Ozon, Wildberries и web-push credentials;
- SQLite operational state, PostgreSQL WMS/read models, backup archives и defect photos.

## Границы доверия

1. Browser/Telegram WebView → public HTTPS reverse proxy.
2. Reverse proxy → loopback web process.
3. Web process → private SQLite и PostgreSQL.
4. Backend/worker → Telegram, Ozon, Wildberries и push endpoints.
5. Admin/employee/TSD roles → server-side authorization and business invariants.
6. Systemd one-shots/timers → filesystem, PostgreSQL socket and operational notifications.

## Основные угрозы и контроли

| Угроза | Контроль | Остаточный риск |
|---|---|---|
| Stolen password / brute force | PBKDF2 310k, account lock, per-IP throttling, generic login error | in-memory IP limit не общий для нескольких процессов |
| Stolen session cookie | random token, hash-only storage, Secure/HttpOnly/SameSite Strict, absolute/idle TTL, revoke | фактические cookie flags требуют signed-in live проверки |
| CSRF / hostile Origin | exact Origin check, per-session CSRF token for mutation, SameSite Strict | live CSRF rejection требует signed-in session |
| Telegram account takeover / replay | initData HMAC, constant-time compare, future guard, 24h max age | 24h window должен быть принят владельцем или сокращён |
| Role escalation / forged employee ID | employee and role resolved server-side; admin/WMS access checks | ошибочное назначение роли администратором остаётся операционным риском |
| Duplicate production/WMS movement | idempotency keys, source IDs, transactions, outbox retry and reconciliation | ручная корректировка вне приложения может нарушить инварианты |
| Negative or conflicting stock | row locks/constraints, reconciliation and alerts | внешние legacy writers должны быть выведены из эксплуатации |
| Upload abuse | request/file size limits, image MIME allowlist, auth and ownership checks | нужен lifecycle/retention для defect photos |
| SQL injection | parameter binding; dynamic identifiers/select lists limited to code allowlists/constants | Bandit medium findings требуют пофайловой triage |
| SSRF / unsafe outbound URL | marketplace hosts and paths constructed by connector code, HTTPS APIs | `urlopen` callsites требуют explicit scheme/host assertions during medium triage |
| Command injection | subprocess uses argv arrays without shell; operational commands are code constants | executable PATH trust must remain root-owned in systemd environment |
| Reverse-proxy spoofing / debug exposure | forwarded headers opt-in, HTTPS origin/secure-cookie/debug startup guard, loopback backend | proxy configuration changes require release review |
| Secret disclosure | environment-owned credentials, no secret values in Git/evidence, fingerprints instead of tokens | rotation/restart verification remains operational procedure |
| Backup theft or destructive restore | 0600/0700 artifacts, isolated restore test, immutable releases and explicit rollback | formal off-host encrypted copy and retention ownership not defined |
| Marketplace outage/rate limit | typed error mapping, Retry-After handling, snapshots and readiness state | cached data can be stale; UI must show freshness/partial status |

## Release acceptance

- Dependency audit and Bandit high-severity gate must pass in CI.
- Public health, CSP/HSTS, invalid Origin and unauthenticated mutation rejection must pass.
- Signed-in session must prove cookie flags, CSRF rejection, admin boundary and logout revocation.
- A–G and TSD acceptance must use controlled records and prove no duplicate/negative movement.
- Every release retains previous immutable path and fresh pre-release backups.

## Owner decisions still required

- Accept or reduce Telegram initData maximum age (currently 24 hours).
- Approve retention/anonymization periods for PII, IP/user-agent fingerprints and defect photos.
- Define encrypted off-host backup owner, retention and restore-drill cadence.
