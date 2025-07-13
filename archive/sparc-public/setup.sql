-- SPARC One-Click Database Setup
-- Copy and paste this entire script into your Supabase SQL Editor
-- Click "Run" once and you're done!

CREATE TABLE agent_executions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    namespace TEXT NOT NULL,
    project_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    phase TEXT NOT NULL,
    execution_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    input_data JSONB,
    output_data JSONB,
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE sparc_contexts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    namespace TEXT NOT NULL,
    project_id TEXT NOT NULL,
    context_type TEXT NOT NULL,
    context_key TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    phase TEXT NOT NULL,
    content JSONB NOT NULL,
    token_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(namespace, context_type, context_key)
);

CREATE TABLE agent_tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    namespace TEXT NOT NULL,
    project_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    phase TEXT NOT NULL,
    task_type TEXT NOT NULL,
    task_data JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    dependencies TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE approval_queue (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    namespace TEXT NOT NULL,
    project_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    phase TEXT NOT NULL,
    approval_type TEXT NOT NULL,
    request_data JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    approved_by TEXT,
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE project_memorys (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    namespace TEXT NOT NULL,
    project_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    memory_key TEXT NOT NULL,
    content JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(namespace, memory_type, memory_key)
);

-- Performance indexes
CREATE INDEX idx_agent_executions_namespace ON agent_executions(namespace);
CREATE INDEX idx_sparc_contexts_namespace ON sparc_contexts(namespace);
CREATE INDEX idx_agent_tasks_namespace ON agent_tasks(namespace);
CREATE INDEX idx_approval_queue_namespace ON approval_queue(namespace);
CREATE INDEX idx_project_memorys_namespace ON project_memorys(namespace);

-- Allow full access for SPARC agents
ALTER TABLE agent_executions DISABLE ROW LEVEL SECURITY;
ALTER TABLE sparc_contexts DISABLE ROW LEVEL SECURITY;
ALTER TABLE agent_tasks DISABLE ROW LEVEL SECURITY;
ALTER TABLE approval_queue DISABLE ROW LEVEL SECURITY;
ALTER TABLE project_memorys DISABLE ROW LEVEL SECURITY;