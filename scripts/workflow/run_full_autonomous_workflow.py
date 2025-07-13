#!/usr/bin/env python3
"""
Run complete autonomous SPARC workflow with proper 36-agent coordination
"""

import os
import subprocess
import sys
import time
import asyncio
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from supabase import create_client

load_dotenv()
console = Console()

class AutonomousWorkflowRunner:
    """Run complete autonomous SPARC workflow"""
    
    def __init__(self):
        self.namespace = "test_sparc_1752415022"
        self.supabase = self._init_supabase()
        self.base_path = Path.cwd()
        self.phases = [
            'goal-clarification',
            'specification', 
            'pseudocode',
            'architecture',
            'implementation',
            'testing',
            'documentation'
        ]
        self.current_phase = 0
        
    def _init_supabase(self):
        """Initialize Supabase client"""
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            console.print("[red]❌ Missing Supabase credentials[/red]")
            return None
            
        return create_client(url, key)
    
    def run_autonomous_workflow(self):
        """Run complete autonomous workflow"""
        console.print("🤖 [bold blue]Starting Full Autonomous SPARC Workflow[/bold blue]")
        console.print(f"📋 Goal: Build a grocery planning app")
        console.print(f"🏷️ Namespace: {self.namespace}")
        
        # Step 1: Clear any existing tasks
        self._clear_pending_tasks()
        
        # Step 2: Create proper project record
        self._create_project_record()
        
        # Step 3: Run each phase sequentially
        for phase_name in self.phases:
            console.print(f"\\n🚀 [bold]Starting Phase: {phase_name}[/bold]")
            
            success = self._run_phase(phase_name)
            
            if success:
                console.print(f"✅ Phase {phase_name} completed successfully")
                self._update_project_phase(phase_name)
            else:
                console.print(f"❌ Phase {phase_name} failed")
                break
                
            # Brief pause between phases
            time.sleep(2)
        
        # Step 4: Show final results
        self._show_final_results()
    
    def _clear_pending_tasks(self):
        """Clear any pending tasks from previous runs"""
        if not self.supabase:
            return
            
        try:
            # Clear old tasks for this namespace
            result = self.supabase.table('agent_tasks').delete().eq('namespace', self.namespace).execute()
            console.print(f"🧹 Cleared {len(result.data) if result.data else 0} pending tasks")
        except Exception as e:
            console.print(f"⚠️ Could not clear tasks: {e}")
    
    def _create_project_record(self):
        """Create proper project record in database"""
        if not self.supabase:
            return
            
        try:
            project_data = {
                'namespace': self.namespace,
                'project_name': 'Grocery Planning App',
                'project_goal': 'Build a comprehensive grocery planning and shopping app with meal planning, barcode scanning, and budget tracking',
                'current_phase': 'goal-clarification',
                'status': 'active',
                'start_date': datetime.now().isoformat()
            }
            
            # Check if project already exists
            existing = self.supabase.table('sparc_projects').select("*").eq('namespace', self.namespace).execute()
            
            if existing.data:
                # Update existing project
                result = self.supabase.table('sparc_projects').update(project_data).eq('namespace', self.namespace).execute()
                console.print("📝 Updated existing project record")
            else:
                # Create new project
                result = self.supabase.table('sparc_projects').insert(project_data).execute()
                console.print("📝 Created new project record")
                
        except Exception as e:
            console.print(f"⚠️ Could not create project record: {e}")
    
    def _run_phase(self, phase_name: str) -> bool:
        """Run a specific SPARC phase using universal agent runner"""
        from run_agent import UniversalAgentRunner
        
        try:
            runner = UniversalAgentRunner(self.base_path)
            
            # Add goal parameter for goal-clarification phase
            kwargs = {}
            if phase_name == 'goal-clarification':
                kwargs['goal'] = 'Build a comprehensive grocery planning app'
            
            result = runner.run_orchestrator_phase(phase_name, self.namespace, **kwargs)
            
            return result['success']
            
        except Exception as e:
            console.print(f"❌ Error running {phase_name}: {e}")
            return False
    
    def _update_project_phase(self, phase_name: str):
        """Update project phase in database"""
        if not self.supabase:
            return
            
        try:
            update_data = {
                'current_phase': phase_name,
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('sparc_projects').update(update_data).eq('namespace', self.namespace).execute()
            
        except Exception as e:
            console.print(f"⚠️ Could not update project phase: {e}")
    
    def _show_final_results(self):
        """Show final workflow results"""
        console.print("\\n🎉 [bold green]Autonomous Workflow Complete![/bold green]")
        
        # Check what files were created
        docs_created = []
        docs_dirs = ['docs', 'src', 'tests']
        
        for docs_dir in docs_dirs:
            if (self.base_path / docs_dir).exists():
                for file_path in (self.base_path / docs_dir).rglob('*'):
                    if file_path.is_file() and file_path.suffix in ['.md', '.py', '.js', '.ts', '.html', '.css']:
                        rel_path = file_path.relative_to(self.base_path)
                        docs_created.append(str(rel_path))
        
        console.print(f"\\n📁 [bold]Files Created ({len(docs_created)}):[/bold]")
        for doc in sorted(docs_created):
            console.print(f"  ✅ {doc}")
        
        # Check database state
        if self.supabase:
            try:
                # Agent tasks
                tasks = self.supabase.table('agent_tasks').select("*").eq('namespace', self.namespace).execute()
                
                # Agent executions
                executions = self.supabase.table('agent_executions').select("*").eq('namespace', self.namespace).execute()
                
                # Project memories
                memories = self.supabase.table('project_memorys').select("*").eq('namespace', self.namespace).execute()
                
                console.print(f"\\n📊 [bold]Database State:[/bold]")
                console.print(f"  🤖 Agent tasks: {len(tasks.data) if tasks.data else 0}")
                console.print(f"  ⚡ Agent executions: {len(executions.data) if executions.data else 0}")
                console.print(f"  💾 Project memories: {len(memories.data) if memories.data else 0}")
                
            except Exception as e:
                console.print(f"⚠️ Could not check database: {e}")
        
        console.print(f"\\n🎯 [bold blue]Next Steps:[/bold blue]")
        console.print("  • Review generated documentation and code")
        console.print("  • Test the autonomous workflow output")
        console.print("  • Begin manual implementation if needed")

def main():
    """Main entry point"""
    runner = AutonomousWorkflowRunner()
    runner.run_autonomous_workflow()

if __name__ == "__main__":
    main()