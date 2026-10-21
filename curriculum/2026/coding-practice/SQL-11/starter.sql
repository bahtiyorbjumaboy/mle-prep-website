-- SQL-11: Experiment Metrics + Sample-Ratio Checks
-- Tables: assignments(user_id, variant, assigned_ts)   may repeat rows; a few users have two variants
--         exposures(user_id, exposure_ts)              many rows per user
--         conversions(order_id, user_id, conversion_ts)
--         revenue(order_id, amount)                    amount may be NULL (treat as 0)
--
-- Analysis population: users assigned to exactly one distinct variant ("clean" users).
-- A clean user's assignment time is their earliest assigned_ts.
--   exposed     the user has at least one exposure at or after their assignment time;
--               their first such exposure is their exposure time
--   converter   an exposed user with at least one conversion at or after their exposure time
--   revenue     amounts of those qualifying conversions only
--
-- 1. experiment_metrics(variant, assigned_users, exposed_users, converters, conversion_rate,
--                       revenue_per_user, assignment_share)
--    conversion_rate = converters / exposed_users; revenue_per_user = revenue / exposed_users;
--    assignment_share = assigned_users / all clean users.
-- 2. assignment_issues(user_id, issue), one row per user per issue (all assignment rows, not just
--    clean users):
--      'duplicate_assignment'       the same (user_id, variant) appears more than once
--      'multiple_variants'          the user is assigned to more than one distinct variant
--      'exposure_after_conversion'  the user's earliest exposure is later than their earliest conversion
-- 3. srm_inputs(variant, observed_users, expected_users, chi_square_component) for an intended
--    50/50 split over clean users: expected_users = 0.5 * clean users,
--    chi_square_component = (observed - expected)^2 / expected.
CREATE OR REPLACE VIEW experiment_metrics AS
SELECT NULL::VARCHAR AS variant, NULL::BIGINT AS assigned_users, NULL::BIGINT AS exposed_users,
       NULL::BIGINT AS converters, NULL::DOUBLE AS conversion_rate, NULL::DOUBLE AS revenue_per_user,
       NULL::DOUBLE AS assignment_share
WHERE FALSE; -- TODO

CREATE OR REPLACE VIEW assignment_issues AS
SELECT NULL::INTEGER AS user_id, NULL::VARCHAR AS issue WHERE FALSE; -- TODO

CREATE OR REPLACE VIEW srm_inputs AS
SELECT NULL::VARCHAR AS variant, NULL::BIGINT AS observed_users, NULL::DOUBLE AS expected_users,
       NULL::DOUBLE AS chi_square_component
WHERE FALSE; -- TODO
