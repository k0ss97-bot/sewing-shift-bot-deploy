"""Persistent Ozon-first catalogue shared by marketplace, WMS and production.

The registry stores product identity only.  Synchronising a marketplace card
never creates physical stock.  Source priority is deliberately fixed:
Ozon > Wildberries > configured production route > retained WMS identity.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable

from wms.connection import get_pg_connection
from wms.models import ProductKey


SOURCE_PRIORITY = {"ozon": 400, "wildberries": 300, "production": 200, "wms": 100}


def _text(value: Any) -> str:
    return "" if value is None else " ".join(str(value).strip().split())


def _normal(value: Any) -> str:
    return _text(value).casefold().replace("ё", "е")


def _article_key(value: Any) -> str:
    return "".join(character for character in _normal(value) if character.isalnum())


def _barcode(value: Any) -> str:
    from wms.barcode import normalize_scanned_barcode

    return normalize_scanned_barcode(_text(value))


def _barcodes(row: dict[str, Any]) -> list[str]:
    values: list[Any] = [row.get("barcode")]
    for key in ("barcodes", "barcodes_json"):
        source = row.get(key)
        if isinstance(source, str):
            try:
                source = json.loads(source)
            except (TypeError, ValueError):
                source = []
        if isinstance(source, list):
            values.extend(source)
    result = []
    for value in values:
        normalized = _barcode(value)
        if normalized and normalized not in result:
            result.append(normalized)
    return result


def _variant(row: dict[str, Any]) -> tuple[str, str, str]:
    return (_normal(row.get("name")), _normal(row.get("size")), _normal(row.get("color")))


def _canonical_key(row: dict[str, Any]) -> str:
    article = _article_key(row.get("article"))
    if article:
        return f"article:{article}"
    barcodes = _barcodes(row)
    if barcodes:
        return f"barcode:{barcodes[0]}"
    raw = "\0".join(_variant(row))
    return "variant:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def merge_catalog_sources(sources: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge normalized source cards with deterministic Ozon-first priority."""

    ordered = sorted(
        (dict(source) for source in sources if isinstance(source, dict)),
        key=lambda row: (-SOURCE_PRIORITY.get(_normal(row.get("source_type")), 0), _text(row.get("source_external_id"))),
    )
    masters: list[dict[str, Any]] = []
    for source in ordered:
        source_type = _normal(source.get("source_type"))
        if source_type not in SOURCE_PRIORITY:
            continue
        source["source_type"] = source_type
        source["article"] = _text(source.get("article") or source.get("offer_id"))
        source["sku"] = _text(source.get("sku"))
        source["name"] = _text(source.get("name")) or source["article"] or source["sku"]
        source["size"] = _text(source.get("size"))
        source["color"] = _text(source.get("color"))
        source_barcodes = set(_barcodes(source))
        source_article = _article_key(source["article"])
        source_variant = _variant(source)

        match = None
        if source_article:
            match = next((row for row in masters if row["article_key"] == source_article), None)
        if match is None and source_barcodes:
            match = next((row for row in masters if source_barcodes.intersection(row["barcode_set"])), None)
        if match is None and all(source_variant):
            match = next((row for row in masters if row["variant_key"] == source_variant), None)
        source_canonical_key = _canonical_key(source)
        if match is None:
            match = next(
                (row for row in masters if row["canonical_key"] == source_canonical_key),
                None,
            )

        reference = {
            "source_type": source_type,
            "source_external_id": _text(source.get("source_external_id")) or _canonical_key(source),
            "article": source["article"],
            "sku": source["sku"],
            "barcode": sorted(source_barcodes)[0] if source_barcodes else "",
        }
        if match is None:
            production_name = _text(source.get("production_product_name")) or source["name"]
            production_size = _text(source.get("production_size")) or source["size"]
            production_color = _text(source.get("production_color")) or source["color"]
            match = {
                "canonical_key": source_canonical_key,
                "article": source["article"],
                "article_key": source_article,
                "sku": source["sku"],
                "barcode_set": set(source_barcodes),
                "name": source["name"],
                "size": source["size"],
                "color": source["color"],
                "variant_key": source_variant,
                "production_product_name": production_name,
                "production_size": production_size,
                "production_color": production_color,
                "route_configured": bool(source.get("route_configured")),
                "authoritative_source": source_type,
                "source_priority": SOURCE_PRIORITY[source_type],
                "is_active": bool(source.get("is_active", True)),
                "conflicts": [],
                "sources": [reference],
            }
            masters.append(match)
            continue

        match["barcode_set"].update(source_barcodes)
        match["sources"].append(reference)
        for field in ("article", "sku", "name", "size", "color"):
            source_value = source[field]
            if match[field] and source_value and _normal(match[field]) != _normal(source_value):
                match["conflicts"].append({
                    "source_type": source_type,
                    "field": field,
                    "authoritative_value": match[field],
                    "source_value": source_value,
                })
        # Lower-priority systems may only fill missing authoritative fields.
        for field in ("article", "sku", "name", "size", "color"):
            if not match[field] and source[field]:
                match[field] = source[field]
        for field in ("production_product_name", "production_size", "production_color"):
            if not match[field] and _text(source.get(field)):
                match[field] = _text(source.get(field))
        match["route_configured"] = bool(match["route_configured"] or source.get("route_configured"))
        match["is_active"] = bool(match["is_active"] or source.get("is_active", True))

    for master in masters:
        master["barcodes"] = sorted(master.pop("barcode_set"))
        marketplace_linked = any(
            source["source_type"] in {"ozon", "wildberries"} for source in master["sources"]
        )
        critical_complete = all((master["article"], master["name"], master["size"], master["color"], master["barcodes"]))
        authoritative_identity_conflicts = [
            conflict for conflict in master["conflicts"]
            if conflict["source_type"] == master["authoritative_source"]
            and conflict["field"] in {"size", "color"}
        ]
        master["validation_status"] = (
            "review_required" if authoritative_identity_conflicts
            else "incomplete" if marketplace_linked and not critical_complete
            else "canonicalized" if master["conflicts"]
            else "complete"
        )
        master.pop("article_key", None)
        master.pop("variant_key", None)
    masters.sort(key=lambda row: (row["name"].casefold(), row["size"], row["color"], row["article"]))
    return masters


