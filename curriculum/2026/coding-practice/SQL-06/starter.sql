-- SQL-06: Rolling Time Windows
-- Tables: purchases(purchase_id, user_id, purchase_ts, amount)
--         config(dataset_end DATE)   one row; the last calendar day of the dataset
--
-- Create daily_rolling with one row per user per calendar day, from the day of the user's
-- first purchase through config.dataset_end inclusive, including days with no purchases.
-- Purchases after dataset_end are ignored (a user whose purchases are all later has no rows).
--   day                    DATE
--   daily_purchases        purchases on that day
--   rolling_7d_purchases   purchases in the 7 calendar days ending on `day` (day-6 .. day)
--   rolling_30d_spend      SUM(amount) in the 30 calendar days ending on `day` (day-29 .. day);
--                          0.0 when there is none
--   rolling_7d_change      rolling_7d_purchases minus the previous day's value; NULL on the
--                          user's first day
CREATE OR REPLACE VIEW daily_rolling AS
SELECT NULL::INTEGER AS user_id, NULL::DATE AS day, NULL::BIGINT AS daily_purchases,
       NULL::BIGINT AS rolling_7d_purchases, NULL::DOUBLE AS rolling_30d_spend,
       NULL::BIGINT AS rolling_7d_change
WHERE FALSE; -- TODO
