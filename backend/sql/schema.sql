-- FretCoach Database Schema
-- Sessions table for storing practice session data

CREATE TABLE IF NOT EXISTS sessions (
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    start_timestamp TIMESTAMP NOT NULL,
    end_timestamp TIMESTAMP,
    pitch_accuracy FLOAT,
    scale_conformity FLOAT,
    timing_stability FLOAT,
    scale_chosen VARCHAR(100) NOT NULL,
    scale_type VARCHAR(20) DEFAULT 'diatonic',
    sensitivity FLOAT NOT NULL,
    strictness FLOAT NOT NULL,
    total_notes_played INT DEFAULT 0,
    correct_notes_played INT DEFAULT 0,
    bad_notes_played INT DEFAULT 0,
    total_inscale_notes INT,
    duration_seconds FLOAT,
    ambient_light_option BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (session_id, user_id)
);

-- Indices for better query performance
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_start_timestamp ON sessions(start_timestamp DESC);
