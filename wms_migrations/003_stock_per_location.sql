-- Upgrade an already-created WMS schema to location-aware stock balances.
-- PostgreSQL 15+ is required for UNIQUE NULLS NOT DISTINCT.

DO $$
DECLARE
    constraint_name TEXT;
BEGIN
    SELECT c.conname INTO constraint_name
      FROM pg_constraint c
     WHERE c.conrelid = 'warehouse_stock'::regclass
       AND c.contype = 'u'
       AND pg_get_constraintdef(c.oid) =
           'UNIQUE (item_type, product_name, product_size, product_color, stage_name, ready_for_position, unit, item_state)'
     LIMIT 1;

    IF constraint_name IS NOT NULL THEN
        EXECUTE format(
            'ALTER TABLE warehouse_stock DROP CONSTRAINT %I',
            constraint_name
        );
    END IF;
END $$;

ALTER TABLE warehouse_stock
    DROP CONSTRAINT IF EXISTS warehouse_stock_location_unique;

ALTER TABLE warehouse_stock
    ADD CONSTRAINT warehouse_stock_location_unique UNIQUE NULLS NOT DISTINCT (
        item_type, product_name, product_size, product_color, stage_name,
        ready_for_position, unit, item_state, location_id
    );

ALTER TABLE warehouse_stock
    DROP CONSTRAINT IF EXISTS warehouse_stock_quantity_nonnegative;
ALTER TABLE warehouse_stock
    ADD CONSTRAINT warehouse_stock_quantity_nonnegative CHECK (quantity >= 0);

ALTER TABLE warehouse_stock
    DROP CONSTRAINT IF EXISTS warehouse_stock_reserved_valid;
ALTER TABLE warehouse_stock
    ADD CONSTRAINT warehouse_stock_reserved_valid CHECK (
        reserved_quantity >= 0 AND reserved_quantity <= quantity
    );

CREATE UNIQUE INDEX IF NOT EXISTS idx_whstock_legacy_unique
    ON warehouse_stock(legacy_sqlite_id)
    WHERE legacy_sqlite_id IS NOT NULL;

ALTER TABLE wms_inventory_counts
    ADD COLUMN IF NOT EXISTS request_key TEXT;

UPDATE wms_inventory_counts
   SET request_key = 'legacy:inventory:' || id
 WHERE request_key IS NULL;

ALTER TABLE wms_inventory_counts
    ALTER COLUMN request_key SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_inventory_counts_request_key
    ON wms_inventory_counts(request_key);

INSERT INTO wms_locations (zone_id, code, barcode, name_ru, pick_priority, route_order)
SELECT id, 'RECEIVE-01', 'LOC:RECEIVE-01', 'Приёмка 1', 0, 0
  FROM wms_zones
 WHERE code = 'RECEIVE'
ON CONFLICT (code) DO NOTHING;
