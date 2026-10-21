CREATE OR REPLACE VIEW learner_result AS
WITH signups AS (
  SELECT user_id, country, acquisition_channel
  FROM users
  WHERE signup_ts >= TIMESTAMP '2026-01-01' AND signup_ts < TIMESTAMP '2027-01-01'
), converters AS (
  SELECT DISTINCT user_id
  FROM orders
  WHERE status = 'paid'
    AND order_ts >= TIMESTAMP '2026-01-01' AND order_ts < TIMESTAMP '2027-01-01'
)
SELECT
  s.country,
  COUNT(*) AS signups_2026,
  COUNT(c.user_id) AS converted_users,
  COUNT(c.user_id)::DOUBLE / COUNT(*) AS conversion_rate,
  COUNT(*) FILTER (WHERE s.acquisition_channel = 'paid_search')::DOUBLE / COUNT(*) AS paid_search_signup_share
FROM signups s
LEFT JOIN converters c USING (user_id)
GROUP BY s.country
HAVING COUNT(*) >= 100;
