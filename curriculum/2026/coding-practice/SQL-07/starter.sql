-- SQL-07: Deduplication / NULL Semantics
-- Tables: users(user_id), items(item_id),
--         events(event_id, user_id, item_id, event_type, event_ts)
-- user_id and item_id in `events` can be NULL (anonymous traffic, non-item clicks).
--
-- 1. deduped_events(event_id, user_id, item_id, event_type, event_ts):
--    - exact duplicate rows appear once;
--    - an event is a near duplicate, and is dropped, when the immediately preceding event
--      with the same (user_id, item_id, event_type) is at most 5 seconds earlier (a gap of
--      exactly 5 seconds is a duplicate). NULL keys group together like any other value.
--    - among events with the same key and the same event_ts, keep the lowest event_id.
-- 2. never_clicked(user_id): users in `users` with no click in deduped_events.
-- 3. items_without_clicks(item_id): items in `items` with at least one impression and no
--    click in deduped_events.
CREATE OR REPLACE VIEW deduped_events AS
SELECT * FROM events WHERE FALSE; -- TODO

CREATE OR REPLACE VIEW never_clicked AS
SELECT NULL::INTEGER AS user_id WHERE FALSE; -- TODO

CREATE OR REPLACE VIEW items_without_clicks AS
SELECT NULL::INTEGER AS item_id WHERE FALSE; -- TODO
