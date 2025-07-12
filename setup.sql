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

-- Interactive conversations tracking
CREATE TABLE IF NOT EXISTS interactive_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    agent_name VARCHAR(255) NOT NULL,
    question_data JSONB NOT NULL,
    user_response JSONB,
    ai_verifiable_criteria JSONB NOT NULL,
    verification_result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    responded_at TIMESTAMP WITH TIME ZONE
);

-- Cognitive triangulation results
CREATE TABLE IF NOT EXISTS triangulation_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    artifact_path TEXT NOT NULL,
    phase VARCHAR(100) NOT NULL,
    viewpoint_agent VARCHAR(255) NOT NULL,
    perspective VARCHAR(100) NOT NULL,
    validation_result JSONB NOT NULL,
    triangulation_session_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- BMO intent tracking
CREATE TABLE IF NOT EXISTS intent_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    intent_type VARCHAR(100) NOT NULL,  -- "goal", "preference", "anti_goal", "constraint"
    intent_data JSONB NOT NULL,
    confidence_score FLOAT DEFAULT 1.0,
    source VARCHAR(100) NOT NULL,  -- "explicit", "inferred", "custom_answer"
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Test oracle criteria
CREATE TABLE IF NOT EXISTS test_oracle_criteria (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    phase VARCHAR(100) NOT NULL,
    original_goal TEXT NOT NULL,
    verifiable_criteria JSONB NOT NULL,
    success_examples JSONB,
    failure_examples JSONB,
    glass_box_tests JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Perfect prompts storage
CREATE TABLE IF NOT EXISTS perfect_prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    agent_name VARCHAR(255) NOT NULL,
    task_id VARCHAR(255) NOT NULL,
    prompt_content TEXT NOT NULL,
    context_data JSONB,
    oracle_criteria JSONB,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    executed_at TIMESTAMP WITH TIME ZONE,
    execution_result JSONB
);

-- Add indexes for new tables
CREATE INDEX IF NOT EXISTS idx_interactive_conversations_namespace ON interactive_conversations(namespace);
CREATE INDEX IF NOT EXISTS idx_triangulation_results_namespace ON triangulation_results(namespace);
CREATE INDEX IF NOT EXISTS idx_triangulation_session ON triangulation_results(triangulation_session_id);
CREATE INDEX IF NOT EXISTS idx_intent_tracking_namespace ON intent_tracking(namespace);
CREATE INDEX IF NOT EXISTS idx_test_oracle_namespace ON test_oracle_criteria(namespace);
CREATE INDEX IF NOT EXISTS idx_perfect_prompts_namespace ON perfect_prompts(namespace);
CREATE INDEX IF NOT EXISTS idx_perfect_prompts_task ON perfect_prompts(task_id);

-- RLS policies for new tables
ALTER TABLE interactive_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE triangulation_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE intent_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_oracle_criteria ENABLE ROW LEVEL SECURITY;
ALTER TABLE perfect_prompts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations on interactive_conversations" ON interactive_conversations FOR ALL USING (true);
CREATE POLICY "Allow all operations on triangulation_results" ON triangulation_results FOR ALL USING (true);
CREATE POLICY "Allow all operations on intent_tracking" ON intent_tracking FOR ALL USING (true);
CREATE POLICY "Allow all operations on test_oracle_criteria" ON test_oracle_criteria FOR ALL USING (true);
CREATE POLICY "Allow all operations on perfect_prompts" ON perfect_prompts FOR ALL USING (true);

-- Agent Communication System Tables

-- Agent messages for inter-agent communication
CREATE TABLE IF NOT EXISTS agent_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id VARCHAR(255) UNIQUE NOT NULL,
    namespace VARCHAR(255) NOT NULL,
    from_agent VARCHAR(255) NOT NULL,
    to_agent VARCHAR(255) NOT NULL,
    message_type VARCHAR(100) NOT NULL,  -- task_delegation, completion_signal, etc.
    priority VARCHAR(50) NOT NULL,  -- critical, high, medium, low
    phase VARCHAR(100) NOT NULL,  -- goal_clarification, specification, architecture, etc.
    subject TEXT NOT NULL,
    content JSONB NOT NULL,
    attachments JSONB DEFAULT '[]',
    workflow_context JSONB DEFAULT '{}',
    parent_message_id VARCHAR(255),
    requires_response BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP WITH TIME ZONE,
    verifiable_criteria JSONB DEFAULT '[]',
    intent_alignment_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    acknowledged_at TIMESTAMP WITH TIME ZONE
);

