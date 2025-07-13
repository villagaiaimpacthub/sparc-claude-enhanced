"""
Supabase Management for SPARC CLI
Handles Supabase configuration, connection, and database setup
"""

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()


class SupabaseManager:
    """Manages Supabase configuration and database operations"""
    
    def __init__(self):
        self.global_config_dir = Path.home() / ".sparc"
        self.config_file = self.global_config_dir / "config.json"
        
        # Load configuration
        self.config = self._load_config()
        self.supabase_config = self.config.get("supabase", {})
    
    def _load_config(self) -> Dict[str, Any]:
        """Load global configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                console.print(f"⚠️  [yellow]Warning: Could not load config: {e}[/yellow]")
                return {}
        return {}
    
    def _save_config(self) -> bool:
        """Save global configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            console.print(f"❌ [red]Error saving config: {e}[/red]")
            return False
    
    def is_configured(self) -> bool:
        """Check if Supabase is properly configured"""
        required_fields = ["project_url", "anon_key"]
        return all(self.supabase_config.get(field) for field in required_fields)
    
    def configure_interactive(self) -> bool:
        """Interactive Supabase configuration"""
        console.print("🗄️  [cyan]Supabase Configuration[/cyan]")
        console.print()
        
        console.print("SPARC uses Supabase for:")
        console.print("• 📊 Project state management")
        console.print("• 🤖 Agent communication and coordination")
        console.print("• 📝 Memory and context storage")
        console.print("• 📈 Real-time monitoring and analytics")
        console.print()
        
        if not Confirm.ask("Do you have a Supabase account?"):
            self._show_account_creation_instructions()
            if not Confirm.ask("Have you created a Supabase project?"):
                console.print("⚠️  [yellow]Supabase configuration skipped.[/yellow]")
                console.print("You can configure it later with: sparc config set supabase.*")
                return True
        
        # Get project configuration
        console.print("🔧 [blue]Enter your Supabase project details:[/blue]")
        
        project_url = Prompt.ask(
            "Project URL",
            default=self.supabase_config.get("project_url", "https://your-project.supabase.co")
        )
        
        anon_key = Prompt.ask(
            "Anon Key",
            password=True,
            default=self.supabase_config.get("anon_key", "")
        )
        
        service_role_key = Prompt.ask(
            "Service Role Key (optional, for admin operations)",
            password=True,
            default=self.supabase_config.get("service_role_key", "")
        )
        
        # Update configuration
        self.supabase_config.update({
            "project_url": project_url,
            "anon_key": anon_key,
            "service_role_key": service_role_key if service_role_key else None,
            "configured_at": time.time()
        })
        
        self.config["supabase"] = self.supabase_config
        
        if self._save_config():
            console.print("✅ [green]Supabase configuration saved![/green]")
            
            # Test connection
            if Confirm.ask("Test connection?"):
                return self.test_connection()
            
            return True
        else:
            console.print("❌ [red]Failed to save Supabase configuration[/red]")
            return False
    
    def _show_account_creation_instructions(self):
        """Show instructions for creating a Supabase account"""
        console.print("📝 [blue]Creating a Supabase Account:[/blue]")
        console.print()
        console.print("1. Go to https://supabase.com")
        console.print("2. Click 'Start your project'")
        console.print("3. Sign up with GitHub, Google, or email")
        console.print("4. Create a new project:")
        console.print("   • Choose a project name")
        console.print("   • Set a strong database password")
        console.print("   • Select a region close to you")
        console.print("5. Wait for project creation (1-2 minutes)")
        console.print("6. Go to Settings > API to find your keys")
        console.print()
    
    def test_connection(self) -> bool:
        """Test Supabase connection"""
        if not self.is_configured():
            console.print("❌ [red]Supabase not configured[/red]")
            return False
        
        try:
            import requests
            
            console.print("🔍 [blue]Testing Supabase connection...[/blue]")
            
            # Test basic API endpoint
            url = f"{self.supabase_config['project_url']}/rest/v1/"
            headers = {
                "apikey": self.supabase_config["anon_key"],
                "Authorization": f"Bearer {self.supabase_config['anon_key']}"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                console.print("✅ [green]Supabase connection successful![/green]")
                
                # Get project info
                try:
                    project_info = self._get_project_info()
                    if project_info:
                        table = Table(title="Supabase Project Information")
                        table.add_column("Property", style="cyan")
                        table.add_column("Value", style="green")
                        
                        for key, value in project_info.items():
                            table.add_row(key, str(value))
                        
                        console.print(table)
                except Exception:
                    pass  # Project info is optional
                
                return True
            else:
                console.print(f"❌ [red]Connection failed: HTTP {response.status_code}[/red]")
                return False
                
        except ImportError:
            console.print("⚠️  [yellow]requests library not available for testing[/yellow]")
            return True  # Assume it's OK
        except Exception as e:
            console.print(f"❌ [red]Connection test failed: {e}[/red]")
            return False
    
    def _get_project_info(self) -> Optional[Dict[str, Any]]:
        """Get basic project information"""
        try:
            import requests
            
            # This would typically require the service role key
            # For now, just return basic info from the URL
            project_url = self.supabase_config["project_url"]
            project_id = project_url.split("//")[1].split(".")[0]
            
            return {
                "Project ID": project_id,
                "Project URL": project_url,
                "API Status": "Connected"
            }
        except Exception:
            return None
    
    def setup_database_schema(self) -> bool:
        """Set up SPARC database schema in Supabase"""
        if not self.is_configured():
            console.print("❌ [red]Supabase not configured[/red]")
            return False
        
        console.print("🗄️  [cyan]Setting up SPARC database schema...[/cyan]")
        
        # SQL schema for SPARC tables with namespace-based isolation
        schema_sql = """
-- SPARC System Tables (Namespace-based Multi-tenancy)

-- Project memories table
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

-- SPARC contexts table
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

-- Agent tasks table
CREATE TABLE IF NOT EXISTS agent_tasks (
    id BIGSERIAL PRIMARY KEY,
    namespace TEXT NOT NULL,
    project_id TEXT, -- Legacy compatibility
    from_agent TEXT NOT NULL,
    to_agent TEXT NOT NULL,
    task_type TEXT NOT NULL,
    priority INTEGER DEFAULT 1,
    status TEXT DEFAULT 'pending',
    task_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent executions table
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

-- Approval queue table
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
CREATE INDEX IF NOT EXISTS idx_agent_executions_namespace ON agent_executions(namespace);
CREATE INDEX IF NOT EXISTS idx_agent_executions_project_id ON agent_executions(project_id); -- Legacy
CREATE INDEX IF NOT EXISTS idx_approval_queue_namespace ON approval_queue(namespace);
CREATE INDEX IF NOT EXISTS idx_approval_queue_project_id ON approval_queue(project_id); -- Legacy

-- Enable Row Level Security (RLS)
ALTER TABLE project_memorys ENABLE ROW LEVEL SECURITY;
ALTER TABLE sparc_contexts ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_queue ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (allow all for service role, restrict for others)
-- Note: Adjust these policies based on your security requirements

-- Project memories policies
CREATE POLICY IF NOT EXISTS "Allow all for service role" ON project_memorys
    FOR ALL USING (auth.role() = 'service_role');

-- SPARC contexts policies  
CREATE POLICY IF NOT EXISTS "Allow all for service role" ON sparc_contexts
    FOR ALL USING (auth.role() = 'service_role');

-- Agent tasks policies
CREATE POLICY IF NOT EXISTS "Allow all for service role" ON agent_tasks
    FOR ALL USING (auth.role() = 'service_role');

-- Agent executions policies
CREATE POLICY IF NOT EXISTS "Allow all for service role" ON agent_executions
    FOR ALL USING (auth.role() = 'service_role');

-- Approval queue policies
CREATE POLICY IF NOT EXISTS "Allow all for service role" ON approval_queue
    FOR ALL USING (auth.role() = 'service_role');
"""
        
        try:
            # For now, just save the schema to a file
            # In a real implementation, this would execute against Supabase
            schema_file = self.global_config_dir / "supabase_schema.sql"
            with open(schema_file, 'w') as f:
                f.write(schema_sql)
            
            console.print(f"✅ [green]Schema saved to: {schema_file}[/green]")
            console.print("📝 [blue]To apply this schema:[/blue]")
            console.print("1. Go to your Supabase dashboard")
            console.print("2. Navigate to SQL Editor")
            console.print("3. Copy and paste the schema from the saved file")
            console.print("4. Execute the SQL")
            
            return True
            
        except Exception as e:
            console.print(f"❌ [red]Error setting up schema: {e}[/red]")
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get Supabase connection information"""
        if not self.is_configured():
            return {"configured": False}
        
        return {
            "configured": True,
            "project_url": self.supabase_config["project_url"],
            "has_anon_key": bool(self.supabase_config.get("anon_key")),
            "has_service_key": bool(self.supabase_config.get("service_role_key")),
            "configured_at": self.supabase_config.get("configured_at")
        }
    
    def update_config(self, key: str, value: str) -> bool:
        """Update a specific Supabase configuration value"""
        try:
            if "supabase" not in self.config:
                self.config["supabase"] = {}
            
            self.config["supabase"][key] = value
            return self._save_config()
            
        except Exception as e:
            console.print(f"❌ [red]Error updating config: {e}[/red]")
            return False
    
    def remove_config(self) -> bool:
        """Remove Supabase configuration"""
        try:
            if "supabase" in self.config:
                del self.config["supabase"]
                self.supabase_config = {}
                return self._save_config()
            return True
            
        except Exception as e:
            console.print(f"❌ [red]Error removing config: {e}[/red]")
            return False