# SECURITY REVIEW

**Дата:** 2026-08-07  
**Объём:** code controls + public HTTPS headers/origin/auth-boundary smoke. Секреты и production-базы не читались.

| Контроль | Фактическое состояние | Статус |
|---|---|---|
| Password hashing | PBKDF2-HMAC-SHA256, per-account 16-byte salt, 310,000 iterations, constant-time compare | PASS CODE |
| Login lock | 5 account failures → 5 minutes; per-IP 10 attempts/5 minutes | PASS CODE |
| Sessions | random token, only SHA-256 token hash in DB, absolute/idle TTL bounds, revoke on logout/password/employee disable | PASS CODE |
| Cookie | production name `__Host-sewing_web_session`, `Secure`, `HttpOnly`, `SameSite=Strict`, Path `/` | PASS CODE |
| CSRF | server-side session token required for mutating web API | PASS CODE |
| Origin | exact configured origin using constant-time comparison | PASS CODE |
| Telegram auth | Telegram WebApp HMAC, constant-time compare, future guard, 24-hour max age | PASS CODE |
| Admin APIs | active employee + server-side role checks; client employee IDs are not trusted for WMS writes | PASS TESTED |
| Uploads | 15 MiB request cap; 10 MiB attachment; 2 MiB defect photo; image MIME allowlist | PASS CODE/TESTS |
| Reverse proxy | production startup guard; public HSTS, referrer and content-type controls; invalid Origin rejected 403 | PASS LIVE PARTIAL |
| CSP | self-default, no object, hashed inline script/style blocks, no script attributes, upgrade insecure requests | PASS LIVE |
| Dependencies | GitHub quality job runs `pip check` and pinned `pip-audit 2.10.1` on Python 3.11; Actions use current Node 24-based major versions | PASS CI |
| SAST | Bandit 1.8.6 full local scan: 0 high, 76 medium, 22 low; CI run `31168318311` rejects every high-severity finding | PASS HIGH GATE; MEDIUM TRIAGE OPEN |
| Secret rotation | environment-owned secrets, no value in Git/report; rotation requires restart/fingerprint reconciliation | PLAN PRESENT; LIVE PENDING |
| Personal data | deletion blocked when production history exists; formal retention/anonymization policy absent | GAP |

## Открытые риски

1. `AUTH_MAX_AGE_SECONDS` для Telegram равен 24 часам. Это допустимо для Mini App-сессии, но до релиза нужно явно принять или сократить TTL.
2. CSP допускает `style-src-attr 'unsafe-inline'`; вне стабилизации нужно поэтапно убрать inline style attributes.
3. Bandit отметил 76 medium findings: преимущественно параметризованные SQL-запросы с безопасными константными SELECT-списками/placeholder lists, а также `urlopen` и контролируемые subprocess-вызовы. High findings отсутствуют; medium findings требуют пофайловой triage, а не массового подавления.
4. In-memory IP rate limit сбрасывается при restart и не общий для нескольких backend-процессов.
5. Нет утверждённого срока хранения/анонимизации ФИО, email, phone, IP/user-agent fingerprints и фото брака.

## Gate до релиза

- Medium Bandit findings вести отдельным пофайловым triage.
- В авторизованной сессии проверить фактический cookie name/flags и CSRF rejection; CSP и Origin rejection уже PASS live.
- Зафиксировать threat model для Telegram account takeover, stolen cookie, admin escalation, upload abuse и reverse-proxy spoofing.
- Утвердить secret rotation и personal-data retention/anonymization policy.
