-- SPARC Database Setup
-- Run this in your Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create agents table for SPARC agents
CREATE TABLE IF NOT EXISTS sparc_agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    agent_type VARCHAR(100) NOT NULL,
    agent_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'idle',
    current_task TEXT,
    memory JSONB DEFAULT '{}',
    context_embeddings vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create projects table
CREATE TABLE IF NOT EXISTS sparc_projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) UNIQUE NOT NULL,
    project_name VARCHAR(255) NOT NULL,
    project_path TEXT,
    current_phase VARCHAR(100) DEFAULT 'goal_clarification',
    goal TEXT,
    progress JSONB DEFAULT '{}',
    state JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create conversations table for agent interactions
CREATE TABLE IF NOT EXISTS sparc_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    agent_from VARCHAR(255),
    agent_to VARCHAR(255),
    message_type VARCHAR(100),
    content TEXT,
    metadata JSONB DEFAULT '{}',
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create artifacts table for generated code/docs
CREATE TABLE IF NOT EXISTS sparc_artifacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    artifact_type VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    content TEXT,
    metadata JSONB DEFAULT '{}',
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_agents_namespace ON sparc_agents(namespace);
CREATE INDEX IF NOT EXISTS idx_agents_type ON sparc_agents(agent_type);
CREATE INDEX IF NOT EXISTS idx_projects_namespace ON sparc_projects(namespace);
CREATE INDEX IF NOT EXISTS idx_conversations_namespace ON sparc_conversations(namespace);
CREATE INDEX IF NOT EXISTS idx_artifacts_namespace ON sparc_artifacts(namespace);

-- Enable Row Level Security (RLS)
ALTER TABLE sparc_agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE sparc_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE sparc_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE sparc_artifacts ENABLE ROW LEVEL SECURITY;

-- Create policies (allow all operations for now - customize as needed)
CREATE POLICY "Allow all operations on agents" ON sparc_agents FOR ALL USING (true);
CREATE POLICY "Allow all operations on projects" ON sparc_projects FOR ALL USING (true);
CREATE POLICY "Allow all operations on conversations" ON sparc_conversations FOR ALL USING (true);
CREATE POLICY "Allow all operations on artifacts" ON sparc_artifacts FOR ALL USING (true);

-- Create functions for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for auto-updating timestamps
CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON sparc_agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON sparc_projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_artifacts_updated_at BEFORE UPDATE ON sparc_artifacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Success message
SELECT 'SPARC database setup complete! 🚀' AS status;