DROP VIEW IF EXISTS user_spend;
DROP VIEW IF EXISTS category_spend;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS orders;
CREATE TABLE orders(order_id INTEGER, user_id INTEGER, order_ts TIMESTAMP, status VARCHAR);
CREATE TABLE order_items(order_id INTEGER, line_id INTEGER, item_id INTEGER, quantity INTEGER, unit_price DOUBLE);
CREATE TABLE items(item_id INTEGER, category VARCHAR, list_price DOUBLE);
-- Order 1 was ingested twice (exact duplicate header row). Order 6 is still pending (NULL status).
INSERT INTO orders VALUES
  (1, 1, TIMESTAMP '2026-01-01 10:00', 'paid'),
  (1, 1, TIMESTAMP '2026-01-01 10:00', 'paid'),
  (2, 1, TIMESTAMP '2026-01-02 10:00', 'cancelled'),
  (3, 1, TIMESTAMP '2026-01-03 10:00', 'shipped'),
  (4, 2, TIMESTAMP '2026-01-03 11:00', 'paid'),
  (5, 2, TIMESTAMP '2026-01-04 11:00', 'returned'),
  (6, 3, TIMESTAMP '2026-01-05 12:00', NULL),
  (7, 4, TIMESTAMP '2026-01-05 13:00', 'cancelled'),
  (8, 5, TIMESTAMP '2026-01-06 09:00', 'paid');
INSERT INTO items VALUES (10, 'apparel', 5.0), (11, 'apparel', 4.0), (12, 'books', 7.0), (13, 'books', 3.0);
INSERT INTO order_items VALUES
  (1, 1, 10, 2, 5.0),
  (1, 2, 11, 1, 4.0),
  (1, 3, 10, 1, 4.5),
  (2, 1, 12, 100, 7.0),
  (3, 1, 10, 1, 5.0),
  (3, 2, 12, 2, 6.0),
  (4, 1, 12, 1, 7.0),
  (4, 2, 13, 3, 3.0),
  (5, 1, 11, 10, 4.0),
  (6, 1, 13, 2, 2.5),
  (6, 2, 99, 1, 8.0),
  (7, 1, 10, 50, 5.0);