-- Agent responses to messages
CREATE TABLE IF NOT EXISTS agent_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    response_id VARCHAR(255) UNIQUE NOT NULL,
    original_message_id VARCHAR(255) NOT NULL,
    namespace VARCHAR(255) NOT NULL,
    from_agent VARCHAR(255) NOT NULL,
    to_agent VARCHAR(255) NOT NULL,
    status VARCHAR(100) NOT NULL,  -- success, partial, error, acknowledged
    response_content JSONB NOT NULL,
    execution_results JSONB DEFAULT '{}',
    completion_score FLOAT DEFAULT 0.0,
    quality_metrics JSONB DEFAULT '{}',
    next_agent VARCHAR(255),
    workflow_continuation JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent error tracking
CREATE TABLE IF NOT EXISTS agent_errors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    error_source VARCHAR(255) NOT NULL,
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    error_context JSONB,
    stack_trace TEXT,
    recovery_attempted BOOLEAN DEFAULT FALSE,
    recovery_success BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Communication metrics tracking
CREATE TABLE IF NOT EXISTS communication_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    metric_type VARCHAR(100) NOT NULL,  -- message_count, response_time, success_rate, etc.
    metric_value FLOAT NOT NULL,
    measurement_window VARCHAR(50),  -- hourly, daily, weekly
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for agent communication tables
CREATE INDEX IF NOT EXISTS idx_agent_messages_namespace ON agent_messages(namespace);
CREATE INDEX IF NOT EXISTS idx_agent_messages_to_agent ON agent_messages(to_agent);
CREATE INDEX IF NOT EXISTS idx_agent_messages_from_agent ON agent_messages(from_agent);
CREATE INDEX IF NOT EXISTS idx_agent_messages_type ON agent_messages(message_type);
CREATE INDEX IF NOT EXISTS idx_agent_messages_phase ON agent_messages(phase);
CREATE INDEX IF NOT EXISTS idx_agent_messages_processed ON agent_messages(processed_at);
CREATE INDEX IF NOT EXISTS idx_agent_messages_expires ON agent_messages(expires_at);

CREATE INDEX IF NOT EXISTS idx_agent_responses_namespace ON agent_responses(namespace);
CREATE INDEX IF NOT EXISTS idx_agent_responses_original_msg ON agent_responses(original_message_id);
CREATE INDEX IF NOT EXISTS idx_agent_responses_from_agent ON agent_responses(from_agent);

CREATE INDEX IF NOT EXISTS idx_agent_errors_namespace ON agent_errors(namespace);
CREATE INDEX IF NOT EXISTS idx_agent_errors_source ON agent_errors(error_source);
CREATE INDEX IF NOT EXISTS idx_agent_errors_type ON agent_errors(error_type);
CREATE INDEX IF NOT EXISTS idx_agent_errors_resolved ON agent_errors(resolved_at);

CREATE INDEX IF NOT EXISTS idx_communication_metrics_namespace ON communication_metrics(namespace);
CREATE INDEX IF NOT EXISTS idx_communication_metrics_type ON communication_metrics(metric_type);

-- RLS policies for agent communication tables
ALTER TABLE agent_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_errors ENABLE ROW LEVEL SECURITY;
ALTER TABLE communication_metrics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations on agent_messages" ON agent_messages FOR ALL USING (true);
CREATE POLICY "Allow all operations on agent_responses" ON agent_responses FOR ALL USING (true);
CREATE POLICY "Allow all operations on agent_errors" ON agent_errors FOR ALL USING (true);
CREATE POLICY "Allow all operations on communication_metrics" ON communication_metrics FOR ALL USING (true);

-- Error Handling and Monitoring Tables

-- System alerts for error threshold monitoring
CREATE TABLE IF NOT EXISTS system_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    alert_type VARCHAR(100) NOT NULL,  -- error_threshold, performance, security, etc.
    severity VARCHAR(50) NOT NULL,  -- critical, high, medium, low
    message TEXT NOT NULL,
    error_count INTEGER,
    threshold INTEGER,
    triggered_by_error_id VARCHAR(255),
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(255),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Escalations for human intervention
CREATE TABLE IF NOT EXISTS escalations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    error_id VARCHAR(255) NOT NULL,
    escalation_reason TEXT NOT NULL,
    priority VARCHAR(50) NOT NULL,  -- urgent, high, medium, low
    assigned_to VARCHAR(255),
    status VARCHAR(100) DEFAULT 'pending',  -- pending, in_progress, resolved, dismissed
    resolution_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Error pattern analysis
