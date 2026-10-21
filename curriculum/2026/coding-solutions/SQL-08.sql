-- One row per session with a 2026-01-01 search, flagging the deepest stages it reaches.
-- Each stage keeps every event that can extend some chain from the previous stage, so a
-- later prior event (e.g. a second search) can qualify when the first one is too old.
CREATE OR REPLACE VIEW funnel_session_stages AS
WITH searches AS (
  SELECT session_id, event_ts FROM events
  WHERE event_type = 'search' AND CAST(event_ts AS DATE) = DATE '2026-01-01'
), impressions AS (
  SELECT DISTINCT e.session_id, e.event_ts
  FROM events e JOIN searches p ON e.session_id = p.session_id
   AND e.event_ts > p.event_ts AND e.event_ts <= p.event_ts + INTERVAL 30 MINUTE
  WHERE e.event_type = 'impression'
), clicks AS (
  SELECT DISTINCT e.session_id, e.event_ts
  FROM events e JOIN impressions p ON e.session_id = p.session_id
   AND e.event_ts > p.event_ts AND e.event_ts <= p.event_ts + INTERVAL 30 MINUTE
  WHERE e.event_type = 'click'
), carts AS (
  SELECT DISTINCT e.session_id, e.event_ts
  FROM events e JOIN clicks p ON e.session_id = p.session_id
   AND e.event_ts > p.event_ts AND e.event_ts <= p.event_ts + INTERVAL 30 MINUTE
  WHERE e.event_type = 'add_to_cart'
), purchases AS (
  SELECT DISTINCT e.session_id, e.event_ts
  FROM events e JOIN carts p ON e.session_id = p.session_id
   AND e.event_ts > p.event_ts AND e.event_ts <= p.event_ts + INTERVAL 30 MINUTE
  WHERE e.event_type = 'purchase'
), session_channel AS (
  SELECT DISTINCT e.session_id, COALESCE(u.acquisition_channel, 'unknown') AS acquisition_channel
  FROM events e LEFT JOIN users u USING (user_id)
)
SELECT s.session_id, c.acquisition_channel,
       s.session_id IN (SELECT session_id FROM impressions) AS reached_impression,
       s.session_id IN (SELECT session_id FROM clicks) AS reached_click,
       s.session_id IN (SELECT session_id FROM carts) AS reached_cart,
       s.session_id IN (SELECT session_id FROM purchases) AS reached_purchase
FROM (SELECT DISTINCT session_id FROM searches) s
JOIN session_channel c USING (session_id);

CREATE OR REPLACE VIEW funnel_by_channel AS
WITH counts AS (
  SELECT acquisition_channel,
         COUNT(*) AS searches,
         COUNT(*) FILTER (WHERE reached_impression) AS impressions,
         COUNT(*) FILTER (WHERE reached_click) AS clicks,
         COUNT(*) FILTER (WHERE reached_cart) AS add_to_carts,
         COUNT(*) FILTER (WHERE reached_purchase) AS purchases
  FROM funnel_session_stages
  GROUP BY acquisition_channel
)
SELECT *,
       impressions::DOUBLE / NULLIF(searches, 0) AS search_to_impression_rate,
       clicks::DOUBLE / NULLIF(impressions, 0) AS impression_to_click_rate,
       add_to_carts::DOUBLE / NULLIF(clicks, 0) AS click_to_cart_rate,
       purchases::DOUBLE / NULLIF(add_to_carts, 0) AS cart_to_purchase_rate
FROM counts;

CREATE OR REPLACE VIEW funnel_overall AS
WITH counts AS (
  SELECT COUNT(*) AS searches,
         COUNT(*) FILTER (WHERE reached_impression) AS impressions,
         COUNT(*) FILTER (WHERE reached_click) AS clicks,
         COUNT(*) FILTER (WHERE reached_cart) AS add_to_carts,
         COUNT(*) FILTER (WHERE reached_purchase) AS purchases
  FROM funnel_session_stages
)
SELECT *,
       impressions::DOUBLE / NULLIF(searches, 0) AS search_to_impression_rate,
       clicks::DOUBLE / NULLIF(impressions, 0) AS impression_to_click_rate,
       add_to_carts::DOUBLE / NULLIF(clicks, 0) AS click_to_cart_rate,
       purchases::DOUBLE / NULLIF(add_to_carts, 0) AS cart_to_purchase_rate
FROM counts;
