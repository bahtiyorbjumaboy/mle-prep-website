DROP VIEW IF EXISTS session_summary;
DROP TABLE IF EXISTS events;
CREATE TABLE events(event_id INTEGER, user_id INTEGER, session_id VARCHAR, event_ts TIMESTAMP, event_type VARCHAR);
-- Rows are deliberately unsorted; stored session_id values are unreliable and must be ignored.
INSERT INTO events VALUES
  (9, 1, 's1', TIMESTAMP '2026-01-01 12:30:59', 'purchase'),
  (3, 1, 's1', TIMESTAMP '2026-01-01 11:00:01', 'view'),
  (1, 1, 's1', TIMESTAMP '2026-01-01 10:00:00', 'view'),
  (20, 2, 's9', TIMESTAMP '2026-01-01 10:15:00', 'purchase'),
  (5, 1, 's2', TIMESTAMP '2026-01-01 11:29:59', 'click'),
  (2, 1, 's1', TIMESTAMP '2026-01-01 10:30:00', 'click'),
  (4, 1, 's2', TIMESTAMP '2026-01-01 11:29:59', 'purchase'),
  (8, 1, 's2', TIMESTAMP '2026-01-01 12:00:30', 'view'),
  (31, 3, 's7', TIMESTAMP '2026-01-01 08:50:00', 'view'),
  (30, 3, 's7', TIMESTAMP '2026-01-01 08:00:00', 'view'),
  (32, 3, 's7', TIMESTAMP '2026-01-01 08:10:00', 'click');
