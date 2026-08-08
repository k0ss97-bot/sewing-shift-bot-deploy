-- Article-first identity for finished goods.
--
-- The marketplace seller article (for example КДШВН-2/110) is the stable
-- identifier shared by production, WMS, Ozon and Wildberries.  Name, size,
-- colour and barcode remain attributes.  Empty article is retained only for
-- legacy/material/semi-finished rows until they are reconciled.

ALTER TABLE warehouse_stock
    ADD COLUMN IF NOT EXISTS product_article TEXT NOT NULL DEFAULT '';

ALTER TABLE warehouse_stock
    DROP CONSTRAINT IF EXISTS warehouse_stock_location_unique;

CREATE UNIQUE INDEX IF NOT EXISTS warehouse_stock_finished_article_unique
    ON warehouse_stock (product_article, unit, item_state, location_id) NULLS NOT DISTINCT
    WHERE item_type = 'finished' AND product_article <> '';

CREATE UNIQUE INDEX IF NOT EXISTS warehouse_stock_legacy_location_unique
    ON warehouse_stock (
        item_type, product_name, product_size, product_color,
        stage_name, ready_for_position, unit, item_state, location_id
    ) NULLS NOT DISTINCT
    WHERE item_type <> 'finished' OR product_article = '';

CREATE INDEX IF NOT EXISTS idx_whstock_article
    ON warehouse_stock (product_article)
    WHERE product_article <> '';

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'wms') THEN
        GRANT SELECT, INSERT, UPDATE ON warehouse_stock TO wms;
    END IF;
END
$$;
