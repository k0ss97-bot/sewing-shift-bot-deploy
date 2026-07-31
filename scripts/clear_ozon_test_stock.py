#!/usr/bin/env python3
"""Remove only the explicitly named Ozon TSD rehearsal stock from WMS.

The script reverses the physical balance made by ``seed_ozon_test_stock.py``
and its optional test shipment.  It never contacts Ozon/Wildberries and does
not touch employees, production records, address cells or barcode registry.

Run a dry check first.  Use ``--apply`` only after a database backup exists::

    python scripts/clear_ozon_test_stock.py \
      --batch ozon-tsd-test-20260731 \
      --shipment TEST-SHP-20260731-001
    python scripts/clear_ozon_test_stock.py \
      --batch ozon-tsd-test-20260731 \
      --shipment TEST-SHP-20260731-001 --apply
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wms import repository as repo
from wms.connection import get_pg_connection
from wms.models import ProductKey


def _product_key(value: object) -> ProductKey:
    data = value if isinstance(value, dict) else json.loads(str(value))
    return ProductKey.from_dict(data)


def run(batch: str, shipment: str, *, apply: bool) -> dict:
    """Remove one named rehearsal batch without touching non-test stock."""
    if not batch.strip() or not shipment.strip():
        raise ValueError("Нужно указать batch и номер тестовой отгрузки.")

    conn = get_pg_connection()
    try:
        batch_prefix = f"wms:ozon-test:{batch}:%"
        shipment_prefix = f"wms:test-shipment:{shipment}:%"
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, request_key, movement_type, product_key, quantity,
                          from_location_id, to_location_id
                     FROM wms_movements
                    WHERE request_key LIKE %s OR request_key LIKE %s
                    ORDER BY id""",
                (batch_prefix, shipment_prefix),
            )
            movements = cur.fetchall()

        if not movements:
            return {"batch": batch, "shipment": shipment, "movements": 0, "removed_units": 0}

        balances: Counter[tuple[str, int]] = Counter()
        keys: dict[tuple[str, int], ProductKey] = {}
        for movement in movements:
            kind = str(movement["movement_type"])
            if kind not in {"test_receipt", "test_putaway", "ship"}:
                raise RuntimeError(f"Найдена неподдерживаемая тестовая операция: {kind}.")
            product = _product_key(movement["product_key"])
            encoded = json.dumps(product.to_dict(), ensure_ascii=False, sort_keys=True)
            quantity = int(movement["quantity"])
            from_location = movement["from_location_id"]
            to_location = movement["to_location_id"]
            if from_location is not None:
                key = (encoded, int(from_location))
                balances[key] -= quantity
                keys[key] = product
            if to_location is not None:
                key = (encoded, int(to_location))
                balances[key] += quantity
                keys[key] = product

        removals = [(key, qty) for key, qty in balances.items() if qty > 0]
        for (encoded, location_id), quantity in removals:
            stock = repo.find_stock(conn, keys[(encoded, location_id)], location_id=location_id, for_update=True)
            if stock is None or stock.quantity < quantity:
                raise RuntimeError(
                    f"В ячейке {location_id} недостаточно остатка для безопасной очистки теста."
                )
            if stock.reserved_quantity:
                raise RuntimeError(
                    f"В тестовом остатке ячейки {location_id} есть резерв; очистка остановлена."
                )

        result = {
            "batch": batch,
            "shipment": shipment,
            "movements": len(movements),
            "stock_rows": len(removals),
            "removed_units": sum(quantity for _, quantity in removals),
            "mode": "apply" if apply else "dry_run",
        }
        if not apply:
            conn.rollback()
            return result

        empty_stock_ids: list[int] = []
        for (encoded, location_id), quantity in removals:
            product = keys[(encoded, location_id)]
            stock_id = repo.upsert_stock(conn, product, delta=-quantity, location_id=location_id)
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT quantity, reserved_quantity FROM warehouse_stock WHERE id=%s FOR UPDATE",
                    (stock_id,),
                )
                row = cur.fetchone()
            if row and int(row["quantity"]) == 0 and int(row["reserved_quantity"]) == 0:
                empty_stock_ids.append(stock_id)

        with conn.cursor() as cur:
            if empty_stock_ids:
                cur.execute("DELETE FROM warehouse_stock WHERE id = ANY(%s)", (empty_stock_ids,))
            cur.execute(
                "DELETE FROM wms_movements WHERE request_key LIKE %s OR request_key LIKE %s",
                (batch_prefix, shipment_prefix),
            )
            result["deleted_movements"] = cur.rowcount
            result["deleted_empty_stock_rows"] = len(empty_stock_ids)
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", required=True, help="ID тестовой загрузки")
    parser.add_argument("--shipment", required=True, help="Номер тестовой отгрузки")
    parser.add_argument("--apply", action="store_true", help="Подтвердить удаление тестовых остатков")
    args = parser.parse_args()
    result = run(args.batch, args.shipment, apply=args.apply)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if not args.apply:
        print("Dry run only. Re-run with --apply after the backup to remove test stock.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
