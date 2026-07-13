# Repository Instructions

## Scope

These instructions apply to the whole repository. Keep changes narrow, preserve
existing behavior outside the assigned task, and follow the ownership guidance
in the project agents under `.codex/agents/`.

## Data Safety

- Treat `.env`, `bot.db`, `backups/`, `exports/`, and `logs/` as private runtime
  data. Never inspect, copy, modify, commit, or upload them during development or
  verification.
- Run every database-aware check with a fresh temporary `DB_DIR`. Never point a
  test, demo, or smoke server at a working database.
- Before importing `database.py` in an isolated script, set `DB_DIR` and change
  the current directory to the same empty temporary directory. The legacy path
  resolver can otherwise discover and copy a `bot.db` from the current directory.
- Bind local smoke servers to `127.0.0.1` and an ephemeral port. Do not expose a
  debug server on a public interface.
- Do not use real Telegram tokens, employee identifiers, or production exports
  in tests. Use obvious synthetic values.

## Collaboration

- Inspect `git status` before editing. Other agents and people may be changing
  the same checkout.
- Do not revert, overwrite, reformat, stage, or commit changes you did not make.
- Stay within the files assigned to your role. Ask the coordinating agent before
  crossing a role boundary or changing a shared contract.
- Prefer the standard library and existing dependencies. Do not add dependencies,
  external services, or network calls without explicit approval.
- Keep secrets and runtime data out of logs and failure messages.

## Specialized Agents

- `database`: SQLite schema, migrations, transactions, persistence invariants,
  and database-focused tests.
- `backend`: shared PWA/Mini App HTTP handlers, authentication boundaries,
  request parsing, and bot-to-web integration.
- `frontend`: shared PWA/Mini App HTML, CSS, JavaScript, responsive behavior,
  installability, and accessibility.
- `qa`: read-only review and verification across compile, unit, and isolated
  web smoke checks.

Use parallel agents mainly for independent read-heavy work. Coordinate shared
test files and contracts through the parent task before concurrent edits.

## Verification

Run the narrowest relevant check first, then the complete quality set before
handoff:

```bash
python3 scripts/check_python_compile.py
python3 scripts/run_unittests_isolated.py
python3 scripts/smoke_web.py
```

The unittest wrapper and smoke audit must remain self-contained, offline, and
isolated from the working database.

## Delivery

Report changed files, checks run, and any residual risk. Quality automation does
not deploy or publish changes. Never push, release, deploy, or otherwise publish
without a separate explicit user request.
