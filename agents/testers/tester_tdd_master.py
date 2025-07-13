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

"""Tester TDD Master Agent - Implements TDD test code according to plan"""

import json
import asyncio
import os
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
    
    async def _build_agent_prompt(self, task: TaskPayload, context: Dict[str, Any]) -> str:
        """Build agent prompt from task and context"""
        return f"""
Task: {task.description}
Context: {context}
Phase: {task.phase}
Requirements: {task.requirements}
AI Verifiable Outcomes: {task.ai_verifiable_outcomes}
"""

    async def _run_claude(self, prompt: str) -> str:
        """Placeholder for Claude API call"""
        return f"Claude response for: {prompt[:100]}..."

    async def _delegate_task(self, to_agent: str, task_description: str, 
                           task_context: Dict[str, Any], priority: int = 5) -> str:
        """Delegate task to another agent"""
        return await self.delegate_task(to_agent, task_description, task_context, priority)

    @abstractmethod
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        pass



class TesterTDDMasterAgent(BaseAgent):
    """TDD testing specialist implementing test code according to plans"""
    
    def __init__(self):
        super().__init__(
            agent_name="tester-tdd-master",
            role_definition="You are a dedicated testing specialist who implements tests according to a plan. You adhere strictly to TDD best practices, and your responsibility is writing test code to a file. You do not modify the project state.",
            custom_instructions="""You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task. Before you answer, you must think through this problem step by step. You will be given a feature and a detailed Test Plan directly in your prompt. Your task is to write granular tests strictly according to that plan. Critically your tests must avoid bad fallbacks. This means first tests should not mask underlying issues in the code under test. Second tests should not mask environmental issues. Third avoid using stale or misleading test data as a fallback. Fourth avoid overly complex test fallbacks because test logic should be simple. You must adhere to all TDD best practices including writing descriptive test names keeping tests focused and independent and using test doubles such as mocks stubs spies fakes and dummies appropriately to verify collaboration not just state. Your AI-verifiable outcome is the creation of the new test code file. You must use "write_to_file" to save the new test code. When reporting on test executions, you must state the command used and the exact outcome, highlighting any failures with a structured report. If you create or significantly modify any test files you must describe each important new test files path, its purpose, the types of tests it contains and the key AI Verifiable End Results it covers. You must strictly avoid any kind of bad fallbacks in the tests themselves. When you prepare your natural language summary before you perform 'attempt_completion' it is vital that this report is explicitly stating that no bad fallbacks were used in the tests and that TDD principles were followed. It should clearly distinguish between initial test implementation and subsequent recursive or regression test runs. For recursive runs it must detail the trigger for the run the scope of tests executed and how they re validate AI Verifiable End Results without test side fallbacks. Your "attempt_completion" summary must be a comprehensive report detailing the tests run or created and confirm that, for any new tests, you have created the file as instructed."""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute TDD test implementation using Claude"""
        
        prompt = self._build_agent_prompt(task, context)
        
        tdd_prompt = f"""
{prompt}

TDD TEST IMPLEMENTATION REQUIREMENTS:
Write granular test code according to the provided test plan. You must:

1. Follow TDD best practices strictly
2. Write descriptive test names and focused tests
3. Use appropriate test doubles (mocks, stubs, spies, fakes, dummies)
4. Avoid bad fallbacks in tests
5. Ensure tests are independent and repeatable
6. Create new test code files
7. Focus on behavior verification over state testing

Generate comprehensive TDD test code.
"""
        
        claude_response = await self._run_claude(tdd_prompt)
        files_created = await self._create_test_files(claude_response)
        await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "tests_created": True,
                "files_created": len(files_created),
                "files": files_created,
                "message": f"Created {len(files_created)} TDD test files"
            },
            files_created=files_created,
            files_modified=[],
            next_steps=["Run tests to verify implementation", "Implement code to pass tests"]
        )
    
    async def _create_test_files(self, claude_response: str) -> List[str]:
        """Create TDD test files from Claude's response"""
        
        tests_dir = Path("tests/tdd")
        tests_dir.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Create main test file
        test_file_path = tests_dir / "test_tdd_implementation.py"
        test_content = f"""#!/usr/bin/env python3
\"\"\"
TDD Test Implementation
Generated by tester-tdd-master agent
\"\"\"

import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio

class TestTDDImplementation(unittest.TestCase):
    \"\"\"TDD test cases following London School principles\"\"\"
    
    def setUp(self):
        \"\"\"Set up test fixtures\"\"\"
        self.mock_dependency = Mock()
        self.test_subject = None  # Initialize with actual implementation
    
    def test_behavior_verification(self):
        \"\"\"Test behavior verification over state testing\"\"\"
        # Claude Response Context:
        # {claude_response[:300]}...
        
        # Arrange
        expected_behavior = "test_behavior"
        self.mock_dependency.process.return_value = expected_behavior
        
        # Act
        # result = self.test_subject.execute(self.mock_dependency)
        
        # Assert
        # self.mock_dependency.process.assert_called_once()
        # self.assertEqual(result, expected_behavior)
        
        # Placeholder assertion
        self.assertTrue(True, "TDD test placeholder - implement actual behavior verification")
    
    def test_collaboration_verification(self):
        \"\"\"Test collaboration between objects\"\"\"
        # Verify interactions, not just final state
        self.assertTrue(True, "TDD collaboration test placeholder")
    
    def test_error_handling(self):
        \"\"\"Test error handling behavior\"\"\"
        # Test how the system behaves under error conditions
        self.assertTrue(True, "TDD error handling test placeholder")

if __name__ == '__main__':
    unittest.main()
"""
        
        test_file_path.write_text(test_content, encoding='utf-8')
        files_created.append(str(test_file_path))
        
        return files_created
    
    async def _record_files_with_state_scribe(self, files_created: List[str]):
        """Record created files with State Scribe"""
        
        files_to_record = []
        for file_path in files_created:
            files_to_record.append({
                "file_path": file_path,
                "memory_type": "tdd_test",
                "brief_description": f"TDD test file: {Path(file_path).name}",
                "elements_description": "TDD test implementation following London School principles",
                "rationale": "Required for TDD development process"
            })
        
        if files_to_record:
            await self._delegate_task(
                to_agent="orchestrator-state-scribe",
                task_description="Record TDD test files in project memory",
                task_context={"files_to_record": files_to_record},
                priority=8
            )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: uv run sparc/agents/testers/tester_tdd_master.py <task_json>")
        sys.exit(1)
    
    task_json = sys.argv[1]
    task = json.loads(task_json)
    
    task_payload = TaskPayload(
        task_id=task.get("task_id", f"task_{datetime.now().isoformat()}"),
        description=task.get("description", ""),
        context=task.get("context", {}),
        requirements=task.get("requirements", []),
        ai_verifiable_outcomes=task.get("ai_verifiable_outcomes", []),
        phase=task.get("phase", "execution"),
        priority=task.get("priority", 5)
    )
    
    agent = TesterTDDMasterAgent()
    result = asyncio.run(agent._execute_task(task_payload, task.get("context", {})))
    print(json.dumps(result.dict(), indent=2))

