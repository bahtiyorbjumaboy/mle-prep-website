-- SQL-13: Data Reconciliation / Quality Invariants
-- Tables: raw_events(event_id, source, event_ts, user_id, amount)
--         features(event_id, source, event_date, user_id, amount, feature_ts)  should hold exactly
--                  one row per raw event, with event_date = the raw event's date
--         predictions(prediction_id, event_id, source, prediction_ts, score)
-- Keys and amounts can be NULL. Amount sums ignore NULLs and are 0.0 for an empty side.
--
-- 1. reconciliation_by_day_source(event_date, source, raw_rows, feature_rows, raw_amount,
--      feature_amount, row_diff, amount_diff, status)
--    Raw rows are dated by CAST(event_ts AS DATE); feature rows by event_date. One row per
--    (event_date, source) present on either side. row_diff = feature_rows - raw_rows,
--    amount_diff = feature_amount - raw_amount. status = 'ok' when row_diff = 0 and
--    |amount_diff| <= 0.5, otherwise 'mismatch'. Row counts include rows with NULL keys.
-- 2. data_quality_issues(check_name, table_name, record_id, event_date, source), one row per
--    failing record per check. record_id is event_id (raw_events, features) or prediction_id
--    (predictions); event_date is the row's own date (raw: event_ts date, features: event_date,
--    predictions: prediction_ts date). Rows with a NULL event_id are only reported as null_key.
--      null_key                  raw_events or features row with NULL event_id
--      missing_feature           raw event with no feature row             (table raw_events)
--      unexpected_feature        feature row with no raw event             (table features)
--      duplicate_feature_key     event_id with more than one feature row; one row per key
--                                (event_date/source from any of its rows)  (table features)
--      feature_date_mismatch     feature event_date differs from the raw event's date
--      feature_before_event      feature_ts earlier than the raw event_ts
--      orphan_prediction         prediction whose event_id has no feature row, including NULL
--      prediction_before_feature prediction_ts earlier than the event's earliest feature_ts
-- 3. failure_summary(event_date, source, check_name, failures): issue counts per day/source/check.
CREATE OR REPLACE VIEW reconciliation_by_day_source AS
SELECT NULL::DATE AS event_date, NULL::VARCHAR AS source, NULL::BIGINT AS raw_rows, NULL::BIGINT AS feature_rows,
       NULL::DOUBLE AS raw_amount, NULL::DOUBLE AS feature_amount, NULL::BIGINT AS row_diff,
       NULL::DOUBLE AS amount_diff, NULL::VARCHAR AS status
WHERE FALSE; -- TODO

CREATE OR REPLACE VIEW data_quality_issues AS
SELECT NULL::VARCHAR AS check_name, NULL::VARCHAR AS table_name, NULL::INTEGER AS record_id,
       NULL::DATE AS event_date, NULL::VARCHAR AS source
WHERE FALSE; -- TODO

CREATE OR REPLACE VIEW failure_summary AS
SELECT NULL::DATE AS event_date, NULL::VARCHAR AS source, NULL::VARCHAR AS check_name, NULL::BIGINT AS failures
WHERE FALSE; -- TODO
