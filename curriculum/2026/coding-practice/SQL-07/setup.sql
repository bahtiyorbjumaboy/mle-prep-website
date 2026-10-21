DROP VIEW IF EXISTS deduped_events;
DROP VIEW IF EXISTS never_clicked;
DROP VIEW IF EXISTS items_without_clicks;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS items;
CREATE TABLE users(user_id INTEGER);
CREATE TABLE items(item_id INTEGER);
CREATE TABLE events(event_id INTEGER, user_id INTEGER, item_id INTEGER, event_type VARCHAR, event_ts TIMESTAMP);
INSERT INTO users VALUES (1), (2), (3), (4);
INSERT INTO items VALUES (10), (11), (12), (13);
INSERT INTO events VALUES
  (1, 1, 10, 'impression', TIMESTAMP '2026-01-01 10:00:00'),
  (1, 1, 10, 'impression', TIMESTAMP '2026-01-01 10:00:00'),
  (2, 1, 10, 'impression', TIMESTAMP '2026-01-01 10:00:05'),
  (3, 1, 10, 'impression', TIMESTAMP '2026-01-01 10:00:11'),
  (5, 1, 10, 'click', TIMESTAMP '2026-01-01 10:00:12'),
  (4, 1, 10, 'click', TIMESTAMP '2026-01-01 10:00:12'),
  (6, 2, 11, 'impression', TIMESTAMP '2026-01-01 11:00:00'),
  (7, 2, 11, 'impression', TIMESTAMP '2026-01-01 11:00:04'),
  (13, 2, 11, 'impression', TIMESTAMP '2026-01-01 11:00:10'),
  (8, 2, NULL, 'click', TIMESTAMP '2026-01-01 11:00:30'),
  (9, NULL, 13, 'click', TIMESTAMP '2026-01-01 12:00:00'),
  (10, 3, 13, 'impression', TIMESTAMP '2026-01-01 12:00:01'),
  (11, 3, 13, 'impression', TIMESTAMP '2026-01-01 12:00:01');
