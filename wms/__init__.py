"""WMS (warehouse management) module for the sewing factory.

A Postgres-backed warehouse layer that coexists with the legacy SQLite
database. Provides zones, locations, barcodes, item states, an immutable
movement journal with idempotency, and the core warehouse operations
(receipt, putaway, transfer, pick, inventory count, scrap).

See ``WMS_DESIGN.md`` for the full schema and integration plan.
"""

from __future__ import annotations

__version__ = "0.1.0"
