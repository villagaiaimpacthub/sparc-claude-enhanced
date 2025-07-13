#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase>=2.0.0",
#   "click>=8.1.0",
#   "rich>=13.0.0",
#   "python-dotenv>=1.0.0",
# ]
# ///

"""
SPARC Autonomous Development Orchestrator
Coordinates 36 AI agents for complete software development using UV scripts
"""

import os
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

try:
    import click
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from supabase import create_client, Client
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("This script requires dependencies listed in the header.")
    exit(1)

console = Console()

class SPARCOrchestrator:
    """Main SPARC system orchestrator using UV single file agents"""
    
    def __init__(self, namespace: str):
        self.namespace = namespace
        self.supabase = self._init_supabase()
        self.sparc_dir = Path.cwd()  # Use current working directory
        
    def _init_supabase(self) -> Client:
        """Initialize Supabase client"""
        load_dotenv()
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            console.print("[red]❌ Missing Supabase credentials in .env file[/red]")
            exit(1)
            
        return create_client(url, key)
    
    async def initialize_project(self, goal: str):
        """Initialize new SPARC project with goal"""
        console.print(f"[bold blue]🚀 Initializing SPARC project: {self.namespace}[/bold blue]")
        console.print(f"[green]🎯 Goal: {goal}[/green]")
        
        # Save namespace for hooks
        sparc_dir = Path('.sparc')
        sparc_dir.mkdir(exist_ok=True)
        (sparc_dir / 'namespace').write_text(self.namespace)
        
        # Create CLAUDE.md with project configuration
        claude_content = f"""# SPARC Autonomous Development Project

project_id: {self.namespace}

## Goal
{goal}

## Status
- Phase: initialization
- Started: {datetime.now().isoformat()}
- Agents: 36-agent autonomous system active

## Architecture
This project uses the SPARC methodology with 36 specialized AI agents:
- **Specification** → **Pseudocode** → **Architecture** → **Refinement** → **Completion**

All agent workflows are managed via namespace-isolated memory and task queues.

## Autonomous Development
Use `/sparc` commands to continue autonomous development.
The agent system will handle complete software development workflows.
"""
        Path('CLAUDE.md').write_text(claude_content)
        
        # Create initial task for uber orchestrator
        initial_task = {
            'namespace': self.namespace,
            'from_agent': 'human',
            'to_agent': 'uber-orchestrator',
            'task_type': 'project_initialization',
            'task_payload': {
                'task_id': f"init_{datetime.now().isoformat()}",
                'description': f"Initialize SPARC autonomous development for: {goal}",
                'context': {
                    'project_goal': goal,
                    'namespace': self.namespace,
                    'initialization_time': datetime.now().isoformat()
                },
                'requirements': [
                    'Analyze project goal',
                    'Begin goal clarification phase',
                    'Set up agent workflow coordination'
                ],
                'ai_verifiable_outcomes': [
                    'Goal analysis completed',
                    'Phase sequence initialized',
                    'Agent coordination active'
                ],
                'phase': 'initialization',
                'priority': 10
            },
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        self.supabase.table('agent_tasks').insert(initial_task).execute()
        
        console.print("[green]✅ Project initialized successfully[/green]")
        console.print(f"[blue]📦 Namespace: {self.namespace}[/blue]")
        console.print("[yellow]💡 Agents will now process the goal autonomously[/yellow]")
        
    async def start_agent_polling(self):
        """Start the main agent polling loop"""
        console.print("[blue]🤖 Starting autonomous agent system...[/blue]")
        
        # Start uber orchestrator agent polling
        uber_script = self.sparc_dir / 'agents' / 'uber_orchestrator.py'
        
        if uber_script.exists():
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Running autonomous development...", total=None)
                
                try:
                    # Start uber orchestrator in background
                    process = subprocess.Popen([
                        'uv', 'run', str(uber_script),
                        '--namespace', self.namespace
                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    
                    console.print(f"[green]✅ Uber orchestrator started (PID: {process.pid})[/green]")
                    console.print("[yellow]💡 Agents are now working autonomously![/yellow]")
                    console.print("[dim]Press Ctrl+C to stop monitoring[/dim]")
                    
                    # Monitor process
                    while process.poll() is None:
                        await asyncio.sleep(1)
                    
                    # Get final output
                    stdout, stderr = process.communicate()
                    if stdout:
                        console.print(stdout)
                    if stderr and process.returncode != 0:
                        console.print(f"[red]❌ Error: {stderr}[/red]")
                        
                except KeyboardInterrupt:
                    console.print("\n[yellow]⏹️ Stopping autonomous development monitoring[/yellow]")
                    if 'process' in locals():
                        process.terminate()
                except Exception as e:
                    console.print(f"[red]❌ Error starting agents: {e}[/red]")
        else:
            console.print(f"[red]❌ Uber orchestrator not found: {uber_script}[/red]")
            console.print("[yellow]💡 Make sure SPARC is properly installed[/yellow]")
    
    async def show_status(self):
        """Show current project status"""
        console.print(f"[bold blue]📊 SPARC Project Status: {self.namespace}[/bold blue]")
        
        try:
            # Get recent tasks
            tasks_result = self.supabase.table('agent_tasks').select(
                'from_agent, to_agent, task_type, status, created_at'
            ).eq('namespace', self.namespace).order(
                'created_at', desc=True
            ).limit(10).execute()
            
            if tasks_result.data:
                table = Table(title="Recent Agent Tasks")
                table.add_column("From Agent")
                table.add_column("To Agent") 
                table.add_column("Task Type")
                table.add_column("Status")
                table.add_column("Created")
                
                for task in tasks_result.data:
                    status_color = {
                        'pending': 'yellow',
                        'in_progress': 'blue', 
                        'completed': 'green',
                        'failed': 'red'
                    }.get(task['status'], 'white')
                    
                    table.add_row(
                        task['from_agent'],
                        task['to_agent'],
                        task['task_type'],
                        f"[{status_color}]{task['status']}[/{status_color}]",
                        task['created_at'][:19]
                    )
                
                console.print(table)
            else:
                console.print("[yellow]No tasks found for this project[/yellow]")
                
            # Get file changes
            changes_result = self.supabase.table('sparc_file_changes').select(
                'file_path, tool_used, timestamp'
            ).eq('namespace', self.namespace).order(
                'timestamp', desc=True
            ).limit(5).execute()
            
            if changes_result.data:
                console.print("\n[bold]Recent File Changes:[/bold]")
                for change in changes_result.data:
                    console.print(f"[green]📝[/green] {change['file_path']} ({change['tool_used']}) - {change['timestamp'][:19]}")
            
        except Exception as e:
            console.print(f"[red]❌ Error fetching status: {e}[/red]")

@click.command()
@click.option('--goal', help='Project goal for autonomous development')
@click.option('--namespace', help='Project namespace (auto-generated if not provided)')
@click.option('--status', is_flag=True, help='Show project status')
@click.option('--start-agents', is_flag=True, help='Start autonomous agent polling')
def main(goal: Optional[str], namespace: Optional[str], status: bool, start_agents: bool):
    """SPARC Autonomous Development System - 36 AI agents for complete software development"""
    
    # Load namespace from project if available
    if not namespace:
        sparc_dir = Path('.sparc')
        namespace_file = sparc_dir / 'namespace'
        if namespace_file.exists():
            namespace = namespace_file.read_text().strip()
        else:
            # Generate new namespace
            import hashlib
            project_name = Path.cwd().name
            path_hash = hashlib.md5(str(Path.cwd().resolve()).encode()).hexdigest()[:8]
            namespace = f"{project_name}_{path_hash}".replace('-', '_').replace(' ', '_').lower()
    
    orchestrator = SPARCOrchestrator(namespace)
    
    async def run():
        if status:
            await orchestrator.show_status()
        elif start_agents:
            await orchestrator.start_agent_polling()
        elif goal:
            await orchestrator.initialize_project(goal)
            console.print("\n[yellow]💡 To start autonomous development, run:[/yellow]")
            console.print(f"[cyan]uv run orchestrator.py --start-agents[/cyan]")
        else:
            console.print("[yellow]💡 Usage examples:[/yellow]")
            console.print("[cyan]uv run orchestrator.py --goal 'Build a REST API with authentication'[/cyan]")
            console.print("[cyan]uv run orchestrator.py --status[/cyan]")
            console.print("[cyan]uv run orchestrator.py --start-agents[/cyan]")
    
    asyncio.run(run())

if __name__ == "__main__":
    main()