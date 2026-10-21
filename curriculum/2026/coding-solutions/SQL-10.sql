CREATE OR REPLACE VIEW cohort_retention AS
WITH cohort_users AS (
  SELECT user_id, CAST(signup_ts AS DATE) AS signup_date,
         CAST(date_trunc('week', signup_ts) AS DATE) AS cohort_week
  FROM users
), user_weeks AS (
  -- One row per (user, week) no matter how many events fall in it.
  SELECT DISTINCT c.user_id, c.cohort_week,
         CAST((CAST(e.event_ts AS DATE) - c.signup_date) // 7 AS INTEGER) AS week_number
  FROM cohort_users c
  JOIN events e USING (user_id)
  WHERE CAST(e.event_ts AS DATE) >= c.signup_date
    AND CAST(e.event_ts AS DATE) - c.signup_date < 63
), cohort_sizes AS (
  SELECT cohort_week, COUNT(*) AS cohort_users FROM cohort_users GROUP BY cohort_week
), grid AS (
  SELECT s.cohort_week, CAST(w.week_number AS INTEGER) AS week_number, s.cohort_users
  FROM cohort_sizes s CROSS JOIN range(0, 9) AS w(week_number)
)
SELECT g.cohort_week, g.week_number, g.cohort_users,
       COUNT(uw.user_id) AS retained_users,
       COUNT(uw.user_id)::DOUBLE / g.cohort_users AS retention_rate
FROM grid g
LEFT JOIN user_weeks uw USING (cohort_week, week_number)
GROUP BY g.cohort_week, g.week_number, g.cohort_users;
