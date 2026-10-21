-- Aggregate each side to (day, source) before the full outer join, so duplicate rows on one
-- side cannot multiply the other and days present on only one side survive.
CREATE OR REPLACE VIEW reconciliation_by_day_source AS
WITH raw_side AS (
  SELECT CAST(event_ts AS DATE) AS event_date, source,
         COUNT(*) AS raw_rows, COALESCE(SUM(amount), 0.0) AS raw_amount
  FROM raw_events GROUP BY 1, 2
), feature_side AS (
  SELECT event_date, source,
         COUNT(*) AS feature_rows, COALESCE(SUM(amount), 0.0) AS feature_amount
  FROM features GROUP BY 1, 2
), joined AS (
  SELECT COALESCE(r.event_date, f.event_date) AS event_date,
         COALESCE(r.source, f.source) AS source,
         COALESCE(r.raw_rows, 0) AS raw_rows, COALESCE(f.feature_rows, 0) AS feature_rows,
         COALESCE(r.raw_amount, 0.0) AS raw_amount, COALESCE(f.feature_amount, 0.0) AS feature_amount
  FROM raw_side r
  FULL OUTER JOIN feature_side f ON r.event_date = f.event_date AND r.source = f.source
)
SELECT *,
       feature_rows - raw_rows AS row_diff,
       feature_amount - raw_amount AS amount_diff,
       CASE WHEN feature_rows = raw_rows AND abs(feature_amount - raw_amount) <= 0.5 THEN 'ok' ELSE 'mismatch' END AS status
FROM joined;

CREATE OR REPLACE VIEW data_quality_issues AS
WITH raw_keys AS (
  SELECT event_id, source, event_ts, CAST(event_ts AS DATE) AS event_date FROM raw_events WHERE event_id IS NOT NULL
), feature_keys AS (
  SELECT * FROM features WHERE event_id IS NOT NULL
)
SELECT 'null_key' AS check_name, 'raw_events' AS table_name, event_id AS record_id, CAST(event_ts AS DATE) AS event_date, source
FROM raw_events WHERE event_id IS NULL
UNION ALL
SELECT 'null_key', 'features', event_id, event_date, source FROM features WHERE event_id IS NULL
UNION ALL
SELECT 'missing_feature', 'raw_events', r.event_id, r.event_date, r.source
FROM raw_keys r WHERE NOT EXISTS (SELECT 1 FROM feature_keys f WHERE f.event_id = r.event_id)
UNION ALL
SELECT 'unexpected_feature', 'features', f.event_id, f.event_date, f.source
FROM feature_keys f WHERE NOT EXISTS (SELECT 1 FROM raw_keys r WHERE r.event_id = f.event_id)
UNION ALL
SELECT 'duplicate_feature_key', 'features', event_id, MIN(event_date), MIN(source)
FROM feature_keys GROUP BY event_id HAVING COUNT(*) > 1
UNION ALL
SELECT 'feature_date_mismatch', 'features', f.event_id, f.event_date, f.source
FROM feature_keys f JOIN raw_keys r USING (event_id) WHERE f.event_date <> r.event_date
UNION ALL
SELECT 'feature_before_event', 'features', f.event_id, f.event_date, f.source
FROM feature_keys f JOIN raw_keys r USING (event_id) WHERE f.feature_ts < r.event_ts
UNION ALL
SELECT 'orphan_prediction', 'predictions', p.prediction_id, CAST(p.prediction_ts AS DATE), p.source
FROM predictions p WHERE NOT EXISTS (SELECT 1 FROM feature_keys f WHERE f.event_id = p.event_id)
UNION ALL
SELECT 'prediction_before_feature', 'predictions', p.prediction_id, CAST(p.prediction_ts AS DATE), p.source
FROM predictions p
JOIN (SELECT event_id, MIN(feature_ts) AS first_feature_ts FROM feature_keys GROUP BY event_id) f USING (event_id)
WHERE p.prediction_ts < f.first_feature_ts;

CREATE OR REPLACE VIEW failure_summary AS
SELECT event_date, source, check_name, COUNT(*) AS failures
FROM data_quality_issues
GROUP BY event_date, source, check_name;
