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

"""Spec-To-TestPlan Converter Agent - Creates detailed test plans from specifications"""

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



class SpecToTestplanConverterAgent(BaseAgent):
    """Converts specifications to detailed test plans for granular testing"""
    
    def __init__(self):
        super().__init__(
            agent_name="spec-to-testplan-converter",
            role_definition="Your primary role is to produce a detailed Test Plan document for the granular testing of a specific feature or module. This plan is derived from the feature's specification, its detailed pseudocode, and the AI Verifiable End Results from the primary project planning document. Your test plan must emphasize interaction-based testing and define comprehensive strategies for regression, edge case, and chaos testing. Every task and phase within your plan must itself have an AI-verifiable completion criterion.",
            custom_instructions="""You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task. Before you answer, think through this problem step by step. When you write documents, you must avoid every '|' character and substitute it with '--', and also avoid patterns like ':---'. You will receive the name of the feature to plan for and all necessary context in the prompt. Your task is to design and write the test plan document in Markdown format. This document must explicitly define the test scope in terms of which specific AI Verifiable End Results are being targeted. It must detail the adoption of London School TDD principles, focusing on mocking collaborators and verifying observable outcomes. You must define strategies for recursive regression testing, edge case testing, and chaos testing. You will save this test plan to a specified path within the 'docs/test-plans/' directory. This action is your AI-verifiable outcome. Your "attempt_completion" summary must be a narrative confirming the test plan's completion, specifying its location, detailing its focus on AI-actionable outcomes, and outlining the incorporated strategies for recursive, edge case, and chaos testing, providing the final file path."""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute test plan conversion using Claude"""
        
        # Build comprehensive prompt for Claude
        prompt = self._build_agent_prompt(task, context)
        
        # Add test plan specific instructions
        testplan_prompt = f"""
{prompt}

TEST PLAN CONVERSION REQUIREMENTS:
Create a detailed test plan document from specifications. You must:

1. Define test scope targeting specific AI-verifiable outcomes
2. Adopt London School TDD principles with mocking
3. Design strategies for regression, edge case, and chaos testing
4. Ensure every test has AI-verifiable completion criteria
5. Focus on interaction-based testing and observable outcomes
6. Save test plan to 'docs/test-plans/' directory
7. Avoid using '|' characters and ':---' patterns in documents

Your output should include:
- Comprehensive test plan document
- Test scope and coverage strategy
- TDD approach with mocking strategy
- Regression and edge case testing plans
- Chaos testing methodology

Generate detailed test plan documentation.
"""
        
        # Use Claude via base class
        claude_response = await self._run_claude(testplan_prompt)
        
        # Create files based on response
        files_created = await self._create_testplan_files(claude_response)
        
        # Record files with State Scribe
        await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "testplan_created": True,
                "files_created": len(files_created),
                "files": files_created,
                "message": f"Created {len(files_created)} test plan files"
            },
            files_created=files_created,
            files_modified=[],
            next_steps=["Review test plan", "Implement test cases", "Execute test strategy"]
        )
    
    async def _create_testplan_files(self, claude_response: str) -> List[str]:
        """Create test plan files from Claude's response"""
        
        # Create test plans directory
        testplan_dir = Path("docs/test-plans")
        testplan_dir.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Create main test plan document
        main_testplan_path = testplan_dir / "main_test_plan.md"
        main_content = f"""# Main Test Plan

## Overview
This document provides a comprehensive test plan for granular testing of project features, emphasizing interaction-based testing and AI-verifiable outcomes.

## Test Plan Details
{claude_response}

## Test Scope
- **Unit Testing**: Individual component verification
- **Integration Testing**: Service interaction validation
- **End-to-End Testing**: Complete workflow verification
- **Regression Testing**: Continuous validation of existing functionality
- **Edge Case Testing**: Boundary condition verification
- **Chaos Testing**: Resilience and fault tolerance validation

## London School TDD Approach
- Mock external dependencies and collaborators
- Focus on behavior verification over state testing
- Verify observable outcomes and interactions
- Maintain test isolation and independence

## AI-Verifiable Outcomes
- All test cases have clear pass/fail criteria
- Test results are programmatically verifiable
- Coverage metrics are measurable
- Performance benchmarks are defined

---
*Generated by spec-to-testplan-converter agent*
"""
        
        main_testplan_path.write_text(main_content, encoding='utf-8')
        files_created.append(str(main_testplan_path))
        
        # Create specific test strategy documents
        test_strategies = [
            ("unit_test_strategy.md", "Unit Test Strategy", "Individual component testing approach"),
            ("integration_test_strategy.md", "Integration Test Strategy", "Service interaction testing approach"),
            ("regression_test_strategy.md", "Regression Test Strategy", "Continuous validation approach"),
            ("edge_case_test_strategy.md", "Edge Case Test Strategy", "Boundary condition testing approach"),
            ("chaos_test_strategy.md", "Chaos Test Strategy", "Resilience testing approach")
        ]
        
        for filename, title, description in test_strategies:
            strategy_path = testplan_dir / filename
            strategy_content = f"""# {title}

## Overview
{description}

## Strategy Details
{claude_response[:400]}...

## Test Approach
- **Preparation**: Set up test environment and fixtures
- **Execution**: Run tests with proper isolation
- **Verification**: Validate outcomes against expectations
- **Cleanup**: Restore system state after testing

## AI-Verifiable Criteria
- Test execution results are measurable
- Coverage metrics are tracked
- Performance benchmarks are monitored
- Failure patterns are identified

## Implementation Guidelines
- Follow TDD principles consistently
- Mock external dependencies appropriately
- Verify behavior through interactions
- Maintain test independence and repeatability

---
*Generated by spec-to-testplan-converter agent*
"""
            
            strategy_path.write_text(strategy_content, encoding='utf-8')
            files_created.append(str(strategy_path))
        
        return files_created
    
    async def _record_files_with_state_scribe(self, files_created: List[str]):
        """Record created files with State Scribe"""
        
        files_to_record = []
        for file_path in files_created:
            files_to_record.append({
                "file_path": file_path,
                "memory_type": "test_plan",
                "brief_description": f"Test plan file: {Path(file_path).name}",
                "elements_description": "Detailed test plan with TDD and verification strategies",
                "rationale": "Required for SPARC testing phase completion"
            })
        
        # Delegate to State Scribe
        if files_to_record:
            await self._delegate_task(
                to_agent="orchestrator-state-scribe",
                task_description="Record test plan files in project memory",
                task_context={"files_to_record": files_to_record},
                priority=8
            )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: uv run sparc/agents/writers/spec_to_testplan_converter.py <task_json>")
        sys.exit(1)
    
    task_json = sys.argv[1]
    task = json.loads(task_json)
    
    task_payload = TaskPayload(
        description=task.get("description", ""),
        context=task.get("context", {}),
        priority=task.get("priority", 5)
    )
    
    agent = SpecToTestplanConverterAgent()
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
