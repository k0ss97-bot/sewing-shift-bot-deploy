-- Marketplace analytics Phase 1A baseline.
--
-- Production already has this migration recorded.  The file is kept in Git so
-- a clean installation can reproduce the PostgreSQL marketplace projection.

CREATE SCHEMA IF NOT EXISTS marketplace;

CREATE TABLE IF NOT EXISTS marketplace.accounts (
    id BIGSERIAL PRIMARY KEY,
    marketplace TEXT NOT NULL,
    account_key TEXT NOT NULL UNIQUE,
    account_name TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS marketplace.account_capabilities (
    account_id BIGINT NOT NULL REFERENCES marketplace.accounts(id) ON DELETE CASCADE,
    capability TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'unknown',
    checked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    safe_message TEXT NOT NULL DEFAULT '',
    details_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (account_id, capability)
);

CREATE TABLE IF NOT EXISTS marketplace.endpoint_registry (
    marketplace TEXT NOT NULL,
    dataset TEXT NOT NULL,
    method TEXT NOT NULL,
    path TEXT NOT NULL,
    pagination_kind TEXT NOT NULL DEFAULT 'none',
    request_limit INTEGER,
    verification_status TEXT NOT NULL DEFAULT 'unverified',
    verified_at TIMESTAMPTZ,
    official_url TEXT,
    notes TEXT NOT NULL DEFAULT '',
    read_only BOOLEAN NOT NULL DEFAULT TRUE,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (marketplace, dataset, method, path)
);

CREATE TABLE IF NOT EXISTS marketplace.sync_runs (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES marketplace.accounts(id) ON DELETE CASCADE,
    dataset TEXT NOT NULL,
    trigger_kind TEXT NOT NULL DEFAULT 'scheduled',
    status TEXT NOT NULL DEFAULT 'queued',
    expected_count BIGINT,
    received_count BIGINT NOT NULL DEFAULT 0,
    unique_count BIGINT NOT NULL DEFAULT 0,
    inserted_count BIGINT NOT NULL DEFAULT 0,
    updated_count BIGINT NOT NULL DEFAULT 0,
    skipped_count BIGINT NOT NULL DEFAULT 0,
    page_count INTEGER NOT NULL DEFAULT 0,
    retry_count INTEGER NOT NULL DEFAULT 0,
    checkpoint_before TEXT,
    checkpoint_after TEXT,
    termination_reason TEXT,
    error_summary TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS marketplace.sync_pages (
    run_id BIGINT NOT NULL REFERENCES marketplace.sync_runs(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    request_cursor TEXT,
    response_cursor TEXT,
    rows_received BIGINT NOT NULL DEFAULT 0,
    retry_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'running',
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    committed_at TIMESTAMPTZ,
    PRIMARY KEY (run_id, page_number)
);

CREATE TABLE IF NOT EXISTS marketplace.sync_errors (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES marketplace.sync_runs(id) ON DELETE CASCADE,
    dataset TEXT NOT NULL,
    page_number INTEGER,
    error_class TEXT NOT NULL,
    error_code TEXT,
    http_status INTEGER,
    safe_message TEXT NOT NULL,
    retry_count INTEGER NOT NULL DEFAULT 0,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS marketplace.sync_checkpoints (
    account_id BIGINT NOT NULL REFERENCES marketplace.accounts(id) ON DELETE CASCADE,
    dataset TEXT NOT NULL,
    cursor_value TEXT,
    page_number INTEGER NOT NULL DEFAULT 0,
    run_id BIGINT REFERENCES marketplace.sync_runs(id) ON DELETE SET NULL,
    state JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (account_id, dataset)
);

CREATE TABLE IF NOT EXISTS marketplace.products_current (
    account_id BIGINT NOT NULL REFERENCES marketplace.accounts(id) ON DELETE CASCADE,
    external_product_id TEXT NOT NULL,
    offer_id TEXT NOT NULL DEFAULT '',
    sku TEXT NOT NULL DEFAULT '',
    barcode TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL DEFAULT '',
    visibility TEXT NOT NULL DEFAULT 'unknown',
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_updated_at TIMESTAMPTZ,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_run_id BIGINT REFERENCES marketplace.sync_runs(id) ON DELETE SET NULL,
    PRIMARY KEY (account_id, external_product_id, offer_id)
);

CREATE TABLE IF NOT EXISTS marketplace.prices_current (
    account_id BIGINT NOT NULL,
    external_product_id TEXT NOT NULL,
    offer_id TEXT NOT NULL DEFAULT '',
    current_price NUMERIC(18,2),
    old_price NUMERIC(18,2),
    marketing_price NUMERIC(18,2),
    minimum_price NUMERIC(18,2),
    currency CHAR(3) NOT NULL DEFAULT 'RUB',
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_updated_at TIMESTAMPTZ,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_run_id BIGINT REFERENCES marketplace.sync_runs(id) ON DELETE SET NULL,
    PRIMARY KEY (account_id, external_product_id, offer_id),
    FOREIGN KEY (account_id, external_product_id, offer_id)
        REFERENCES marketplace.products_current(account_id, external_product_id, offer_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS marketplace.prices_history (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL,
    external_product_id TEXT NOT NULL,
    offer_id TEXT NOT NULL DEFAULT '',
    current_price NUMERIC(18,2),
    old_price NUMERIC(18,2),
    marketing_price NUMERIC(18,2),
    minimum_price NUMERIC(18,2),
    currency CHAR(3) NOT NULL DEFAULT 'RUB',
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    observed_at TIMESTAMPTZ NOT NULL,
    source_updated_at TIMESTAMPTZ,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    run_id BIGINT NOT NULL REFERENCES marketplace.sync_runs(id) ON DELETE CASCADE,
    row_hash TEXT NOT NULL,
    UNIQUE (run_id, account_id, external_product_id, offer_id, row_hash),
    FOREIGN KEY (account_id, external_product_id, offer_id)
        REFERENCES marketplace.products_current(account_id, external_product_id, offer_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS marketplace.stocks_current (
    account_id BIGINT NOT NULL,
    external_product_id TEXT NOT NULL,
    offer_id TEXT NOT NULL DEFAULT '',
    warehouse_type TEXT NOT NULL DEFAULT '',
    warehouse_name TEXT NOT NULL DEFAULT '',
    stock NUMERIC(20,3),
    reserved NUMERIC(20,3),
    available NUMERIC(20,3),
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_updated_at TIMESTAMPTZ,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_run_id BIGINT REFERENCES marketplace.sync_runs(id) ON DELETE SET NULL,
    PRIMARY KEY (account_id, external_product_id, offer_id, warehouse_type, warehouse_name),
    FOREIGN KEY (account_id, external_product_id, offer_id)
        REFERENCES marketplace.products_current(account_id, external_product_id, offer_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS marketplace.stocks_history (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL,
    external_product_id TEXT NOT NULL,
    offer_id TEXT NOT NULL DEFAULT '',
    warehouse_type TEXT NOT NULL DEFAULT '',
    warehouse_name TEXT NOT NULL DEFAULT '',
    stock NUMERIC(20,3),
    reserved NUMERIC(20,3),
    available NUMERIC(20,3),
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    observed_at TIMESTAMPTZ NOT NULL,
    source_updated_at TIMESTAMPTZ,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    run_id BIGINT NOT NULL REFERENCES marketplace.sync_runs(id) ON DELETE CASCADE,
    row_hash TEXT NOT NULL,
    UNIQUE (run_id, account_id, external_product_id, offer_id, warehouse_type, warehouse_name),
    FOREIGN KEY (account_id, external_product_id, offer_id)
        REFERENCES marketplace.products_current(account_id, external_product_id, offer_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_marketplace_sync_runs_account_dataset
    ON marketplace.sync_runs (account_id, dataset, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_products_offer
    ON marketplace.products_current (account_id, offer_id) WHERE offer_id <> '';
CREATE INDEX IF NOT EXISTS idx_marketplace_products_sku
    ON marketplace.products_current (account_id, sku) WHERE sku <> '';
CREATE INDEX IF NOT EXISTS idx_marketplace_stocks_current_received
    ON marketplace.stocks_current (account_id, received_at DESC);
