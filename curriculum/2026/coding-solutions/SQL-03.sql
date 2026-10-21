-- Rank whole orders (not order lines) so line fan-out cannot pick a single line.
CREATE OR REPLACE VIEW latest_orders AS
WITH order_totals AS (
  SELECT o.order_id, o.user_id, o.order_ts,
         COALESCE(SUM(oi.quantity * oi.unit_price), 0.0) AS total_value
  FROM orders o
  LEFT JOIN order_items oi USING (order_id)
  WHERE o.status = 'paid'
  GROUP BY o.order_id, o.user_id, o.order_ts
), ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_ts DESC, order_id DESC) AS rn
  FROM order_totals
)
SELECT user_id, order_id, order_ts, total_value
FROM ranked
WHERE rn = 1;

-- Same result without a window: max timestamp first, then max order_id within that timestamp.
CREATE OR REPLACE VIEW latest_orders_no_window AS
WITH paid AS (
  SELECT order_id, user_id, order_ts FROM orders WHERE status = 'paid'
), latest_ts AS (
  SELECT user_id, MAX(order_ts) AS order_ts FROM paid GROUP BY user_id
), latest_id AS (
  SELECT p.user_id, MAX(p.order_id) AS order_id
  FROM paid p JOIN latest_ts l USING (user_id, order_ts)
  GROUP BY p.user_id
)
SELECT p.user_id, p.order_id, p.order_ts,
       COALESCE((SELECT SUM(oi.quantity * oi.unit_price) FROM order_items oi WHERE oi.order_id = p.order_id), 0.0) AS total_value
FROM paid p
JOIN latest_id l USING (user_id, order_id);

CREATE OR REPLACE VIEW latest_predictions AS
SELECT user_id, item_id, prediction_id, prediction_ts, score
FROM predictions
QUALIFY ROW_NUMBER() OVER (PARTITION BY user_id, item_id ORDER BY prediction_ts DESC, prediction_id DESC) = 1;
