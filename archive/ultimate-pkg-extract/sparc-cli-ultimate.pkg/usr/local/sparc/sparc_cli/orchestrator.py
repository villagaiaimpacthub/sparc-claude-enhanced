#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase",
#   "click",
#   "rich",
#   "asyncio",
#   "python-dotenv",
# ]
# ///

"""Main SPARC system orchestrator"""

import asyncio
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv

from .memory.manager import MemoryManager, TaskPayload

# Load environment variables
load_dotenv()

console = Console()

class SPARCOrchestrator:
    """Main SPARC system orchestrator"""
    
    def __init__(self, namespace: str):
        self.namespace = namespace
        self.project_id = namespace  # For compatibility
        self.memory = MemoryManager(namespace)
        self.agents = self._initialize_agents()
        
    def _initialize_agents(self) -> dict:
        """Initialize core agents"""
        agents = {}
        
        try:
            # Import and initialize key orchestrator agents
            from agents.orchestrators.uber import UberOrchestratorAgent
            from agents.orchestrators.goal_clarification import GoalClarificationOrchestrator
            
            agents["uber-orchestrator"] = UberOrchestratorAgent()
            agents["orchestrator-goal-clarification"] = GoalClarificationOrchestrator()
            
            console.print(f"[green]✅ Initialized {len(agents)} agents[/green]")
            
        except ImportError as e:
            console.print(f"[red]⚠️ Could not import agents: {str(e)}[/red]")
            console.print("[yellow]Running in minimal mode[/yellow]")
            
        return agents
    
    async def run(self, goal: Optional[str] = None):
        """Run the SPARC system"""
        console.print(f"[bold blue]🚀 Starting SPARC for namespace: {self.namespace}[/bold blue]")
        
        if goal:
            # Starting new project
            console.print(f"[green]Goal: {goal}[/green]")
            await self._initialize_project(goal)
        
        # Main execution loop
        iteration = 0
        max_iterations = 100  # Prevent infinite loops
        
        while iteration < max_iterations:
            iteration += 1
            console.print(f"[cyan]--- Iteration {iteration} ---[/cyan]")
            
            # Get next pending task
            task = await self._get_next_task()
            
            if not task:
                console.print("[yellow]No pending tasks. Checking for approvals...[/yellow]")
                if await self._check_approvals():
                    await asyncio.sleep(5)  # Wait a bit before checking again
                    continue
                console.print("[green]✅ All tasks completed![/green]")
                break
            
            # Execute task
            agent_name = task["to_agent"]
            agent = self.agents.get(agent_name)
            
            if not agent:
                console.print(f"[red]❌ Unknown agent: {agent_name}[/red]")
                await self._mark_task_failed(task["id"], f"Unknown agent: {agent_name}")
                continue
            
            try:
                task_payload = TaskPayload(**task["task_payload"])
                console.print(f"[blue]Executing: {task_payload.description}[/blue]")
                
                result = await agent.execute(task_payload)
                
                if result.success:
                    console.print(f"[green]✅ Task completed successfully[/green]")
                else:
                    console.print(f"[red]❌ Task failed: {result.errors}[/red]")
                    
            except Exception as e:
                console.print(f"[red]❌ Task execution failed: {str(e)}[/red]")
                await self._mark_task_failed(task["id"], str(e))
        
        if iteration >= max_iterations:
            console.print("[red]⚠️ Maximum iterations reached[/red]")
    
    async def _initialize_project(self, goal: str):
        """Initialize a new project"""
        # Create CLAUDE.md
        claude_content = f"""# SPARC Project

project_id: {self.project_id}

## Goal
{goal}

## Status
Phase: initialization
Started: {datetime.now().isoformat()}
"""
        Path("CLAUDE.md").write_text(claude_content)
        
        # Create initial task for uber orchestrator
        task_payload = {
            "task_id": f"init_{datetime.now().isoformat()}",
            "description": f"Initialize SPARC project with goal: {goal}",
            "context": {"project_goal": goal},
            "requirements": ["Complete SPARC workflow"],
            "ai_verifiable_outcomes": ["All phases completed"],
            "phase": "initialization",
            "priority": 10
        }
        
        await self.memory.create_task(
            from_agent="human",
            to_agent="uber-orchestrator",
            task_type="new_task",
            task_payload=task_payload
        )
        
        console.print("[green]✅ Project initialized[/green]")
    
    async def _get_next_task(self):
        """Get next pending task from queue"""
        tasks = await self.memory.get_pending_tasks("")  # Get all pending tasks
        
        if not tasks:
            return None
        
        # Sort by priority and creation time
        task = sorted(tasks, key=lambda t: (-t["priority"], t["created_at"]))[0]
        
        # Mark as in progress
        await self.memory.supabase.table("agent_tasks").update({
            "status": "in_progress",
            "started_at": datetime.now().isoformat()
        }).eq("id", task["id"]).execute()
        
        return task
    
    async def _check_approvals(self) -> bool:
        """Check for pending approvals"""
        approvals = await self.memory.check_pending_approvals()
        
        if approvals:
            approval = approvals[0]
            console.print(f"[yellow]⏳ Waiting for approval: {approval['summary']}[/yellow]")
            console.print(f"[dim]Phase: {approval['phase']} | Agent: {approval['requesting_agent']}[/dim]")
            return True
        return False
    
    async def _mark_task_failed(self, task_id: str, error: str):
        """Mark a task as failed"""
        await self.memory.supabase.table("agent_tasks").update({
            "status": "failed",
            "error": error,
            "completed_at": datetime.now().isoformat()
        }).eq("id", task_id).execute()

@click.command()
@click.option('--project-id', help='Project ID (auto-generated if not provided)')
@click.option('--goal', help='Project goal (for new projects)')
@click.option('--status', is_flag=True, help='Show project status')
def main(project_id: str, goal: Optional[str], status: bool):
    """SPARC System Orchestrator"""
    
    if status:
        show_status(project_id)
        return
    
    if not project_id:
        project_id = f"sparc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        console.print(f"[green]Created project: {project_id}[/green]")
    
    # Run orchestrator
    orchestrator = SPARCOrchestrator(project_id)
    asyncio.run(orchestrator.run(goal))

def show_status(project_id: str):
    """Show project status"""
    if not project_id:
        # Try to get from CLAUDE.md
        claude_md = Path("CLAUDE.md")
        if claude_md.exists():
            content = claude_md.read_text()
            for line in content.split('\n'):
                if line.startswith('project_id:'):
                    project_id = line.split(':', 1)[1].strip()
                    break
        else:
            console.print("[red]No project ID provided and no CLAUDE.md found[/red]")
            return
    
    memory = MemoryManager(project_id)
    
    # Get current state
    async def get_status():
        result = await memory.supabase.table("sparc_contexts").select("phase, agent_name, created_at").eq(
            "project_id", project_id
        ).order(
            "created_at", desc=True
        ).limit(10).execute()
        
        if result.data:
            table = Table(title=f"Project Status: {project_id}")
            table.add_column("Phase")
            table.add_column("Agent")
            table.add_column("Time")
            
            for row in result.data:
                table.add_row(
                    row["phase"],
                    row["agent_name"],
                    row["created_at"]
                )
            
            console.print(table)
        else:
            console.print(f"[yellow]No activity found for project: {project_id}[/yellow]")
    
    asyncio.run(get_status())

if __name__ == "__main__":
    main()