-- Fix existing table schemas that need additional columns
-- Execute this in Supabase SQL editor as a follow-up

-- Fix agent_tasks table - add missing columns
ALTER TABLE agent_tasks 
ADD COLUMN IF NOT EXISTS task_data JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS change_type TEXT,
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed'));

-- Fix sparc_contexts table - add missing columns  
ALTER TABLE sparc_contexts
ADD COLUMN IF NOT EXISTS context_data JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- Fix sparc_file_changes table - add missing columns
ALTER TABLE sparc_file_changes 
ADD COLUMN IF NOT EXISTS change_type TEXT DEFAULT 'modify' CHECK (change_type IN ('create', 'modify', 'delete')),
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'failed'));

-- Fix sparc_projects table - add missing columns
ALTER TABLE sparc_projects
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'cancelled'));

-- Fix agent_executions table - make phase nullable or add default
ALTER TABLE agent_executions 
ALTER COLUMN phase DROP NOT NULL;

-- Alternative: Add default value for phase if you prefer
-- ALTER TABLE agent_executions 
-- ALTER COLUMN phase SET DEFAULT 'unknown';

-- Verify the changes work
SELECT 'agent_tasks columns' as table_name, 
       array_agg(column_name ORDER BY ordinal_position) as columns
FROM information_schema.columns 
WHERE table_name = 'agent_tasks' AND table_schema = 'public'
UNION ALL
SELECT 'sparc_contexts columns' as table_name, 
       array_agg(column_name ORDER BY ordinal_position) as columns
FROM information_schema.columns 
WHERE table_name = 'sparc_contexts' AND table_schema = 'public'
UNION ALL
SELECT 'sparc_file_changes columns' as table_name, 
       array_agg(column_name ORDER BY ordinal_position) as columns
FROM information_schema.columns 
WHERE table_name = 'sparc_file_changes' AND table_schema = 'public'
UNION ALL
SELECT 'sparc_projects columns' as table_name, 
       array_agg(column_name ORDER BY ordinal_position) as columns
FROM information_schema.columns 
WHERE table_name = 'sparc_projects' AND table_schema = 'public';