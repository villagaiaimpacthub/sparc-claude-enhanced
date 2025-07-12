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

-- Create agent_tasks table for task queue
CREATE TABLE IF NOT EXISTS agent_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    from_agent VARCHAR(255),
    to_agent VARCHAR(255) NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    task_payload JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    result JSONB,
    error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create project_memorys table for file tracking
CREATE TABLE IF NOT EXISTS project_memorys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    memory_type VARCHAR(100) DEFAULT 'general',
    brief_description TEXT,
    elements_description TEXT,
    rationale TEXT,
    version INTEGER DEFAULT 1,
    content_hash VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create sparc_file_changes table for hook tracking
CREATE TABLE IF NOT EXISTS sparc_file_changes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    tool_used VARCHAR(50) NOT NULL,
    session_id VARCHAR(255),
    content_preview TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create approvals table for human approvals
CREATE TABLE IF NOT EXISTS approvals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    approval_type VARCHAR(100) NOT NULL,
    context JSONB NOT NULL,
    message TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    response JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
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
CREATE INDEX IF NOT EXISTS idx_agent_tasks_namespace ON agent_tasks(namespace);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_to_agent ON agent_tasks(to_agent);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_status ON agent_tasks(status);
CREATE INDEX IF NOT EXISTS idx_project_memorys_namespace ON project_memorys(namespace);
CREATE INDEX IF NOT EXISTS idx_sparc_file_changes_namespace ON sparc_file_changes(namespace);
CREATE INDEX IF NOT EXISTS idx_approvals_namespace ON approvals(namespace);
CREATE INDEX IF NOT EXISTS idx_projects_namespace ON sparc_projects(namespace);
CREATE INDEX IF NOT EXISTS idx_conversations_namespace ON sparc_conversations(namespace);
CREATE INDEX IF NOT EXISTS idx_artifacts_namespace ON sparc_artifacts(namespace);

-- Enable Row Level Security (RLS)
ALTER TABLE sparc_agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_memorys ENABLE ROW LEVEL SECURITY;
ALTER TABLE sparc_file_changes ENABLE ROW LEVEL SECURITY;
ALTER TABLE approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE sparc_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE sparc_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE sparc_artifacts ENABLE ROW LEVEL SECURITY;

-- Create policies (allow all operations for now - customize as needed)
CREATE POLICY "Allow all operations on agents" ON sparc_agents FOR ALL USING (true);
CREATE POLICY "Allow all operations on agent_tasks" ON agent_tasks FOR ALL USING (true);
CREATE POLICY "Allow all operations on project_memorys" ON project_memorys FOR ALL USING (true);
CREATE POLICY "Allow all operations on sparc_file_changes" ON sparc_file_changes FOR ALL USING (true);
CREATE POLICY "Allow all operations on approvals" ON approvals FOR ALL USING (true);
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

CREATE TRIGGER update_project_memorys_updated_at BEFORE UPDATE ON project_memorys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON sparc_projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_artifacts_updated_at BEFORE UPDATE ON sparc_artifacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Success message
SELECT 'SPARC database setup complete! 🚀' AS status;