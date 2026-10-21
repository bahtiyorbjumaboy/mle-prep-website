-- Aggregate to item grain first; ranking raw sales rows would rank individual sales.
CREATE OR REPLACE VIEW top_items AS
WITH item_units AS (
  SELECT category, item_id, SUM(units) AS units_sold
  FROM sales
  WHERE sold_ts >= TIMESTAMP '2026-01-01' AND sold_ts < TIMESTAMP '2026-02-01'
  GROUP BY category, item_id
), ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY units_sold DESC, item_id ASC) AS sales_rank
  FROM item_units
)
SELECT category, item_id, units_sold, sales_rank
FROM ranked
WHERE sales_rank <= 3;

CREATE OR REPLACE VIEW top_items_with_ties AS
WITH item_units AS (
  SELECT category, item_id, SUM(units) AS units_sold
  FROM sales
  WHERE sold_ts >= TIMESTAMP '2026-01-01' AND sold_ts < TIMESTAMP '2026-02-01'
  GROUP BY category, item_id
), ranked AS (
  SELECT *, RANK() OVER (PARTITION BY category ORDER BY units_sold DESC) AS sales_rank
  FROM item_units
)
SELECT category, item_id, units_sold, sales_rank
FROM ranked
WHERE sales_rank <= 3;
