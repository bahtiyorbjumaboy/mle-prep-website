DROP VIEW IF EXISTS learner_result;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS users;
CREATE TABLE users(user_id INTEGER, country VARCHAR, signup_ts TIMESTAMP, acquisition_channel VARCHAR);
CREATE TABLE orders(order_id INTEGER, user_id INTEGER, order_ts TIMESTAMP, status VARCHAR);
-- US: 120 signups in 2026 (30 paid_search, 10 with unknown channel) plus 10 signups in 2025.
INSERT INTO users
SELECT i, 'US', TIMESTAMP '2026-01-01' + i * INTERVAL 2 DAY,
       CASE WHEN i <= 30 THEN 'paid_search' WHEN i > 110 THEN NULL ELSE 'organic' END
FROM range(1, 121) t(i);
INSERT INTO users SELECT i, 'US', TIMESTAMP '2025-03-01' + i * INTERVAL 1 DAY, 'paid_search' FROM range(121, 131) t(i);
-- CA: exactly 100 signups in 2026 (boundary of the HAVING threshold), none of whom converts.
INSERT INTO users
SELECT i, 'CA', TIMESTAMP '2026-02-01' + (i - 200) * INTERVAL 1 DAY, CASE WHEN i <= 210 THEN 'paid_search' ELSE 'referral' END
FROM range(201, 301) t(i);
-- MX: 99 signups in 2026 and 50 in 2025: only all-time counting reaches 100.
INSERT INTO users SELECT i, 'MX', TIMESTAMP '2026-03-01' + (i - 300) * INTERVAL 1 DAY, 'organic' FROM range(301, 400) t(i);
INSERT INTO users SELECT i, 'MX', TIMESTAMP '2025-01-01' + (i - 400) * INTERVAL 1 DAY, 'organic' FROM range(400, 450) t(i);
-- Year-boundary signups.
INSERT INTO users VALUES (900, 'US', TIMESTAMP '2025-12-31 23:59:59', 'organic'), (901, 'US', TIMESTAMP '2027-01-01 00:00:00', 'organic');
INSERT INTO orders VALUES
  (1, 1, TIMESTAMP '2026-01-10', 'paid'),
  (2, 1, TIMESTAMP '2026-01-11', 'paid'),
  (3, 1, TIMESTAMP '2026-02-11', 'paid'),
  (4, 2, TIMESTAMP '2026-01-12', 'paid'),
  (5, 2, TIMESTAMP '2026-01-13', 'cancelled'),
  (6, 3, TIMESTAMP '2025-12-31 23:59:59', 'paid'),
  (7, 4, TIMESTAMP '2026-01-15', 'cancelled'),
  (8, 5, TIMESTAMP '2027-01-01 00:00:00', 'paid'),
  (9, 6, TIMESTAMP '2026-12-31 23:59:59', 'paid'),
  (10, 121, TIMESTAMP '2026-04-01', 'paid'),
  (11, 900, TIMESTAMP '2026-04-01', 'paid'),
  (12, NULL, TIMESTAMP '2026-04-01', 'paid'),
  (13, 201, TIMESTAMP '2026-04-01', 'cancelled'),
  (14, 202, TIMESTAMP '2025-06-01', 'paid'),
  (15, 203, TIMESTAMP '2026-05-01', NULL),
  (16, 301, TIMESTAMP '2026-05-01', 'paid');
