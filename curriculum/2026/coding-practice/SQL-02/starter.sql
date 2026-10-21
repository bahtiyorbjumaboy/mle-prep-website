-- SQL-02: Join Grain and Fan-Out
-- Tables: orders(order_id, user_id, order_ts, status)
--         order_items(order_id, line_id, item_id, quantity, unit_price)   one row per order line
--         items(item_id, category, list_price)                            one row per item
--
-- Spend is quantity * unit_price (the price actually charged), summed over order lines.
-- Exclude orders whose status is 'cancelled' or 'returned'; every other order counts,
-- including orders whose status is still NULL (pending).
-- `orders` may contain exact duplicate rows from repeated ingestion; each order line
-- must be counted once.
--
-- 1. user_spend(user_id, spend, distinct_items): one row per user with at least one
--    counted order line; distinct_items counts different item_ids.
-- 2. category_spend(category, spend, distinct_buyers): one row per category in `items`
--    with at least one counted line; lines whose item_id is missing from `items` still
--    count toward user_spend but not toward any category.
CREATE OR REPLACE VIEW user_spend AS
SELECT NULL::INTEGER AS user_id, NULL::DOUBLE AS spend, NULL::BIGINT AS distinct_items
WHERE FALSE; -- TODO

CREATE OR REPLACE VIEW category_spend AS
SELECT NULL::VARCHAR AS category, NULL::DOUBLE AS spend, NULL::BIGINT AS distinct_buyers
WHERE FALSE; -- TODO
