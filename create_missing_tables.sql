-- Create all missing SPARC tables with proper schemas
-- Execute this in Supabase SQL editor

-- 1. approval_requests table
CREATE TABLE IF NOT EXISTS approval_requests (
    id SERIAL PRIMARY KEY,
    project_id TEXT,
    phase TEXT NOT NULL,
    request_data JSONB NOT NULL DEFAULT '{}',
    message TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    requested_by TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. bmo_verifications table
CREATE TABLE IF NOT EXISTS bmo_verifications (
    id SERIAL PRIMARY KEY,
    project_id TEXT,
    verification_type TEXT NOT NULL,
    behavior_model JSONB NOT NULL DEFAULT '{}',
    oracle_results JSONB NOT NULL DEFAULT '{}',
    triangulation_score DECIMAL(3,2) CHECK (triangulation_score >= 0 AND triangulation_score <= 1),
    verification_status TEXT NOT NULL CHECK (verification_status IN ('passed', 'failed', 'pending')),
    results JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. memory_insights table
CREATE TABLE IF NOT EXISTS memory_insights (
    id SERIAL PRIMARY KEY,
    namespace TEXT NOT NULL,
    insight_type TEXT NOT NULL,
    content TEXT NOT NULL,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    application_count INTEGER DEFAULT 0,
    success_rate DECIMAL(3,2) CHECK (success_rate >= 0 AND success_rate <= 1),
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. cross_project_learnings table
CREATE TABLE IF NOT EXISTS cross_project_learnings (
    id SERIAL PRIMARY KEY,
    learning_type TEXT NOT NULL,
    source_projects TEXT[] DEFAULT '{}',
    pattern_description TEXT NOT NULL,
    applicability_score DECIMAL(3,2) CHECK (applicability_score >= 0 AND applicability_score <= 1),
    usage_frequency INTEGER DEFAULT 0,
    success_contexts JSONB DEFAULT '[]',
    failure_contexts JSONB DEFAULT '[]',
    recommendation TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. quality_benchmarks table
CREATE TABLE IF NOT EXISTS quality_benchmarks (
    id SERIAL PRIMARY KEY,
    benchmark_type TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    target_value DECIMAL(10,2),
    current_average DECIMAL(10,2),
    trend_direction TEXT CHECK (trend_direction IN ('improving', 'declining', 'stable')),
    measurement_count INTEGER DEFAULT 0,
    industry_percentile DECIMAL(5,2),
    context_tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. user_preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_identifier TEXT NOT NULL,
    preference_type TEXT NOT NULL,
    preference_value JSONB NOT NULL DEFAULT '{}',
    confidence_level DECIMAL(3,2) CHECK (confidence_level >= 0 AND confidence_level <= 1),
    learned_from_interactions INTEGER DEFAULT 0,
    last_reinforced TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_identifier, preference_type)
);

-- 7. failure_patterns table
CREATE TABLE IF NOT EXISTS failure_patterns (
    id SERIAL PRIMARY KEY,
    pattern_type TEXT NOT NULL,
    failure_signature TEXT NOT NULL,
    occurrence_count INTEGER DEFAULT 1,
    severity_level TEXT NOT NULL CHECK (severity_level IN ('low', 'medium', 'high', 'critical')),
    resolution_strategy TEXT,
    prevention_measures TEXT[] DEFAULT '{}',
    affected_components TEXT[] DEFAULT '{}',
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add missing columns to existing tables

-- Fix sparc_projects table
ALTER TABLE sparc_projects 
ADD COLUMN IF NOT EXISTS project_goal TEXT,
ADD COLUMN IF NOT EXISTS completion_percentage DECIMAL(5,2) DEFAULT 0.0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
ADD COLUMN IF NOT EXISTS quality_score DECIMAL(3,2) DEFAULT 0.0 CHECK (quality_score >= 0 AND quality_score <= 1),
ADD COLUMN IF NOT EXISTS estimated_completion TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS start_date TIMESTAMPTZ DEFAULT NOW();

-- Fix sparc_file_changes table 
ALTER TABLE sparc_file_changes 
ADD COLUMN IF NOT EXISTS agent_name TEXT,
ADD COLUMN IF NOT EXISTS content_preview TEXT,
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_approval_requests_project_id ON approval_requests(project_id);
CREATE INDEX IF NOT EXISTS idx_approval_requests_status ON approval_requests(status);
CREATE INDEX IF NOT EXISTS idx_bmo_verifications_project_id ON bmo_verifications(project_id);
CREATE INDEX IF NOT EXISTS idx_memory_insights_namespace ON memory_insights(namespace);
CREATE INDEX IF NOT EXISTS idx_memory_insights_type ON memory_insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_cross_project_learnings_type ON cross_project_learnings(learning_type);
CREATE INDEX IF NOT EXISTS idx_quality_benchmarks_type ON quality_benchmarks(benchmark_type);
CREATE INDEX IF NOT EXISTS idx_user_preferences_user ON user_preferences(user_identifier);
CREATE INDEX IF NOT EXISTS idx_failure_patterns_type ON failure_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_failure_patterns_severity ON failure_patterns(severity_level);

-- Add RLS policies (if needed for security)
-- ALTER TABLE approval_requests ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE bmo_verifications ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE memory_insights ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE cross_project_learnings ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE quality_benchmarks ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE failure_patterns ENABLE ROW LEVEL SECURITY;

-- Grant necessary permissions
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;