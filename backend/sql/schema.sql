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
    scale_type VARCHAR(20) DEFAULT 'natural',
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


-- Table: public.ai_practice_plans

-- DROP TABLE IF EXISTS public.ai_practice_plans;

CREATE TABLE IF NOT EXISTS public.ai_practice_plans
(
    practice_id uuid NOT NULL,
    user_id character varying(255) COLLATE pg_catalog."default" NOT NULL,
    generated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    practice_plan text COLLATE pg_catalog."default" NOT NULL,
    executed_session_id character varying(255) COLLATE pg_catalog."default",
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ai_practice_plans_pkey PRIMARY KEY (practice_id)
)

TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_practice_plans_user_time
ON public.ai_practice_plans (user_id, generated_at DESC);

CREATE INDEX IF NOT EXISTS idx_practice_plans_execution
ON public.ai_practice_plans (executed_session_id);
