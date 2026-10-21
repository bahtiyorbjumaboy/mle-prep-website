-- SQL-09: ML / Serving Log Analysis
-- Tables: impressions(impression_id, request_id, user_id, item_id, model_version, position, impression_ts)
--         clicks(click_id, impression_id, click_ts)   an impression can be clicked more than once;
--                                                    some rows reference unknown impressions
--         carts(cart_id, impression_id, cart_ts)      same caveats as clicks
--         predictions(impression_id, model_version, score)  retries create exact duplicate rows;
--                                                    each impression has one logical score
--         assignments(user_id, variant, assigned_ts) a user can have repeated rows
--
-- All rates are at impression grain: clicked impressions / impressions, where an impression
-- is "clicked" (or "carted") if it has at least one matching row.
--
-- 1. ctr_by_model_position(model_version, position_bucket, impressions, clicked_impressions, ctr)
--    position_bucket: '1-3', '4-10', '11+'. Buckets with zero clicks are still returned.
-- 2. experiment_metrics(variant, users, impressions, ctr, cart_rate)
--    Exclude users assigned to more than one distinct variant. A clean user's assignment
--    time is their earliest assigned_ts; only impressions at or after it count. `users` is
--    the number of clean users assigned to the variant, whether or not they had impressions.
-- 3. high_score_zero_click(item_id, impressions, avg_score)
--    Items with at least 100 impressions, no clicked impressions, and an average
--    per-impression score of at least 0.75.
CREATE OR REPLACE VIEW ctr_by_model_position AS
SELECT NULL::VARCHAR AS model_version, NULL::VARCHAR AS position_bucket, NULL::BIGINT AS impressions,
       NULL::BIGINT AS clicked_impressions, NULL::DOUBLE AS ctr
WHERE FALSE; -- TODO

CREATE OR REPLACE VIEW experiment_metrics AS
SELECT NULL::VARCHAR AS variant, NULL::BIGINT AS users, NULL::BIGINT AS impressions,
       NULL::DOUBLE AS ctr, NULL::DOUBLE AS cart_rate
WHERE FALSE; -- TODO

CREATE OR REPLACE VIEW high_score_zero_click AS
SELECT NULL::INTEGER AS item_id, NULL::BIGINT AS impressions, NULL::DOUBLE AS avg_score
WHERE FALSE; -- TODO
