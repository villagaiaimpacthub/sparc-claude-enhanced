-- SPARC Supabase Schema with Namespace-based Multi-tenancy
-- Run this SQL in your Supabase SQL Editor

-- Project memories table (namespace-based)
CREATE TABLE IF NOT EXISTS project_memorys (
    id BIGSERIAL PRIMARY KEY,
    namespace TEXT NOT NULL,
    project_id TEXT, -- Legacy compatibility 
    file_path TEXT NOT NULL,
    memory_type TEXT,
    brief_description TEXT,
    elements_description TEXT,
    rationale TEXT,
    imports TEXT,
    exports TEXT,
    functions TEXT,
    classes TEXT,
    version INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated_timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- SPARC contexts table (namespace-based)
CREATE TABLE IF NOT EXISTS sparc_contexts (
    id BIGSERIAL PRIMARY KEY,
    namespace TEXT NOT NULL,
    project_id TEXT, -- Legacy compatibility
    context_type TEXT NOT NULL,
    context_key TEXT NOT NULL,
    agent_name TEXT,
    phase TEXT,
    content JSONB NOT NULL,
    token_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent tasks table (namespace-based)
CREATE TABLE IF NOT EXISTS agent_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    namespace TEXT NOT NULL,
    project_id TEXT, -- Legacy compatibility
    from_agent TEXT NOT NULL,
    to_agent TEXT NOT NULL,
    task_type TEXT NOT NULL,
    priority INTEGER DEFAULT 1,
    status TEXT DEFAULT 'pending',
    task_payload JSONB NOT NULL,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- Agent executions table (namespace-based)
CREATE TABLE IF NOT EXISTS agent_executions (
    id BIGSERIAL PRIMARY KEY,
    namespace TEXT NOT NULL,
    project_id TEXT, -- Legacy compatibility
    agent_name TEXT NOT NULL,
    phase TEXT NOT NULL,
    execution_type TEXT NOT NULL,
    input_data JSONB,
    output_data JSONB,
    status TEXT NOT NULL,
    error_message TEXT,
    execution_time_ms INTEGER,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Approval queue table (namespace-based)
CREATE TABLE IF NOT EXISTS approval_queue (
    id BIGSERIAL PRIMARY KEY,
    namespace TEXT NOT NULL,
    project_id TEXT, -- Legacy compatibility
    phase TEXT NOT NULL,
    requesting_agent TEXT NOT NULL,
    approval_type TEXT NOT NULL,
    artifacts JSONB NOT NULL,
    summary TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    approved_by TEXT
);

-- Create indexes for better performance (namespace-based)
CREATE INDEX IF NOT EXISTS idx_project_memorys_namespace ON project_memorys(namespace);
CREATE INDEX IF NOT EXISTS idx_project_memorys_project_id ON project_memorys(project_id); -- Legacy
CREATE INDEX IF NOT EXISTS idx_sparc_contexts_namespace ON sparc_contexts(namespace);
CREATE INDEX IF NOT EXISTS idx_sparc_contexts_project_id ON sparc_contexts(project_id); -- Legacy
CREATE INDEX IF NOT EXISTS idx_agent_tasks_namespace ON agent_tasks(namespace);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_project_id ON agent_tasks(project_id); -- Legacy
CREATE INDEX IF NOT EXISTS idx_agent_tasks_to_agent ON agent_tasks(to_agent);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_status ON agent_tasks(status);
CREATE INDEX IF NOT EXISTS idx_agent_executions_namespace ON agent_executions(namespace);
CREATE INDEX IF NOT EXISTS idx_agent_executions_project_id ON agent_executions(project_id); -- Legacy
CREATE INDEX IF NOT EXISTS idx_approval_queue_namespace ON approval_queue(namespace);
CREATE INDEX IF NOT EXISTS idx_approval_queue_project_id ON approval_queue(project_id); -- Legacy
CREATE INDEX IF NOT EXISTS idx_approval_queue_status ON approval_queue(status);

-- Enable Row Level Security (RLS)
ALTER TABLE project_memorys ENABLE ROW LEVEL SECURITY;
ALTER TABLE sparc_contexts ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_queue ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (allow all for service role, restrict for others)
-- Note: Adjust these policies based on your security requirements

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Allow all for service role" ON project_memorys;
DROP POLICY IF EXISTS "Allow all for service role" ON sparc_contexts;
DROP POLICY IF EXISTS "Allow all for service role" ON agent_tasks;
DROP POLICY IF EXISTS "Allow all for service role" ON agent_executions;
DROP POLICY IF EXISTS "Allow all for service role" ON approval_queue;

-- Project memories policies
CREATE POLICY "Allow all for service role" ON project_memorys
    FOR ALL USING (auth.role() = 'service_role');

-- SPARC contexts policies  
CREATE POLICY "Allow all for service role" ON sparc_contexts
    FOR ALL USING (auth.role() = 'service_role');

-- Agent tasks policies
CREATE POLICY "Allow all for service role" ON agent_tasks
    FOR ALL USING (auth.role() = 'service_role');

-- Agent executions policies
CREATE POLICY "Allow all for service role" ON agent_executions
    FOR ALL USING (auth.role() = 'service_role');

-- Approval queue policies
CREATE POLICY "Allow all for service role" ON approval_queue
    FOR ALL USING (auth.role() = 'service_role');

-- Optional: Create a function to automatically update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_agent_tasks_updated_at BEFORE UPDATE ON agent_tasks 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create a view for easy namespace-based queries
CREATE OR REPLACE VIEW namespace_project_summary AS
SELECT 
    namespace,
    COUNT(DISTINCT agent_name) as active_agents,
    COUNT(*) as total_contexts,
    MAX(created_at) as last_activity
FROM sparc_contexts 
GROUP BY namespace;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;