CREATE TABLE IF NOT EXISTS error_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    pattern_key VARCHAR(255) NOT NULL,  -- category_errortype combination
    pattern_description TEXT,
    occurrence_count INTEGER DEFAULT 1,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    recovery_success_rate FLOAT DEFAULT 0.0,
    recommended_strategy VARCHAR(100),
    pattern_data JSONB
);

-- System health monitoring
CREATE TABLE IF NOT EXISTS system_health (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    component_name VARCHAR(255) NOT NULL,
    health_status VARCHAR(50) NOT NULL,  -- healthy, degraded, unhealthy, critical
    health_metrics JSONB,
    last_check TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status_since TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    check_interval INTEGER DEFAULT 300  -- seconds
);

-- Performance metrics for system monitoring
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    component_name VARCHAR(255) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_unit VARCHAR(50),
    measurement_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    aggregation_period VARCHAR(50) DEFAULT 'instant'  -- instant, 1min, 5min, 1hour, 1day
);

-- Add indexes for error handling and monitoring tables
CREATE INDEX IF NOT EXISTS idx_system_alerts_namespace ON system_alerts(namespace);
CREATE INDEX IF NOT EXISTS idx_system_alerts_severity ON system_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_system_alerts_acknowledged ON system_alerts(acknowledged);
CREATE INDEX IF NOT EXISTS idx_system_alerts_created ON system_alerts(created_at);

CREATE INDEX IF NOT EXISTS idx_escalations_namespace ON escalations(namespace);
CREATE INDEX IF NOT EXISTS idx_escalations_error_id ON escalations(error_id);
CREATE INDEX IF NOT EXISTS idx_escalations_status ON escalations(status);
CREATE INDEX IF NOT EXISTS idx_escalations_priority ON escalations(priority);

CREATE INDEX IF NOT EXISTS idx_error_patterns_namespace ON error_patterns(namespace);
CREATE INDEX IF NOT EXISTS idx_error_patterns_key ON error_patterns(pattern_key);
CREATE INDEX IF NOT EXISTS idx_error_patterns_last_seen ON error_patterns(last_seen);

CREATE INDEX IF NOT EXISTS idx_system_health_namespace ON system_health(namespace);
CREATE INDEX IF NOT EXISTS idx_system_health_component ON system_health(component_name);
CREATE INDEX IF NOT EXISTS idx_system_health_status ON system_health(health_status);
CREATE INDEX IF NOT EXISTS idx_system_health_check ON system_health(last_check);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_namespace ON performance_metrics(namespace);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_component ON performance_metrics(component_name);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_name ON performance_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(measurement_timestamp);

-- RLS policies for error handling and monitoring tables
ALTER TABLE system_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE escalations ENABLE ROW LEVEL SECURITY;
ALTER TABLE error_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_health ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_metrics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations on system_alerts" ON system_alerts FOR ALL USING (true);
CREATE POLICY "Allow all operations on escalations" ON escalations FOR ALL USING (true);
CREATE POLICY "Allow all operations on error_patterns" ON error_patterns FOR ALL USING (true);
CREATE POLICY "Allow all operations on system_health" ON system_health FOR ALL USING (true);
CREATE POLICY "Allow all operations on performance_metrics" ON performance_metrics FOR ALL USING (true);

-- Production Project State Management Tables

-- Project states for comprehensive project tracking
CREATE TABLE IF NOT EXISTS project_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id VARCHAR(255) NOT NULL,
    namespace VARCHAR(255) NOT NULL,
    state_data JSONB NOT NULL,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, version)
);

-- Project state change events for audit trail
CREATE TABLE IF NOT EXISTS project_state_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id VARCHAR(255) UNIQUE NOT NULL,
    project_id VARCHAR(255) NOT NULL,
    namespace VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,  -- project_created, state_updated, phase_transition, artifact_added, etc.
    old_state JSONB,
    new_state JSONB,
    triggered_by VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Project artifacts metadata
CREATE TABLE IF NOT EXISTS project_artifacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    artifact_id VARCHAR(255) UNIQUE NOT NULL,
    project_id VARCHAR(255) NOT NULL,
    namespace VARCHAR(255) NOT NULL,
    artifact_name VARCHAR(255) NOT NULL,
    artifact_type VARCHAR(100) NOT NULL,  -- documentation, code, configuration, etc.
    file_path TEXT NOT NULL,
    description TEXT,
    content_hash VARCHAR(64),
    file_size BIGINT,
    created_by_agent VARCHAR(255),
    phase_created VARCHAR(100),
    quality_score FLOAT DEFAULT 0.0,
    validation_status VARCHAR(50) DEFAULT 'pending',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Project milestones and quality gates
