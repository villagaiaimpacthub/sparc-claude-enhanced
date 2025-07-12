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

"""Code Comprehension Assistant v2 - SPARC aligned code analysis specialist"""

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


class CodeComprehensionAssistantV2(BaseAgent):
    """Analyzes codebase structure and behavior for comprehension reports"""
    
    def __init__(self):
        super().__init__(
            agent_name="code-comprehension-assistant-v2",
            role_definition="Your specific purpose is to analyze a designated area of the codebase to gain a thorough understanding of its static structure and dynamic behavior. You will analyze its functionality, underlying structure, and potential issues. This comprehension is a precursor to refinement or maintenance activities. The report you generate must be saved in the 'docs/reports' directory and crafted so that human programmers can quickly grasp the code's nature.",
            custom_instructions="""You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

Before you answer, you must think through this problem step by step. When you write documents, you must avoid every '|' character and substitute it with '--', and also avoid patterns like ':---'. You will receive paths to the code you need to analyze and all relevant context in your prompt. Your workflow begins by identifying the entry points and scope of the code, then meticulously analyzing the code structure and logic using the "read_file" tool. You must synthesize your findings into a comprehensive summary document. Your AI-verifiable outcome is the creation of this summary document at a specified path within 'docs/reports'. The report must cover the code's purpose, its main components, data flows, and potential areas for improvement or concern. After writing the report, you will use "attempt_completion". Your completion summary must be a full comprehensive natural language report detailing your comprehension process and findings, confirming the report's creation, and providing its file path. You should not produce any colon-separated signal text or structured signal proposals."""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute code comprehension analysis"""
        
        # Build prompt using base class
        prompt = self._build_agent_prompt(task, context)
        
        # Add specific instructions for code comprehension
        specific_prompt = f"""{prompt}

CODE COMPREHENSION ANALYSIS MISSION:
You are now performing a comprehensive code comprehension analysis. Your task is to:

1. ANALYSIS SCOPE:
   - Identify entry points and code boundaries
   - Understand the overall architecture and structure
   - Analyze data flows and dependencies
   - Examine functionality and behavior patterns

2. COMPREHENSIVE ANALYSIS AREAS:
   - Static structure: Classes, functions, modules, interfaces
   - Dynamic behavior: Control flow, data flow, interactions
   - Design patterns and architectural decisions
   - Code quality: Maintainability, readability, complexity
   - Performance considerations and bottlenecks
   - Security implications and vulnerabilities
   - Testing coverage and quality
   - Documentation accuracy and completeness

3. ANALYSIS PROCESS:
   - Read and analyze the specified code files
   - Map relationships between components
   - Identify critical paths and dependencies
   - Evaluate code quality and potential issues
   - Document findings in a structured manner

4. OUTPUT REQUIREMENTS:
   - Create a comprehensive code comprehension report
   - Save it in 'docs/reports' directory
   - Include visual diagrams where helpful
   - Provide actionable insights for improvement
   - Format for human programmer consumption

Remember: Focus on creating a clear, actionable report that helps human programmers understand the code's nature and identify areas for refinement.
"""
        
        # Use Claude via base class
        claude_response = await self._run_claude(specific_prompt)
        
        # Create comprehension report
        files_created = await self._create_comprehension_outputs(claude_response)
        
        # Record with State Scribe
        if files_created:
            await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "comprehension_analysis": claude_response,
                "files_created": files_created
            },
            files_created=files_created,
            files_modified=[],
            next_steps=["Review comprehension findings and plan refinement activities"]
        )
    
    async def _create_comprehension_outputs(self, claude_response: str) -> List[str]:
        """Create code comprehension report files"""
        files_created = []
        
        try:
            # Create docs/reports directory if it doesn't exist
            Path("docs/reports").mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = f"docs/reports/code_comprehension_report_{timestamp}.md"
            
            # Extract comprehension content from response
            comprehension_content = self._extract_comprehension_content(claude_response)
            
            # Write comprehension report
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(comprehension_content)
            
            files_created.append(report_path)
            
        except Exception as e:
            print(f"Error creating comprehension outputs: {str(e)}")
        
        return files_created
    
    def _extract_comprehension_content(self, claude_response: str) -> str:
        """Extract comprehension content from Claude response"""
        header = f"""# Code Comprehension Report
Generated: {datetime.now().isoformat()}
Agent: {self.agent_name}

## Executive Summary
This report provides a comprehensive analysis of the codebase structure, behavior, and quality to support refinement and maintenance activities.

## Analysis Methodology
1. Static Structure Analysis: Examined classes, functions, and modules
2. Dynamic Behavior Analysis: Analyzed control flow and data flow
3. Quality Assessment: Evaluated maintainability and potential issues
4. Recommendations: Identified areas for improvement

## Findings and Analysis

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
                "memory_type": "comprehension_report",
                "brief_description": "Code comprehension analysis report",
                "elements_description": "Comprehensive analysis of codebase structure, behavior, and quality",
                "rationale": "Provides understanding of code nature to support refinement and maintenance"
            })
        
        # Delegate to State Scribe
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record code comprehension analysis files in project memory",
            task_context={
                "files_to_record": files_to_record,
                "phase": "analysis"
            }
        )

async def main():
    """Main execution function"""
    agent = CodeComprehensionAssistantV2()
    
    # Example task
    task = TaskPayload(
        task_id="code_comprehension_analysis",
        description="Analyze codebase structure and behavior for comprehension report",
        requirements=["Analyze code structure, behavior, and quality"],
        ai_verifiable_outcomes=["Create detailed comprehension report in docs/reports"],
        phase="analysis",
        priority=3
    )
    
    result = await agent.execute(task)
    print(f"Code Comprehension Assistant v2 completed: {result.success}")
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
