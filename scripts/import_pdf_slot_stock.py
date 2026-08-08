#!/usr/bin/env python3
"""Reclassify one posted PDF stock receipt by article and put it into cells.

The command is dry-run by default.  It accepts only a prepared JSON manifest,
verifies its declared totals and the posted receipt, then uses exact seller
articles from ``marketplace.product_master``.  Re-runs are safe because every
reclassification and putaway movement has a deterministic request key.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from wms.connection import get_pg_connection
from wms.models import ProductKey, normalize_product_article
from wms import operations, repository


IMPORT_KEY = "pdf-slots-20260807-160016"


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def _legacy_identity(product_key: ProductKey) -> tuple[str, ...]:
    return (
        product_key.item_type,
        product_key.product_name,
        product_key.product_size,
        product_key.product_color,
        product_key.stage_name,
        product_key.ready_for_position,
    )


def _load_manifest(path: Path) -> tuple[list[dict[str, Any]], int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows")
    summary = payload.get("summary") or {}
    if not isinstance(rows, list) or not rows:
        raise ValueError("Manifest has no cell rows.")
    normalized = []
    for index, row in enumerate(rows, start=1):
        article = normalize_product_article(row.get("article"))
        location = str(row.get("location_code") or "").strip().upper()
        quantity = int(row.get("quantity") or 0)
        if not article or not location or quantity <= 0:
            raise ValueError(f"Invalid manifest row {index}.")
        normalized.append({"article": article, "location": location, "quantity": quantity})
    declared_rows = int(summary.get("rows") or 0)
    declared_articles = int(summary.get("unique_articles") or 0)
    declared_locations = int(summary.get("unique_locations") or 0)
    declared_total = int(summary.get("total_quantity") or 0)
    if (
        len(normalized) != declared_rows
        or len({row["article"] for row in normalized}) != declared_articles
        or len({row["location"] for row in normalized}) != declared_locations
        or sum(row["quantity"] for row in normalized) != declared_total
    ):
        raise ValueError("Manifest summary does not match its cell rows.")
    return normalized, declared_total


def _product_keys(conn, articles: set[str]) -> dict[str, ProductKey]:
    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT article,production_product_name,production_size,production_color,
                      authoritative_source,source_priority
                 FROM marketplace.product_master
                WHERE is_active=TRUE AND article<>''
                  AND production_product_name<>'' AND production_size<>'' AND production_color<>''
             ORDER BY source_priority DESC,id"""
        )
        rows = cursor.fetchall()
    candidates: dict[str, list[tuple[Any, ...]]] = defaultdict(list)
    for row in rows:
        article = normalize_product_article(row[0])
        if article in articles:
            candidates[article].append(tuple(row))
    resolved = {}
    for article in sorted(articles):
        options = candidates.get(article) or []
        if not options:
            raise ValueError(f"Article is absent from the unified catalogue: {article}")
        highest_priority = int(options[0][5] or 0)
        highest = [row for row in options if int(row[5] or 0) == highest_priority]
        identities = {(str(row[1]), str(row[2]), str(row[3])) for row in highest}
        if len(identities) != 1:
            raise ValueError(f"Article has conflicting production identities: {article}")
        name, size, color = identities.pop()
        resolved[article] = ProductKey(
            item_type="finished",
            product_article=article,
            product_name=name,
            product_size=size,
            product_color=color,
            stage_name="Упаковано",
            ready_for_position="Склад",
        )
    return resolved


