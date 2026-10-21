-- SQL-04: Top-N Per Group
-- Table: sales(sale_id, category, item_id, sold_ts, units); an item belongs to one category
-- and can have many sales rows.
--
-- Time window: January 2026, i.e. sold_ts >= 2026-01-01 and sold_ts < 2026-02-01.
-- units_sold is an item's total units within the window.
--
-- 1. top_items(category, item_id, units_sold, sales_rank): the top 3 items per category by
--    units_sold (highest first). Exactly min(3, items in category) rows per category; break
--    ties by the lower item_id, and sales_rank is 1, 2, 3 with no repeats.
-- 2. top_items_with_ties(category, item_id, units_sold, sales_rank): "top 3 plus ties" -
--    tied items share a rank and the following rank is skipped (10, 8, 8, 5 -> 1, 2, 2, 4).
--    Return every item whose rank is <= 3.
CREATE OR REPLACE VIEW top_items AS
SELECT NULL::VARCHAR AS category, NULL::INTEGER AS item_id, NULL::BIGINT AS units_sold, NULL::BIGINT AS sales_rank
WHERE FALSE; -- TODO

CREATE OR REPLACE VIEW top_items_with_ties AS
SELECT NULL::VARCHAR AS category, NULL::INTEGER AS item_id, NULL::BIGINT AS units_sold, NULL::BIGINT AS sales_rank
WHERE FALSE; -- TODO
