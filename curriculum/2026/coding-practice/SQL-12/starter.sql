-- SQL-12: Point-in-Time Features in SQL
-- Tables: labels(label_id, entity_id, label_ts)
--         events(event_id, entity_id, event_ts, amount)    amount may be NULL
--         profiles(profile_id, entity_id, profile_ts, tier) history of profile values
--
-- Only information strictly before label_ts may be used (event_ts < label_ts,
-- profile_ts < label_ts). An N-day window covers label_ts - N days <= event_ts < label_ts.
--
-- Create point_in_time_features with exactly one row per label row:
--   label_id, entity_id, label_ts,
--   event_count_1d, event_count_7d, event_count_30d   events in each window (0 if none)
--   amount_30d     SUM(amount) over the 30-day window, ignoring NULL amounts; 0.0 if none
--   latest_tier    tier of the latest profile row before label_ts (ties on profile_ts go to
--                  the larger profile_id); NULL if there is none
CREATE OR REPLACE VIEW point_in_time_features AS
SELECT NULL::INTEGER AS label_id, NULL::INTEGER AS entity_id, NULL::TIMESTAMP AS label_ts,
       NULL::BIGINT AS event_count_1d, NULL::BIGINT AS event_count_7d, NULL::BIGINT AS event_count_30d,
       NULL::DOUBLE AS amount_30d, NULL::VARCHAR AS latest_tier
WHERE FALSE; -- TODO
