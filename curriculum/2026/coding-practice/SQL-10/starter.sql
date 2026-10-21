-- SQL-10: Cohort Retention
-- Tables: users(user_id, signup_ts), events(user_id, event_ts)
--
-- cohort_week   Monday of the signup date's week (ISO week start), as a DATE
-- week_number   elapsed weeks since signup, by calendar date:
--               (event date - signup date) in days, integer-divided by 7. Signup day and the
--               next 6 days are week 0. Events before signup, or after week 8, are ignored.
-- Only events from users in `users` count.
--
-- Create cohort_retention(cohort_week, week_number, cohort_users, retained_users, retention_rate)
-- with exactly one row for every cohort and every week_number 0..8, even when no one returned.
--   cohort_users    users who signed up in the cohort week (all of them)
--   retained_users  cohort users with at least one event in that week_number
--   retention_rate  retained_users / cohort_users
CREATE OR REPLACE VIEW cohort_retention AS
SELECT NULL::DATE AS cohort_week, NULL::INTEGER AS week_number, NULL::BIGINT AS cohort_users,
       NULL::BIGINT AS retained_users, NULL::DOUBLE AS retention_rate
WHERE FALSE; -- TODO
