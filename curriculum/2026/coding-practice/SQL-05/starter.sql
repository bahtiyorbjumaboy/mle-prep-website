-- SQL-05: Sessionization
-- Table: events(event_id, user_id, session_id, event_ts, event_type)
--
-- Ignore the stored session_id. A session is a maximal run of one user's events, in
-- event_ts order, where consecutive events are at most 30 minutes apart: a gap of exactly
-- 30:00 stays in the same session; any longer gap (even by one second) starts a new one.
--
-- Create session_summary with one row per (user_id, session_number):
--   session_number                      1, 2, ... per user in time order
--   session_start, session_end          first / last event_ts in the session
--   event_count                         events in the session
--   has_purchase                        TRUE if any event_type = 'purchase'
--   gap_from_previous_session_minutes   (session_start - previous session's session_end)
--                                       in minutes as a DOUBLE, including seconds;
--                                       NULL for a user's first session
CREATE OR REPLACE VIEW session_summary AS
SELECT NULL::INTEGER AS user_id, NULL::BIGINT AS session_number, NULL::TIMESTAMP AS session_start,
       NULL::TIMESTAMP AS session_end, NULL::BIGINT AS event_count, NULL::BOOLEAN AS has_purchase,
       NULL::DOUBLE AS gap_from_previous_session_minutes
WHERE FALSE; -- TODO
