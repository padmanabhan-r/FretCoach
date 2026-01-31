-- Add user_configs table for user-specific session configurations
CREATE TABLE IF NOT EXISTS fretcoach.user_configs
(
    user_id VARCHAR(255) NOT NULL,
    enabled_metrics JSONB NOT NULL DEFAULT '{"pitch_accuracy": true, "scale_conformity": true, "timing_stability": true}'::jsonb,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT user_configs_pkey PRIMARY KEY (user_id)
);

-- Enable RLS
ALTER TABLE fretcoach.user_configs ENABLE ROW LEVEL SECURITY;

-- Allow all operations for service role
CREATE POLICY "Allow all for service role" ON fretcoach.user_configs
    FOR ALL USING (true) WITH CHECK (true);
