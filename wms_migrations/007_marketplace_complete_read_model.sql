-- Complete read-only Ozon projection: both fulfilment schemes and analytics.

CREATE TABLE IF NOT EXISTS marketplace.orders_history (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES marketplace.accounts(id) ON DELETE CASCADE,
    external_order_id TEXT NOT NULL,
    posting_number TEXT NOT NULL DEFAULT '',
    warehouse_type TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT '',
    shipment_date TIMESTAMPTZ,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    run_id BIGINT NOT NULL REFERENCES marketplace.sync_runs(id) ON DELETE CASCADE,
    row_hash TEXT NOT NULL,
    UNIQUE (run_id, account_id, external_order_id, row_hash)
);

CREATE TABLE IF NOT EXISTS marketplace.returns_current (
    account_id BIGINT NOT NULL REFERENCES marketplace.accounts(id) ON DELETE CASCADE,
    external_return_id TEXT NOT NULL,
    scheme TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT '',
    posting_number TEXT NOT NULL DEFAULT '',
    external_product_id TEXT NOT NULL DEFAULT '',
    offer_id TEXT NOT NULL DEFAULT '',
    sku TEXT NOT NULL DEFAULT '',
    product_name TEXT NOT NULL DEFAULT '',
    quantity NUMERIC(20,3) NOT NULL DEFAULT 0,
    amount NUMERIC(18,2),
    currency CHAR(3) NOT NULL DEFAULT 'RUB',
    returned_at TIMESTAMPTZ,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_run_id BIGINT REFERENCES marketplace.sync_runs(id) ON DELETE SET NULL,
    PRIMARY KEY (account_id, external_return_id)
);

CREATE TABLE IF NOT EXISTS marketplace.returns_history (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES marketplace.accounts(id) ON DELETE CASCADE,
    external_return_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT '',
    quantity NUMERIC(20,3) NOT NULL DEFAULT 0,
    amount NUMERIC(18,2),
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    run_id BIGINT NOT NULL REFERENCES marketplace.sync_runs(id) ON DELETE CASCADE,
    row_hash TEXT NOT NULL,
    UNIQUE (run_id, account_id, external_return_id, row_hash)
);

CREATE TABLE IF NOT EXISTS marketplace.finance_transactions (
    account_id BIGINT NOT NULL REFERENCES marketplace.accounts(id) ON DELETE CASCADE,
    operation_id TEXT NOT NULL,
    operation_date TIMESTAMPTZ,
    operation_type TEXT NOT NULL DEFAULT '',
    operation_name TEXT NOT NULL DEFAULT '',
    posting_number TEXT NOT NULL DEFAULT '',
    sku TEXT NOT NULL DEFAULT '',
    amount NUMERIC(18,2) NOT NULL DEFAULT 0,
    accruals_for_sale NUMERIC(18,2) NOT NULL DEFAULT 0,
    sale_commission NUMERIC(18,2) NOT NULL DEFAULT 0,
    delivery_charge NUMERIC(18,2) NOT NULL DEFAULT 0,
    return_delivery_charge NUMERIC(18,2) NOT NULL DEFAULT 0,
    currency CHAR(3) NOT NULL DEFAULT 'RUB',
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_run_id BIGINT REFERENCES marketplace.sync_runs(id) ON DELETE SET NULL,
    PRIMARY KEY (account_id, operation_id)
);

CREATE TABLE IF NOT EXISTS marketplace.ratings_history (
    account_id BIGINT NOT NULL REFERENCES marketplace.accounts(id) ON DELETE CASCADE,
    observed_date DATE NOT NULL,
    rating NUMERIC(8,3),
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_run_id BIGINT REFERENCES marketplace.sync_runs(id) ON DELETE SET NULL,
    PRIMARY KEY (account_id, observed_date)
);

CREATE INDEX IF NOT EXISTS idx_marketplace_orders_history_time
    ON marketplace.orders_history (account_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_returns_current_time
    ON marketplace.returns_current (account_id, returned_at DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_returns_product
    ON marketplace.returns_current (account_id, external_product_id, offer_id, sku);
CREATE INDEX IF NOT EXISTS idx_marketplace_finance_date
    ON marketplace.finance_transactions (account_id, operation_date DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_finance_posting
    ON marketplace.finance_transactions (account_id, posting_number);
CREATE INDEX IF NOT EXISTS idx_marketplace_ratings_date
    ON marketplace.ratings_history (account_id, observed_date DESC);
