CREATE OR REPLACE VIEW daily_rolling AS
WITH in_range AS (
  SELECT user_id, CAST(purchase_ts AS DATE) AS day, amount
  FROM purchases
  WHERE CAST(purchase_ts AS DATE) <= (SELECT dataset_end FROM config)
), daily AS (
  SELECT user_id, day, COUNT(*) AS daily_purchases, SUM(amount) AS daily_spend
  FROM in_range
  GROUP BY user_id, day
), spine AS (
  SELECT u.user_id, CAST(d.day AS DATE) AS day
  FROM (SELECT user_id, MIN(day) AS first_day FROM daily GROUP BY user_id) u
  CROSS JOIN LATERAL generate_series(u.first_day, (SELECT dataset_end FROM config), INTERVAL 1 DAY) AS d(day)
), dense AS (
  SELECT s.user_id, s.day,
         COALESCE(d.daily_purchases, 0) AS daily_purchases,
         COALESCE(d.daily_spend, 0.0) AS daily_spend
  FROM spine s
  LEFT JOIN daily d USING (user_id, day)
), rolled AS (
  -- RANGE over the date makes the frame calendar days, not rows.
  SELECT user_id, day, daily_purchases,
         SUM(daily_purchases) OVER (PARTITION BY user_id ORDER BY day RANGE BETWEEN INTERVAL 6 DAY PRECEDING AND CURRENT ROW) AS rolling_7d_purchases,
         SUM(daily_spend) OVER (PARTITION BY user_id ORDER BY day RANGE BETWEEN INTERVAL 29 DAY PRECEDING AND CURRENT ROW) AS rolling_30d_spend
  FROM dense
)
SELECT user_id, day, daily_purchases, rolling_7d_purchases, rolling_30d_spend,
       rolling_7d_purchases - LAG(rolling_7d_purchases) OVER (PARTITION BY user_id ORDER BY day) AS rolling_7d_change
FROM rolled;
