#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase",
#   "rich",
#   "pydantic",
#   "python-dotenv",
# ]
# ///

"""BMO Completion Phase Orchestrator"""

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


class BMOCompletionPhaseOrchestrator(BaseAgent):
    """Orchestrator for the BMO (Big Mental Object) Completion phase"""
    
    def __init__(self):
        super().__init__(
            agent_name="orchestrator-bmo-completion-phase",
            role_definition="You orchestrate the BMO completion phase, the final validation that ensures the implemented solution matches the original human intent. You coordinate comprehensive verification through multiple specialized BMO agents to validate intent alignment, generate holistic test suites, and provide final approval recommendations.",
            custom_instructions="""
You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

You orchestrate the BMO completion phase by:
1. Triangulating original intent against final implementation
2. Generating comprehensive validation test suites
3. Verifying contracts and behavioral expectations
4. Synthesizing system-wide mental model validation
5. Conducting end-to-end intent verification
6. Providing final holistic validation and approval recommendation

Your primary outputs:
- docs/bmo_validation_report.md (comprehensive validation report)
- docs/bmo_intent_analysis.md (intent triangulation analysis)
- docs/bmo_test_suite.md (BMO-generated test documentation)
- docs/bmo_contract_verification.md (contract validation results)
- docs/bmo_system_model.md (system mental model synthesis)
- tests/bmo_e2e/ (BMO end-to-end validation tests)

You delegate to:
- bmo-intent-triangulator for intent analysis
- bmo-test-suite-generator for comprehensive test generation
- bmo-contract-verifier for contract validation
- bmo-system-model-synthesizer for mental model creation
- bmo-e2e-test-generator for end-to-end validation
- bmo-holistic-intent-verifier for final verification

This phase requires human approval before proceeding to completion phases.
"""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute BMO completion phase"""
        
        # Check if phase already completed
        existing_bmo = await self._check_existing_bmo_validation(context)
        if existing_bmo["has_validation_report"]:
            return AgentResult(
                success=True,
                outputs={
                    "message": "BMO completion phase already complete",
                    "bmo_validation": existing_bmo
                },
                files_created=[],
                files_modified=[]
            )
        
        # Validate prerequisites
        prereqs = await self._validate_prerequisites(context)
        if not prereqs["valid"]:
            return AgentResult(
                success=False,
                outputs={"error": f"Prerequisites not met: {prereqs['missing']}"},
                files_created=[],
                files_modified=[],
                errors=[f"Prerequisites not met: {prereqs['missing']}"]
            )
        
        # Step 1: Triangulate original intent against implementation
        intent_triangulation_task_id = await self._delegate_task(
            to_agent="bmo-intent-triangulator",
            task_description="Triangulate original intent against final implementation",
            task_context={
                "original_goal": prereqs["original_goal"],
                "mutual_understanding": prereqs["mutual_understanding"],
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "implementation_summary": prereqs["implementation_summary"],
                "output_file": "docs/bmo_intent_analysis.md",
                "requirements": [
                    "Analyze alignment between original intent and implementation",
                    "Identify any drift or misalignment from original goals",
                    "Validate that core objectives have been met",
                    "Document intent preservation throughout development",
                    "Assess completeness of original vision realization"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/bmo_intent_analysis.md",
                    "Intent alignment analysis completed",
                    "Drift analysis documented",
                    "Objective completion validated",
                    "Vision realization assessed"
                ]
            },
            priority=10
        )
        
        # Step 2: Generate comprehensive BMO test suite
        bmo_test_generation_task_id = await self._delegate_task(
            to_agent="bmo-test-suite-generator",
            task_description="Generate comprehensive BMO validation test suite",
            task_context={
                "original_goal": prereqs["original_goal"],
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "implementation_summary": prereqs["implementation_summary"],
                "intent_analysis_task_id": intent_triangulation_task_id,
                "output_file": "docs/bmo_test_suite.md",
                "requirements": [
                    "Generate tests that validate original intent fulfillment",
                    "Create behavioral validation scenarios",
                    "Design user experience validation tests",
                    "Generate stress tests for core objectives",
                    "Create regression tests for intent preservation"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/bmo_test_suite.md",
                    "Intent validation tests generated",
                    "Behavioral scenarios created",
                    "UX validation tests documented",
                    "Regression tests for intent created"
                ]
            },
            priority=9
        )
        
        # Step 3: Verify contracts and behavioral expectations
        contract_verification_task_id = await self._delegate_task(
            to_agent="bmo-contract-verifier",
            task_description="Verify contracts and behavioral expectations",
            task_context={
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "implementation_summary": prereqs["implementation_summary"],
                "architecture_design": prereqs.get("architecture_design", ""),
                "intent_analysis_task_id": intent_triangulation_task_id,
                "output_file": "docs/bmo_contract_verification.md",
                "requirements": [
                    "Verify all specified contracts are implemented",
                    "Validate behavioral expectations are met",
                    "Check API contracts and interface compliance",
                    "Verify error handling and edge case contracts",
                    "Validate performance and scalability contracts"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/bmo_contract_verification.md",
                    "Contract compliance verified",
                    "Behavioral expectations validated",
                    "API contract compliance checked",
                    "Performance contracts verified"
                ]
            },
            priority=9
        )
        
        # Step 4: Synthesize system-wide mental model
        system_model_task_id = await self._delegate_task(
            to_agent="bmo-system-model-synthesizer",
            task_description="Synthesize comprehensive system mental model",
            task_context={
                "original_goal": prereqs["original_goal"],
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "architecture_design": prereqs.get("architecture_design", ""),
                "implementation_summary": prereqs["implementation_summary"],
                "intent_analysis_task_id": intent_triangulation_task_id,
                "output_file": "docs/bmo_system_model.md",
                "requirements": [
                    "Create comprehensive system mental model",
                    "Document system behavior and interactions",
                    "Model user experience and workflows",
                    "Synthesize emergent system properties",
                    "Document system boundaries and constraints"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/bmo_system_model.md",
                    "System mental model documented",
                    "System behaviors modeled",
                    "User workflows documented",
                    "System properties synthesized"
                ]
            },
            priority=8
        )
        
        # Step 5: Generate end-to-end BMO validation tests
        e2e_validation_task_id = await self._delegate_task(
            to_agent="bmo-e2e-test-generator",
            task_description="Generate end-to-end BMO validation tests",
            task_context={
                "original_goal": prereqs["original_goal"],
                "bmo_test_suite_task_id": bmo_test_generation_task_id,
                "system_model_task_id": system_model_task_id,
                "contract_verification_task_id": contract_verification_task_id,
                "output_directory": "tests/bmo_e2e/",
                "requirements": [
                    "Create end-to-end validation test scenarios",
                    "Implement user journey validation tests",
                    "Create system integration validation tests",
                    "Generate performance and scalability validation",
                    "Create intent preservation validation tests"
                ],
                "ai_verifiable_outcomes": [
                    "E2E validation tests created in tests/bmo_e2e/",
                    "User journey tests implemented",
                    "System integration tests created",
                    "Performance validation tests generated",
                    "Intent preservation tests implemented"
                ]
            },
            priority=8
        )
        
        # Step 6: Conduct holistic intent verification
        holistic_verification_task_id = await self._delegate_task(
            to_agent="bmo-holistic-intent-verifier",
            task_description="Conduct final holistic intent verification",
            task_context={
                "original_goal": prereqs["original_goal"],
                "intent_analysis_task_id": intent_triangulation_task_id,
                "contract_verification_task_id": contract_verification_task_id,
                "system_model_task_id": system_model_task_id,
                "e2e_validation_task_id": e2e_validation_task_id,
                "output_file": "docs/bmo_validation_report.md",
                "requirements": [
                    "Conduct comprehensive intent verification",
                    "Synthesize all BMO validation results",
                    "Provide final approval recommendation",
                    "Document any remaining gaps or concerns",
                    "Create final validation summary and next steps"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/bmo_validation_report.md",
                    "Intent verification completed",
                    "Validation results synthesized",
                    "Approval recommendation provided",
                    "Final validation summary created"
                ]
            },
            priority=10
        )
        
        # Wait for all tasks to complete
        all_tasks = [intent_triangulation_task_id, bmo_test_generation_task_id, 
                    contract_verification_task_id, system_model_task_id, 
                    e2e_validation_task_id, holistic_verification_task_id]
        completed_tasks = await self._wait_for_tasks(all_tasks)
        
        # Identify created documents
        documents_created = await self._identify_created_documents()
        
        if not documents_created:
            return AgentResult(
                success=False,
                outputs={"error": "No BMO validation documents were created"},
                files_created=[],
                files_modified=[],
                errors=["Failed to create required BMO validation documents"]
            )
        
        # Delegate to state scribe for recording
        await self._delegate_to_state_scribe(documents_created)
        
        # Parse validation results for approval decision
        validation_results = await self._parse_validation_results(documents_created)
        
        # Request approval
        approval_id = await self._request_approval("bmo-completion", {
            "documents": documents_created,
            "phase": "bmo-completion",
            "completed_tasks": completed_tasks,
            "validation_results": validation_results,
            "timestamp": datetime.now().isoformat()
        }, f"BMO completion phase finished. Final validation shows: {validation_results['summary']}. Please review the comprehensive validation report and approve if the implementation meets the original intent.")
        
        return AgentResult(
            success=True,
            outputs={
                "phase": "bmo-completion",
                "documents_created": documents_created,
                "completed_tasks": completed_tasks,
                "validation_results": validation_results,
                "approval_requested": approval_id,
                "next_phase": "maintenance",
                "message": "BMO completion phase finished, approval requested"
            },
            files_created=[doc["path"] for doc in documents_created],
            files_modified=[],
            next_steps=["Wait for human approval", "Proceed to maintenance phase if approved"]
        )
    
    async def _check_existing_bmo_validation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if BMO validation documents already exist"""
        project_files = context.get("project_state", {}).get("files", {})
        
        has_validation_report = any("bmo_validation_report.md" in path for path in project_files.keys())
        has_intent_analysis = any("bmo_intent_analysis.md" in path for path in project_files.keys())
        has_test_suite = any("bmo_test_suite.md" in path for path in project_files.keys())
        has_e2e_tests = any("tests/bmo_e2e/" in path for path in project_files.keys())
        
        return {
            "has_validation_report": has_validation_report,
            "has_intent_analysis": has_intent_analysis,
            "has_test_suite": has_test_suite,
            "has_e2e_tests": has_e2e_tests,
            "existing_files": list(project_files.keys())
        }
    
    async def _validate_prerequisites(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that implementation phase is complete"""
        project_files = context.get("project_state", {}).get("files", {})
        
        original_goal = None
        mutual_understanding = None
        comprehensive_spec = None
        implementation_summary = None
        architecture_design = None
        missing = []
        
        # Check for original goal (from mutual understanding)
        mutual_path = next((path for path in project_files.keys() if "Mutual_Understanding_Document.md" in path), None)
        if mutual_path:
            mutual_understanding = Path(mutual_path).read_text() if Path(mutual_path).exists() else None
            original_goal = mutual_understanding  # Contains original goal
        else:
            missing.append("Mutual Understanding Document")
        
        # Check for comprehensive specification
        spec_path = next((path for path in project_files.keys() if "comprehensive_spec.md" in path), None)
        if spec_path:
            comprehensive_spec = Path(spec_path).read_text() if Path(spec_path).exists() else None
        else:
            missing.append("Comprehensive Specification")
        
        # Check for implementation (source code)
        has_implementation = any("src/" in path for path in project_files.keys())
        if has_implementation:
            implementation_summary = "Implementation completed in src/ directory"
        else:
            missing.append("Implementation (src/ directory)")
        
        # Check for architecture design (optional)
        arch_path = next((path for path in project_files.keys() if "system_design.md" in path), None)
        if arch_path:
            architecture_design = Path(arch_path).read_text() if Path(arch_path).exists() else None
        
        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "original_goal": original_goal,
            "mutual_understanding": mutual_understanding,
            "comprehensive_spec": comprehensive_spec,
            "implementation_summary": implementation_summary,
            "architecture_design": architecture_design
        }
    
    async def _identify_created_documents(self) -> List[Dict[str, Any]]:
        """Identify which BMO validation documents were created"""
        docs_created = []
        
        # BMO validation documents
        bmo_docs = [
            ("docs/bmo_validation_report.md", "bmo_validation_report", "Comprehensive BMO validation report"),
            ("docs/bmo_intent_analysis.md", "bmo_intent_analysis", "Intent triangulation analysis"),
            ("docs/bmo_test_suite.md", "bmo_test_suite", "BMO test suite documentation"),
            ("docs/bmo_contract_verification.md", "bmo_contract_verification", "Contract verification results"),
            ("docs/bmo_system_model.md", "bmo_system_model", "System mental model synthesis")
        ]
        
        for path, doc_type, description in bmo_docs:
            if Path(path).exists():
                docs_created.append({
                    "path": path,
                    "type": doc_type,
                    "description": description,
                    "memory_type": "report"
                })
        
        # BMO E2E test files
        if Path("tests/bmo_e2e/").exists():
            for test_file in Path("tests/bmo_e2e/").rglob("*.py"):
                docs_created.append({
                    "path": str(test_file),
                    "type": "bmo_e2e_test",
                    "description": f"BMO E2E validation test: {test_file.name}",
                    "memory_type": "test"
                })
        
        # Additional BMO reports
        if Path("docs/reports").exists():
            for report_file in Path("docs/reports").glob("*bmo*.md"):
                docs_created.append({
                    "path": str(report_file),
                    "type": "bmo_report",
                    "description": f"BMO analysis report: {report_file.name}",
                    "memory_type": "report"
                })
        
        return docs_created
    
    async def _parse_validation_results(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse validation results from BMO documents"""
        validation_report_path = next((doc["path"] for doc in documents if doc["type"] == "bmo_validation_report"), None)
        
        if not validation_report_path or not Path(validation_report_path).exists():
            return {
                "summary": "Validation report not found",
                "approved": False,
                "concerns": ["Missing validation report"]
            }
        
        try:
            validation_content = Path(validation_report_path).read_text()
            
            # Simple heuristic parsing - in real implementation would be more sophisticated
            approved = "APPROVED" in validation_content.upper() or "RECOMMENDATION: APPROVE" in validation_content.upper()
            concerns = []
            
            # Look for concern indicators
            if "CONCERN" in validation_content.upper():
                concerns.append("Concerns identified in validation report")
            if "GAP" in validation_content.upper():
                concerns.append("Gaps identified in implementation")
            if "RISK" in validation_content.upper():
                concerns.append("Risks identified in validation")
            
            return {
                "summary": "Intent validation completed" if approved else "Validation concerns identified",
                "approved": approved,
                "concerns": concerns,
                "validation_content_length": len(validation_content)
            }
        except Exception as e:
            return {
                "summary": f"Error parsing validation results: {str(e)}",
                "approved": False,
                "concerns": ["Error parsing validation report"]
            }
    
    async def _delegate_to_state_scribe(self, documents: List[Dict[str, Any]]) -> None:
        """Delegate to state scribe to record documents"""
        files_to_record = []
        
        for doc in documents:
            files_to_record.append({
                "file_path": doc["path"],
                "memory_type": doc["memory_type"],
                "brief_description": doc["description"],
                "elements_description": f"Document type: {doc['type']}",
                "rationale": "Created during BMO completion phase"
            })
        
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record BMO validation documents",
            task_context={
                "files_to_record": files_to_record,
                "phase": "bmo-completion",
                "requirements": ["Record all files in project_memorys table"],
                "ai_verifiable_outcomes": ["All files recorded with appropriate version"]
            },
            priority=8
        )

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