def _reclassify_receive_stock(
    conn,
    *,
    products: dict[str, ProductKey],
    totals: dict[str, int],
    expected_total: int,
    receipt_request_key: str,
    apply: bool,
) -> str:
    receive = repository.get_location_by_code(conn, "RECEIVE-01")
    if receive is None:
        raise ValueError("RECEIVE-01 is missing.")
    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT id,status,total_quantity FROM wms_stock_receipts
                WHERE request_key=%s""",
            (receipt_request_key,),
        )
        receipt = cursor.fetchone()
        if receipt is None or str(receipt[1]) != "posted" or int(receipt[2]) != expected_total:
            raise ValueError("The source receipt is missing, not posted or has another total.")
        cursor.execute(
            """SELECT * FROM warehouse_stock
                WHERE item_type='finished' AND product_article='' AND quantity>0
                  AND location_id=%s AND item_state='SELLABLE' AND unit='шт'
                ORDER BY id FOR UPDATE""",
            (receive.id,),
        )
        old_rows = cursor.fetchall()
        cursor.execute(
            """SELECT COALESCE(SUM(quantity),0) FROM warehouse_stock
                WHERE item_type='finished' AND product_article<>''
                  AND item_state='SELLABLE' AND unit='шт'"""
        )
        article_total = int(cursor.fetchone()[0] or 0)

    old_total = sum(int(row["quantity"] or 0) for row in old_rows)
    if old_total == 0:
        if article_total != expected_total:
            raise ValueError("Reclassification is partial or unrelated finished stock exists.")
        conn.rollback()
        return "already_reclassified"
    if old_total != expected_total or article_total != 0:
        raise ValueError("Finished stock does not match the untouched source receipt.")
    if any(int(row["reserved_quantity"] or 0) for row in old_rows):
        raise ValueError("Source receipt contains reserved stock.")

    expected_by_legacy: dict[tuple[str, ...], int] = defaultdict(int)
    for article, quantity in totals.items():
        expected_by_legacy[_legacy_identity(products[article])] += quantity
    actual_by_legacy: dict[tuple[str, ...], int] = defaultdict(int)
    for row in old_rows:
        actual_by_legacy[
            (
                str(row["item_type"]), str(row["product_name"]), str(row["product_size"]),
                str(row["product_color"]), str(row["stage_name"]), str(row["ready_for_position"]),
            )
        ] += int(row["quantity"])
    if actual_by_legacy != expected_by_legacy:
        raise ValueError("Legacy RECEIVE identities do not match the article manifest.")
    if not apply:
        conn.rollback()
        return "ready"

    for row in old_rows:
        old_key = ProductKey(
            item_type=str(row["item_type"]), product_name=str(row["product_name"]),
            product_size=str(row["product_size"]), product_color=str(row["product_color"]),
            stage_name=str(row["stage_name"]), ready_for_position=str(row["ready_for_position"]),
        )
        quantity = int(row["quantity"])
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE warehouse_stock SET quantity=0,updated_at=now() WHERE id=%s AND quantity=%s",
                (int(row["id"]), quantity),
            )
            if cursor.rowcount != 1:
                raise ValueError("Source stock changed during reclassification.")
        repository.insert_movement(
            conn,
            request_key=f"{IMPORT_KEY}:reclass:out:{int(row['id'])}",
            movement_type="article_reclassification_out",
            product_key=old_key,
            quantity=quantity,
            from_location_id=receive.id,
            to_location_id=receive.id,
            from_state="SELLABLE",
            to_state="SELLABLE",
            source_type="stock_receipt",
            source_id=int(receipt[0]),
            reason="Разделение оприходования по артикулам перед адресным размещением",
        )
    for article, quantity in sorted(totals.items()):
        product_key = products[article]
        repository.upsert_stock(
            conn, product_key, delta=quantity, item_state="SELLABLE",
            location_id=receive.id, unit="шт",
        )
        repository.insert_movement(
            conn,
            request_key=f"{IMPORT_KEY}:reclass:in:{_digest(article)}",
            movement_type="article_reclassification_in",
            product_key=product_key,
            quantity=quantity,
            from_location_id=receive.id,
            to_location_id=receive.id,
            from_state="SELLABLE",
            to_state="SELLABLE",
            source_type="stock_receipt",
            source_id=int(receipt[0]),
            reason="Присвоение единого ключа изделия по артикулу",
        )
    conn.commit()
    return "reclassified"


def run(manifest_path: Path, *, receipt_request_key: str, apply: bool) -> dict[str, Any]:
    rows, expected_total = _load_manifest(manifest_path)
    totals: dict[str, int] = defaultdict(int)
    placements: dict[tuple[str, str], int] = defaultdict(int)
    for row in rows:
        totals[row["article"]] += row["quantity"]
        placements[(row["article"], row["location"])] += row["quantity"]

    conn = get_pg_connection()
    try:
        products = _product_keys(conn, set(totals))
        state = _reclassify_receive_stock(
            conn,
            products=products,
            totals=totals,
            expected_total=expected_total,
            receipt_request_key=receipt_request_key,
            apply=apply,
        )
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    placed = 0
    if apply:
        for (article, location), quantity in sorted(placements.items()):
            result = operations.putaway(
                products[article], quantity,
                to_location_code=location,
                request_key=f"{IMPORT_KEY}:putaway:{_digest(article + '|' + location)}",
                reason="Адресное размещение по PDF-отчёту остатков",
                tsd_device_id="pdf-slot-import",
            )
            if not result.ok:
                raise RuntimeError(f"Putaway failed for {article} / {location}: {result.reason}")
            placed += quantity

        verify = get_pg_connection()
        try:
            with verify.cursor() as cursor:
                cursor.execute(
                    """SELECT ws.product_article,l.code,SUM(ws.quantity)
                         FROM warehouse_stock ws
                         JOIN wms_locations l ON l.id=ws.location_id
                        WHERE ws.item_type='finished' AND ws.product_article<>''
                          AND ws.item_state='SELLABLE' AND ws.unit='шт' AND ws.quantity>0
                     GROUP BY ws.product_article,l.code"""
                )
                actual = {
                    (normalize_product_article(row[0]), str(row[1])): int(row[2])
                    for row in cursor.fetchall()
                }
            verify.rollback()
        finally:
            verify.close()
        if actual != dict(placements):
            raise RuntimeError("Post-import stock does not exactly match the manifest.")

    return {
        "mode": "apply" if apply else "dry-run",
        "state": state,
        "manifest_rows": len(rows),
        "placement_rows": len(placements),
        "articles": len(totals),
        "locations": len({location for _article, location in placements}),
        "quantity": expected_total,
        "placed": placed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--receipt-request-key", default="pdf-slots-20260807-160016")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(
        args.manifest,
        receipt_request_key=args.receipt_request_key,
        apply=args.apply,
    ), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
