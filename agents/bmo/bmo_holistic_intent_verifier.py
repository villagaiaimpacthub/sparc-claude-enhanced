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

"""BMO Holistic Intent Verifier - Final arbiter of correctness using cognitive triangulation"""

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


class BMOHolisticIntentVerifier(BaseAgent):
    """Final arbiter of correctness using cognitive triangulation principles"""
    
    def __init__(self):
        super().__init__(
            agent_name="bmo-holistic-intent-verifier",
            role_definition="You are the final arbiter of correctness, acting as a holistic verifier of user intent by applying the principles of Cognitive Triangulation. Your role is to perform a three-way comparison between the specified user intent (Behavior), the documented system implementation (Model), and the observed test results (Oracle). Your purpose is to uncover not just functional bugs, but any misalignment between what the user wanted, what the developers built, and what the system actually does.",
            custom_instructions="""You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

You will be tasked by the BMO orchestrator to perform the final verification. Your process is a strict three-step triangulation. First, you must use the read_file tool to ingest the 'Behavior' layer from the Gherkin files in tests/bdd/ and the 'Model' layer from docs/bmo/system_model.md. Second, you must establish the 'Oracle' layer by using the execute_command tool to run the entire end-to-end test suite located in tests/e2e/. Third, you must conduct a deep analysis comparing these three sources. Your AI-verifiable outcome is the creation of a comprehensive report at docs/reports/bmo_triangulation_report.md using the write_to_file tool. This report must explicitly detail your findings, highlighting not only test failures but also any discrepancies found, such as a feature being implemented differently than modeled (Model-Oracle mismatch) or a user behavior not being covered by any implementation (Behavior-Model mismatch). Your attempt_completion summary must provide a clear status of the triangulation, detailing any and all discrepancies found between Behavior, Model, and Oracle, and provide the path to your comprehensive report."""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute holistic intent verification using cognitive triangulation"""
        
        # Build prompt using base class
        prompt = self._build_agent_prompt(task, context)
        
        # Add specific instructions for holistic verification
        specific_prompt = f"""{prompt}

BMO HOLISTIC INTENT VERIFICATION MISSION:
You are now performing the final verification using cognitive triangulation. Your task is to:

1. THREE-LAYER TRIANGULATION SETUP:
   - **Behavior Layer**: Read Gherkin files from tests/bdd/ (user intent)
   - **Model Layer**: Read system model from docs/bmo/system_model.md (implementation)
   - **Oracle Layer**: Execute E2E tests from tests/e2e/ (actual behavior)

2. BEHAVIOR LAYER ANALYSIS:
   - Parse all Gherkin .feature files
   - Extract user scenarios and expected behaviors
   - Identify all user requirements and acceptance criteria
   - Map user journeys and interaction patterns
   - Document complete user intent specification

3. MODEL LAYER ANALYSIS:
   - Read comprehensive system model document
   - Understand implemented architecture and components
   - Identify actual system capabilities and limitations
   - Map implementation details to user requirements
   - Analyze system design decisions and trade-offs

4. ORACLE LAYER ESTABLISHMENT:
   - Execute complete E2E test suite
   - Capture all test results and outputs
   - Analyze test failures and successes
   - Document actual system behavior
   - Identify performance and quality metrics

5. TRIANGULATION ANALYSIS:
   - **Behavior-Model Comparison**: Does the implementation match user intent?
   - **Model-Oracle Comparison**: Does the system behave as implemented?
   - **Behavior-Oracle Comparison**: Does the system meet user expectations?
   - **Three-way Alignment**: Are all three layers consistent?

6. DISCREPANCY IDENTIFICATION:
   - **Behavior-Model Mismatch**: User requirements not implemented
   - **Model-Oracle Mismatch**: Implementation differs from documentation
   - **Behavior-Oracle Mismatch**: System doesn't meet user expectations
   - **Missing Coverage**: User behaviors not tested or implemented
   - **Implementation Gaps**: Features documented but not working

7. COMPREHENSIVE REPORTING:
   - Create detailed triangulation report
   - Document all discrepancies and mismatches
   - Provide specific remediation recommendations
   - Include evidence and supporting data
   - Save to docs/reports/bmo_triangulation_report.md

8. FINAL VERIFICATION STATUS:
   - **PASS**: 100% alignment between all three layers
   - **FAIL**: Critical misalignments requiring immediate attention
   - **PARTIAL**: Minor issues that can be addressed

Remember: You are looking for ANY misalignment between what was wanted, what was built, and what actually works.
"""
        
        # Use Claude via base class
        claude_response = await self._run_claude(specific_prompt)
        
        # Create triangulation report
        files_created = await self._create_triangulation_outputs(claude_response)
        
        # Record with State Scribe
        if files_created:
            await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "triangulation_verification": claude_response,
                "files_created": files_created
            },
            files_created=files_created,
            files_modified=[],
            next_steps=["Address any discrepancies found", "Complete BMO verification process"]
        )
    
    async def _create_triangulation_outputs(self, claude_response: str) -> List[str]:
        """Create comprehensive triangulation report"""
        files_created = []
        
        try:
            # Create docs/reports directory if it doesn't exist
            Path("docs/reports").mkdir(parents=True, exist_ok=True)
            
            # Create BMO triangulation report
            report_path = "docs/reports/bmo_triangulation_report.md"
            triangulation_content = self._extract_triangulation_content(claude_response)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(triangulation_content)
            
            files_created.append(report_path)
            
        except Exception as e:
            print(f"Error creating triangulation outputs: {str(e)}")
        
        return files_created
    
    def _extract_triangulation_content(self, claude_response: str) -> str:
        """Extract triangulation content from Claude response"""
        header = f"""# BMO Triangulation Report
Generated: {datetime.now().isoformat()}
Agent: {self.agent_name}

## Executive Summary
This report presents the final verification results using cognitive triangulation principles, comparing user intent (Behavior), system implementation (Model), and actual system behavior (Oracle).

## Triangulation Overview
The BMO framework uses three-way comparison to ensure complete alignment:
- **Behavior**: User intent from Gherkin specifications
- **Model**: System implementation from documentation
- **Oracle**: Actual system behavior from E2E tests

## Triangulation Process
1. **Behavior Layer Analysis**: Analyzed user intent from Gherkin files
2. **Model Layer Analysis**: Reviewed system model documentation
3. **Oracle Layer Establishment**: Executed E2E test suite
4. **Three-way Comparison**: Compared all layers for alignment
5. **Discrepancy Analysis**: Identified mismatches and gaps

## Triangulation Results

### Overall Verification Status
- **Status**: [PASS/FAIL/PARTIAL]
- **Behavior-Model Alignment**: [percentage]
- **Model-Oracle Alignment**: [percentage]
- **Behavior-Oracle Alignment**: [percentage]
- **Overall Alignment**: [percentage]

### Critical Discrepancies
(Any critical misalignments requiring immediate attention)

### Detailed Triangulation Analysis

#### Behavior-Model Comparison
Analysis of user intent vs. system implementation:

#### Model-Oracle Comparison
Analysis of documented system vs. actual behavior:

#### Behavior-Oracle Comparison
Analysis of user expectations vs. system reality:

### Discrepancy Summary

#### Behavior-Model Mismatches
- User requirements not implemented
- Implementation differs from user intent
- Missing features or functionality

#### Model-Oracle Mismatches
- System behaves differently than documented
- Implementation bugs or errors
- Performance discrepancies

#### Behavior-Oracle Mismatches
- System doesn't meet user expectations
- Functional gaps in user workflows
- User experience issues

### Remediation Recommendations

#### Immediate Actions Required
(Critical issues that must be addressed)

#### Suggested Improvements
(Non-critical enhancements for better alignment)

#### Future Considerations
(Long-term improvements and optimizations)

## Detailed Analysis

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
                "memory_type": "triangulation_report",
                "brief_description": "BMO triangulation verification report",
                "elements_description": "Comprehensive three-way comparison of user intent, system model, and actual behavior",
                "rationale": "Final verification using cognitive triangulation to ensure complete alignment between all BMO components"
            })
        
        # Delegate to State Scribe
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record BMO triangulation verification files in project memory",
            task_context={
                "files_to_record": files_to_record,
                "phase": "bmo_triangulation"
            }
        )

async def main():
    """Main execution function"""
    agent = BMOHolisticIntentVerifier()
    
    # Example task
    task = TaskPayload(
        task_id="bmo_triangulation_verification",
        description="Perform final verification using cognitive triangulation",
        requirements=["Compare Behavior, Model, and Oracle layers", "Identify discrepancies"],
        ai_verifiable_outcomes=["Create BMO triangulation report"],
        phase="bmo_triangulation",
        priority=1
    )
    
    result = await agent.execute(task)
    print(f"BMO Holistic Intent Verifier completed: {result.success}")
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
