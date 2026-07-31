#!/usr/bin/env python3
"""Place a test quantity of every Ozon variant into addressed WMS storage.

The import is deliberately explicit and idempotent: it is intended for a
controlled TSD rehearsal, not for regular Ozon synchronisation.  Every item
gets a receipt and a putaway journal event, both tagged with the supplied
batch id.  Marketplace barcodes are registered in the WMS barcode registry.

Usage (with the production environment variables loaded)::

    python scripts/seed_ozon_test_stock.py --batch ozon-tsd-test-20260731 --apply
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

# Running ``python scripts/...`` makes Python place ``scripts`` rather than the
# repository root on sys.path.  Keep this operational script directly usable
# from a release directory.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from marketplaces import warehouse_catalog
from wms.connection import get_pg_connection
from wms.models import ProductKey
from wms import repository as repo


TEST_DEVICE = "TSD-TEST-OZON"


def _text(value: object, fallback: str = "—") -> str:
    value = str(value or "").strip()
    return value or fallback


def _product_key(item: dict) -> ProductKey:
    """Keep production-linked goods on the canonical production key.

    Unlinked cards are still put away and scannable.  Their offer id becomes
    part of the warehouse name so two marketplace variants cannot merge by
    accident before their production route has been configured.
    """
    if item.get("production_status") == "linked":
        return ProductKey(
            item_type="finished",
            product_name=_text(item.get("production_product_name")),
            product_size=_text(item.get("production_size")),
            product_color=_text(item.get("production_color")),
            stage_name="Упаковано",
            ready_for_position="Склад",
        )
    article = _text(item.get("offer_id") or item.get("sku"), "без артикула")
    return ProductKey(
        item_type="finished",
        product_name=f"Ozon · {_text(item.get('name'), 'Товар')} · {article}",
        product_size=_text(item.get("size")),
        product_color=_text(item.get("color")),
        stage_name="Упаковано",
        ready_for_position="Склад",
    )


def _register_barcode(conn, barcode: str, product_key: ProductKey) -> None:
    barcode = barcode.strip()
    if not barcode:
        return
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO wms_barcodes (barcode, barcode_type, entity_type, entity_key)
               VALUES (%s, 'product', 'warehouse_stock', %s)
               ON CONFLICT (barcode) DO UPDATE SET entity_key = EXCLUDED.entity_key""",
            (barcode, json.dumps(product_key.to_dict())),
        )


def _exists(conn, request_key: str) -> bool:
    return repo.movement_exists(conn, request_key)


def run(batch: str, quantity: int, *, apply: bool) -> dict:
    catalog = warehouse_catalog()
    products = catalog["products"]
    conn = get_pg_connection()
    try:
        locations = [
            loc for loc in repo.list_locations(conn)
            if loc.status == "active" and loc.code.startswith("Z")
        ]
        if not locations:
            raise RuntimeError("Нет активных адресных ячеек Z1–Z4.")
        receive = repo.get_location_by_code(conn, "RECEIVE-01")
        if receive is None:
            raise RuntimeError("Системная ячейка приёмки RECEIVE-01 не найдена.")

        result = Counter()
        result["variants"] = len(products)
        result["quantity_per_variant"] = quantity
        result["planned_units"] = len(products) * quantity
        result["linked_to_production"] = sum(
            item.get("production_status") == "linked" for item in products
        )
        result["without_production_route"] = len(products) - result["linked_to_production"]
        result["address_cells"] = len(locations)

        for index, item in enumerate(products):
            item_id = int(item["id"])
            receipt_key = f"wms:ozon-test:{batch}:{item_id}:receipt"
            putaway_key = f"wms:ozon-test:{batch}:{item_id}:putaway"
            if _exists(conn, putaway_key):
                result["skipped_existing"] += 1
                continue
            product_key = _product_key(item)
            target = locations[index % len(locations)]
            reason = (
                f"ТЕСТ ТСД Ozon: {quantity} шт. на вариант; batch={batch}. "
                "Тестовая приёмка и адресное размещение."
            )
            # Receipt to the staging cell, then the same quantity is physically
            # placed into the address cell.  It mirrors the normal scanner flow.
            repo.upsert_stock(conn, product_key, delta=quantity, location_id=receive.id)
            repo.insert_movement(
                conn,
                request_key=receipt_key,
                movement_type="test_receipt",
                product_key=product_key,
                quantity=quantity,
                to_location_id=receive.id,
                to_state="SELLABLE",
                source_type="marketplace",
                reason=reason,
                tsd_device_id=TEST_DEVICE,
            )
            repo.upsert_stock(conn, product_key, delta=-quantity, location_id=receive.id)
            repo.upsert_stock(conn, product_key, delta=quantity, location_id=target.id)
            repo.insert_movement(
                conn,
                request_key=putaway_key,
                movement_type="test_putaway",
                product_key=product_key,
                quantity=quantity,
                from_location_id=receive.id,
                to_location_id=target.id,
                from_state="SELLABLE",
                to_state="SELLABLE",
                source_type="marketplace",
                reason=reason,
                tsd_device_id=TEST_DEVICE,
            )
            _register_barcode(conn, _text(item.get("barcode"), ""), product_key)
            result["placed_variants"] += 1
            result["registered_barcodes"] += int(bool(str(item.get("barcode") or "").strip()))

        if apply:
            conn.commit()
        else:
            conn.rollback()
        return dict(result)
    except Exception:
        conn.rollback()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", required=True, help="Stable id for this test run")
    parser.add_argument("--quantity", type=int, default=10, help="Units per Ozon variant")
    parser.add_argument("--apply", action="store_true", help="Commit test movements")
    args = parser.parse_args()
    if args.quantity <= 0:
        parser.error("quantity must be positive")
    result = run(args.batch, args.quantity, apply=args.apply)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if not args.apply:
        print("Dry run only. Re-run with --apply to write movements.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