def _marketplace_sources() -> list[dict[str, Any]]:
    """Read current Ozon (Postgres) and Wildberries (SQLite) cards."""

    from marketplace_phase1a import account_key
    from marketplace_pg import MarketplacePGRepository
    from marketplaces import _marketplace_payload_barcodes, production_target_for_marketplace_product
    from wildberries import dashboard as wildberries_dashboard

    sources: list[dict[str, Any]] = []
    ozon = MarketplacePGRepository().warehouse_catalog(account_key()).get("products") or []
    try:
        wildberries = wildberries_dashboard(read_only=True).get("products_rows") or []
    except Exception:
        wildberries = []
    for source_type, rows in (("ozon", ozon), ("wildberries", wildberries)):
        for row in rows:
            if not isinstance(row, dict):
                continue
            target = production_target_for_marketplace_product(row)
            payload_barcodes = []
            if source_type == "wildberries":
                payload_barcodes = sorted(_marketplace_payload_barcodes(row.get("payload_json") or "{}"))
            external_identity = "|".join(filter(None, (
                _text(row.get("external_product_id") or row.get("id") or row.get("nm_id")),
                _text(row.get("offer_id") or row.get("vendor_code") or row.get("article")),
                _text(row.get("sku")),
                _text(row.get("size") or row.get("tech_size")),
                _text(row.get("barcode")),
            )))
            sources.append({
                "source_type": source_type,
                "source_external_id": external_identity,
                "article": _text(row.get("offer_id") or row.get("vendor_code") or row.get("article") or row.get("sku")),
                "sku": _text(row.get("sku") or row.get("nm_id")),
                "barcode": _text(row.get("barcode")),
                "barcodes": list(row.get("barcodes_json") or row.get("barcodes") or []) + payload_barcodes,
                "name": _text(row.get("name") or row.get("title")),
                "size": _text(row.get("size") or row.get("tech_size")),
                "color": _text(row.get("color")),
                "production_product_name": target[0] if target else "",
                "production_size": target[1] if target else "",
                "production_color": target[2] if target else "",
                "route_configured": bool(target),
                "is_active": not bool(row.get("is_archived") or row.get("is_inactive")),
            })
    return sources


def _internal_sources(conn) -> list[dict[str, Any]]:
    from database import get_product_colors, get_product_sizes
    from route_maps import PRODUCT_ROUTE_MAPS

    sources: list[dict[str, Any]] = []
    for product_name in PRODUCT_ROUTE_MAPS:
        for size in get_product_sizes(product_name):
            for color in get_product_colors(product_name):
                external_id = f"{product_name}|{size}|{color}"
                sources.append({
                    "source_type": "production", "source_external_id": external_id,
                    "name": product_name, "size": size, "color": color,
                    "production_product_name": product_name, "production_size": size,
                    "production_color": color, "route_configured": True,
                })
    with conn.cursor() as cur:
        cur.execute(
            """SELECT DISTINCT item_type,product_name,product_size,product_color,
                              stage_name,ready_for_position
                 FROM warehouse_stock
                WHERE item_type IN ('finished','semifinished')"""
        )
        for row in cur.fetchall():
            external_id = "|".join(str(value) for value in row)
            sources.append({
                "source_type": "wms", "source_external_id": external_id,
                "name": str(row[1]), "size": str(row[2]), "color": str(row[3]),
                "production_product_name": str(row[1]), "production_size": str(row[2]),
                "production_color": str(row[3]), "route_configured": False,
                "product_key": ProductKey(*[str(value) for value in row]).to_dict(),
            })
    return sources


