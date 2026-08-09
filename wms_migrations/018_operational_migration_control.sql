-- Audit/control plane for phased SQLite -> PostgreSQL operational cutover.

CREATE SCHEMA IF NOT EXISTS migration_control;

CREATE TABLE IF NOT EXISTS migration_control.runs (
    id BIGSERIAL PRIMARY KEY,
    run_key TEXT NOT NULL UNIQUE,
    phase TEXT NOT NULL CHECK (phase IN ('inventory', 'shadow_copy', 'dual_read', 'canary', 'cutover', 'rollback', 'completed')),
    status TEXT NOT NULL CHECK (status IN ('running', 'ready', 'blocked', 'failed', 'completed', 'rolled_back')),
    source_release TEXT NOT NULL,
    target_release TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    approved_by_employee_id INTEGER,
    note TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS migration_control.table_checkpoints (
    run_id BIGINT NOT NULL REFERENCES migration_control.runs(id) ON DELETE CASCADE,
    table_name TEXT NOT NULL,
    source_row_count BIGINT NOT NULL CHECK (source_row_count >= 0),
    target_row_count BIGINT NOT NULL CHECK (target_row_count >= 0),
    source_checksum TEXT NOT NULL,
    target_checksum TEXT NOT NULL,
    replication_lag_seconds NUMERIC(18, 3) CHECK (replication_lag_seconds >= 0),
    writes_quiesced BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (run_id, table_name)
);

CREATE TABLE IF NOT EXISTS migration_control.gate_results (
    run_id BIGINT NOT NULL REFERENCES migration_control.runs(id) ON DELETE CASCADE,
    gate_name TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    evidence TEXT NOT NULL,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (run_id, gate_name)
);

CREATE TABLE IF NOT EXISTS migration_control.cutover_events (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES migration_control.runs(id) ON DELETE RESTRICT,
    event_type TEXT NOT NULL CHECK (event_type IN ('approval', 'traffic_shift', 'write_switch', 'verification', 'rollback')),
    previous_state JSONB NOT NULL DEFAULT '{}'::jsonb,
    next_state JSONB NOT NULL DEFAULT '{}'::jsonb,
    actor_employee_id INTEGER,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'wms') THEN
        GRANT USAGE ON SCHEMA migration_control TO wms;
        GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA migration_control TO wms;
        GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA migration_control TO wms;
    END IF;
END
$$;
