-- SQL-08: Ordered Funnel
-- Tables: users(user_id, acquisition_channel)        channel may be NULL -> report 'unknown'
--         events(event_id, session_id, user_id, event_type, event_ts)   one user per session
--
-- Funnel: search -> impression -> click -> add_to_cart -> purchase, for the day 2026-01-01.
-- A session reaches a stage when it has a chain of events, one per stage, in which each
-- event is in the same session, strictly later than the previous stage's event, and at
-- most 30 minutes after it (exactly 30 minutes qualifies). Any search on 2026-01-01 may
-- start the chain; later stages may fall after midnight. Counts are numbers of sessions
-- reaching each stage. Step rates are stage count / previous stage count, NULL when the
-- previous stage count is 0.
--
-- 1. funnel_overall: one row with the columns below except acquisition_channel.
-- 2. funnel_by_channel: one row per acquisition_channel that has at least one search session.
-- Columns: acquisition_channel, searches, impressions, clicks, add_to_carts, purchases,
--          search_to_impression_rate, impression_to_click_rate, click_to_cart_rate,
--          cart_to_purchase_rate
CREATE OR REPLACE VIEW funnel_overall AS
SELECT NULL::BIGINT AS searches, NULL::BIGINT AS impressions, NULL::BIGINT AS clicks,
       NULL::BIGINT AS add_to_carts, NULL::BIGINT AS purchases,
       NULL::DOUBLE AS search_to_impression_rate, NULL::DOUBLE AS impression_to_click_rate,
       NULL::DOUBLE AS click_to_cart_rate, NULL::DOUBLE AS cart_to_purchase_rate
WHERE FALSE; -- TODO

CREATE OR REPLACE VIEW funnel_by_channel AS
SELECT NULL::VARCHAR AS acquisition_channel, NULL::BIGINT AS searches, NULL::BIGINT AS impressions,
       NULL::BIGINT AS clicks, NULL::BIGINT AS add_to_carts, NULL::BIGINT AS purchases,
       NULL::DOUBLE AS search_to_impression_rate, NULL::DOUBLE AS impression_to_click_rate,
       NULL::DOUBLE AS click_to_cart_rate, NULL::DOUBLE AS cart_to_purchase_rate
WHERE FALSE; -- TODO