def sync_unified_product_catalog() -> dict[str, Any]:
    """Rebuild active source links and upsert the unified internal registry."""

    conn = get_pg_connection()
    try:
        sources = _marketplace_sources() + _internal_sources(conn)
        masters = merge_catalog_sources(sources)
        with conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", ("marketplace:unified-product-catalog",))
            cur.execute("UPDATE marketplace.product_master SET is_active=FALSE,updated_at=now()")
            cur.execute("DELETE FROM marketplace.product_master_sources")
            for master in masters:
                cur.execute(
                    """INSERT INTO marketplace.product_master
                              (canonical_key,article,sku,barcode,barcodes_json,name,size,color,
                               production_product_name,production_size,production_color,
                               route_configured,authoritative_source,source_priority,
                               validation_status,conflicts_json,is_active,updated_at)
                         VALUES (%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,now())
                         ON CONFLICT (canonical_key) DO UPDATE SET
                           article=excluded.article,sku=excluded.sku,barcode=excluded.barcode,
                           barcodes_json=excluded.barcodes_json,name=excluded.name,size=excluded.size,
                           color=excluded.color,production_product_name=excluded.production_product_name,
                           production_size=excluded.production_size,production_color=excluded.production_color,
                           route_configured=excluded.route_configured,
                           authoritative_source=excluded.authoritative_source,
                           source_priority=excluded.source_priority,
                           validation_status=excluded.validation_status,
                           conflicts_json=excluded.conflicts_json,
                           is_active=excluded.is_active,updated_at=now()
                      RETURNING id""",
                    (
                        master["canonical_key"], master["article"], master["sku"],
                        master["barcodes"][0] if master["barcodes"] else "",
                        json.dumps(master["barcodes"], ensure_ascii=False), master["name"],
                        master["size"], master["color"], master["production_product_name"],
                        master["production_size"], master["production_color"],
                        master["route_configured"], master["authoritative_source"],
                        master["source_priority"], master["validation_status"],
                        json.dumps(master["conflicts"], ensure_ascii=False), master["is_active"],
                    ),
                )
                master_id = int(cur.fetchone()[0])
                for source in master["sources"]:
                    cur.execute(
                        """INSERT INTO marketplace.product_master_sources
                                  (product_master_id,source_type,source_external_id,article,sku,barcode)
                             VALUES (%s,%s,%s,%s,%s,%s)""",
                        (
                            master_id, source["source_type"], source["source_external_id"],
                            source["article"], source["sku"], source["barcode"],
                        ),
                    )
                if master["production_product_name"] and master["production_size"] and master["production_color"]:
                    product_key = ProductKey(
                        "finished", master["production_product_name"], master["production_size"],
                        master["production_color"], "Упаковано", "Склад",
                    )
                    for barcode in master["barcodes"]:
                        cur.execute(
                            """INSERT INTO wms_barcodes
                                      (barcode,barcode_type,entity_type,entity_key,entity_id)
                                 VALUES (%s,'product','product_master',%s::jsonb,%s)
                                 ON CONFLICT (barcode) DO UPDATE SET
                                   barcode_type='product',entity_type='product_master',
                                   entity_key=excluded.entity_key,entity_id=excluded.entity_id""",
                            (barcode, json.dumps(product_key.to_dict(), ensure_ascii=False), master_id),
                        )
        conn.commit()
        ozon_only = sum(
            1 for master in masters
            if {source["source_type"] for source in master["sources"]} == {"ozon"}
        )
        return {
            "ok": True,
            "products": len(masters),
            "ozon_products": sum(1 for row in sources if row["source_type"] == "ozon"),
            "wildberries_products": sum(1 for row in sources if row["source_type"] == "wildberries"),
            "created_from_marketplaces": sum(
                1 for master in masters
                if any(source["source_type"] in {"ozon", "wildberries"} for source in master["sources"])
            ),
            "ozon_only": ozon_only,
            "review_required": sum(1 for master in masters if master["validation_status"] == "review_required"),
            "incomplete": sum(1 for master in masters if master["validation_status"] == "incomplete"),
            "canonicalized": sum(1 for master in masters if master["validation_status"] == "canonicalized"),
        }
    except Exception:
        conn.rollback()
        raise


def unified_catalog_summary() -> dict[str, Any]:
    conn = get_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT COUNT(*),
                          COUNT(*) FILTER (WHERE authoritative_source='ozon'),
                          COUNT(*) FILTER (WHERE authoritative_source='wildberries'),
                          COUNT(*) FILTER (WHERE route_configured),
                          COUNT(*) FILTER (WHERE barcode=''),
                          COUNT(*) FILTER (WHERE validation_status='review_required'),
                          COUNT(*) FILTER (WHERE validation_status='incomplete'),
                          COUNT(*) FILTER (WHERE validation_status='canonicalized')
                     FROM marketplace.product_master WHERE is_active=TRUE"""
            )
            row = cur.fetchone()
        conn.rollback()
        return {
            "ok": True, "products": int(row[0] or 0), "ozon_priority": int(row[1] or 0),
            "wildberries_priority": int(row[2] or 0), "route_configured": int(row[3] or 0),
            "without_barcode": int(row[4] or 0),
            "review_required": int(row[5] or 0), "incomplete": int(row[6] or 0),
            "canonicalized": int(row[7] or 0),
        }
    except Exception:
        conn.rollback()
        return {"ok": False, "products": 0}
