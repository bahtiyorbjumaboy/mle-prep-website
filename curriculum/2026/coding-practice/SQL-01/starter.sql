-- SQL-01: Aggregation / Conversion
-- Tables: users(user_id, country, signup_ts, acquisition_channel)
--         orders(order_id, user_id, order_ts, status)
--
-- Return one row per country with:
--   signups_2026              users whose signup_ts falls in calendar year 2026
--   converted_users           of those 2026 signups, users with at least one qualifying
--                             order (status = 'paid' and order_ts in calendar year 2026)
--   conversion_rate           converted_users / signups_2026
--   paid_search_signup_share  share of 2026 signups with acquisition_channel = 'paid_search'
--                             (signups with an unknown channel stay in the denominator)
-- Keep only countries with at least 100 signups in 2026; countries that convert nobody
-- still appear.
CREATE OR REPLACE VIEW learner_result AS
SELECT
  NULL::VARCHAR AS country,
  NULL::BIGINT AS signups_2026,
  NULL::BIGINT AS converted_users,
  NULL::DOUBLE AS conversion_rate,
  NULL::DOUBLE AS paid_search_signup_share
WHERE FALSE; -- TODO: replace with your query
