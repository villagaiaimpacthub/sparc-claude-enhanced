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
SPARC Uber Orchestrator Agent
Master conductor of the entire SPARC autonomous development workflow
Coordinates all 36 agents through phase-based progression
"""

import os
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    import click
    from rich.console import Console
    from rich.table import Table
    from supabase import create_client, Client
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing dependency: {e}")
    exit(1)

console = Console()

# SPARC Phase Sequence
PHASE_SEQUENCE = [
    "initialization",
    "goal-clarification", 
    "specification",
    "pseudocode",
    "architecture", 
    "refinement-testing",
    "refinement-implementation",
    "bmo-completion",
    "maintenance",
    "documentation"
]

# Phase to Orchestrator Agent Mapping
PHASE_ORCHESTRATORS = {
    "goal-clarification": "goal-clarification-orchestrator",
    "specification": "specification-phase-orchestrator", 
    "pseudocode": "pseudocode-phase-orchestrator",
    "architecture": "architecture-phase-orchestrator",
    "refinement-testing": "refinement-testing-orchestrator",
    "refinement-implementation": "refinement-implementation-orchestrator",
    "bmo-completion": "bmo-completion-orchestrator",
    "maintenance": "maintenance-orchestrator",
    "documentation": "documentation-orchestrator"
}

class UberOrchestratorAgent:
    """Master conductor of the entire SPARC workflow"""
    
    def __init__(self, namespace: str):
        self.namespace = namespace
        self.agent_name = "uber-orchestrator"
        self.supabase = self._init_supabase()
        self.sparc_dir = Path('/usr/local/sparc')
        
    def _init_supabase(self) -> Client:
        """Initialize Supabase client"""
        load_dotenv()
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            console.print("[red]❌ Missing Supabase credentials[/red]")
            exit(1)
            
        return create_client(url, key)
    
    async def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get pending tasks for this agent"""
        try:
            result = self.supabase.table('agent_tasks').select('*').eq(
                'namespace', self.namespace
            ).eq(
                'to_agent', self.agent_name
            ).eq(
                'status', 'pending'
            ).order('priority', desc=True).order('created_at').execute()
            
            return result.data if result.data else []
        except Exception as e:
            console.print(f"[red]❌ Error fetching tasks: {e}[/red]")
            return []
    
    async def mark_task_in_progress(self, task_id: str):
        """Mark task as in progress"""
        try:
            self.supabase.table('agent_tasks').update({
                'status': 'in_progress',
                'started_at': datetime.now().isoformat()
            }).eq('id', task_id).execute()
        except Exception as e:
            console.print(f"[red]❌ Error updating task status: {e}[/red]")
    
    async def complete_task(self, task_id: str, result: Dict[str, Any]):
        """Mark task as completed with results"""
        try:
            self.supabase.table('agent_tasks').update({
                'status': 'completed',
                'completed_at': datetime.now().isoformat(),
                'result': result
            }).eq('id', task_id).execute()
        except Exception as e:
            console.print(f"[red]❌ Error completing task: {e}[/red]")
    
    async def delegate_task(self, to_agent: str, task_description: str, 
                          context: Dict[str, Any], priority: int = 5) -> str:
        """Delegate task to another agent"""
        task_data = {
            'namespace': self.namespace,
            'from_agent': self.agent_name,
            'to_agent': to_agent,
            'task_type': 'phase_delegation',
            'task_payload': {
                'task_id': f"{self.agent_name}_{datetime.now().isoformat()}",
                'description': task_description,
                'context': context,
                'requirements': context.get('requirements', []),
                'ai_verifiable_outcomes': context.get('ai_verifiable_outcomes', []),
                'phase': context.get('phase', 'unknown'),
                'priority': priority
            },
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        result = self.supabase.table('agent_tasks').insert(task_data).execute()
        return result.data[0]['id'] if result.data else None
    
    async def determine_current_phase(self) -> str:
        """Determine current project phase"""
        try:
            # Get latest completed tasks to understand progress
            result = self.supabase.table('agent_tasks').select(
                'task_payload'
            ).eq('namespace', self.namespace).eq(
                'status', 'completed'
            ).order('completed_at', desc=True).limit(5).execute()
            
            if not result.data:
                return "initialization"
            
            # Analyze completed phases
            completed_phases = set()
            for task in result.data:
                payload = task.get('task_payload', {})
                phase = payload.get('phase')
                if phase and phase in PHASE_SEQUENCE:
                    completed_phases.add(phase)
            
            # Return next phase in sequence
            for phase in PHASE_SEQUENCE:
                if phase not in completed_phases:
                    return phase
            
            return "documentation"  # Final phase
            
        except Exception as e:
            console.print(f"[red]❌ Error determining phase: {e}[/red]")
            return "initialization"
    
    async def create_phase_prompt_file(self, phase: str, goal: str, context: Dict[str, Any]):
        """Create detailed prompt file for Claude Code to process"""
        prompt_dir = Path('.sparc/prompts')
        prompt_dir.mkdir(parents=True, exist_ok=True)
        
        phase_prompt = f"""# SPARC {phase.title()} Phase - Autonomous Development

## Project Goal
{goal}

## Current Phase: {phase}

## Phase Objectives
{self._get_phase_objectives(phase)}

## Context
- Namespace: {self.namespace}
- Previous Phases: {context.get('completed_phases', [])}
- Current Files: {context.get('current_files', [])}

## Instructions for Claude Code
This prompt was generated by the SPARC Uber Orchestrator. Please process this phase according to the SPARC methodology and create/modify files as needed.

The agents are coordinating the overall workflow - your role is to execute the specific development tasks for this phase.

## Success Criteria
- {phase} phase deliverables completed
- Files created/modified according to specifications
- Ready for next phase: {self._get_next_phase(phase)}

Please proceed with the {phase} phase implementation.
"""
        
        prompt_file = prompt_dir / f"{phase}_prompt.md"
        prompt_file.write_text(phase_prompt)
        
        console.print(f"[blue]📝 Created phase prompt: {prompt_file}[/blue]")
        return str(prompt_file)
    
    def _get_phase_objectives(self, phase: str) -> str:
        """Get objectives for specific phase"""
        objectives = {
            "goal-clarification": "Clarify and refine project requirements, define scope and constraints",
            "specification": "Create detailed technical specifications and requirements documentation", 
            "pseudocode": "Develop high-level pseudocode and algorithm designs",
            "architecture": "Design system architecture, components, and data flow",
            "refinement-testing": "Create comprehensive test suite and testing strategy",
            "refinement-implementation": "Implement production-quality code",
            "bmo-completion": "Validate with BMO framework (Behavior-Model-Oracle)",
            "maintenance": "Set up maintenance procedures and documentation",
            "documentation": "Create user documentation and deployment guides"
        }
        return objectives.get(phase, f"Complete {phase} phase objectives")
    
    def _get_next_phase(self, current_phase: str) -> str:
        """Get next phase in sequence"""
        try:
            current_index = PHASE_SEQUENCE.index(current_phase)
            if current_index < len(PHASE_SEQUENCE) - 1:
                return PHASE_SEQUENCE[current_index + 1]
        except ValueError:
            pass
        return "completion"
    
    async def execute_task(self, task: Dict[str, Any]):
        """Execute uber orchestrator task"""
        task_payload = task['task_payload']
        description = task_payload['description']
        context = task_payload.get('context', {})
        
        console.print(f"[bold blue]🎯 Uber Orchestrator: {description}[/bold blue]")
        
        # Mark task in progress
        await self.mark_task_in_progress(task['id'])
        
        try:
            # Determine current phase
            current_phase = await self.determine_current_phase()
            console.print(f"[green]📊 Current Phase: {current_phase}[/green]")
            
            # Get project goal
            goal = context.get('project_goal', 'Project goal not specified')
            
            # Create phase prompt for Claude Code
            prompt_file = await self.create_phase_prompt_file(current_phase, goal, context)
            
            # Delegate to phase orchestrator if available
            phase_orchestrator = PHASE_ORCHESTRATORS.get(current_phase)
            if phase_orchestrator:
                await self.delegate_task(
                    to_agent=phase_orchestrator,
                    task_description=f"Execute {current_phase} phase",
                    context={
                        'phase': current_phase,
                        'goal': goal,
                        'prompt_file': prompt_file,
                        'requirements': [f"Complete {current_phase} phase deliverables"],
                        'ai_verifiable_outcomes': [f"{current_phase} phase validation passed"]
                    },
                    priority=9
                )
                console.print(f"[blue]➡️ Delegated to {phase_orchestrator}[/blue]")
            
            # Complete task
            result = {
                'success': True,
                'phase': current_phase,
                'prompt_file': prompt_file,
                'next_phase': self._get_next_phase(current_phase),
                'delegated_to': phase_orchestrator
            }
            
            await self.complete_task(task['id'], result)
            console.print(f"[green]✅ Uber orchestrator task completed[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Task execution failed: {e}[/red]")
            await self.supabase.table('agent_tasks').update({
                'status': 'failed',
                'error': str(e),
                'completed_at': datetime.now().isoformat()
            }).eq('id', task['id']).execute()
    
    async def run_polling_loop(self):
        """Main agent polling loop"""
        console.print(f"[bold green]🚀 Uber Orchestrator started for namespace: {self.namespace}[/bold green]")
        
        iteration = 0
        max_iterations = 100  # Prevent infinite loops
        
        while iteration < max_iterations:
            iteration += 1
            
            try:
                # Get pending tasks
                tasks = await self.get_pending_tasks()
                
                if not tasks:
                    console.print(f"[dim]⏳ No pending tasks (iteration {iteration})[/dim]")
                    await asyncio.sleep(5)  # Wait 5 seconds between checks
                    continue
                
                # Process each task
                for task in tasks:
                    await self.execute_task(task)
                    await asyncio.sleep(1)  # Brief pause between tasks
                
            except KeyboardInterrupt:
                console.print("\n[yellow]⏹️ Uber Orchestrator stopped by user[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]❌ Polling error: {e}[/red]")
                await asyncio.sleep(10)  # Wait longer on errors
        
        if iteration >= max_iterations:
            console.print("[yellow]⚠️ Max iterations reached[/yellow]")

@click.command()
@click.option('--namespace', required=True, help='Project namespace')
@click.option('--single-run', is_flag=True, help='Process one batch of tasks and exit')
def main(namespace: str, single_run: bool):
    """SPARC Uber Orchestrator - Master workflow conductor"""
    
    agent = UberOrchestratorAgent(namespace)
    
    async def run():
        if single_run:
            tasks = await agent.get_pending_tasks()
            if tasks:
                for task in tasks:
                    await agent.execute_task(task)
            else:
                console.print("[yellow]No pending tasks found[/yellow]")
        else:
            await agent.run_polling_loop()
    
    asyncio.run(run())

if __name__ == "__main__":
    main()