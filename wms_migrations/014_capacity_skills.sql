-- Finite-capacity and employee-skill planning snapshots.
-- Employee ids reference the legacy personnel master without a cross-DB FK.

CREATE SCHEMA IF NOT EXISTS planning;

CREATE TABLE IF NOT EXISTS planning.operations (
    operation_code TEXT PRIMARY KEY,
    name_ru TEXT NOT NULL,
    standard_minutes_per_unit NUMERIC(12, 4) NOT NULL CHECK (standard_minutes_per_unit > 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS planning.resources (
    id BIGSERIAL PRIMARY KEY,
    external_employee_id INTEGER NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    daily_capacity_minutes NUMERIC(12, 2) NOT NULL DEFAULT 480 CHECK (daily_capacity_minutes > 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS planning.resource_skills (
    resource_id BIGINT NOT NULL REFERENCES planning.resources(id) ON DELETE CASCADE,
    operation_code TEXT NOT NULL REFERENCES planning.operations(operation_code) ON DELETE RESTRICT,
    proficiency NUMERIC(6, 4) NOT NULL DEFAULT 1 CHECK (proficiency >= 0.25 AND proficiency <= 2),
    certified_until DATE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (resource_id, operation_code)
);

CREATE INDEX IF NOT EXISTS resource_skills_operation
    ON planning.resource_skills (operation_code, resource_id);

CREATE TABLE IF NOT EXISTS planning.capacity_runs (
    id BIGSERIAL PRIMARY KEY,
    request_key TEXT NOT NULL UNIQUE,
    horizon_start DATE NOT NULL,
    horizon_end DATE NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('ready', 'over_capacity', 'incomplete')),
    jobs_count INTEGER NOT NULL CHECK (jobs_count >= 0),
    assigned_count INTEGER NOT NULL CHECK (assigned_count >= 0),
    unassigned_count INTEGER NOT NULL CHECK (unassigned_count >= 0),
    source_reference TEXT NOT NULL DEFAULT '',
    created_by_employee_id INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (horizon_end >= horizon_start)
);

CREATE TABLE IF NOT EXISTS planning.capacity_assignments (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES planning.capacity_runs(id) ON DELETE CASCADE,
    job_key TEXT NOT NULL,
    operation_code TEXT NOT NULL,
    resource_id BIGINT REFERENCES planning.resources(id) ON DELETE RESTRICT,
    standard_minutes NUMERIC(18, 6) NOT NULL CHECK (standard_minutes >= 0),
    clock_minutes NUMERIC(18, 6) NOT NULL CHECK (clock_minutes >= 0),
    assigned_quantity NUMERIC(18, 6) NOT NULL CHECK (assigned_quantity >= 0),
    assignment_status TEXT NOT NULL CHECK (assignment_status IN ('assigned', 'unassigned')),
    reason TEXT NOT NULL DEFAULT '',
    sequence_no INTEGER NOT NULL,
    UNIQUE (run_id, job_key, sequence_no)
);

CREATE INDEX IF NOT EXISTS capacity_assignments_resource
    ON planning.capacity_assignments (run_id, resource_id, sequence_no);

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'wms') THEN
        GRANT USAGE ON SCHEMA planning TO wms;
        GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA planning TO wms;
        GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA planning TO wms;
    END IF;
END
$$;
