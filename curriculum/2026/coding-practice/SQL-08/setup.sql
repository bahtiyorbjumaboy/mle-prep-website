DROP VIEW IF EXISTS funnel_overall;
DROP VIEW IF EXISTS funnel_by_channel;
DROP VIEW IF EXISTS funnel_metrics;
DROP VIEW IF EXISTS funnel_session_stages;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS users;
CREATE TABLE users(user_id INTEGER, acquisition_channel VARCHAR);
CREATE TABLE events(event_id INTEGER, session_id INTEGER, user_id INTEGER, event_type VARCHAR, event_ts TIMESTAMP);
INSERT INTO users VALUES (1, 'paid'), (2, 'organic'), (3, 'paid'), (4, 'organic'), (5, NULL);
INSERT INTO events VALUES
  -- S1: complete ordered funnel
  (101, 1, 1, 'search', TIMESTAMP '2026-01-01 10:00'), (102, 1, 1, 'impression', TIMESTAMP '2026-01-01 10:01'),
  (103, 1, 1, 'click', TIMESTAMP '2026-01-01 10:02'), (104, 1, 1, 'add_to_cart', TIMESTAMP '2026-01-01 10:03'),
  (105, 1, 1, 'purchase', TIMESTAMP '2026-01-01 10:04'),
  -- S2: skips impression
  (201, 2, 2, 'search', TIMESTAMP '2026-01-01 11:00'), (202, 2, 2, 'click', TIMESTAMP '2026-01-01 11:01'),
  -- S3: next step 40 minutes later
  (301, 3, 1, 'search', TIMESTAMP '2026-01-01 12:00'), (302, 3, 1, 'impression', TIMESTAMP '2026-01-01 12:40'),
  -- S4: impression happens before the search
  (401, 4, 3, 'impression', TIMESTAMP '2026-01-01 09:00'), (402, 4, 3, 'search', TIMESTAMP '2026-01-01 09:05'),
  (403, 4, 3, 'click', TIMESTAMP '2026-01-01 09:06'),
  -- S5: only the second search is close enough; click is exactly 30 minutes after the impression;
  -- its add_to_cart happens before its click, so it never counts
  (501, 5, 4, 'search', TIMESTAMP '2026-01-01 13:00'), (502, 5, 4, 'search', TIMESTAMP '2026-01-01 13:40'),
  (503, 5, 4, 'impression', TIMESTAMP '2026-01-01 13:45'), (504, 5, 4, 'click', TIMESTAMP '2026-01-01 14:15'),
  (505, 5, 4, 'add_to_cart', TIMESTAMP '2026-01-01 14:00'),
  -- S6: crosses midnight; user has no channel
  (601, 6, 5, 'search', TIMESTAMP '2026-01-01 23:50'), (602, 6, 5, 'impression', TIMESTAMP '2026-01-01 23:55'),
  (603, 6, 5, 'click', TIMESTAMP '2026-01-02 00:10'),
  -- S7: different day
  (701, 7, 2, 'search', TIMESTAMP '2026-01-02 08:00'), (702, 7, 2, 'impression', TIMESTAMP '2026-01-02 08:01'),
  -- S8: same-timestamp impression does not follow the search; the later one is 31 minutes after
  (801, 8, 3, 'search', TIMESTAMP '2026-01-01 15:00'), (802, 8, 3, 'impression', TIMESTAMP '2026-01-01 15:00'),
  (803, 8, 3, 'impression', TIMESTAMP '2026-01-01 15:31'),
  -- S9: repeated steps
  (901, 9, 1, 'search', TIMESTAMP '2026-01-01 16:00'), (902, 9, 1, 'impression', TIMESTAMP '2026-01-01 16:01'),
  (903, 9, 1, 'impression', TIMESTAMP '2026-01-01 16:02'), (904, 9, 1, 'click', TIMESTAMP '2026-01-01 16:03'),
  (905, 9, 1, 'click', TIMESTAMP '2026-01-01 16:04'), (906, 9, 1, 'add_to_cart', TIMESTAMP '2026-01-01 16:05'),
  -- S10: same user as S5 but a different session with no search
  (1001, 10, 4, 'impression', TIMESTAMP '2026-01-01 13:50'), (1002, 10, 4, 'click', TIMESTAMP '2026-01-01 13:55'),
  (1003, 10, 4, 'add_to_cart', TIMESTAMP '2026-01-01 13:58');
