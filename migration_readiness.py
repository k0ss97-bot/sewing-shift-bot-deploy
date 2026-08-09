"""Fail-closed cutover gates for operational SQLite-to-PostgreSQL migration."""

from __future__ import annotations

from typing import Iterable, Mapping


REQUIRED_GLOBAL_GATES = {
    "backup_restore_verified",
    "rollback_rehearsed",
    "write_idempotency_verified",
    "monitoring_ready",
    "operator_approval",
}


def evaluate_cutover_readiness(
    checkpoints: Iterable[Mapping],
    gates: Mapping[str, bool],
    *,
    maximum_replication_lag_seconds: float = 5.0,
) -> dict[str, object]:
    """Return a deterministic gate report; unknown/missing evidence blocks."""

    rows = list(checkpoints)
    blockers = []
    if not rows:
        blockers.append("Нет сверки таблиц")
    seen_tables = set()
    for row in rows:
        table_name = str(row.get("table_name") or "").strip()
        if not table_name:
            blockers.append("Сверка содержит таблицу без имени")
            continue
        if table_name in seen_tables:
            blockers.append(f"Дублируется сверка таблицы {table_name}")
            continue
        seen_tables.add(table_name)
        try:
            source_count = int(row.get("source_row_count"))
            target_count = int(row.get("target_row_count"))
            lag = float(row.get("replication_lag_seconds"))
        except (TypeError, ValueError):
            blockers.append(f"{table_name}: неполные числовые метрики")
            continue
        if source_count != target_count:
            blockers.append(f"{table_name}: не совпадает количество строк")
        if not str(row.get("source_checksum") or "") or row.get("source_checksum") != row.get("target_checksum"):
            blockers.append(f"{table_name}: не совпадает контрольная сумма")
        if lag < 0 or lag > maximum_replication_lag_seconds:
            blockers.append(f"{table_name}: задержка репликации {lag:g} сек.")
        if row.get("writes_quiesced") is not True:
            blockers.append(f"{table_name}: запись в источник не остановлена")

    missing_gates = sorted(name for name in REQUIRED_GLOBAL_GATES if gates.get(name) is not True)
    blockers.extend(f"Не пройден gate: {name}" for name in missing_gates)
    return {
        "ready": not blockers,
        "status": "ready" if not blockers else "blocked",
        "tables_checked": len(seen_tables),
        "required_gates": sorted(REQUIRED_GLOBAL_GATES),
        "blockers": blockers,
    }


def require_cutover_ready(report: Mapping) -> None:
    if report.get("ready") is not True:
        blockers = "; ".join(str(item) for item in report.get("blockers") or [])
        raise RuntimeError(f"Operational cutover is blocked: {blockers or 'no verified evidence'}")
