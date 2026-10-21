-- Collapse duplicate order headers to order grain before joining to lines.
CREATE OR REPLACE VIEW user_spend AS
WITH counted_orders AS (
  SELECT DISTINCT order_id, user_id
  FROM orders
  WHERE status IS NULL OR status NOT IN ('cancelled', 'returned')
), lines AS (
  SELECT o.user_id, oi.item_id, oi.quantity * oi.unit_price AS line_spend
  FROM counted_orders o
  JOIN order_items oi USING (order_id)
)
SELECT user_id, SUM(line_spend) AS spend, COUNT(DISTINCT item_id) AS distinct_items
FROM lines
GROUP BY user_id;

CREATE OR REPLACE VIEW category_spend AS
WITH counted_orders AS (
  SELECT DISTINCT order_id, user_id
  FROM orders
  WHERE status IS NULL OR status NOT IN ('cancelled', 'returned')
)
SELECT i.category,
       SUM(oi.quantity * oi.unit_price) AS spend,
       COUNT(DISTINCT o.user_id) AS distinct_buyers
FROM counted_orders o
JOIN order_items oi USING (order_id)
JOIN items i USING (item_id)
GROUP BY i.category;
