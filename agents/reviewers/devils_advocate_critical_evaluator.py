#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase>=2.0.0",
#   "rich",
#   "pydantic",
#   "python-dotenv",
# ]
# ///

"""Devil's Advocate Critical Evaluator - State-aware critical project evaluator"""

import json
import asyncio
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime


# Base agent classes embedded for UV standalone execution
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

try:
    from pydantic import BaseModel
    from rich.console import Console
    from supabase import create_client, Client
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing dependency: {e}")
    exit(1)

console = Console()

class AgentResult(BaseModel):
    success: bool
    outputs: Dict[str, Any]
    files_created: List[str] = []
    files_modified: List[str] = []
    next_steps: Optional[List[str]] = None
    errors: Optional[List[str]] = None

class TaskPayload(BaseModel):
    task_id: str
    description: str
    context: Dict[str, Any]
    requirements: List[str]
    ai_verifiable_outcomes: List[str]
    phase: str
    priority: int = 5

class BaseAgent(ABC):
    def __init__(self, agent_name: str, role_definition: str, custom_instructions: str):
        self.agent_name = agent_name
        self.role_definition = role_definition
        self.custom_instructions = custom_instructions
        
        # Load project context
        self.project_id = self._load_project_id()
        self.supabase = self._init_supabase()
        
    def _load_project_id(self) -> str:
        sparc_dir = Path('.sparc')
        namespace_file = sparc_dir / 'namespace'
        if namespace_file.exists():
            return namespace_file.read_text().strip()
        return os.environ.get("DEFAULT_PROJECT_ID", "default")
    
    def _init_supabase(self) -> Client:
        load_dotenv()
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        if not url or not key:
            console.print("[red]❌ Missing Supabase credentials[/red]")
            exit(1)
        return create_client(url, key)
    
    async def delegate_task(self, to_agent: str, task_description: str, 
                          context: Dict[str, Any], priority: int = 5) -> str:
        task_data = {
            'namespace': self.project_id,
            'from_agent': self.agent_name,
            'to_agent': to_agent,
            'task_type': 'delegation',
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
    
    @abstractmethod
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        pass


class DevilsAdvocateCriticalEvaluator(BaseAgent):
    """Acts as a Devil's Advocate performing critical evaluation of project aspects"""
    
    def __init__(self):
        super().__init__(
            agent_name="devils-advocate-critical-evaluator",
            role_definition="Your sole purpose is to act as a Devil's Advocate. You first gain a comprehensive understanding of the project's high-level structure by querying the 'project_memorys' Supabase database. You then perform deep-dive analysis by reading the actual source files referenced in the database. You critically evaluate every aspect of the project, including strategies, requirements, architecture, and code. You are designed to question assumptions, find potential flaws, and propose simpler, more robust alternatives. Your output is a purely advisory critique.",
            custom_instructions="""You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

Before you answer, think through this problem step by step. When you write documents, you must avoid every '|' character and substitute it with '--', and also avoid patterns like ':---'. Your workflow is a two-phase process. In Phase 1, State Reconnaissance, your mandatory first step is to use "use_mcp_tool" to execute queries against the 'project_memorys' Supabase database to build a map of the project. Your queries should focus on retrieving the high-level index of files and documents and their rationale. This will create your 'reading list'. In Phase 2, Deep-Dive Analysis, use the "read_file" tool to read the contents of the most important documents and code files from your reading list. Your critique will be born from comparing the high-level information from the database with the low-level reality of the file contents. Look for discrepancies, over-complications, and logical flaws. Your AI-verifiable outcome is the creation of your critique report. Use "write_to_file" to save this comprehensive critique in 'docs/devil/critique_report_[timestamp].md'. Your "attempt_completion" summary must state that your critique is complete, explain your two-phase analysis process, highlight the key areas of concern you identified, and provide the path to your detailed report."""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute critical evaluation of project aspects"""
        
        # Build prompt using base class
        prompt = self._build_agent_prompt(task, context)
        
        # Add specific instructions for devil's advocate analysis
        specific_prompt = f"""{prompt}

CRITICAL EVALUATION MISSION:
You are now performing a comprehensive Devil's Advocate analysis of the project. Your task is to:

1. PHASE 1 - State Reconnaissance:
   - Query the project_memorys database to build a complete map of all files and their metadata
   - Identify the most critical files that need deep analysis
   - Create a strategic reading list based on file importance and rationale

2. PHASE 2 - Deep-Dive Analysis:
   - Read the actual contents of the most important files
   - Compare database metadata with actual file contents
   - Look for discrepancies, over-complications, and logical flaws
   - Question all assumptions and design decisions

3. CRITICAL EVALUATION AREAS:
   - Architecture complexity vs. actual needs
   - Over-engineering vs. simplicity
   - Requirements clarity and feasibility
   - Code quality and maintainability
   - Security vulnerabilities
   - Performance bottlenecks
   - Test coverage and quality
   - Documentation accuracy

4. OUTPUT REQUIREMENTS:
   - Create a comprehensive critique report
   - Save it as 'docs/devil/critique_report_[timestamp].md'
   - Include specific recommendations for improvement
   - Propose simpler, more robust alternatives where applicable

Remember: You are the Devil's Advocate. Be thorough, skeptical, and constructive in your criticism.
"""
        
        # Use Claude via base class
        claude_response = await self._run_claude(specific_prompt)
        
        # Create critique report
        files_created = await self._create_critique_outputs(claude_response)
        
        # Record with State Scribe
        if files_created:
            await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "critique_analysis": claude_response,
                "files_created": files_created
            },
            files_created=files_created,
            files_modified=[],
            next_steps=["Review critique findings and address critical issues identified"]
        )
    
    async def _create_critique_outputs(self, claude_response: str) -> List[str]:
        """Create critique report files"""
        files_created = []
        
        try:
            # Parse Claude response for critique content
            if "critique_report" in claude_response.lower():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                critique_report_path = f"docs/devil/critique_report_{timestamp}.md"
                
                # Create docs/devil directory if it doesn't exist
                Path("docs/devil").mkdir(parents=True, exist_ok=True)
                
                # Extract critique content from response
                critique_content = self._extract_critique_content(claude_response)
                
                # Write critique report
                with open(critique_report_path, 'w', encoding='utf-8') as f:
                    f.write(critique_content)
                
                files_created.append(critique_report_path)
                
        except Exception as e:
            print(f"Error creating critique outputs: {str(e)}")
        
        return files_created
    
    def _extract_critique_content(self, claude_response: str) -> str:
        """Extract critique content from Claude response"""
        # This is a simplified extraction - in practice, you'd parse the structured response
        header = f"""# Devil's Advocate Critique Report
Generated: {datetime.now().isoformat()}
Agent: {self.agent_name}

## Executive Summary
This report contains a comprehensive critical evaluation of the project, identifying potential issues, over-complications, and areas for improvement.

## Analysis Process
1. State Reconnaissance: Analyzed project_memorys database
2. Deep-Dive Analysis: Reviewed critical files and components
3. Critical Evaluation: Questioned assumptions and design decisions

## Findings and Recommendations

"""
        
        # Add Claude's response content
        return header + claude_response
    
    async def _record_files_with_state_scribe(self, files_created: List[str]) -> None:
        """Record created files with State Scribe"""
        if not files_created:
            return
        
        files_to_record = []
        for file_path in files_created:
            files_to_record.append({
                "file_path": file_path,
                "memory_type": "critique_report",
                "brief_description": "Devil's Advocate critical evaluation report",
                "elements_description": "Comprehensive critique of project aspects including architecture, requirements, and code quality",
                "rationale": "Critical evaluation to identify potential issues and improvement opportunities"
            })
        
        # Delegate to State Scribe
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record devil's advocate critique files in project memory",
            task_context={
                "files_to_record": files_to_record,
                "phase": "review"
            }
        )

async def main():
    """Main execution function"""
    agent = DevilsAdvocateCriticalEvaluator()
    
    # Example task
    task = TaskPayload(
        task_id="devils_advocate_evaluation",
        description="Perform comprehensive critical evaluation of the project",
        requirements=["Analyze project structure and identify potential issues"],
        ai_verifiable_outcomes=["Create detailed critique report with specific recommendations"],
        phase="review",
        priority=3
    )
    
    result = await agent.execute(task)
    print(f"Devil's Advocate Critical Evaluator completed: {result.success}")
    if result.files_created:
        print(f"Files created: {', '.join(result.files_created)}")

if __name__ == "__main__":
    asyncio.run(main())

# CLI interface for standalone UV execution
import asyncio
import click

@click.command()
@click.option('--namespace', required=True, help='Project namespace')
@click.option('--task-id', help='Specific task ID to process')
@click.option('--goal', help='Project goal for context')
def main(namespace: str, task_id: str, goal: str):
    """Run this SPARC agent standalone"""
    
    # Create mock task for testing
    if not task_id:
        task = TaskPayload(
            task_id=f"test_{datetime.now().isoformat()}",
            description=f"Test execution for {namespace}",
            context={'project_goal': goal or 'Test goal'},
            requirements=[],
            ai_verifiable_outcomes=[],
            phase='test',
            priority=5
        )
    else:
        # In real implementation, load task from database
        task = TaskPayload(
            task_id=task_id,
            description="Loaded from database",
            context={},
            requirements=[],
            ai_verifiable_outcomes=[],
            phase='unknown',
            priority=5
        )
    
    # Create agent and execute
    agent_class_name = [name for name in globals() if name.endswith('Agent') or name.endswith('Orchestrator')]
    if agent_class_name:
        agent_class = globals()[agent_class_name[0]]
        agent = agent_class()
        
        async def run():
            try:
                result = await agent._execute_task(task, task.context)
                console.print(f"[green]✅ {agent.agent_name} completed successfully[/green]")
                console.print(f"Result: {result}")
            except Exception as e:
                console.print(f"[red]❌ {agent.agent_name} failed: {e}[/red]")
        
        asyncio.run(run())
    else:
        console.print("[red]❌ No agent class found[/red]")

if __name__ == "__main__":
    main()
