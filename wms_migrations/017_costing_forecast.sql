-- Versioned product costing and explicitly labelled forecast snapshots.

CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.product_cost_versions (
    id BIGSERIAL PRIMARY KEY,
    product_master_id BIGINT NOT NULL REFERENCES marketplace.product_master(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'retired')),
    effective_from DATE,
    effective_to DATE,
    currency CHAR(3) NOT NULL DEFAULT 'RUB',
    note TEXT NOT NULL DEFAULT '',
    created_by_employee_id INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (product_master_id, version),
    CHECK (effective_to IS NULL OR effective_from IS NULL OR effective_to >= effective_from)
);

CREATE UNIQUE INDEX IF NOT EXISTS product_cost_one_active_version
    ON analytics.product_cost_versions (product_master_id)
    WHERE status = 'active';

CREATE TABLE IF NOT EXISTS analytics.product_cost_components (
    id BIGSERIAL PRIMARY KEY,
    cost_version_id BIGINT NOT NULL REFERENCES analytics.product_cost_versions(id) ON DELETE CASCADE,
    component_type TEXT NOT NULL CHECK (component_type IN ('material', 'labor', 'overhead', 'packaging', 'other')),
    component_code TEXT NOT NULL,
    component_name TEXT NOT NULL,
    amount_per_unit NUMERIC(18, 6) NOT NULL CHECK (amount_per_unit >= 0),
    source_reference TEXT NOT NULL DEFAULT '',
    sort_order INTEGER NOT NULL DEFAULT 0,
    UNIQUE (cost_version_id, component_type, component_code)
);

CREATE TABLE IF NOT EXISTS analytics.forecast_runs (
    id BIGSERIAL PRIMARY KEY,
    request_key TEXT NOT NULL UNIQUE,
    method TEXT NOT NULL,
    history_start DATE NOT NULL,
    history_end DATE NOT NULL,
    horizon_days INTEGER NOT NULL CHECK (horizon_days > 0 AND horizon_days <= 366),
    status TEXT NOT NULL CHECK (status IN ('ready', 'partial', 'unavailable')),
    warnings_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (history_end >= history_start)
);

CREATE TABLE IF NOT EXISTS analytics.forecast_lines (
    run_id BIGINT NOT NULL REFERENCES analytics.forecast_runs(id) ON DELETE CASCADE,
    product_article TEXT NOT NULL,
    forecast_date DATE NOT NULL,
    forecast_units NUMERIC(18, 6) NOT NULL CHECK (forecast_units >= 0),
    lower_bound_units NUMERIC(18, 6),
    upper_bound_units NUMERIC(18, 6),
    PRIMARY KEY (run_id, product_article, forecast_date)
);

CREATE INDEX IF NOT EXISTS forecast_lines_article_date
    ON analytics.forecast_lines (product_article, forecast_date);

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'wms') THEN
        GRANT USAGE ON SCHEMA analytics TO wms;
        GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA analytics TO wms;
        GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA analytics TO wms;
    END IF;
END
$$;
