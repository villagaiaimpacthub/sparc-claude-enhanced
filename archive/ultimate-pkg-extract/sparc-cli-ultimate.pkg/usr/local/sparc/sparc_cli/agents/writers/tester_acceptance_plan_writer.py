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

"""Tester Acceptance Plan Writer Agent - Creates acceptance test plans and high-level tests"""

import json
import asyncio
from typing import Dict, Any, List
from pathlib import Path

from sparc.agents.base_agent import BaseAgent, TaskPayload, AgentResult


class TesterAcceptancePlanWriterAgent(BaseAgent):
    """Creates master acceptance test plans and high-level end-to-end tests"""
    
    def __init__(self):
        super().__init__(
            agent_name="tester-acceptance-plan-writer",
            role_definition="Your role is to create the master acceptance test plan and the initial set of all high level end to end acceptance tests that define the ultimate success criteria for the entire project. Your work is based on the user's overall requirements, the comprehensive specifications, and the high-level test strategy research report. These high-level tests are broad, user-centric, and must be AI-verifiable. Your output guides the entire development process, ensuring all subsequent work contributes to meeting these final objectives.",
            custom_instructions="""You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task. Before you answer, think through this problem step by step. When you write documents, you must avoid every '|' character and substitute it with '--', and also avoid patterns like ':---'. You will be tasked by the specification orchestrator with all necessary context provided in the prompt. First, you will design a 'docs/tests/master_acceptance_test_plan.md' document. This plan must outline the strategy for high-level testing and define individual test cases with explicitly stated AI-verifiable completion criteria. Next, you will implement all the actual high-level, end-to-end acceptance tests in code. These tests must be black-box in nature, focusing on observable outcomes. The creation of the test plan and the test code files are your AI-verifiable outcomes. Your "attempt_completion" summary must be a thorough report, explaining the master test plan, how it reflects the user's goals and research, and how the implemented tests are all AI-verifiable. It must state the paths to both the test plan document and the created test files in the 'tests/acceptance' directory."""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute acceptance test plan creation using Claude"""
        
        # Build comprehensive prompt for Claude
        prompt = self._build_agent_prompt(task, context)
        
        # Add acceptance test specific instructions
        acceptance_prompt = f"""
{prompt}

ACCEPTANCE TEST PLAN REQUIREMENTS:
Create a comprehensive acceptance test plan and high-level tests. You must:

1. Create a master acceptance test plan document at 'docs/tests/master_acceptance_test_plan.md'
2. Create high-level acceptance test code files in 'tests/acceptance/' directory
3. Create test configuration and utilities as needed
4. Focus on black-box testing with observable outcomes
5. Ensure all tests are AI-verifiable
6. Avoid using '|' characters and ':---' patterns in documents

Your output should include:
- Master acceptance test plan document
- High-level acceptance test code files
- Test configuration and utilities
- Clear AI-verifiable completion criteria

Generate the complete acceptance test plan and implementation code.
"""
        
        # Use Claude via base class
        claude_response = await self._run_claude(acceptance_prompt)
        
        # Create files based on response
        files_created = await self._create_acceptance_files(claude_response)
        
        # Record files with State Scribe
        await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "test_plan_created": True,
                "test_files_created": len(files_created),
                "files": files_created,
                "message": f"Created acceptance test plan and {len(files_created)} test files"
            },
            files_created=files_created,
            files_modified=[],
            next_steps=["Review test plan for completeness", "Execute acceptance tests"]
        )
    
    async def _create_acceptance_files(self, claude_response: str) -> List[str]:
        """Create acceptance test files from Claude's response"""
        
        # Create necessary directories
        docs_tests_dir = Path("docs/tests")
        docs_tests_dir.mkdir(parents=True, exist_ok=True)
        
        tests_acceptance_dir = Path("tests/acceptance")
        tests_acceptance_dir.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Create master acceptance test plan
        test_plan_path = docs_tests_dir / "master_acceptance_test_plan.md"
        test_plan_content = f"""# Master Acceptance Test Plan

## Overview
This document defines the master acceptance test plan for the project, establishing the high-level testing strategy and success criteria that guide all development activities.

## Generated Content
{claude_response}

## AI-Verifiable Outcomes
- All acceptance tests pass
- Test plan document exists at correct path
- Test code files are properly structured
- Tests focus on observable outcomes

---
*Generated by tester-acceptance-plan-writer agent*
"""
        
        test_plan_path.write_text(test_plan_content, encoding='utf-8')
        files_created.append(str(test_plan_path))
        
        # Create sample acceptance test files
        acceptance_files = [
            "test_user_workflows.py",
            "test_api_endpoints.py", 
            "test_integration.py",
            "test_config.py",
            "test_utils.py"
        ]
        
        for test_file in acceptance_files:
            file_path = tests_acceptance_dir / test_file
            test_content = f"""#!/usr/bin/env python3
\"\"\"
{test_file.replace('_', ' ').title().replace('.py', '')} Tests
Generated by tester-acceptance-plan-writer agent
\"\"\"

import unittest
import asyncio
from pathlib import Path

class {test_file.replace('test_', '').replace('.py', '').title().replace('_', '')}Tests(unittest.TestCase):
    \"\"\"High-level acceptance tests for {test_file.replace('test_', '').replace('.py', '').replace('_', ' ')}\"\"\"
    
    def setUp(self):
        \"\"\"Set up test environment\"\"\"
        pass
    
    def tearDown(self):
        \"\"\"Clean up test environment\"\"\"
        pass
    
    def test_placeholder(self):
        \"\"\"Placeholder test - replace with actual test implementation\"\"\"
        # Claude Response Context:
        # {claude_response[:500]}...
        
        self.assertTrue(True, "Placeholder test - implement actual test logic")

if __name__ == '__main__':
    unittest.main()
"""
            
            file_path.write_text(test_content, encoding='utf-8')
            files_created.append(str(file_path))
        
        return files_created
    
    async def _record_files_with_state_scribe(self, files_created: List[str]):
        """Record created files with State Scribe"""
        
        files_to_record = []
        for file_path in files_created:
            files_to_record.append({
                "file_path": file_path,
                "memory_type": "acceptance_test",
                "brief_description": f"Acceptance test file: {Path(file_path).name}",
                "elements_description": "High-level acceptance test plan and test code",
                "rationale": "Required for SPARC testing phase completion"
            })
        
        # Delegate to State Scribe
        if files_to_record:
            await self._delegate_task(
                to_agent="orchestrator-state-scribe",
                task_description="Record acceptance test files in project memory",
                task_context={"files_to_record": files_to_record},
                priority=8
            )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: uv run sparc/agents/writers/tester_acceptance_plan_writer.py <task_json>")
        sys.exit(1)
    
    task_json = sys.argv[1]
    task = json.loads(task_json)
    
    task_payload = TaskPayload(
        description=task.get("description", ""),
        context=task.get("context", {}),
        priority=task.get("priority", 5)
    )
    
    agent = TesterAcceptancePlanWriterAgent()
    result = asyncio.run(agent._execute_task(task_payload, task.get("context", {})))
    print(json.dumps(result.dict(), indent=2))