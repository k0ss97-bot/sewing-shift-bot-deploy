-- Authoritative read-only Ozon FBO supply projection.

CREATE TABLE IF NOT EXISTS marketplace.supplies_current (
    account_id BIGINT NOT NULL REFERENCES marketplace.accounts(id) ON DELETE CASCADE,
    external_supply_id TEXT NOT NULL,
    external_order_id TEXT NOT NULL DEFAULT '',
    order_number TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    order_state TEXT NOT NULL DEFAULT '',
    bundle_id TEXT NOT NULL DEFAULT '',
    is_crossdock BOOLEAN NOT NULL DEFAULT FALSE,
    macrolocal_cluster_id TEXT NOT NULL DEFAULT '',
    dropoff_warehouse_id TEXT NOT NULL DEFAULT '',
    dropoff_warehouse_name TEXT NOT NULL DEFAULT '',
    storage_warehouse_id TEXT NOT NULL DEFAULT '',
    storage_warehouse_name TEXT NOT NULL DEFAULT '',
    timeslot_from TIMESTAMPTZ,
    timeslot_to TIMESTAMPTZ,
    created_at_external TIMESTAMPTZ,
    state_updated_at TIMESTAMPTZ,
    items_count BIGINT NOT NULL DEFAULT 0,
    total_quantity NUMERIC(20,3) NOT NULL DEFAULT 0,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_run_id BIGINT REFERENCES marketplace.sync_runs(id) ON DELETE SET NULL,
    PRIMARY KEY (account_id, external_supply_id)
);

CREATE TABLE IF NOT EXISTS marketplace.supply_items_current (
    account_id BIGINT NOT NULL REFERENCES marketplace.accounts(id) ON DELETE CASCADE,
    external_supply_id TEXT NOT NULL,
    item_key TEXT NOT NULL,
    external_product_id TEXT NOT NULL DEFAULT '',
    offer_id TEXT NOT NULL DEFAULT '',
    sku TEXT NOT NULL DEFAULT '',
    barcode TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL DEFAULT '',
    quantity NUMERIC(20,3) NOT NULL DEFAULT 0,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_run_id BIGINT REFERENCES marketplace.sync_runs(id) ON DELETE SET NULL,
    PRIMARY KEY (account_id, external_supply_id, item_key),
    FOREIGN KEY (account_id, external_supply_id)
        REFERENCES marketplace.supplies_current(account_id, external_supply_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS marketplace.supplies_history (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES marketplace.accounts(id) ON DELETE CASCADE,
    external_supply_id TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT '',
    total_quantity NUMERIC(20,3) NOT NULL DEFAULT 0,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    run_id BIGINT NOT NULL REFERENCES marketplace.sync_runs(id) ON DELETE CASCADE,
    row_hash TEXT NOT NULL,
    UNIQUE (run_id, account_id, external_supply_id, row_hash)
);

CREATE INDEX IF NOT EXISTS idx_marketplace_supplies_state
    ON marketplace.supplies_current (account_id, state, state_updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_supplies_timeslot
    ON marketplace.supplies_current (account_id, timeslot_from DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_supply_items_offer
    ON marketplace.supply_items_current (account_id, offer_id) WHERE offer_id <> '';
CREATE INDEX IF NOT EXISTS idx_marketplace_supply_items_sku
    ON marketplace.supply_items_current (account_id, sku) WHERE sku <> '';
