-- Quality management, rework/CAPA and downtime audit trail.

CREATE SCHEMA IF NOT EXISTS quality;

CREATE TABLE IF NOT EXISTS quality.nonconformances (
    id BIGSERIAL PRIMARY KEY,
    external_key TEXT NOT NULL UNIQUE,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL DEFAULT '',
    product_article TEXT NOT NULL DEFAULT '',
    product_name TEXT NOT NULL DEFAULT '',
    defect_code TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('minor', 'major', 'critical')),
    quantity NUMERIC(18, 6) NOT NULL CHECK (quantity > 0),
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'contained', 'rework', 'closed', 'scrapped')),
    detected_by_employee_id INTEGER,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    contained_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    note TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS nonconformances_open
    ON quality.nonconformances (status, severity, detected_at DESC);
CREATE INDEX IF NOT EXISTS nonconformances_article
    ON quality.nonconformances (lower(product_article), detected_at DESC)
    WHERE product_article <> '';

CREATE TABLE IF NOT EXISTS quality.rework_orders (
    id BIGSERIAL PRIMARY KEY,
    request_key TEXT NOT NULL UNIQUE,
    nonconformance_id BIGINT NOT NULL REFERENCES quality.nonconformances(id) ON DELETE RESTRICT,
    operation_code TEXT NOT NULL,
    quantity NUMERIC(18, 6) NOT NULL CHECK (quantity > 0),
    status TEXT NOT NULL DEFAULT 'planned' CHECK (status IN ('planned', 'in_work', 'verification', 'completed', 'failed', 'cancelled')),
    assigned_employee_id INTEGER,
    created_by_employee_id INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS quality.capa_actions (
    id BIGSERIAL PRIMARY KEY,
    external_key TEXT NOT NULL UNIQUE,
    nonconformance_id BIGINT REFERENCES quality.nonconformances(id) ON DELETE RESTRICT,
    action_type TEXT NOT NULL CHECK (action_type IN ('corrective', 'preventive')),
    title TEXT NOT NULL,
    root_cause TEXT NOT NULL DEFAULT '',
    owner_employee_id INTEGER,
    due_date DATE,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'in_progress', 'verification', 'effective', 'ineffective', 'cancelled')),
    effectiveness_result TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS capa_due ON quality.capa_actions (status, due_date);

CREATE TABLE IF NOT EXISTS quality.downtime_events (
    id BIGSERIAL PRIMARY KEY,
    external_key TEXT NOT NULL UNIQUE,
    work_center_code TEXT NOT NULL,
    reason_code TEXT NOT NULL,
    reason_text TEXT NOT NULL DEFAULT '',
    is_planned BOOLEAN NOT NULL DEFAULT FALSE,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    recorded_by_employee_id INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (ended_at IS NULL OR ended_at >= started_at)
);

CREATE INDEX IF NOT EXISTS downtime_work_center_time
    ON quality.downtime_events (work_center_code, started_at DESC);

CREATE TABLE IF NOT EXISTS quality.oee_snapshots (
    id BIGSERIAL PRIMARY KEY,
    request_key TEXT NOT NULL UNIQUE,
    work_center_code TEXT NOT NULL,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('ready', 'partial', 'unavailable')),
    availability NUMERIC(9, 6),
    performance NUMERIC(9, 6),
    quality NUMERIC(9, 6),
    oee NUMERIC(9, 6),
    inputs_json JSONB NOT NULL,
    warnings_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (period_end > period_start)
);

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'wms') THEN
        GRANT USAGE ON SCHEMA quality TO wms;
        GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA quality TO wms;
        GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA quality TO wms;
    END IF;
END
$$;
