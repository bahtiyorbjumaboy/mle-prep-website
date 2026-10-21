-- SQL-03: Latest Record Per Entity
-- Tables: orders(order_id, user_id, order_ts, status)
--         order_items(order_id, item_id, quantity, unit_price)
--         predictions(prediction_id, user_id, item_id, prediction_ts, model_version, score)
--
-- A qualifying order has status = 'paid'. An order's total_value is
-- SUM(quantity * unit_price) over its lines (0.0 if it has no lines).
--
-- 1. latest_orders(user_id, order_id, order_ts, total_value): each user's most recent
--    qualifying order. If several share the latest order_ts, keep the larger order_id.
--    Users with no qualifying order are omitted.
-- 2. latest_orders_no_window: identical output, written without any window function
--    (no OVER clause).
-- 3. latest_predictions(user_id, item_id, prediction_id, prediction_ts, score): the latest
--    prediction for every (user_id, item_id) pair; break prediction_ts ties by the larger
--    prediction_id. The latest row is kept even if its score is NULL.
CREATE OR REPLACE VIEW latest_orders AS
SELECT NULL::INTEGER AS user_id, NULL::INTEGER AS order_id, NULL::TIMESTAMP AS order_ts, NULL::DOUBLE AS total_value
WHERE FALSE; -- TODO

CREATE OR REPLACE VIEW latest_orders_no_window AS
SELECT NULL::INTEGER AS user_id, NULL::INTEGER AS order_id, NULL::TIMESTAMP AS order_ts, NULL::DOUBLE AS total_value
WHERE FALSE; -- TODO

CREATE OR REPLACE VIEW latest_predictions AS
SELECT NULL::INTEGER AS user_id, NULL::INTEGER AS item_id, NULL::INTEGER AS prediction_id, NULL::TIMESTAMP AS prediction_ts, NULL::DOUBLE AS score
WHERE FALSE; -- TODO
