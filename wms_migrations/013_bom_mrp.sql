-- Versioned bill of materials and read-only MRP planning snapshots.
-- Product identity remains article-first through marketplace.product_master.

-- Migration 012 introduced article-first identity for finished goods. MRP also
-- consumes materials and semi-finished components with supplier/production
-- articles, so their physical balance key must retain the article too.
DROP INDEX IF EXISTS warehouse_stock_legacy_location_unique;
CREATE UNIQUE INDEX IF NOT EXISTS warehouse_stock_nonfinished_identity_unique
    ON warehouse_stock (
        item_type, product_article, product_name, product_size, product_color,
        stage_name, ready_for_position, unit, item_state, location_id
    ) NULLS NOT DISTINCT
    WHERE item_type <> 'finished' OR product_article = '';

CREATE TABLE IF NOT EXISTS marketplace.product_bom_versions (
    id BIGSERIAL PRIMARY KEY,
    product_master_id BIGINT NOT NULL REFERENCES marketplace.product_master(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'retired')),
    effective_from DATE,
    effective_to DATE,
    note TEXT NOT NULL DEFAULT '',
    created_by_employee_id INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (product_master_id, version),
    CHECK (effective_to IS NULL OR effective_from IS NULL OR effective_to >= effective_from)
);

CREATE UNIQUE INDEX IF NOT EXISTS product_bom_one_active_version
    ON marketplace.product_bom_versions (product_master_id)
    WHERE status = 'active';

CREATE TABLE IF NOT EXISTS marketplace.product_bom_lines (
    id BIGSERIAL PRIMARY KEY,
    bom_version_id BIGINT NOT NULL REFERENCES marketplace.product_bom_versions(id) ON DELETE CASCADE,
    component_type TEXT NOT NULL CHECK (component_type IN ('material', 'semifinished')),
    component_article TEXT NOT NULL DEFAULT '',
    component_name TEXT NOT NULL,
    component_size TEXT NOT NULL DEFAULT '',
    component_color TEXT NOT NULL DEFAULT '',
    unit TEXT NOT NULL,
    quantity_per NUMERIC(18, 6) NOT NULL CHECK (quantity_per > 0),
    scrap_percent NUMERIC(7, 4) NOT NULL DEFAULT 0 CHECK (scrap_percent >= 0 AND scrap_percent <= 100),
    operation_code TEXT NOT NULL DEFAULT '',
    sort_order INTEGER NOT NULL DEFAULT 0,
    UNIQUE (
        bom_version_id, component_type, component_article, component_name,
        component_size, component_color, unit, operation_code
    )
);

CREATE INDEX IF NOT EXISTS product_bom_lines_version
    ON marketplace.product_bom_lines (bom_version_id, sort_order, id);
CREATE INDEX IF NOT EXISTS product_bom_lines_article
    ON marketplace.product_bom_lines (lower(component_article))
    WHERE component_article <> '';

CREATE TABLE IF NOT EXISTS marketplace.mrp_runs (
    id BIGSERIAL PRIMARY KEY,
    request_key TEXT NOT NULL UNIQUE,
    source_type TEXT NOT NULL DEFAULT 'manual',
    source_reference TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL CHECK (status IN ('ready', 'shortage', 'incomplete')),
    demand_count INTEGER NOT NULL CHECK (demand_count >= 0),
    component_count INTEGER NOT NULL CHECK (component_count >= 0),
    shortage_count INTEGER NOT NULL CHECK (shortage_count >= 0),
    missing_bom_product_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_by_employee_id INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS marketplace.mrp_run_lines (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES marketplace.mrp_runs(id) ON DELETE CASCADE,
    component_key JSONB NOT NULL,
    component_type TEXT NOT NULL,
    component_article TEXT NOT NULL DEFAULT '',
    component_name TEXT NOT NULL,
    component_size TEXT NOT NULL DEFAULT '',
    component_color TEXT NOT NULL DEFAULT '',
    unit TEXT NOT NULL,
    required_quantity NUMERIC(18, 6) NOT NULL CHECK (required_quantity >= 0),
    available_quantity NUMERIC(18, 6) NOT NULL CHECK (available_quantity >= 0),
    shortage_quantity NUMERIC(18, 6) NOT NULL CHECK (shortage_quantity >= 0),
    UNIQUE (run_id, component_key)
);

CREATE INDEX IF NOT EXISTS mrp_runs_created ON marketplace.mrp_runs (created_at DESC);
CREATE INDEX IF NOT EXISTS mrp_run_lines_shortage
    ON marketplace.mrp_run_lines (run_id, shortage_quantity DESC);

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'wms') THEN
        GRANT USAGE ON SCHEMA marketplace TO wms;
        GRANT SELECT, INSERT, UPDATE, DELETE ON marketplace.product_bom_versions TO wms;
        GRANT SELECT, INSERT, UPDATE, DELETE ON marketplace.product_bom_lines TO wms;
        GRANT SELECT, INSERT ON marketplace.mrp_runs TO wms;
        GRANT SELECT, INSERT ON marketplace.mrp_run_lines TO wms;
        GRANT USAGE, SELECT ON SEQUENCE marketplace.product_bom_versions_id_seq TO wms;
        GRANT USAGE, SELECT ON SEQUENCE marketplace.product_bom_lines_id_seq TO wms;
        GRANT USAGE, SELECT ON SEQUENCE marketplace.mrp_runs_id_seq TO wms;
        GRANT USAGE, SELECT ON SEQUENCE marketplace.mrp_run_lines_id_seq TO wms;
    END IF;
END
$$;
