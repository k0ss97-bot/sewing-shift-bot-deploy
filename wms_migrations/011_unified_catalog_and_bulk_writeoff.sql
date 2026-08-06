-- Audited full-warehouse write-off and the unified internal product catalogue.
--
-- Ozon is the authoritative source for conflicting product attributes.
-- Wildberries and internal production/WMS identities may only fill fields
-- missing from the Ozon card.  Neither table stores marketplace credentials.

CREATE TABLE IF NOT EXISTS wms_bulk_writeoffs (
    id BIGSERIAL PRIMARY KEY,
    request_key TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'posting',
    reason TEXT NOT NULL,
    actor_employee_id INTEGER,
    rows_count INTEGER NOT NULL DEFAULT 0,
    total_quantity BIGINT NOT NULL DEFAULT 0,
    released_reserved_quantity BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    posted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS wms_bulk_writeoff_lines (
    id BIGSERIAL PRIMARY KEY,
    writeoff_id BIGINT NOT NULL REFERENCES wms_bulk_writeoffs(id) ON DELETE RESTRICT,
    stock_id INTEGER NOT NULL REFERENCES warehouse_stock(id) ON DELETE RESTRICT,
    product_key JSONB NOT NULL,
    item_state TEXT NOT NULL,
    location_id INTEGER REFERENCES wms_locations(id),
    unit TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    released_reserved_quantity INTEGER NOT NULL DEFAULT 0,
    movement_id BIGINT NOT NULL REFERENCES wms_movements(id) ON DELETE RESTRICT,
    UNIQUE (writeoff_id, stock_id)
);

CREATE INDEX IF NOT EXISTS idx_wms_bulk_writeoffs_posted
    ON wms_bulk_writeoffs (posted_at DESC);

CREATE TABLE IF NOT EXISTS marketplace.product_master (
    id BIGSERIAL PRIMARY KEY,
    canonical_key TEXT NOT NULL UNIQUE,
    article TEXT NOT NULL DEFAULT '',
    sku TEXT NOT NULL DEFAULT '',
    barcode TEXT NOT NULL DEFAULT '',
    barcodes_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    name TEXT NOT NULL,
    size TEXT NOT NULL DEFAULT '',
    color TEXT NOT NULL DEFAULT '',
    production_product_name TEXT NOT NULL DEFAULT '',
    production_size TEXT NOT NULL DEFAULT '',
    production_color TEXT NOT NULL DEFAULT '',
    route_configured BOOLEAN NOT NULL DEFAULT FALSE,
    authoritative_source TEXT NOT NULL,
    source_priority INTEGER NOT NULL,
    validation_status TEXT NOT NULL DEFAULT 'complete',
    conflicts_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS marketplace.product_master_sources (
    product_master_id BIGINT NOT NULL REFERENCES marketplace.product_master(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL,
    source_external_id TEXT NOT NULL,
    article TEXT NOT NULL DEFAULT '',
    sku TEXT NOT NULL DEFAULT '',
    barcode TEXT NOT NULL DEFAULT '',
    observed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (source_type, source_external_id)
);

CREATE INDEX IF NOT EXISTS idx_product_master_article
    ON marketplace.product_master (lower(article)) WHERE article <> '';
CREATE INDEX IF NOT EXISTS idx_product_master_barcode
    ON marketplace.product_master (barcode) WHERE barcode <> '';
CREATE INDEX IF NOT EXISTS idx_product_master_variant
    ON marketplace.product_master (lower(name), lower(size), lower(color));
CREATE INDEX IF NOT EXISTS idx_product_master_sources_master
    ON marketplace.product_master_sources (product_master_id);

-- Production migrations are applied by the database owner while the web
-- process connects as the restricted ``wms`` role.
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'wms') THEN
        GRANT SELECT, INSERT, UPDATE ON wms_bulk_writeoffs TO wms;
        GRANT SELECT, INSERT ON wms_bulk_writeoff_lines TO wms;
        GRANT USAGE, SELECT ON SEQUENCE wms_bulk_writeoffs_id_seq TO wms;
        GRANT USAGE, SELECT ON SEQUENCE wms_bulk_writeoff_lines_id_seq TO wms;

        GRANT USAGE ON SCHEMA marketplace TO wms;
        GRANT SELECT, INSERT, UPDATE, DELETE ON marketplace.product_master TO wms;
        GRANT SELECT, INSERT, UPDATE, DELETE ON marketplace.product_master_sources TO wms;
        GRANT USAGE, SELECT ON SEQUENCE marketplace.product_master_id_seq TO wms;
    END IF;
END
$$;
