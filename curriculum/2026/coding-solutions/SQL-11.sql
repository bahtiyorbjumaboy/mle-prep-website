-- Pre-aggregate every table to one row per user before combining, so repeated exposures
-- or assignment rows cannot multiply conversions or revenue.
CREATE OR REPLACE VIEW experiment_metrics AS
WITH clean_users AS (
  SELECT user_id, MIN(variant) AS variant, MIN(assigned_ts) AS assigned_ts
  FROM assignments
  GROUP BY user_id
  HAVING COUNT(DISTINCT variant) = 1
), first_exposure AS (
  SELECT c.user_id, MIN(x.exposure_ts) AS exposure_ts
  FROM clean_users c
  JOIN exposures x ON x.user_id = c.user_id AND x.exposure_ts >= c.assigned_ts
  GROUP BY c.user_id
), user_outcomes AS (
  SELECT f.user_id, COUNT(*) AS conversions, SUM(COALESCE(r.amount, 0.0)) AS revenue
  FROM first_exposure f
  JOIN conversions v ON v.user_id = f.user_id AND v.conversion_ts >= f.exposure_ts
  LEFT JOIN revenue r ON r.order_id = v.order_id
  GROUP BY f.user_id
), per_variant AS (
  SELECT c.variant,
         COUNT(*) AS assigned_users,
         COUNT(f.user_id) AS exposed_users,
         COUNT(o.user_id) AS converters,
         COALESCE(SUM(o.revenue), 0.0) AS revenue
  FROM clean_users c
  LEFT JOIN first_exposure f USING (user_id)
  LEFT JOIN user_outcomes o USING (user_id)
  GROUP BY c.variant
)
SELECT variant, assigned_users, exposed_users, converters,
       converters::DOUBLE / NULLIF(exposed_users, 0) AS conversion_rate,
       revenue / NULLIF(exposed_users, 0) AS revenue_per_user,
       assigned_users::DOUBLE / SUM(assigned_users) OVER () AS assignment_share
FROM per_variant;

CREATE OR REPLACE VIEW assignment_issues AS
SELECT DISTINCT user_id, 'duplicate_assignment' AS issue
FROM assignments GROUP BY user_id, variant HAVING COUNT(*) > 1
UNION ALL
SELECT user_id, 'multiple_variants'
FROM assignments GROUP BY user_id HAVING COUNT(DISTINCT variant) > 1
UNION ALL
SELECT x.user_id, 'exposure_after_conversion'
FROM (SELECT user_id, MIN(exposure_ts) AS first_exposure FROM exposures GROUP BY user_id) x
JOIN (SELECT user_id, MIN(conversion_ts) AS first_conversion FROM conversions GROUP BY user_id) v USING (user_id)
WHERE x.first_exposure > v.first_conversion
  AND x.user_id IN (SELECT user_id FROM assignments);

CREATE OR REPLACE VIEW srm_inputs AS
WITH clean_users AS (
  SELECT user_id, MIN(variant) AS variant
  FROM assignments
  GROUP BY user_id
  HAVING COUNT(DISTINCT variant) = 1
), observed AS (
  SELECT variant, COUNT(*) AS observed_users FROM clean_users GROUP BY variant
)
SELECT variant, observed_users,
       0.5 * SUM(observed_users) OVER () AS expected_users,
       power(observed_users - 0.5 * SUM(observed_users) OVER (), 2) / (0.5 * SUM(observed_users) OVER ()) AS chi_square_component
FROM observed;
