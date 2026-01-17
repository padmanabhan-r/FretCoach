-- FretCoach SQL Queries
-- Named queries loaded at runtime by SessionLogger

-- name: check_new_schema
-- Check if sessions table has the new schema with total_inscale_notes column
SELECT column_name FROM information_schema.columns
WHERE table_name = 'sessions' AND column_name = 'total_inscale_notes';

-- name: check_scale_type_column
-- Check if sessions table has the scale_type column
SELECT column_name FROM information_schema.columns
WHERE table_name = 'sessions' AND column_name = 'scale_type';

-- name: add_scale_type_column
-- Add scale_type column if it doesn't exist
ALTER TABLE sessions ADD COLUMN scale_type VARCHAR(20) DEFAULT 'diatonic';

-- name: insert_session
-- Insert a completed session into the database
INSERT INTO sessions
(session_id, user_id, start_timestamp, end_timestamp,
 pitch_accuracy, scale_conformity, timing_stability,
 scale_chosen, scale_type, sensitivity, strictness,
 total_notes_played, correct_notes_played, bad_notes_played,
 total_inscale_notes, duration_seconds, ambient_light_option)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);

-- name: get_session_stats
-- Retrieve session statistics by session_id
SELECT
    session_id, user_id, start_timestamp, end_timestamp,
    pitch_accuracy, scale_conformity, timing_stability,
    scale_chosen, scale_type, sensitivity, strictness,
    total_notes_played, correct_notes_played, bad_notes_played,
    total_inscale_notes, duration_seconds, ambient_light_option
FROM sessions
WHERE session_id = %s;

-- name: get_user_sessions
-- Retrieve recent sessions for a user
SELECT
    session_id, start_timestamp, end_timestamp, duration_seconds,
    scale_chosen, scale_type, pitch_accuracy, scale_conformity, timing_stability,
    total_notes_played, correct_notes_played, bad_notes_played
FROM sessions
WHERE user_id = %s
ORDER BY start_timestamp DESC
LIMIT %s;