CREATE TABLE IF NOT EXISTS project_milestones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id VARCHAR(255) NOT NULL,
    namespace VARCHAR(255) NOT NULL,
    milestone_name VARCHAR(255) NOT NULL,
    phase VARCHAR(100) NOT NULL,
    milestone_type VARCHAR(100) NOT NULL,  -- quality_gate, deliverable, checkpoint
    criteria JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',  -- pending, in_progress, completed, failed
    completion_time TIMESTAMP WITH TIME ZONE,
    validation_results JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Project team and agent assignments
CREATE TABLE IF NOT EXISTS project_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id VARCHAR(255) NOT NULL,
    namespace VARCHAR(255) NOT NULL,
    agent_name VARCHAR(255) NOT NULL,
    assignment_type VARCHAR(100) NOT NULL,  -- owner, contributor, reviewer, observer
    phase VARCHAR(100),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assignment_status VARCHAR(50) DEFAULT 'active',  -- active, completed, reassigned, removed
    assignment_context JSONB DEFAULT '{}'
);

-- Project dependencies and relationships
CREATE TABLE IF NOT EXISTS project_dependencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id VARCHAR(255) NOT NULL,
    depends_on_project_id VARCHAR(255) NOT NULL,
    namespace VARCHAR(255) NOT NULL,
    dependency_type VARCHAR(100) NOT NULL,  -- prerequisite, optional, enhancement
    dependency_description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for project state management tables
CREATE INDEX IF NOT EXISTS idx_project_states_project_id ON project_states(project_id);
CREATE INDEX IF NOT EXISTS idx_project_states_namespace ON project_states(namespace);
CREATE INDEX IF NOT EXISTS idx_project_states_version ON project_states(version);

CREATE INDEX IF NOT EXISTS idx_project_state_events_project_id ON project_state_events(project_id);
CREATE INDEX IF NOT EXISTS idx_project_state_events_namespace ON project_state_events(namespace);
CREATE INDEX IF NOT EXISTS idx_project_state_events_type ON project_state_events(event_type);
CREATE INDEX IF NOT EXISTS idx_project_state_events_timestamp ON project_state_events(timestamp);

CREATE INDEX IF NOT EXISTS idx_project_artifacts_project_id ON project_artifacts(project_id);
CREATE INDEX IF NOT EXISTS idx_project_artifacts_namespace ON project_artifacts(namespace);
CREATE INDEX IF NOT EXISTS idx_project_artifacts_type ON project_artifacts(artifact_type);
CREATE INDEX IF NOT EXISTS idx_project_artifacts_phase ON project_artifacts(phase_created);
CREATE INDEX IF NOT EXISTS idx_project_artifacts_agent ON project_artifacts(created_by_agent);

CREATE INDEX IF NOT EXISTS idx_project_milestones_project_id ON project_milestones(project_id);
CREATE INDEX IF NOT EXISTS idx_project_milestones_namespace ON project_milestones(namespace);
CREATE INDEX IF NOT EXISTS idx_project_milestones_phase ON project_milestones(phase);
CREATE INDEX IF NOT EXISTS idx_project_milestones_status ON project_milestones(status);

CREATE INDEX IF NOT EXISTS idx_project_assignments_project_id ON project_assignments(project_id);
CREATE INDEX IF NOT EXISTS idx_project_assignments_namespace ON project_assignments(namespace);
CREATE INDEX IF NOT EXISTS idx_project_assignments_agent ON project_assignments(agent_name);
CREATE INDEX IF NOT EXISTS idx_project_assignments_status ON project_assignments(assignment_status);

CREATE INDEX IF NOT EXISTS idx_project_dependencies_project_id ON project_dependencies(project_id);
CREATE INDEX IF NOT EXISTS idx_project_dependencies_depends_on ON project_dependencies(depends_on_project_id);
CREATE INDEX IF NOT EXISTS idx_project_dependencies_namespace ON project_dependencies(namespace);

-- RLS policies for project state management tables
ALTER TABLE project_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_state_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_milestones ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_dependencies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations on project_states" ON project_states FOR ALL USING (true);
CREATE POLICY "Allow all operations on project_state_events" ON project_state_events FOR ALL USING (true);
CREATE POLICY "Allow all operations on project_artifacts" ON project_artifacts FOR ALL USING (true);
CREATE POLICY "Allow all operations on project_milestones" ON project_milestones FOR ALL USING (true);
CREATE POLICY "Allow all operations on project_assignments" ON project_assignments FOR ALL USING (true);
CREATE POLICY "Allow all operations on project_dependencies" ON project_dependencies FOR ALL USING (true);

-- Success message
SELECT 'SPARC database setup complete! 🚀 Full Production System with Project State Management enabled.' AS status;