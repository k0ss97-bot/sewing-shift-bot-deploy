-- Multi-line manual stock receipt documents (Оприходование).

CREATE SEQUENCE IF NOT EXISTS wms_stock_receipt_number_seq;

CREATE TABLE IF NOT EXISTS wms_stock_receipts (
    id BIGSERIAL PRIMARY KEY,
    number TEXT NOT NULL UNIQUE DEFAULT (
        'OPR-' || lpad(nextval('wms_stock_receipt_number_seq')::text, 6, '0')
    ),
    status TEXT NOT NULL DEFAULT 'draft',
    request_key TEXT NOT NULL UNIQUE,
    actor_employee_id INTEGER,
    comment TEXT,
    lines_count INTEGER NOT NULL DEFAULT 0,
    total_quantity INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    posted_at TIMESTAMPTZ,
    CONSTRAINT wms_stock_receipt_status CHECK (status IN ('draft', 'posted', 'cancelled')),
    CONSTRAINT wms_stock_receipt_counts CHECK (lines_count >= 0 AND total_quantity >= 0)
);

CREATE TABLE IF NOT EXISTS wms_stock_receipt_lines (
    id BIGSERIAL PRIMARY KEY,
    receipt_id BIGINT NOT NULL REFERENCES wms_stock_receipts(id),
    line_no INTEGER NOT NULL,
    barcode TEXT NOT NULL,
    product_key JSONB NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    movement_id BIGINT NOT NULL REFERENCES wms_movements(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(receipt_id, line_no),
    UNIQUE(movement_id)
);

CREATE INDEX IF NOT EXISTS idx_wms_stock_receipts_created
    ON wms_stock_receipts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_wms_stock_receipt_lines_receipt
    ON wms_stock_receipt_lines(receipt_id, line_no);
