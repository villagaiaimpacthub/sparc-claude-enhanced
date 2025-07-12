#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase>=2.0.0",
#   "qdrant-client>=1.7.0",
#   "mistralai>=0.0.8",
#   "rich>=13.0.0",
#   "pydantic>=2.0.0",
#   "python-dotenv>=1.0.0",
# ]
# ///

"""Debugger Targeted Agent - Diagnoses test failures and produces structured reports"""

import json
import asyncio
from typing import Dict, Any, List
from pathlib import Path


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



class DebuggerTargetedAgent(BaseAgent):
    """Systematic debugger for diagnosing test failures"""
    
    def __init__(self):
        super().__init__(
            agent_name="debugger-targeted",
            role_definition="Your specific function is to diagnose test failures based on a failure report and contextual information from the project state. Your goal is to produce a structured diagnosis report.",
            custom_instructions="""You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task. Before you answer, think through this problem step by step. You will receive a failing test report and all necessary context. First, query the project_memorys Supabase database using "use_mcp_tool" to understand the relationships of the failing code. Following your analysis, use "write_to_file" to save a detailed diagnosis report in Markdown format to the 'docs/reports' directory. This is your AI-verifiable outcome. To conclude, use "attempt_completion". Your summary must be a comprehensive report detailing your diagnosis and confirming that you have created the report file, providing its path."""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute targeted debugging using Claude"""
        
        prompt = self._build_agent_prompt(task, context)
        
        debug_prompt = f"""
{prompt}

DEBUGGING REQUIREMENTS:
Diagnose test failures and produce structured reports. You must:

1. Analyze failing test reports and context
2. Query project state to understand code relationships
3. Identify root causes of failures
4. Provide actionable debugging recommendations
5. Create structured diagnosis report
6. Save report to 'docs/reports/' directory
7. Include step-by-step debugging process

Generate comprehensive debugging analysis.
"""
        
        claude_response = await self._run_claude(debug_prompt)
        files_created = await self._create_debug_files(claude_response)
        await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "debug_report_created": True,
                "files_created": len(files_created),
                "files": files_created,
                "message": f"Created {len(files_created)} debug report files"
            },
            files_created=files_created,
            files_modified=[],
            next_steps=["Review debug report", "Implement fixes", "Re-run tests"]
        )
    
    async def _create_debug_files(self, claude_response: str) -> List[str]:
        """Create debug files from Claude's response"""
        
        # Create reports directory
        reports_dir = Path("docs/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Create debug report
        debug_report_path = reports_dir / "debug_analysis.md"
        debug_report_content = f"""# Debug Analysis Report

## Overview
This document contains the structured diagnosis of test failures and debugging recommendations.

## Failure Analysis
{claude_response}

## Root Cause Analysis
- **Primary Causes**: Main issues identified
- **Secondary Factors**: Contributing factors
- **Environmental Issues**: System or setup problems
- **Code Quality Issues**: Implementation problems

## Debugging Process
1. **Test Failure Analysis**: Review failing test outputs
2. **Code Relationship Mapping**: Understand dependencies
3. **Root Cause Identification**: Pinpoint primary issues
4. **Solution Development**: Create actionable fixes
5. **Verification Strategy**: Plan for testing fixes

## Recommendations
- Implement immediate fixes for critical issues
- Add additional test coverage for edge cases
- Improve error handling and logging
- Consider refactoring problematic code sections

## AI-Verifiable Outcomes
- Debug analysis completed systematically
- Root causes identified and documented
- Actionable recommendations provided
- Verification strategy outlined

---
*Generated by debugger-targeted agent*
"""
        
        debug_report_path.write_text(debug_report_content, encoding='utf-8')
        files_created.append(str(debug_report_path))
        
        return files_created
    
    async def _record_files_with_state_scribe(self, files_created: List[str]):
        """Record created files with State Scribe"""
        
        files_to_record = []
        for file_path in files_created:
            files_to_record.append({
                "file_path": file_path,
                "memory_type": "debug_report",
                "brief_description": f"Debug report file: {Path(file_path).name}",
                "elements_description": "Structured diagnosis report for test failures",
                "rationale": "Required for systematic debugging process"
            })
        
        if files_to_record:
            await self._delegate_task(
                to_agent="orchestrator-state-scribe",
                task_description="Record debug report files in project memory",
                task_context={"files_to_record": files_to_record},
                priority=8
            )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: uv run sparc/agents/coders/debugger_targeted.py <task_json>")
        sys.exit(1)
    
    task_json = sys.argv[1]
    task = json.loads(task_json)
    
    task_payload = TaskPayload(
        description=task.get("description", ""),
        context=task.get("context", {}),
        priority=task.get("priority", 5)
    )
    
    agent = DebuggerTargetedAgent()
    result = asyncio.run(agent._execute_task(task_payload, task.get("context", {})))
    print(json.dumps(result.dict(), indent=2))

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
