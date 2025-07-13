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

"""Specification Phase Orchestrator"""

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
    
    def _get_namespaced_path(self, path: str) -> str:
        """Create namespace-aware path to prevent project conflicts"""
        if path.startswith('/'):
            # Absolute path - don't modify
            return path
        return f"{self.project_id}/{path}"
    
    def _check_namespaced_file(self, path: str) -> bool:
        """Check if a namespaced file exists"""
        return Path(self._get_namespaced_path(path)).exists()
    
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


class SpecificationPhaseOrchestrator(BaseAgent):
    """Orchestrator for the Specification phase"""
    
    def __init__(self):
        super().__init__(
            agent_name="orchestrator-sparc-specification-phase",
            role_definition="You orchestrate the specification phase, creating comprehensive technical specifications based on the clarified goals. You delegate to specialist writer agents and ensure all functional and non-functional requirements are thoroughly documented.",
            custom_instructions="""
You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

You orchestrate the specification phase by:
1. Analyzing the mutual understanding document and constraints
2. Delegating to spec writers for comprehensive documentation
3. Creating detailed functional and non-functional requirements
4. Ensuring all requirements are measurable and testable
5. Coordinating with research agents for technical analysis
6. Requesting human approval before proceeding to pseudocode phase

Your primary outputs:
- docs/specifications/comprehensive_spec.md (detailed technical specification)
- docs/specifications/functional_requirements.md
- docs/specifications/non_functional_requirements.md
- docs/specifications/api_design.md (if applicable)

You delegate to:
- spec-writer-comprehensive for main specification
- spec-writer-from-examples for example-driven requirements
- research-planner-strategic for technical feasibility analysis
- devils-advocate-critical-evaluator for requirement validation

You coordinate but do NOT write files directly. You orchestrate the creation through delegation.
"""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute specification phase"""
        
        # Check if phase already completed
        existing_specs = await self._check_existing_specifications(context)
        if existing_specs["has_comprehensive_spec"]:
            return AgentResult(
                success=True,
                outputs={
                    "message": "Specification phase already complete",
                    "specifications": existing_specs
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
        
        # Step 1: Research technical feasibility
        research_task_id = await self._delegate_task(
            to_agent="research-planner-strategic",
            task_description="Analyze technical feasibility and research requirements",
            task_context={
                "project_goal": task.context.get("project_goal", task.description),
                "prerequisites_valid": prereqs["valid"],
                "research_focus": "technical_feasibility_analysis",
                "requirements": [
                    "Research technical approaches and frameworks",
                    "Identify potential architectural patterns",
                    "Analyze scalability and performance requirements",
                    "Document technical risks and mitigation strategies"
                ],
                "ai_verifiable_outcomes": [
                    "Technical feasibility report created",
                    "Framework recommendations documented",
                    "Performance requirements analyzed"
                ]
            },
            priority=9
        )
        
        # Step 2: Create comprehensive specification
        spec_task_id = await self._delegate_task(
            to_agent="spec-writer-comprehensive",
            task_description="Create comprehensive technical specification",
            task_context={
                "project_goal": task.context.get("project_goal", task.description),
                "prerequisites_valid": prereqs["valid"],
                "research_task_id": research_task_id,
                "output_file": self._get_namespaced_path("docs/specifications/comprehensive_spec.md"),
                "requirements": [
                    "Create detailed functional requirements",
                    "Define non-functional requirements",
                    "Specify system interfaces and APIs",
                    "Document data models and schemas",
                    "Define acceptance criteria for all features"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/specifications/comprehensive_spec.md",
                    "All functional requirements documented",
                    "Non-functional requirements specified",
                    "Acceptance criteria defined for all features"
                ]
            },
            priority=9
        )
        
        # Step 3: Create example-driven requirements
        examples_task_id = await self._delegate_task(
            to_agent="spec-writer-from-examples",
            task_description="Create example-driven requirements and use cases",
            task_context={
                "project_goal": task.context.get("project_goal", task.description),
                "comprehensive_spec_task_id": spec_task_id,
                "output_file": self._get_namespaced_path("docs/specifications/examples_and_use_cases.md"),
                "requirements": [
                    "Create concrete usage examples",
                    "Document user workflows",
                    "Define error handling scenarios",
                    "Specify edge cases and boundary conditions"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/specifications/examples_and_use_cases.md",
                    "Usage examples documented",
                    "User workflows specified",
                    "Edge cases identified"
                ]
            },
            priority=8
        )
        
        # Step 4: Critical evaluation of requirements
        review_task_id = await self._delegate_task(
            to_agent="devils-advocate-critical-evaluator",
            task_description="Critically evaluate and validate requirements",
            task_context={
                "spec_task_id": spec_task_id,
                "examples_task_id": examples_task_id,
                "evaluation_focus": "requirements_validation",
                "requirements": [
                    "Identify ambiguous requirements",
                    "Find gaps in functional coverage",
                    "Validate non-functional requirements",
                    "Assess testability of requirements",
                    "Check for conflicting requirements"
                ],
                "ai_verifiable_outcomes": [
                    "Requirements validation report created",
                    "Ambiguities identified and documented",
                    "Coverage gaps analyzed",
                    "Testability assessment completed"
                ]
            },
            priority=7
        )
        
        # Wait for all tasks to complete and validate outputs
        all_tasks = [research_task_id, spec_task_id, examples_task_id, review_task_id]
        completed_tasks = await self._wait_for_tasks(all_tasks)
        
        # Identify created documents
        documents_created = await self._identify_created_documents()
        
        if not documents_created:
            return AgentResult(
                success=False,
                outputs={"error": "No specification documents were created"},
                files_created=[],
                files_modified=[],
                errors=["Failed to create required specification documents"]
            )
        
        # Delegate to state scribe for recording
        await self._delegate_to_state_scribe(documents_created)
        
        # Request approval
        approval_id = await self._request_approval("specification", {
            "documents": documents_created,
            "phase": "specification",
            "completed_tasks": completed_tasks,
            "timestamp": datetime.now().isoformat()
        }, "Specification phase completed. Comprehensive technical specification created with functional requirements, non-functional requirements, and usage examples. Please review and approve to proceed to pseudocode phase.")
        
        return AgentResult(
            success=True,
            outputs={
                "phase": "specification",
                "documents_created": documents_created,
                "completed_tasks": completed_tasks,
                "approval_requested": approval_id,
                "next_phase": "pseudocode",
                "message": "Specification phase completed, approval requested"
            },
            files_created=[doc["path"] for doc in documents_created],
            files_modified=[],
            next_steps=["Wait for human approval", "Proceed to pseudocode phase"]
        )
    
    async def _check_existing_specifications(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if specification documents already exist"""
        project_files = context.get("project_state", {}).get("files", {})
        
        has_comprehensive = any("comprehensive_spec.md" in path for path in project_files.keys())
        has_examples = any("examples_and_use_cases.md" in path for path in project_files.keys())
        
        return {
            "has_comprehensive_spec": has_comprehensive,
            "has_examples": has_examples,
            "existing_files": list(project_files.keys())
        }
    
    async def _validate_prerequisites(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that goal clarification phase is complete - FIXED VERSION"""
        
        # Check for actual files on disk instead of context
        missing = []
        
        # Check for mutual understanding document
        mutual_path = Path(self._get_namespaced_path("docs/Mutual_Understanding_Document.md"))
        if not mutual_path.exists():
            missing.append("Mutual Understanding Document")
        
        # Check for constraints document  
        constraints_paths = [
            Path(self._get_namespaced_path("docs/specifications/constraints_and_anti_goals.md")),
            Path(self._get_namespaced_path("docs/constraints_and_anti_goals.md"))
        ]
        constraints_exists = any(path.exists() for path in constraints_paths)
        if not constraints_exists:
            missing.append("Constraints and Anti-goals Document")
        
        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "message": "All prerequisites met" if len(missing) == 0 else f"Missing: {', '.join(missing)}"
        }
    
    async def _identify_created_documents(self) -> List[Dict[str, Any]]:
        """Identify which specification documents were created"""
        docs_created = []
        
        # Check for comprehensive spec
        comprehensive_path = self._get_namespaced_path("docs/specifications/comprehensive_spec.md")
        if Path(comprehensive_path).exists():
            docs_created.append({
                "path": comprehensive_path,
                "type": "comprehensive_specification",
                "description": "Comprehensive technical specification",
                "memory_type": "specification"
            })
        
        # Check for examples and use cases
        examples_path = self._get_namespaced_path("docs/specifications/examples_and_use_cases.md")
        if Path(examples_path).exists():
            docs_created.append({
                "path": examples_path,
                "type": "examples_use_cases",
                "description": "Examples and use cases specification",
                "memory_type": "specification"
            })
        
        # Check for research reports
        research_dir = Path(self._get_namespaced_path("docs/research"))
        research_files = list(research_dir.glob("*.md")) if research_dir.exists() else []
        for research_file in research_files:
            docs_created.append({
                "path": str(research_file),
                "type": "research_report",
                "description": "Technical research and feasibility analysis",
                "memory_type": "research"
            })
        
        return docs_created
    
    async def _delegate_to_state_scribe(self, documents: List[Dict[str, Any]]) -> None:
        """Delegate to state scribe to record documents"""
        files_to_record = []
        
        for doc in documents:
            files_to_record.append({
                "file_path": doc["path"],
                "memory_type": doc["memory_type"],
                "brief_description": doc["description"],
                "elements_description": f"Document type: {doc['type']}",
                "rationale": "Created during specification phase"
            })
        
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record specification documents",
            task_context={
                "files_to_record": files_to_record,
                "phase": "specification",
                "requirements": ["Record all files in project_memorys table"],
                "ai_verifiable_outcomes": ["All files recorded with appropriate version"]
            ,
                "requesting_agent": self.agent_name},
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
    agent = SpecificationPhaseOrchestrator()
    
    async def run():
        try:
            result = await agent._execute_task(task, task.context)
            console.print(f"[green]✅ {agent.agent_name} completed successfully[/green]")
            console.print(f"Result: {result}")
        except Exception as e:
            console.print(f"[red]❌ {agent.agent_name} failed: {e}[/red]")
    
    asyncio.run(run())

if __name__ == "__main__":
    main()
