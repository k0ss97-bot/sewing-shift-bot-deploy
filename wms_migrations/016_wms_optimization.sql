-- Auditable WMS optimization plans. Plans never mutate stock implicitly.

CREATE TABLE IF NOT EXISTS wms_replenishment_tasks (
    id BIGSERIAL PRIMARY KEY,
    request_key TEXT NOT NULL UNIQUE,
    product_key JSONB NOT NULL,
    from_location_id INTEGER NOT NULL REFERENCES wms_locations(id) ON DELETE RESTRICT,
    to_location_id INTEGER NOT NULL REFERENCES wms_locations(id) ON DELETE RESTRICT,
    recommended_quantity INTEGER NOT NULL CHECK (recommended_quantity > 0),
    status TEXT NOT NULL DEFAULT 'planned' CHECK (status IN ('planned', 'released', 'in_work', 'completed', 'cancelled')),
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    CHECK (from_location_id <> to_location_id)
);

CREATE INDEX IF NOT EXISTS replenishment_tasks_status
    ON wms_replenishment_tasks (status, created_at);

CREATE TABLE IF NOT EXISTS wms_cycle_count_plans (
    id BIGSERIAL PRIMARY KEY,
    request_key TEXT NOT NULL UNIQUE,
    plan_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'planned' CHECK (status IN ('planned', 'released', 'completed', 'cancelled')),
    location_count INTEGER NOT NULL CHECK (location_count >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS wms_cycle_count_plan_locations (
    plan_id BIGINT NOT NULL REFERENCES wms_cycle_count_plans(id) ON DELETE CASCADE,
    location_id INTEGER NOT NULL REFERENCES wms_locations(id) ON DELETE RESTRICT,
    priority_score NUMERIC(18, 6) NOT NULL,
    reason TEXT NOT NULL,
    sequence_no INTEGER NOT NULL,
    PRIMARY KEY (plan_id, location_id),
    UNIQUE (plan_id, sequence_no)
);

CREATE TABLE IF NOT EXISTS wms_picking_waves (
    id BIGSERIAL PRIMARY KEY,
    wave_key TEXT NOT NULL UNIQUE,
    marketplace TEXT NOT NULL,
    destination TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'planned' CHECK (status IN ('planned', 'released', 'picking', 'completed', 'cancelled')),
    shipment_count INTEGER NOT NULL CHECK (shipment_count > 0),
    total_quantity INTEGER NOT NULL CHECK (total_quantity > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    released_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS wms_picking_wave_shipments (
    wave_id BIGINT NOT NULL REFERENCES wms_picking_waves(id) ON DELETE CASCADE,
    -- The operational shipment document still lives in the legacy SQLite
    -- application database during the phased migration. Keep its immutable
    -- external id without an invalid cross-database foreign key.
    shipment_task_id BIGINT NOT NULL,
    sequence_no INTEGER NOT NULL,
    PRIMARY KEY (wave_id, shipment_task_id),
    UNIQUE (wave_id, sequence_no)
);

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'wms') THEN
        GRANT SELECT, INSERT, UPDATE ON wms_replenishment_tasks TO wms;
        GRANT SELECT, INSERT, UPDATE ON wms_cycle_count_plans TO wms;
        GRANT SELECT, INSERT ON wms_cycle_count_plan_locations TO wms;
        GRANT SELECT, INSERT, UPDATE ON wms_picking_waves TO wms;
        GRANT SELECT, INSERT ON wms_picking_wave_shipments TO wms;
        GRANT USAGE, SELECT ON SEQUENCE wms_replenishment_tasks_id_seq TO wms;
        GRANT USAGE, SELECT ON SEQUENCE wms_cycle_count_plans_id_seq TO wms;
        GRANT USAGE, SELECT ON SEQUENCE wms_picking_waves_id_seq TO wms;
    END IF;
END
$$;
