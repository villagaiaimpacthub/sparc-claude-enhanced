#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase",
#   "qdrant-client",
#   "mistralai",
#   "rich",
#   "pydantic",
#   "python-dotenv",
# ]
# ///

"""Base agent class for all SPARC agents"""

import os
import json
import asyncio
import subprocess
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from pydantic import BaseModel
from rich.console import Console
from dotenv import load_dotenv

# Import our memory manager
from sparc_cli.memory.manager import MemoryManager, TaskPayload

# Load environment variables
load_dotenv()

console = Console()

class AgentResult(BaseModel):
    """Standard result structure"""
    success: bool
    outputs: Dict[str, Any]
    files_created: List[str]
    files_modified: List[str]
    next_steps: Optional[List[str]] = None
    errors: Optional[List[str]] = None

class BaseAgent(ABC):
    """Base class for all SPARC agents"""
    
    def __init__(self, agent_name: str, role_definition: str, custom_instructions: str):
        self.agent_name = agent_name
        self.role_definition = role_definition
        self.custom_instructions = custom_instructions
        
        # Load project context
        self.project_id = self._load_project_id()
        
        # Initialize memory manager
        self.memory = MemoryManager(self.project_id)
        
    def _load_project_id(self) -> str:
        """Load project ID from CLAUDE.md"""
        claude_md = Path("CLAUDE.md")
        if claude_md.exists():
            content = claude_md.read_text()
            for line in content.split('\n'):
                if line.startswith('project_id:'):
                    return line.split(':', 1)[1].strip()
        return os.environ.get("DEFAULT_PROJECT_ID", "default")
    
    async def execute(self, task: TaskPayload) -> AgentResult:
        """Main execution method"""
        console.print(f"[bold blue]🤖 {self.agent_name} starting...[/bold blue]")
        
        try:
            # 1. Load context from memory
            context = await self._load_context(task)
            
            # 2. Execute agent-specific logic
            result = await self._execute_task(task, context)
            
            # 3. Save results to memory
            await self._save_results(task, result)
            
            # 4. Update task status
            await self._update_task_status(task.task_id, "completed", result)
            
            console.print(f"[bold green]✅ {self.agent_name} completed[/bold green]")
            return result
            
        except Exception as e:
            console.print(f"[bold red]❌ {self.agent_name} failed: {str(e)}[/bold red]")
            await self._update_task_status(task.task_id, "failed", error=str(e))
            raise
    
    async def _load_context(self, task: TaskPayload) -> Dict[str, Any]:
        """Load relevant context from memory systems"""
        context = {
            "task": task.dict(),
            "project_state": {},
            "relevant_files": [],
            "previous_decisions": [],
            "current_phase": task.phase
        }
        
        # Load project state
        context["project_state"] = await self.memory.get_project_state()
        
        # Load agent history
        context["previous_decisions"] = await self.memory.get_agent_history(self.agent_name)
        
        # Semantic search for relevant files
        if task.description:
            context["relevant_files"] = await self.memory.search_code(task.description)
        
        return context
    
    async def _save_results(self, task: TaskPayload, result: AgentResult) -> None:
        """Save agent results to memory systems"""
        # Save context
        await self.memory.save_context(
            agent_name=self.agent_name,
            phase=task.phase,
            context={
                "task": task.dict(),
                "result": result.dict(),
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Index any created files
        for file_path in result.files_created:
            await self.memory.index_file(file_path)
    
    async def _update_task_status(self, task_id: str, status: str, 
                                 result: Optional[AgentResult] = None,
                                 error: Optional[str] = None) -> None:
        """Update task status in Supabase"""
        try:
            update_data = {
                "status": status,
                "completed_at": datetime.now().isoformat() if status in ["completed", "failed"] else None
            }
            
            if result:
                update_data["result"] = result.dict()
            if error:
                update_data["error"] = error
                
            await self.memory.supabase.table("agent_tasks").update(update_data).eq(
                "id", task_id
            ).execute()
        except Exception as e:
            console.print(f"[red]Error updating task status: {str(e)}[/red]")
    
    async def _run_claude(self, prompt: str, max_tokens: int = 50000) -> str:
        """Process prompt with Claude Code via subprocess"""
        console.print(f"[cyan]🤖 {self.agent_name} requesting Claude Code execution...[/cyan]")
        
        # The agents are designed to be run via uv run commands
        # They call Claude Code as a subprocess to do the actual work
        # This is the correct architecture: Agent -> Claude Code -> Results
        
        try:
            # Create a temporary file with the prompt
            temp_prompt_file = f"/tmp/sparc_prompt_{self.agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(temp_prompt_file, 'w') as f:
                f.write(prompt)
            
            # Call Claude Code with the prompt
            # Using echo to pipe the prompt since claude-code reads from stdin
            cmd = f'echo "{prompt}" | claude-code'
            
            console.print(f"[dim]Executing: {cmd[:100]}...[/dim]")
            
            # Execute the command
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            stdout, stderr = await process.communicate()
            
            # Clean up temp file
            if os.path.exists(temp_prompt_file):
                os.remove(temp_prompt_file)
            
            if process.returncode != 0:
                error_msg = f"Claude Code execution failed: {stderr.decode()}"
                console.print(f"[red]❌ {error_msg}[/red]")
                return f"ERROR: {error_msg}"
            
            response = stdout.decode().strip()
            console.print(f"[green]✅ Claude Code response received ({len(response)} chars)[/green]")
            
            return response
            
        except Exception as e:
            error_msg = f"Failed to execute Claude Code: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            return f"ERROR: {error_msg}"
    
    async def _delegate_task(self, to_agent: str, task_description: str, 
                           task_context: Dict[str, Any], priority: int = 5) -> str:
        """Delegate a task to another agent"""
        task_payload = {
            "task_id": f"{self.agent_name}_{datetime.now().isoformat()}",
            "description": task_description,
            "context": task_context,
            "requirements": task_context.get("requirements", []),
            "ai_verifiable_outcomes": task_context.get("ai_verifiable_outcomes", []),
            "phase": task_context.get("phase", "unknown"),
            "priority": priority
        }
        
        return await self.memory.create_task(
            from_agent=self.agent_name,
            to_agent=to_agent,
            task_type="new_task",
            task_payload=task_payload
        )
    
    async def _request_approval(self, phase: str, artifacts: Dict[str, Any], 
                               summary: str) -> str:
        """Request human approval"""
        return await self.memory.request_approval(
            phase=phase,
            agent_name=self.agent_name,
            artifacts=artifacts,
            summary=summary
        )
    
    def _build_agent_prompt(self, task: TaskPayload, context: Dict[str, Any]) -> str:
        """Build comprehensive prompt for Claude"""
        relevant_files_text = ""
        if context.get("relevant_files"):
            relevant_files_text = "\\n\\nRelevant Files:\\n"
            for file_info in context["relevant_files"][:5]:  # Limit to top 5
                relevant_files_text += f"File: {file_info['file_path']}\\n"
                relevant_files_text += f"Content: {file_info['content'][:1000]}...\\n\\n"
        
        # Replace dynamic project ID in custom instructions
        custom_instructions = self.custom_instructions.replace(
            "project_id = 'yjnrxnacpxdvseyetsgi'",
            f"project_id = '{self.project_id}'"
        )
        
        return f"""
{self.role_definition}

{custom_instructions}

Current Task:
{task.description}

Context:
- Project ID: {self.project_id}
- Phase: {task.phase}
- Priority: {task.priority}

Project State:
- Total Files: {context['project_state'].get('total_files', 0)}
- Last Updated: {context['project_state'].get('last_updated', 'Never')}

Requirements:
{chr(10).join(f"- {req}" for req in task.requirements)}

AI-Verifiable Outcomes:
{chr(10).join(f"- {outcome}" for outcome in task.ai_verifiable_outcomes)}

{relevant_files_text}

Execute your task and provide a detailed response with specific actions taken.
"""
    
    @abstractmethod
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Agent-specific task execution logic"""
        pass