#!/usr/bin/env python3
"""Create a traceable test shipment from the Ozon TSD rehearsal stock.

No marketplace API is called. The script selects Ozon test putaway lines,
removes the requested quantity from their physical address cells and records
them in the immutable WMS movement journal as one shipment.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wms.connection import get_pg_connection
from wms.models import ProductKey
from wms import repository as repo


def _key_from_json(value: object) -> ProductKey:
    data = value if isinstance(value, dict) else json.loads(str(value))
    return ProductKey.from_dict(data)


def run(shipment_number: str, batch: str, *, lines: int, quantity: int, apply: bool) -> dict:
    conn = get_pg_connection()
    try:
        locations = {location.id: location for location in repo.list_locations(conn)}
        with conn.cursor() as cur:
            cur.execute(
                """SELECT product_key, to_location_id
                     FROM wms_movements
                    WHERE movement_type='test_putaway'
                      AND request_key LIKE %s
                    ORDER BY id""",
                (f"wms:ozon-test:{batch}:%:putaway",),
            )
            candidates = cur.fetchall()
        if len(candidates) < lines:
            raise RuntimeError(f"Для тестовой отгрузки найдено только {len(candidates)} позиций.")

        step = max(1, len(candidates) // lines)
        selected = [candidates[index] for index in range(0, len(candidates), step)][:lines]
        result = {
            "shipment_number": shipment_number,
            "lines": len(selected),
            "quantity_per_line": quantity,
            "total": len(selected) * quantity,
            "skipped_existing": 0,
        }
        reason = (
            f"ТЕСТОВАЯ ОТГРУЗКА {shipment_number}: {quantity} шт. × {len(selected)} поз. "
            "Списано из адресного хранения. На Ozon и Wildberries не отправлялось."
        )

        for number, row in enumerate(selected, start=1):
            request_key = f"wms:test-shipment:{shipment_number}:{number}"
            if repo.movement_exists(conn, request_key):
                result["skipped_existing"] += 1
                continue
            product_key = _key_from_json(row[0])
            location = locations.get(int(row[1]))
            if location is None:
                raise RuntimeError(f"Не найдена ячейка для строки отгрузки {number}.")
            stock = repo.find_stock(conn, product_key, location_id=location.id, for_update=True)
            available = 0 if stock is None else stock.quantity - stock.reserved_quantity
            if available < quantity:
                raise RuntimeError(f"Недостаточно товара для строки {number}: доступно {available} шт.")
            repo.upsert_stock(conn, product_key, delta=-quantity, location_id=location.id)
            repo.insert_movement(
                conn,
                request_key=request_key,
                movement_type="ship",
                product_key=product_key,
                quantity=quantity,
                from_location_id=location.id,
                from_state="SELLABLE",
                to_state="IN_TRANSIT",
                source_type="shipment",
                reason=reason,
                tsd_device_id="TSD-TEST-SHIPMENT",
            )

        if apply:
            conn.commit()
        else:
            conn.rollback()
        return result
    except Exception:
        conn.rollback()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shipment", required=True)
    parser.add_argument("--batch", required=True)
    parser.add_argument("--lines", type=int, default=10)
    parser.add_argument("--quantity", type=int, default=5)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.lines <= 0 or args.quantity <= 0:
        parser.error("lines and quantity must be positive")
    print(json.dumps(run(args.shipment, args.batch, lines=args.lines, quantity=args.quantity, apply=args.apply), ensure_ascii=False, sort_keys=True))
    if not args.apply:
        print("Dry run only. Re-run with --apply to write the shipment.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
