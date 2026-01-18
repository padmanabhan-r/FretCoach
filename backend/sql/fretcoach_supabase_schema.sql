/* ============================================================
   FretCoach Database Schema
   Target: Supabase PostgreSQL
   Safe for: service-role, text-to-SQL agents, backend APIs
   ============================================================ */

BEGIN;

-- ------------------------------------------------------------
-- Schema
-- ------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS fretcoach;

-- ------------------------------------------------------------
-- Table: fretcoach.sessions
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fretcoach.sessions
(
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,

    start_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    end_timestamp TIMESTAMP WITHOUT TIME ZONE,

    pitch_accuracy DOUBLE PRECISION,
    scale_conformity DOUBLE PRECISION,
    timing_stability DOUBLE PRECISION,

    scale_chosen VARCHAR(100) NOT NULL,
    sensitivity DOUBLE PRECISION NOT NULL,
    strictness DOUBLE PRECISION NOT NULL,

    total_notes_played INTEGER DEFAULT 0,
    correct_notes_played INTEGER DEFAULT 0,
    bad_notes_played INTEGER DEFAULT 0,
    total_inscale_notes INTEGER,

    duration_seconds DOUBLE PRECISION,
    ambient_light_option BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    scale_type VARCHAR(20) DEFAULT 'natural',

    CONSTRAINT sessions_pkey PRIMARY KEY (session_id, user_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_sessions_start_timestamp
ON fretcoach.sessions (start_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id
ON fretcoach.sessions (user_id);

-- Enable RLS (no policies yet)
ALTER TABLE fretcoach.sessions ENABLE ROW LEVEL SECURITY;

-- ------------------------------------------------------------
-- Table: fretcoach.ai_practice_plans
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fretcoach.ai_practice_plans
(
    practice_id UUID NOT NULL,
    user_id VARCHAR(255) NOT NULL,

    generated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    practice_plan TEXT NOT NULL,

    executed_session_id VARCHAR(255),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ai_practice_plans_pkey PRIMARY KEY (practice_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_practice_plans_execution
ON fretcoach.ai_practice_plans (executed_session_id);

CREATE INDEX IF NOT EXISTS idx_practice_plans_user_time
ON fretcoach.ai_practice_plans (user_id, generated_at DESC);

-- Enable RLS with permissive policies
ALTER TABLE fretcoach.ai_practice_plans ENABLE ROW LEVEL SECURITY;

-- Allow all operations for authenticated users (or use service role)
CREATE POLICY "Allow all for service role" ON fretcoach.ai_practice_plans
    FOR ALL USING (true) WITH CHECK (true);

COMMIT;
