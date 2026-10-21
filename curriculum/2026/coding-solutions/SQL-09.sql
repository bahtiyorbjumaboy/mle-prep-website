-- Collapse clicks/carts to impression grain first: double clicks and orphan rows must not
-- change an impression-level rate.
CREATE OR REPLACE VIEW ctr_by_model_position AS
WITH clicked AS (SELECT DISTINCT impression_id FROM clicks)
SELECT i.model_version,
       CASE WHEN i.position <= 3 THEN '1-3' WHEN i.position <= 10 THEN '4-10' ELSE '11+' END AS position_bucket,
       COUNT(*) AS impressions,
       COUNT(c.impression_id) AS clicked_impressions,
       COUNT(c.impression_id)::DOUBLE / COUNT(*) AS ctr
FROM impressions i
LEFT JOIN clicked c USING (impression_id)
GROUP BY 1, 2;

CREATE OR REPLACE VIEW experiment_metrics AS
WITH clean_users AS (
  SELECT user_id, MIN(variant) AS variant, MIN(assigned_ts) AS assigned_ts
  FROM assignments
  GROUP BY user_id
  HAVING COUNT(DISTINCT variant) = 1
), exposed AS (
  SELECT u.variant, i.impression_id,
         i.impression_id IN (SELECT impression_id FROM clicks) AS clicked,
         i.impression_id IN (SELECT impression_id FROM carts) AS carted
  FROM clean_users u
  JOIN impressions i ON i.user_id = u.user_id AND i.impression_ts >= u.assigned_ts
), per_variant AS (
  SELECT variant, COUNT(*) AS impressions,
         AVG(clicked::INTEGER) AS ctr, AVG(carted::INTEGER) AS cart_rate
  FROM exposed
  GROUP BY variant
)
-- Users come from assignments so assigned users with no impressions stay in the count.
SELECT u.variant, COUNT(*) AS users,
       COALESCE(MAX(p.impressions), 0) AS impressions, MAX(p.ctr) AS ctr, MAX(p.cart_rate) AS cart_rate
FROM clean_users u
LEFT JOIN per_variant p USING (variant)
GROUP BY u.variant;

CREATE OR REPLACE VIEW high_score_zero_click AS
WITH impression_scores AS (
  -- Retried predictions are exact duplicates; keep one score per impression.
  SELECT DISTINCT impression_id, score FROM predictions
)
SELECT i.item_id, COUNT(*) AS impressions, AVG(s.score) AS avg_score
FROM impressions i
JOIN impression_scores s USING (impression_id)
GROUP BY i.item_id
HAVING COUNT(*) >= 100
   AND AVG(s.score) >= 0.75
   AND NOT bool_or(i.impression_id IN (SELECT impression_id FROM clicks));
