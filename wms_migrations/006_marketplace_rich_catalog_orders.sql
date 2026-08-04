-- PostgreSQL authoritative Ozon read model: rich catalogue and FBS orders.

ALTER TABLE marketplace.products_current
    ADD COLUMN IF NOT EXISTS size TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS color TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS image_url TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS barcodes_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS attributes_json JSONB NOT NULL DEFAULT '{}'::jsonb;

CREATE TABLE IF NOT EXISTS marketplace.orders_current (
    account_id BIGINT NOT NULL REFERENCES marketplace.accounts(id) ON DELETE CASCADE,
    external_order_id TEXT NOT NULL,
    posting_number TEXT NOT NULL DEFAULT '',
    warehouse_type TEXT NOT NULL DEFAULT 'FBS',
    status TEXT NOT NULL DEFAULT '',
    shipment_date TIMESTAMPTZ,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_updated_at TIMESTAMPTZ,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_run_id BIGINT REFERENCES marketplace.sync_runs(id) ON DELETE SET NULL,
    PRIMARY KEY (account_id, external_order_id)
);

CREATE TABLE IF NOT EXISTS marketplace.order_items_current (
    account_id BIGINT NOT NULL,
    external_order_id TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    external_product_id TEXT NOT NULL DEFAULT '',
    offer_id TEXT NOT NULL DEFAULT '',
    sku TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL DEFAULT '',
    quantity NUMERIC(20,3) NOT NULL DEFAULT 0,
    price NUMERIC(18,2),
    currency CHAR(3) NOT NULL DEFAULT 'RUB',
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (account_id, external_order_id, line_number),
    FOREIGN KEY (account_id, external_order_id)
        REFERENCES marketplace.orders_current(account_id, external_order_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_marketplace_orders_status_time
    ON marketplace.orders_current (account_id, status, shipment_date DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_order_items_product
    ON marketplace.order_items_current (account_id, external_product_id, offer_id, sku);
CREATE INDEX IF NOT EXISTS idx_marketplace_products_barcode
    ON marketplace.products_current (account_id, barcode) WHERE barcode <> '';
