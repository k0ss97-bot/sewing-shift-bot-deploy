-- WMS core schema (Этапы 0-2).
-- Applies to PostgreSQL. Idempotent (CREATE TABLE IF NOT EXISTS).
--
-- This is the WMS layer for the sewing factory. It coexists with the legacy
-- SQLite database: warehouse_stock is mirrored here as the WMS master, while
-- employees/shifts/fabric remain in SQLite (referenced by integer id without FK).
--
-- All write operations go through wms_movements with a UNIQUE request_key for
-- idempotency, mirroring production_trace_events.request_key in the legacy DB.

-- ──────────────────────────────────────────────────────────────────────
-- Schema-migrations bookkeeping
-- ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL UNIQUE,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ──────────────────────────────────────────────────────────────────────
-- Warehouse topology: zones → locations (cells/bins)
-- ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wms_zones (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,              -- 'RECEIVE', 'STORAGE', 'PICK', ...
    name_ru TEXT NOT NULL,                  -- 'Приёмка', 'Основное хранение'
    zone_type TEXT NOT NULL,                -- receive/storage/pick/pack/ship/returns/quarantine/damage/production/transit
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS wms_locations (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER NOT NULL REFERENCES wms_zones(id),
    code TEXT NOT NULL UNIQUE,              -- 'A-03-02'
    barcode TEXT NOT NULL UNIQUE,           -- 'LOC:A-03-02'
    name_ru TEXT,
    allowed_item_types TEXT[],              -- NULL = any type allowed
    max_weight_kg NUMERIC,
    max_volume_m3 NUMERIC,
    pick_priority INTEGER NOT NULL DEFAULT 0,
    route_order INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active',  -- active/blocked/inventory
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_locations_zone ON wms_locations(zone_id);
CREATE INDEX IF NOT EXISTS idx_locations_status ON wms_locations(status);

-- ──────────────────────────────────────────────────────────────────────
-- Item states (enum-like reference table)
-- ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wms_item_states (
    state TEXT PRIMARY KEY,                 -- SELLABLE/RESERVED/PICKED/PACKED/IN_TRANSIT/RETURN_INSPECTION/QUARANTINE/DAMAGED/SCRAPPED
    name_ru TEXT NOT NULL,
    is_sellable BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order INTEGER NOT NULL DEFAULT 0
);

-- ──────────────────────────────────────────────────────────────────────
-- Barcode registry (one product variant may have multiple barcodes)
-- ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wms_barcodes (
    id SERIAL PRIMARY KEY,
    barcode TEXT NOT NULL UNIQUE,
    barcode_type TEXT NOT NULL,             -- product/location/container/lot
    entity_type TEXT NOT NULL,              -- 'warehouse_stock' / 'location' / 'container'
    entity_key JSONB,                       -- {item_type,product_name,size,color,stage}
    entity_id INTEGER,                      -- location.id / container.id
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_barcodes_entity ON wms_barcodes(entity_type, entity_id);

-- ──────────────────────────────────────────────────────────────────────
-- Containers (boxes, pallets, carts) for grouped moves
-- ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wms_containers (
    id SERIAL PRIMARY KEY,
    lpn TEXT NOT NULL UNIQUE,               -- 'LPN:000012589'
    container_type TEXT NOT NULL,           -- box/pallet/cart
    status TEXT NOT NULL DEFAULT 'open',    -- open/sealed/closed
    current_location_id INTEGER REFERENCES wms_locations(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ──────────────────────────────────────────────────────────────────────
-- warehouse_stock — Postgres master for WMS (mirrored from SQLite)
-- ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS warehouse_stock (
    id SERIAL PRIMARY KEY,
    legacy_sqlite_id INTEGER,               -- back-ref to SQLite warehouse_stock.id
    item_type TEXT NOT NULL,                -- 'semifinished' / 'finished'
    product_name TEXT NOT NULL,
    product_size TEXT NOT NULL,
    product_color TEXT NOT NULL,
    stage_name TEXT NOT NULL,
    ready_for_position TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    item_state TEXT NOT NULL DEFAULT 'SELLABLE' REFERENCES wms_item_states(state),
    location_id INTEGER REFERENCES wms_locations(id),
    unit TEXT NOT NULL DEFAULT 'шт',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(item_type, product_name, product_size, product_color, stage_name, ready_for_position, unit, item_state)
);
CREATE INDEX IF NOT EXISTS idx_whstock_product ON warehouse_stock(item_type, product_name, product_size, product_color);
CREATE INDEX IF NOT EXISTS idx_whstock_location ON warehouse_stock(location_id);
CREATE INDEX IF NOT EXISTS idx_whstock_legacy ON warehouse_stock(legacy_sqlite_id);

-- ──────────────────────────────────────────────────────────────────────
-- Movement journal — immutable, idempotent
-- ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wms_movements (
    id BIGSERIAL PRIMARY KEY,
    request_key TEXT NOT NULL UNIQUE,       -- idempotency (INSERT ON CONFLICT DO NOTHING)
    movement_type TEXT NOT NULL,            -- receipt/putaway/transfer/pick/pack/ship/adjust/count/production_receipt/return/scrap
    product_key JSONB NOT NULL,             -- {item_type,product_name,size,color,stage,ready_for_position}
    quantity INTEGER NOT NULL,              -- signed: + for inbound, − for outbound
    from_location_id INTEGER REFERENCES wms_locations(id),
    to_location_id INTEGER REFERENCES wms_locations(id),
    from_state TEXT REFERENCES wms_item_states(state),
    to_state TEXT REFERENCES wms_item_states(state),
    source_type TEXT,                       -- 'production'/'order'/'inventory_count'/'manual'
    source_id INTEGER,
    reason TEXT,
    actor_employee_id INTEGER,              -- ref to SQLite employees.id (no FK cross-DB)
    tsd_device_id TEXT,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_movements_product ON wms_movements(product_key);
CREATE INDEX IF NOT EXISTS idx_movements_type_time ON wms_movements(movement_type, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_movements_source ON wms_movements(source_type, source_id);

-- ──────────────────────────────────────────────────────────────────────
-- Inventory counts (blind counting)
-- ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wms_inventory_counts (
    id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES wms_locations(id),
    status TEXT NOT NULL DEFAULT 'open',    -- open/counted/reconciled/closed
    counted_by_employee_id INTEGER,
    counted_at TIMESTAMPTZ,
    discrepancy_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS wms_inventory_count_lines (
    id SERIAL PRIMARY KEY,
    count_id INTEGER NOT NULL REFERENCES wms_inventory_counts(id),
    product_key JSONB NOT NULL,
    expected_quantity INTEGER NOT NULL DEFAULT 0,
    counted_quantity INTEGER,
    discrepancy INTEGER,                    -- counted − expected
    counted_by_employee_id INTEGER,
    counted_at TIMESTAMPTZ,
    UNIQUE(count_id, product_key)
);
