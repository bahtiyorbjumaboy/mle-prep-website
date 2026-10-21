CREATE OR REPLACE VIEW session_summary AS
WITH flagged AS (
  SELECT user_id, event_ts, event_type,
         CASE
           WHEN LAG(event_ts) OVER (PARTITION BY user_id ORDER BY event_ts) IS NULL THEN 1
           WHEN event_ts - LAG(event_ts) OVER (PARTITION BY user_id ORDER BY event_ts) > INTERVAL 30 MINUTE THEN 1
           ELSE 0
         END AS is_new_session
  FROM events
), numbered AS (
  SELECT *, SUM(is_new_session) OVER (PARTITION BY user_id ORDER BY event_ts) AS session_number
  FROM flagged
), sessions AS (
  SELECT user_id, session_number,
         MIN(event_ts) AS session_start, MAX(event_ts) AS session_end,
         COUNT(*) AS event_count, BOOL_OR(event_type = 'purchase') AS has_purchase
  FROM numbered
  GROUP BY user_id, session_number
)
SELECT *,
       epoch(session_start - LAG(session_end) OVER (PARTITION BY user_id ORDER BY session_number)) / 60.0
         AS gap_from_previous_session_minutes
FROM sessions;
