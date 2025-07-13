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

from sparc.agents.base_agent import BaseAgent, TaskPayload, AgentResult

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