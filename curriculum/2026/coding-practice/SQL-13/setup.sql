DROP VIEW IF EXISTS reconciliation;
DROP VIEW IF EXISTS reconciliation_by_day_source;
DROP VIEW IF EXISTS data_quality_issues;
DROP VIEW IF EXISTS failure_summary;
DROP TABLE IF EXISTS source_a;
DROP TABLE IF EXISTS source_b;
DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS features;
DROP TABLE IF EXISTS raw_events;
CREATE TABLE raw_events(event_id INTEGER, source VARCHAR, event_ts TIMESTAMP, user_id INTEGER, amount DOUBLE);
CREATE TABLE features(event_id INTEGER, source VARCHAR, event_date DATE, user_id INTEGER, amount DOUBLE, feature_ts TIMESTAMP);
CREATE TABLE predictions(prediction_id INTEGER, event_id INTEGER, source VARCHAR, prediction_ts TIMESTAMP, score DOUBLE);
INSERT INTO raw_events VALUES
  (1, 'web', TIMESTAMP '2026-01-01 10:00:00', 1, 10.25),
  (2, 'web', TIMESTAMP '2026-01-01 11:00:00', 2, 5.0),
  (3, 'app', TIMESTAMP '2026-01-01 12:00:00', 3, 7.0),
  (4, 'app', TIMESTAMP '2026-01-01 13:00:00', 4, NULL),
  (5, 'web', TIMESTAMP '2026-01-02 09:00:00', 1, 3.0),
  (6, 'web', TIMESTAMP '2026-01-02 10:00:00', 2, 4.0),
  (7, 'app', TIMESTAMP '2026-01-02 11:00:00', 3, 2.0),
  (NULL, 'web', TIMESTAMP '2026-01-02 12:00:00', 5, 1.0),
  (8, 'app', TIMESTAMP '2026-01-02 23:59:59', 6, 6.0);
INSERT INTO features VALUES
  (1, 'web', DATE '2026-01-01', 1, 10.75, TIMESTAMP '2026-01-01 10:05:00'),
  (2, 'web', DATE '2026-01-01', 2, 5.0, TIMESTAMP '2026-01-01 11:05:00'),
  (3, 'app', DATE '2026-01-01', 3, 7.625, TIMESTAMP '2026-01-01 11:59:00'),
  (4, 'app', DATE '2026-01-01', 4, NULL, TIMESTAMP '2026-01-02 00:30:00'),
  (5, 'web', DATE '2026-01-02', 1, 3.0, TIMESTAMP '2026-01-02 09:05:00'),
  (5, 'web', DATE '2026-01-02', 1, 3.0, TIMESTAMP '2026-01-02 09:06:00'),
  (NULL, 'web', DATE '2026-01-02', 7, 2.0, TIMESTAMP '2026-01-02 12:05:00'),
  (7, 'app', DATE '2026-01-02', 3, 2.0, TIMESTAMP '2026-01-02 11:05:00'),
  (9, 'app', DATE '2026-01-02', 9, 1.0, TIMESTAMP '2026-01-02 12:00:00'),
  (8, 'app', DATE '2026-01-03', 6, 6.0, TIMESTAMP '2026-01-03 00:10:00');
INSERT INTO predictions VALUES
  (1, 1, 'web', TIMESTAMP '2026-01-01 10:10:00', 0.4),
  (2, 2, 'web', TIMESTAMP '2026-01-01 11:00:00', 0.5),
  (3, 6, 'web', TIMESTAMP '2026-01-02 10:10:00', 0.6),
  (4, 42, 'app', TIMESTAMP '2026-01-02 10:00:00', 0.7),
  (5, 5, 'web', TIMESTAMP '2026-01-02 09:05:30', 0.8),
  (6, NULL, 'web', TIMESTAMP '2026-01-02 13:00:00', 0.9),
  (7, 7, 'app', TIMESTAMP '2026-01-02 11:05:00', 0.3);
