#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase",
#   "rich",
#   "pydantic",
#   "python-dotenv",
#   "click",
# ]
# ///

"""Refinement Testing Orchestrator"""

import os
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
    
    async def _delegate_task(self, to_agent: str, task_description: str, 
                           task_context: Dict[str, Any], priority: int = 5) -> str:
        """Delegate task to another agent"""
        return await self.delegate_task(to_agent, task_description, task_context, priority)

    async def _wait_for_tasks(self, task_ids: List[str]) -> Dict[str, Any]:
        """Wait for delegated tasks to complete - placeholder implementation"""
        return {task_id: {"success": True, "output": f"Mock completion for {task_id}"} for task_id in task_ids}

    async def _request_approval(self, phase_name: str, artifacts: Dict[str, Any], message: str = "") -> str:
        """Request approval for phase completion - placeholder implementation"""
        approval_id = f"approval_request_{phase_name}_{datetime.now().isoformat()}"
        return approval_id

    @abstractmethod
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        pass


class RefinementTestingOrchestrator(BaseAgent):
    """Orchestrator for the Refinement Testing phase"""
    
    def __init__(self):
        super().__init__(
            agent_name="orchestrator-sparc-refinement-testing",
            role_definition="You orchestrate the refinement testing phase, creating comprehensive test suites that drive the implementation process. You establish the testing foundation that ensures quality and correctness throughout development.",
            custom_instructions="""
You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

You orchestrate the refinement testing phase by:
1. Creating comprehensive test plans based on specifications and architecture
2. Implementing test-driven development approach with failing tests first
3. Establishing test automation and continuous integration workflows
4. Creating acceptance criteria and validation frameworks
5. Coordinating with chaos engineering for resilience testing
6. Ensuring test coverage meets quality standards

Your primary outputs:
- tests/unit/ (comprehensive unit test suite)
- tests/integration/ (integration test suite)
- tests/e2e/ (end-to-end test suite)
- docs/testing/test_plan.md (comprehensive test strategy)
- docs/testing/acceptance_criteria.md (acceptance testing framework)
- tests/chaos/ (chaos engineering tests)

You delegate to:
- tester-tdd-master for TDD orchestration and test creation
- tester-acceptance-plan-writer for acceptance criteria
- spec-to-testplan-converter for specification-driven test planning
- chaos-engineer for resilience and chaos testing
- edge-case-synthesizer for edge case test coverage

You coordinate but do NOT write files directly. You orchestrate the creation through delegation.
"""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute refinement testing phase"""
        
        # Check if phase already completed
        existing_tests = await self._check_existing_tests(context)
        if existing_tests["has_test_plan"] and existing_tests["has_unit_tests"]:
            return AgentResult(
                success=True,
                outputs={
                    "message": "Refinement testing phase already complete",
                    "tests": existing_tests
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
        
        # Step 1: Create comprehensive test plan from specifications
        test_plan_task_id = await self._delegate_task(
            to_agent="spec-to-testplan-converter",
            task_description="Convert specifications to comprehensive test plan",
            task_context={
                "prerequisites_valid": prereqs["valid"],
                "output_file": "docs/testing/test_plan.md",
                "requirements": [
                    "Create comprehensive test strategy and plan",
                    "Define test categories and coverage targets",
                    "Specify test environments and configurations",
                    "Document test data management strategy",
                    "Create test automation and CI/CD integration plan"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/testing/test_plan.md",
                    "Test strategy documented",
                    "Coverage targets defined",
                    "Test environments specified",
                    "Automation plan created"
                ]
            },
            priority=9
        )
        
        # Step 2: Create acceptance criteria and validation framework
        acceptance_task_id = await self._delegate_task(
            to_agent="tester-acceptance-plan-writer",
            task_description="Create acceptance criteria and validation framework",
            task_context={
                "prerequisites_valid": prereqs["valid"],
                "test_plan_task_id": test_plan_task_id,
                "output_file": "docs/testing/acceptance_criteria.md",
                "requirements": [
                    "Define acceptance criteria for all features",
                    "Create user acceptance testing scenarios",
                    "Specify validation and verification procedures",
                    "Document quality gates and success metrics",
                    "Create traceability matrix for requirements"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/testing/acceptance_criteria.md",
                    "Acceptance criteria defined for all features",
                    "UAT scenarios documented",
                    "Quality gates specified",
                    "Traceability matrix created"
                ]
            },
            priority=9
        )
        
        # Step 3: Implement TDD-driven test suite creation
        tdd_task_id = await self._delegate_task(
            to_agent="tester-tdd-master",
            task_description="Create TDD-driven test suite with failing tests",
            task_context={
                "prerequisites_valid": prereqs["valid"],
                "prerequisites_valid": prereqs["valid"],
                "test_plan_task_id": test_plan_task_id,
                "acceptance_task_id": acceptance_task_id,
                "test_suite_focus": "comprehensive_tdd",
                "requirements": [
                    "Create failing unit tests for all specified functionality",
                    "Implement integration test framework",
                    "Set up test fixtures and mock objects",
                    "Create test utilities and helpers",
                    "Establish test naming and organization conventions"
                ],
                "ai_verifiable_outcomes": [
                    "Unit test files created in tests/unit/",
                    "Integration test framework in tests/integration/",
                    "Test fixtures and utilities implemented",
                    "All tests initially failing (red state)",
                    "Test organization follows conventions"
                ]
            },
            priority=9
        )
        
        # Step 4: Create end-to-end test scenarios
        e2e_task_id = await self._delegate_task(
            to_agent="tester-tdd-master",
            task_description="Create end-to-end test scenarios and framework",
            task_context={
                "prerequisites_valid": prereqs["valid"],
                "prerequisites_valid": prereqs["valid"],
                "acceptance_task_id": acceptance_task_id,
                "test_suite_focus": "e2e_scenarios",
                "requirements": [
                    "Create end-to-end test scenarios",
                    "Implement E2E test framework and infrastructure",
                    "Set up test data and environment management",
                    "Create user journey and workflow tests",
                    "Implement cross-browser and device testing"
                ],
                "ai_verifiable_outcomes": [
                    "E2E test files created in tests/e2e/",
                    "Test framework infrastructure implemented",
                    "User journey tests defined",
                    "Cross-platform test coverage established"
                ]
            },
            priority=8
        )
        
        # Step 5: Create edge case and boundary testing
        edge_case_task_id = await self._delegate_task(
            to_agent="edge-case-synthesizer",
            task_description="Create edge case and boundary condition tests",
            task_context={
                "prerequisites_valid": prereqs["valid"],
                "tdd_task_id": tdd_task_id,
                "test_focus": "edge_cases_boundary_conditions",
                "requirements": [
                    "Identify and create tests for edge cases",
                    "Implement boundary condition testing",
                    "Create negative test scenarios",
                    "Test error handling and recovery",
                    "Implement stress and load testing scenarios"
                ],
                "ai_verifiable_outcomes": [
                    "Edge case tests created",
                    "Boundary condition tests implemented",
                    "Negative test scenarios defined",
                    "Error handling tests created",
                    "Stress test scenarios implemented"
                ]
            },
            priority=8
        )
        
        # Step 6: Implement chaos engineering and resilience testing
        chaos_task_id = await self._delegate_task(
            to_agent="chaos-engineer",
            task_description="Create chaos engineering and resilience tests",
            task_context={
                "prerequisites_valid": prereqs["valid"],
                "test_plan_task_id": test_plan_task_id,
                "chaos_testing_focus": "system_resilience",
                "requirements": [
                    "Design chaos engineering experiments",
                    "Create failure injection scenarios",
                    "Implement network partition and latency tests",
                    "Test service degradation and recovery",
                    "Create monitoring and alerting validation"
                ],
                "ai_verifiable_outcomes": [
                    "Chaos engineering tests created in tests/chaos/",
                    "Failure injection scenarios implemented",
                    "Network resilience tests defined",
                    "Service degradation tests created",
                    "Monitoring validation tests implemented"
                ]
            },
            priority=7
        )
        
        # Step 7: Create performance and load testing
        performance_task_id = await self._delegate_task(
            to_agent="tester-tdd-master",
            task_description="Create performance and load testing suite",
            task_context={
                "prerequisites_valid": prereqs["valid"],
                "prerequisites_valid": prereqs["valid"],
                "test_suite_focus": "performance_load",
                "requirements": [
                    "Create performance benchmark tests",
                    "Implement load testing scenarios",
                    "Set up performance monitoring and profiling",
                    "Create scalability and capacity tests",
                    "Implement memory and resource usage tests"
                ],
                "ai_verifiable_outcomes": [
                    "Performance tests created in tests/performance/",
                    "Load testing scenarios implemented",
                    "Benchmark tests defined",
                    "Resource usage tests created",
                    "Scalability tests implemented"
                ]
            },
            priority=7
        )
        
        # Wait for all tasks to complete
        all_tasks = [test_plan_task_id, acceptance_task_id, tdd_task_id, e2e_task_id, 
                    edge_case_task_id, chaos_task_id, performance_task_id]
        completed_tasks = await self._wait_for_tasks(all_tasks)
        
        # Identify created documents and test files
        documents_created = await self._identify_created_documents()
        
        if not documents_created:
            return AgentResult(
                success=False,
                outputs={"error": "No test documents or files were created"},
                files_created=[],
                files_modified=[],
                errors=["Failed to create required test suite"]
            )
        
        # Delegate to state scribe for recording
        await self._delegate_to_state_scribe(documents_created)
        
        # Validate test suite completeness
        validation_result = await self._validate_test_suite(documents_created)
        
        return AgentResult(
            success=True,
            outputs={
                "phase": "refinement-testing",
                "documents_created": documents_created,
                "completed_tasks": completed_tasks,
                "test_validation": validation_result,
                "next_phase": "refinement-implementation",
                "message": "Refinement testing phase completed successfully"
            },
            files_created=[doc["path"] for doc in documents_created],
            files_modified=[],
            next_steps=["Proceed to refinement-implementation phase", "Begin TDD development cycle"]
        )
    
    async def _check_existing_tests(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if test documents and files already exist"""
        project_files = context.get("project_state", {}).get("files", {})
        
        has_test_plan = any("test_plan.md" in path for path in project_files.keys())
        has_unit_tests = any("tests/unit/" in path for path in project_files.keys())
        has_integration_tests = any("tests/integration/" in path for path in project_files.keys())
        has_e2e_tests = any("tests/e2e/" in path for path in project_files.keys())
        has_chaos_tests = any("tests/chaos/" in path for path in project_files.keys())
        
        return {
            "has_test_plan": has_test_plan,
            "has_unit_tests": has_unit_tests,
            "has_integration_tests": has_integration_tests,
            "has_e2e_tests": has_e2e_tests,
            "has_chaos_tests": has_chaos_tests,
            "existing_files": list(project_files.keys())
        }
    
    async def _validate_prerequisites(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that architecture phase is complete - FIXED VERSION"""
        
        # Check for actual files on disk instead of context
        missing = []
        
        # Check for comprehensive specification
        spec_paths = [
            Path("docs/specifications/comprehensive_spec.md"),
            Path("docs/comprehensive_spec.md")
        ]
        spec_exists = any(path.exists() for path in spec_paths)
        if not spec_exists:
            missing.append("Comprehensive Specification")
        
        # Check for architecture design files
        arch_paths = [
            Path("docs/architecture/system_design.md"),
            Path("docs/architecture/system_architecture.md"),
            Path("docs/architecture/deployment_architecture.md")
        ]
        arch_exists = any(path.exists() for path in arch_paths)
        if not arch_exists:
            missing.append("System Architecture Design")
        
        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "message": "All prerequisites met" if len(missing) == 0 else f"Missing: {', '.join(missing)}"
        }
    
    async def _identify_created_documents(self) -> List[Dict[str, Any]]:
        """Identify which test documents and files were created"""
        docs_created = []
        
        # Test documentation
        test_docs = [
            ("docs/testing/test_plan.md", "test_plan", "Comprehensive test strategy and plan"),
            ("docs/testing/acceptance_criteria.md", "acceptance_criteria", "Acceptance criteria and validation framework")
        ]
        
        for path, doc_type, description in test_docs:
            if Path(path).exists():
                docs_created.append({
                    "path": path,
                    "type": doc_type,
                    "description": description,
                    "memory_type": "test"
                })
        
        # Test files in different directories
        test_directories = [
            ("tests/unit/", "unit_test", "Unit test"),
            ("tests/integration/", "integration_test", "Integration test"),
            ("tests/e2e/", "e2e_test", "End-to-end test"),
            ("tests/chaos/", "chaos_test", "Chaos engineering test"),
            ("tests/performance/", "performance_test", "Performance test")
        ]
        
        for test_dir, test_type, description in test_directories:
            if Path(test_dir).exists():
                for test_file in Path(test_dir).rglob("*.py"):
                    docs_created.append({
                        "path": str(test_file),
                        "type": test_type,
                        "description": f"{description}: {test_file.name}",
                        "memory_type": "test"
                    })
        
        # Additional test configuration files
        test_config_files = [
            "pytest.ini", "conftest.py", "test_requirements.txt", 
            "tests/fixtures/", "tests/utils/", "tests/config/"
        ]
        
        for config_path in test_config_files:
            if Path(config_path).exists():
                if Path(config_path).is_file():
                    docs_created.append({
                        "path": config_path,
                        "type": "test_config",
                        "description": f"Test configuration: {config_path}",
                        "memory_type": "configuration"
                    })
                else:
                    for config_file in Path(config_path).rglob("*"):
                        if config_file.is_file():
                            docs_created.append({
                                "path": str(config_file),
                                "type": "test_config",
                                "description": f"Test configuration: {config_file.name}",
                                "memory_type": "configuration"
                            })
        
        return docs_created
    
    async def _validate_test_suite(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate test suite completeness"""
        test_types = set(doc["type"] for doc in documents)
        
        required_types = {"test_plan", "unit_test"}
        recommended_types = {"integration_test", "e2e_test", "acceptance_criteria"}
        
        missing_required = required_types - test_types
        missing_recommended = recommended_types - test_types
        
        return {
            "complete": len(missing_required) == 0,
            "missing_required": list(missing_required),
            "missing_recommended": list(missing_recommended),
            "test_types_present": list(test_types),
            "total_test_files": len([doc for doc in documents if "test" in doc["type"]])
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
                "rationale": "Created during refinement testing phase"
            })
        
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record test documents and files",
            task_context={
                "files_to_record": files_to_record,
                "phase": "refinement-testing",
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
    agent_class_names = [name for name in globals() if name.endswith('Agent') or name.endswith('Orchestrator')]
    # Prefer concrete orchestrator over BaseAgent
    concrete_agent = next((name for name in agent_class_names if 'Phase' in name or 'Orchestrator' in name and name != 'BaseAgent'), None)
    agent_class_name = concrete_agent or agent_class_names[0] if agent_class_names else None
    
    if agent_class_name:
        agent_class = globals()[agent_class_name]
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
