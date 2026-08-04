-- Keep the marketplace sync role usable when migrations are applied by a
-- database owner different from the runtime role (as on production).

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'wms') THEN
        GRANT USAGE ON SCHEMA marketplace TO wms;

        GRANT SELECT, INSERT ON marketplace.orders_history TO wms;
        GRANT SELECT, INSERT, UPDATE ON marketplace.returns_current TO wms;
        GRANT SELECT, INSERT ON marketplace.returns_history TO wms;
        GRANT SELECT, INSERT, UPDATE ON marketplace.finance_transactions TO wms;
        GRANT SELECT, INSERT, UPDATE ON marketplace.ratings_history TO wms;

        GRANT USAGE, SELECT ON SEQUENCE marketplace.orders_history_id_seq TO wms;
        GRANT USAGE, SELECT ON SEQUENCE marketplace.returns_history_id_seq TO wms;
    END IF;
END
$$;
