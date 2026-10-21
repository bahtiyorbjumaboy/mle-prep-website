CREATE OR REPLACE VIEW deduped_events AS
WITH distinct_rows AS (
  SELECT DISTINCT event_id, user_id, item_id, event_type, event_ts FROM events
), with_prev AS (
  SELECT *,
         LAG(event_ts) OVER (PARTITION BY user_id, item_id, event_type ORDER BY event_ts, event_id) AS prev_ts
  FROM distinct_rows
)
SELECT event_id, user_id, item_id, event_type, event_ts
FROM with_prev
WHERE prev_ts IS NULL OR event_ts - prev_ts > INTERVAL 5 SECOND;

-- NOT EXISTS is NULL-safe: a click with a NULL user_id/item_id cannot empty the result,
-- unlike `x NOT IN (subquery containing NULL)`.
CREATE OR REPLACE VIEW never_clicked AS
SELECT u.user_id
FROM users u
WHERE NOT EXISTS (
  SELECT 1 FROM deduped_events e WHERE e.event_type = 'click' AND e.user_id = u.user_id
);

CREATE OR REPLACE VIEW items_without_clicks AS
SELECT i.item_id
FROM items i
WHERE EXISTS (SELECT 1 FROM deduped_events e WHERE e.event_type = 'impression' AND e.item_id = i.item_id)
  AND NOT EXISTS (SELECT 1 FROM deduped_events e WHERE e.event_type = 'click' AND e.item_id = i.item_id);
