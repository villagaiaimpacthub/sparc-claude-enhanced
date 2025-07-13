# 🗄️ Supabase Database Setup for SPARC

This guide will help you set up the required Supabase database tables for the SPARC autonomous development system.

## 📋 Prerequisites

1. **Supabase Account**: Create one at [supabase.com](https://supabase.com)
2. **New Project**: Create a new Supabase project
3. **API Keys**: Get your URL and anon key from Settings > API

## 🔧 Quick Setup

### Step 1: Create Supabase Project

1. Go to [supabase.com/dashboard](https://supabase.com/dashboard)
2. Click "New Project"
3. Choose organization and set project name
4. Wait for project to initialize (~2 minutes)

### Step 2: Get API Credentials

1. Go to **Settings > API** in your project
2. Copy these values:
   - **Project URL** (looks like: `https://xyz.supabase.co`)
   - **anon public** key (long JWT token)
   - **service_role** key (longer JWT token)

### Step 3: Create Database Tables

Go to **SQL Editor** in your Supabase dashboard and run this SQL:

```sql
-- SPARC Database Schema
-- Run this in your Supabase SQL Editor

-- Agent Executions Table
CREATE TABLE IF NOT EXISTS agent_executions (
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

-- SPARC Contexts Table
CREATE TABLE IF NOT EXISTS sparc_contexts (
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

-- Agent Tasks Table
CREATE TABLE IF NOT EXISTS agent_tasks (
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

-- Approval Queue Table
CREATE TABLE IF NOT EXISTS approval_queue (
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

-- Project Memory Table
CREATE TABLE IF NOT EXISTS project_memorys (
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

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_executions_namespace ON agent_executions(namespace);
CREATE INDEX IF NOT EXISTS idx_agent_executions_project ON agent_executions(project_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_agent ON agent_executions(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_executions_phase ON agent_executions(phase);

CREATE INDEX IF NOT EXISTS idx_sparc_contexts_namespace ON sparc_contexts(namespace);
CREATE INDEX IF NOT EXISTS idx_sparc_contexts_type_key ON sparc_contexts(context_type, context_key);

CREATE INDEX IF NOT EXISTS idx_agent_tasks_namespace ON agent_tasks(namespace);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_status ON agent_tasks(status);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_priority ON agent_tasks(priority);

CREATE INDEX IF NOT EXISTS idx_approval_queue_namespace ON approval_queue(namespace);
CREATE INDEX IF NOT EXISTS idx_approval_queue_status ON approval_queue(status);

CREATE INDEX IF NOT EXISTS idx_project_memorys_namespace ON project_memorys(namespace);
CREATE INDEX IF NOT EXISTS idx_project_memorys_type_key ON project_memorys(memory_type, memory_key);

-- Disable RLS for SPARC operations (allow all access)
ALTER TABLE agent_executions DISABLE ROW LEVEL SECURITY;
ALTER TABLE sparc_contexts DISABLE ROW LEVEL SECURITY;
ALTER TABLE agent_tasks DISABLE ROW LEVEL SECURITY;
ALTER TABLE approval_queue DISABLE ROW LEVEL SECURITY;
ALTER TABLE project_memorys DISABLE ROW LEVEL SECURITY;
```

### Step 4: Verify Setup

After running the SQL, you should see 5 new tables in your **Table Editor**:
- `agent_executions`
- `sparc_contexts`
- `agent_tasks`
- `approval_queue`
- `project_memorys`

## 🔐 Security Configuration

### Option 1: Disable RLS (Recommended for SPARC)

RLS (Row Level Security) is already disabled in the setup SQL above. This allows the SPARC agents full access to operate.

### Option 2: Enable RLS with Permissive Policies (Advanced)

If you prefer to keep RLS enabled, run this additional SQL:

```sql
-- Enable RLS
ALTER TABLE agent_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE sparc_contexts ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_memorys ENABLE ROW LEVEL SECURITY;

-- Create permissive policies for anon role
CREATE POLICY "Allow all operations on agent_executions" ON agent_executions
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on sparc_contexts" ON sparc_contexts
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on agent_tasks" ON agent_tasks
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on approval_queue" ON approval_queue
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on project_memorys" ON project_memorys
    FOR ALL USING (true) WITH CHECK (true);
```

## 🧪 Test Your Setup

You can test your Supabase connection using this Python script:

```python
import requests
import json

# Your Supabase credentials
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key-here"

headers = {
    "apikey": SUPABASE_KEY,
    "Content-Type": "application/json"
}

# Test insert
test_data = {
    "namespace": "test_setup",
    "project_id": "test_project",
    "agent_name": "setup_test_agent",
    "phase": "testing",
    "execution_type": "setup_verification",
    "status": "completed",
    "input_data": {"test": "setup"},
    "output_data": {"result": "success"},
    "execution_time_ms": 100
}

response = requests.post(
    f"{SUPABASE_URL}/rest/v1/agent_executions",
    headers=headers,
    json=test_data
)

if response.status_code == 201:
    print("✅ Supabase setup successful!")
    print("✅ Tables created and accessible")
else:
    print("❌ Setup failed:")
    print(f"Status: {response.status_code}")
    print(f"Error: {response.text}")
```

## 🔄 Environment Configuration

After setting up Supabase, update your project's `.env` file:

```bash
# Database Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-key-here

# Vector Database
QDRANT_URL=http://localhost:6336
QDRANT_API_KEY=

# Project Configuration
PROJECT_NAMESPACE=your_project_namespace
```

## 🚨 Troubleshooting

### Common Issues

**1. "new row violates row-level security policy"**
- Solution: Make sure you ran the RLS disable commands in the SQL setup

**2. "relation does not exist"**
- Solution: Verify all tables were created in the SQL Editor

**3. "Invalid API key"**
- Solution: Double-check your anon key from Settings > API

**4. Connection timeout**
- Solution: Verify your project URL is correct and project is not paused

### Getting Help

1. Check Supabase project logs in the Dashboard
2. Verify table creation in Table Editor
3. Test API connection with the test script above
4. Check `.env` file configuration

## 🎯 Next Steps

Once Supabase is configured:

1. **Update your `.env`** with the credentials
2. **Run `sparc-init`** to verify connectivity
3. **Use `/sparc`** in Claude Code for autonomous development
4. **Monitor usage** in your Supabase dashboard

Your SPARC system now has unlimited external memory for agent coordination and context management!