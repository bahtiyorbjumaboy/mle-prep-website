DROP VIEW IF EXISTS latest_orders;
DROP VIEW IF EXISTS latest_orders_no_window;
DROP VIEW IF EXISTS latest_predictions;
DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
CREATE TABLE orders(order_id INTEGER, user_id INTEGER, order_ts TIMESTAMP, status VARCHAR);
CREATE TABLE order_items(order_id INTEGER, item_id INTEGER, quantity INTEGER, unit_price DOUBLE);
CREATE TABLE predictions(prediction_id INTEGER, user_id INTEGER, item_id INTEGER, prediction_ts TIMESTAMP, model_version VARCHAR, score DOUBLE);
INSERT INTO orders VALUES
  (1, 1, TIMESTAMP '2026-01-01 08:00', 'paid'),
  (2, 1, TIMESTAMP '2026-01-03 09:00', 'paid'),
  (3, 1, TIMESTAMP '2026-01-03 09:00', 'paid'),
  (4, 1, TIMESTAMP '2026-01-09 09:00', 'cancelled'),
  (5, 2, TIMESTAMP '2026-01-02 12:00', 'paid'),
  (6, 3, TIMESTAMP '2026-01-04 12:00', 'cancelled'),
  (20, 4, TIMESTAMP '2026-01-05 10:00', 'paid'),
  (15, 4, TIMESTAMP '2026-01-07 10:00', 'paid'),
  (30, 5, TIMESTAMP '2026-01-06 10:00', 'paid'),
  (31, 5, TIMESTAMP '2026-01-08 10:00', 'paid');
INSERT INTO order_items VALUES
  (1, 100, 1, 50.0),
  (2, 100, 1, 99.0),
  (3, 100, 2, 3.0),
  (3, 101, 1, 4.0),
  (3, 102, 1, 1.5),
  (4, 100, 9, 9.0),
  (5, 101, 3, 2.0),
  (20, 100, 1, 1.0),
  (15, 101, 1, 6.0),
  (15, 102, 2, 2.5),
  (30, 100, 1, 8.0);
INSERT INTO predictions VALUES
  (1, 1, 10, TIMESTAMP '2026-01-01 00:00', 'v1', 0.20),
  (2, 1, 10, TIMESTAMP '2026-01-02 00:00', 'v1', 0.80),
  (7, 1, 10, TIMESTAMP '2026-01-02 00:00', 'v2', 0.65),
  (3, 1, 11, TIMESTAMP '2026-01-01 00:00', 'v1', 0.10),
  (4, 2, 10, TIMESTAMP '2026-01-05 00:00', 'v1', 0.50),
  (5, 2, 10, TIMESTAMP '2026-01-03 00:00', 'v2', 0.90),
  (6, 2, 11, TIMESTAMP '2026-01-06 00:00', 'v2', NULL);
