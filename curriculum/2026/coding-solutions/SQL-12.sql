-- Aggregate events and profiles per label_id separately, then attach both to the label rows,
-- so neither side can multiply the other and labels without history survive.
CREATE OR REPLACE VIEW point_in_time_features AS
WITH event_features AS (
  SELECT l.label_id,
         COUNT(*) FILTER (WHERE e.event_ts >= l.label_ts - INTERVAL 1 DAY) AS event_count_1d,
         COUNT(*) FILTER (WHERE e.event_ts >= l.label_ts - INTERVAL 7 DAY) AS event_count_7d,
         COUNT(*) AS event_count_30d,
         SUM(e.amount) AS amount_30d
  FROM labels l
  JOIN events e
    ON e.entity_id = l.entity_id
   AND e.event_ts < l.label_ts
   AND e.event_ts >= l.label_ts - INTERVAL 30 DAY
  GROUP BY l.label_id
), profile_asof AS (
  SELECT l.label_id, p.tier
  FROM labels l
  JOIN profiles p ON p.entity_id = l.entity_id AND p.profile_ts < l.label_ts
  QUALIFY ROW_NUMBER() OVER (PARTITION BY l.label_id ORDER BY p.profile_ts DESC, p.profile_id DESC) = 1
)
SELECT l.label_id, l.entity_id, l.label_ts,
       COALESCE(f.event_count_1d, 0) AS event_count_1d,
       COALESCE(f.event_count_7d, 0) AS event_count_7d,
       COALESCE(f.event_count_30d, 0) AS event_count_30d,
       COALESCE(f.amount_30d, 0.0) AS amount_30d,
       p.tier AS latest_tier
FROM labels l
LEFT JOIN event_features f USING (label_id)
LEFT JOIN profile_asof p USING (label_id);
