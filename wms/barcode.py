"""Barcode registry and prefix-based parsing.

WMS uses prefixed barcodes to avoid confusing a product barcode with a
location code on the ТСД:

- ``LOC:A-03-02``  — a storage location / cell.
- ``LPN:000012589`` — a logistics container (box / pallet / cart).
- anything else   — treated as a product barcode and resolved via the registry.

The registry maps a product barcode to a :class:`~wms.models.ProductKey` so the
ТСД can identify the goods from a single scan.
"""

from __future__ import annotations

import json
import re
from typing import Any

from .connection import get_pg_connection
from .models import ProductKey

LOCATION_PREFIX = "LOC:"
CONTAINER_PREFIX = "LPN:"
PHYSICAL_LOCATION_PATTERN = re.compile(r"^Z\d+-S\d+-P\d+-\d+$", re.IGNORECASE)
SCANNER_SYMBOLOGY_PREFIX = re.compile(r"^\][A-Za-z][0-9]")


def normalize_scanned_barcode(raw: str) -> str:
    """Remove harmless framing added by handheld scanners.

    CR/LF suffixes and three-character AIM symbology prefixes (for example
    ``]C1``) are not part of the product code. Significant digits, including
    leading zeroes, are preserved.
    """
    value = "".join(character for character in str(raw or "") if ord(character) >= 32).strip()
    if SCANNER_SYMBOLOGY_PREFIX.match(value):
        value = value[3:].strip()
    return value


def barcode_lookup_candidates(raw: str) -> tuple[str, ...]:
    """Return safe scanner candidates without changing registered labels.

    Some handhelds return EAN-13 as a zero-padded GTIN-14, while GS1-128 may
    prepend application identifier ``01`` to that GTIN. Exact values stay
    first; only these lossless numeric representations are added.
    """
    original = str(raw or "").strip()
    normalized = normalize_scanned_barcode(original)
    candidates = list(dict.fromkeys(value for value in (original, normalized) if value))
    for value in list(candidates):
        if value.isdigit() and value.startswith("01") and len(value) >= 16:
            candidates.append(value[2:16])
        if value.isdigit() and len(value) == 14 and value.startswith("0"):
            candidates.append(value[1:])
        if value.isdigit() and len(value) == 13:
            candidates.append(f"0{value}")
    for value in list(candidates):
        if value.isdigit() and len(value) == 14 and value.startswith("0"):
            candidates.append(value[1:])
    return tuple(dict.fromkeys(candidates))


def is_location_barcode(raw: str) -> bool:
    """Return whether *raw* is a supported warehouse-cell barcode.

    Existing physical labels from MoySklad contain the cell code itself
    (``Z1-S1-P1-1``) and must remain printable/scannable without a ``LOC:``
    prefix. Legacy prefixed labels stay supported for compatibility.
    """
    value = normalize_scanned_barcode(raw)
    return value.upper().startswith(LOCATION_PREFIX) or bool(
        PHYSICAL_LOCATION_PATTERN.fullmatch(value)
    )


def classify_barcode(raw: str) -> str:
    """Return the kind of a scanned barcode string."""
    s = normalize_scanned_barcode(raw)
    if is_location_barcode(s):
        return "location"
    if s.startswith(CONTAINER_PREFIX):
        return "container"
    return "product"


def location_code_from_barcode(raw: str) -> str:
    """Extract a normalized location code from a supported cell scan."""
    value = normalize_scanned_barcode(raw)
    if value.upper().startswith(LOCATION_PREFIX):
        return value[len(LOCATION_PREFIX) :].strip().upper()
    if PHYSICAL_LOCATION_PATTERN.fullmatch(value):
        return value.upper()
    raise ValueError("barcode is not a warehouse location")


def register_product_barcode(
    barcode: str, product_key: ProductKey
) -> None:
    """Link a product barcode to a product key (idempotent)."""
    if classify_barcode(barcode) != "product":
        raise ValueError("location/container barcode cannot be registered as a product")
    conn = get_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO wms_barcodes (barcode, barcode_type, entity_type, entity_key)
                   VALUES (%s, 'product', 'warehouse_stock', %s)
                   ON CONFLICT (barcode) DO UPDATE SET entity_key = EXCLUDED.entity_key""",
                (normalize_scanned_barcode(barcode), json.dumps(product_key.to_dict())),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def resolve_product_barcode(barcode: str) -> ProductKey | None:
    """Return the ProductKey linked to a product barcode, or None."""
    conn = get_pg_connection()
    with conn.cursor() as cur:
        candidates = barcode_lookup_candidates(barcode)
        if not candidates:
            return None
        cur.execute(
            "SELECT entity_key FROM wms_barcodes WHERE barcode = ANY(%s) AND barcode_type = 'product' LIMIT 1",
            (list(candidates),),
        )
        row = cur.fetchone()
    if row is None or not row[0]:
        return None
    return ProductKey.from_dict(row[0])


def register_location_barcode(barcode: str, location_id: int) -> None:
    conn = get_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO wms_barcodes (barcode, barcode_type, entity_type, entity_id)
                   VALUES (%s, 'location', 'location', %s)
                   ON CONFLICT (barcode) DO UPDATE SET entity_id = EXCLUDED.entity_id""",
                (barcode.strip(), location_id),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
