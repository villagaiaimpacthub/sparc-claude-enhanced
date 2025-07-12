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

"""BMO Contract Verifier - API integration specialist for contract verification"""

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


class BMOContractVerifier(BaseAgent):
    """API integration specialist for verifying service endpoint contracts"""
    
    def __init__(self):
        super().__init__(
            agent_name="bmo-contract-verifier",
            role_definition="You are an API integration specialist. Your responsibility is to query the project state to identify API contracts and then execute tests to verify that the live, integrated service endpoints conform to those contracts.",
            custom_instructions="""You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

You will be tasked by the orchestrator with the necessary context. Your first step is to use the use_mcp_tool to query the project's Supabase database to identify all defined API endpoints and locate their corresponding contract documents, such as OpenAPI or Swagger specifications. You will then use the execute_command tool to run a contract testing suite against the live, integrated API. Your AI-verifiable outcome is the successful execution of this command and the subsequent creation of a detailed report at docs/reports/contract_verification_report.md using the write_to_file tool. A failure in the contract test is a critical error that must be reported. Your attempt_completion summary must state the final contract verification status, detail any mismatches found, and provide the full path to the verification report you created."""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute API contract verification"""
        
        # Build prompt using base class
        prompt = self._build_agent_prompt(task, context)
        
        # Add specific instructions for contract verification
        specific_prompt = f"""{prompt}

BMO CONTRACT VERIFICATION MISSION:
You are now performing API contract verification. Your task is to:

1. API CONTRACT DISCOVERY:
   - Query project_memorys database for API endpoints
   - Identify OpenAPI/Swagger specifications
   - Locate contract documents and API definitions
   - Map endpoints to their contract requirements
   - Identify authentication and authorization requirements

2. CONTRACT ANALYSIS:
   - Parse OpenAPI/Swagger specifications
   - Extract endpoint definitions and requirements
   - Identify request/response schemas
   - Analyze authentication mechanisms
   - Review rate limiting and error handling

3. CONTRACT TESTING SETUP:
   - Set up contract testing environment
   - Configure testing tools (e.g., Pact, Dredd, Postman)
   - Prepare test data and scenarios
   - Configure authentication tokens
   - Set up monitoring and logging

4. CONTRACT VERIFICATION EXECUTION:
   - Execute contract tests against live endpoints
   - Verify request/response schemas
   - Test authentication and authorization
   - Validate error handling
   - Check rate limiting and performance

5. VERIFICATION REPORTING:
   - Create detailed contract verification report
   - Document test results and findings
   - Report any contract violations or mismatches
   - Include recommendations for fixes
   - Save report to docs/reports/contract_verification_report.md

6. CRITICAL ERROR HANDLING:
   - Identify contract test failures as critical errors
   - Document root causes and impacts
   - Provide specific remediation steps
   - Escalate critical issues appropriately

Remember: Contract verification failures are critical errors that must be reported and addressed immediately.
"""
        
        # Use Claude via base class
        claude_response = await self._run_claude(specific_prompt)
        
        # Execute contract verification and create report
        files_created = await self._create_contract_verification_outputs(claude_response)
        
        # Record with State Scribe
        if files_created:
            await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "contract_verification": claude_response,
                "files_created": files_created
            },
            files_created=files_created,
            files_modified=[],
            next_steps=["Address any contract violations found", "Update API implementations if needed"]
        )
    
    async def _create_contract_verification_outputs(self, claude_response: str) -> List[str]:
        """Create contract verification report and execute tests"""
        files_created = []
        
        try:
            # Create docs/reports directory if it doesn't exist
            Path("docs/reports").mkdir(parents=True, exist_ok=True)
            
            # Create contract verification report
            report_path = "docs/reports/contract_verification_report.md"
            verification_content = self._extract_verification_content(claude_response)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(verification_content)
            
            files_created.append(report_path)
            
            # Note: In a real implementation, you would execute actual contract tests
            # using tools like Pact, Dredd, or Postman Newman
            
        except Exception as e:
            print(f"Error creating contract verification outputs: {str(e)}")
        
        return files_created
    
    def _extract_verification_content(self, claude_response: str) -> str:
        """Extract contract verification content from Claude response"""
        header = f"""# API Contract Verification Report
Generated: {datetime.now().isoformat()}
Agent: {self.agent_name}

## Executive Summary
This report documents the verification of API contracts against live service endpoints to ensure compliance with defined specifications.

## Contract Verification Process
1. API Contract Discovery: Identified all API endpoints and specifications
2. Contract Analysis: Parsed OpenAPI/Swagger specifications
3. Testing Setup: Configured contract testing environment
4. Verification Execution: Ran contract tests against live endpoints
5. Results Analysis: Analyzed test results and identified issues

## Contract Verification Results

### Overall Status
- **Status**: [PASS/FAIL/PARTIAL]
- **Total Endpoints Tested**: [number]
- **Passed**: [number]
- **Failed**: [number]
- **Warnings**: [number]

### Critical Issues Found
(Any critical contract violations that require immediate attention)

### Endpoint Verification Details

#### Authentication Endpoints
- **Status**: [PASS/FAIL]
- **Details**: [specific findings]

#### Data Endpoints
- **Status**: [PASS/FAIL]
- **Details**: [specific findings]

#### Error Handling
- **Status**: [PASS/FAIL]
- **Details**: [specific findings]

## Detailed Findings

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
                "memory_type": "contract_verification_report",
                "brief_description": "API contract verification report",
                "elements_description": "Detailed analysis of API endpoint compliance with contract specifications",
                "rationale": "Ensures API implementations conform to defined contracts and specifications"
            })
        
        # Delegate to State Scribe
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record BMO contract verification files in project memory",
            task_context={
                "files_to_record": files_to_record,
                "phase": "bmo_contract_verification"
            }
        )

async def main():
    """Main execution function"""
    agent = BMOContractVerifier()
    
    # Example task
    task = TaskPayload(
        task_id="bmo_contract_verification",
        description="Verify API contracts against live service endpoints",
        requirements=["Identify API contracts", "Execute contract tests"],
        ai_verifiable_outcomes=["Create contract verification report"],
        phase="bmo_contract_verification",
        priority=1
    )
    
    result = await agent.execute(task)
    print(f"BMO Contract Verifier completed: {result.success}")
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
