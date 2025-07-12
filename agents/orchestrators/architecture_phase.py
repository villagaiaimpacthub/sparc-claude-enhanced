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

"""Architecture Phase Orchestrator"""

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


class ArchitecturePhaseOrchestrator(BaseAgent):
    """Orchestrator for the Architecture phase"""
    
    def __init__(self):
        super().__init__(
            agent_name="orchestrator-sparc-architecture-phase",
            role_definition="You orchestrate the architecture phase, creating comprehensive system design documentation. You translate specifications and pseudocode into detailed architectural blueprints that guide implementation and deployment.",
            custom_instructions="""
You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

You orchestrate the architecture phase by:
1. Analyzing specifications and pseudocode to understand system requirements
2. Designing high-level system architecture and component interactions
3. Creating detailed module and interface specifications
4. Defining deployment and infrastructure requirements
5. Ensuring architectural decisions support scalability and maintainability
6. Requesting human approval before proceeding to implementation phases

Your primary outputs:
- docs/architecture/system_design.md (comprehensive system architecture)
- docs/architecture/component_interfaces.md (detailed interface specifications)
- docs/architecture/deployment_architecture.md (deployment and infrastructure)
- docs/architecture/data_architecture.md (data flow and storage design)
- docs/architecture/security_architecture.md (security considerations)

You delegate to:
- architect-highlevel-module for system design creation
- security-reviewer-module for security architecture analysis
- optimizer-module for performance architecture optimization
- devils-advocate-critical-evaluator for architecture validation

You coordinate but do NOT write files directly. You orchestrate the creation through delegation.
"""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute architecture phase"""
        
        # Check if phase already completed
        existing_architecture = await self._check_existing_architecture(context)
        if existing_architecture["has_system_design"]:
            return AgentResult(
                success=True,
                outputs={
                    "message": "Architecture phase already complete",
                    "architecture": existing_architecture
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
        
        # Step 1: Create high-level system architecture
        system_design_task_id = await self._delegate_task(
            to_agent="architect-highlevel-module",
            task_description="Create comprehensive system architecture design",
            task_context={
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "pseudocode_summary": prereqs["pseudocode_summary"],
                "constraints": prereqs.get("constraints", ""),
                "output_file": "docs/architecture/system_design.md",
                "architecture_focus": "system_design",
                "requirements": [
                    "Design high-level system architecture",
                    "Define component relationships and dependencies",
                    "Specify communication patterns and protocols",
                    "Document architectural patterns and principles",
                    "Create system topology and layer definitions"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/architecture/system_design.md",
                    "System components defined and documented",
                    "Component relationships specified",
                    "Communication patterns documented",
                    "Architectural patterns identified"
                ]
            },
            priority=9
        )
        
        # Step 2: Create component interfaces specification
        interfaces_task_id = await self._delegate_task(
            to_agent="architect-highlevel-module",
            task_description="Create detailed component interfaces specification",
            task_context={
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "pseudocode_summary": prereqs["pseudocode_summary"],
                "system_design_task_id": system_design_task_id,
                "output_file": "docs/architecture/component_interfaces.md",
                "architecture_focus": "component_interfaces",
                "requirements": [
                    "Define all component interfaces and contracts",
                    "Specify API endpoints and data formats",
                    "Document service boundaries and responsibilities",
                    "Create interface versioning strategy",
                    "Define error handling and fault tolerance"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/architecture/component_interfaces.md",
                    "All component interfaces defined",
                    "API contracts documented",
                    "Service boundaries specified",
                    "Error handling strategies defined"
                ]
            },
            priority=8
        )
        
        # Step 3: Create deployment architecture
        deployment_task_id = await self._delegate_task(
            to_agent="architect-highlevel-module",
            task_description="Create deployment and infrastructure architecture",
            task_context={
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "constraints": prereqs.get("constraints", ""),
                "system_design_task_id": system_design_task_id,
                "output_file": "docs/architecture/deployment_architecture.md",
                "architecture_focus": "deployment_infrastructure",
                "requirements": [
                    "Design deployment topology and infrastructure",
                    "Define scaling strategies and load balancing",
                    "Specify monitoring and logging architecture",
                    "Document backup and disaster recovery",
                    "Create CI/CD pipeline architecture"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/architecture/deployment_architecture.md",
                    "Deployment topology documented",
                    "Scaling strategies defined",
                    "Monitoring architecture specified",
                    "CI/CD pipeline designed"
                ]
            },
            priority=8
        )
        
        # Step 4: Create data architecture
        data_architecture_task_id = await self._delegate_task(
            to_agent="architect-highlevel-module",
            task_description="Create data architecture and flow design",
            task_context={
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "pseudocode_summary": prereqs["pseudocode_summary"],
                "system_design_task_id": system_design_task_id,
                "output_file": "docs/architecture/data_architecture.md",
                "architecture_focus": "data_architecture",
                "requirements": [
                    "Design data storage and persistence layer",
                    "Define data flow and processing pipelines",
                    "Specify data synchronization and consistency",
                    "Document data migration and versioning",
                    "Create data backup and archival strategy"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/architecture/data_architecture.md",
                    "Data storage architecture defined",
                    "Data flow pipelines documented",
                    "Consistency strategies specified",
                    "Migration plans created"
                ]
            },
            priority=7
        )
        
        # Step 5: Security architecture review
        security_task_id = await self._delegate_task(
            to_agent="security-reviewer-module",
            task_description="Create security architecture and threat analysis",
            task_context={
                "system_design_task_id": system_design_task_id,
                "interfaces_task_id": interfaces_task_id,
                "deployment_task_id": deployment_task_id,
                "output_file": "docs/architecture/security_architecture.md",
                "security_focus": "architecture_security",
                "requirements": [
                    "Perform architecture security threat analysis",
                    "Define authentication and authorization architecture",
                    "Specify encryption and data protection measures",
                    "Document security monitoring and incident response",
                    "Create security compliance and audit strategies"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/architecture/security_architecture.md",
                    "Threat analysis completed",
                    "Authentication architecture defined",
                    "Encryption strategies specified",
                    "Security monitoring designed"
                ]
            },
            priority=7
        )
        
        # Step 6: Performance optimization analysis
        optimization_task_id = await self._delegate_task(
            to_agent="optimizer-module",
            task_description="Analyze and optimize architecture for performance",
            task_context={
                "system_design_task_id": system_design_task_id,
                "data_architecture_task_id": data_architecture_task_id,
                "deployment_task_id": deployment_task_id,
                "optimization_focus": "architecture_performance",
                "requirements": [
                    "Analyze architecture for performance bottlenecks",
                    "Recommend caching and optimization strategies",
                    "Define performance monitoring and metrics",
                    "Create capacity planning recommendations",
                    "Document performance tuning guidelines"
                ],
                "ai_verifiable_outcomes": [
                    "Performance analysis report created",
                    "Optimization recommendations documented",
                    "Monitoring metrics defined",
                    "Capacity planning completed"
                ]
            },
            priority=6
        )
        
        # Step 7: Critical architecture validation
        validation_task_id = await self._delegate_task(
            to_agent="devils-advocate-critical-evaluator",
            task_description="Validate architecture design and identify potential issues",
            task_context={
                "system_design_task_id": system_design_task_id,
                "interfaces_task_id": interfaces_task_id,
                "deployment_task_id": deployment_task_id,
                "security_task_id": security_task_id,
                "evaluation_focus": "architecture_validation",
                "requirements": [
                    "Validate architecture against requirements",
                    "Identify architectural inconsistencies",
                    "Assess scalability and maintainability",
                    "Review technology choices and trade-offs",
                    "Identify potential failure points and risks"
                ],
                "ai_verifiable_outcomes": [
                    "Architecture validation report created",
                    "Inconsistencies identified and documented",
                    "Scalability assessment completed",
                    "Risk analysis performed"
                ]
            },
            priority=6
        )
        
        # Wait for all tasks to complete
        all_tasks = [system_design_task_id, interfaces_task_id, deployment_task_id, 
                    data_architecture_task_id, security_task_id, optimization_task_id, validation_task_id]
        completed_tasks = await self._wait_for_tasks(all_tasks)
        
        # Identify created documents
        documents_created = await self._identify_created_documents()
        
        if not documents_created:
            return AgentResult(
                success=False,
                outputs={"error": "No architecture documents were created"},
                files_created=[],
                files_modified=[],
                errors=["Failed to create required architecture documents"]
            )
        
        # Delegate to state scribe for recording
        await self._delegate_to_state_scribe(documents_created)
        
        # Request approval
        approval_id = await self._request_approval("architecture", {
            "documents": documents_created,
            "phase": "architecture",
            "completed_tasks": completed_tasks,
            "timestamp": datetime.now().isoformat()
        }, "Architecture phase completed. Comprehensive system design created with component interfaces, deployment architecture, data architecture, and security considerations. Please review and approve to proceed to implementation phases.")
        
        return AgentResult(
            success=True,
            outputs={
                "phase": "architecture",
                "documents_created": documents_created,
                "completed_tasks": completed_tasks,
                "approval_requested": approval_id,
                "next_phase": "refinement-testing",
                "message": "Architecture phase completed, approval requested"
            },
            files_created=[doc["path"] for doc in documents_created],
            files_modified=[],
            next_steps=["Wait for human approval", "Proceed to refinement-testing phase"]
        )
    
    async def _check_existing_architecture(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if architecture documents already exist"""
        project_files = context.get("project_state", {}).get("files", {})
        
        has_system_design = any("system_design.md" in path for path in project_files.keys())
        has_interfaces = any("component_interfaces.md" in path for path in project_files.keys())
        has_deployment = any("deployment_architecture.md" in path for path in project_files.keys())
        has_security = any("security_architecture.md" in path for path in project_files.keys())
        
        return {
            "has_system_design": has_system_design,
            "has_interfaces": has_interfaces,
            "has_deployment": has_deployment,
            "has_security": has_security,
            "existing_files": list(project_files.keys())
        }
    
    async def _validate_prerequisites(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that pseudocode phase is complete"""
        project_files = context.get("project_state", {}).get("files", {})
        
        comprehensive_spec = None
        pseudocode_summary = None
        constraints = None
        missing = []
        
        # Check for comprehensive specification
        spec_path = next((path for path in project_files.keys() if "comprehensive_spec.md" in path), None)
        if spec_path:
            comprehensive_spec = Path(spec_path).read_text() if Path(spec_path).exists() else None
        else:
            missing.append("Comprehensive Specification")
        
        # Check for pseudocode (at least main algorithms)
        pseudocode_path = next((path for path in project_files.keys() if "main_algorithms.md" in path), None)
        if pseudocode_path:
            pseudocode_summary = Path(pseudocode_path).read_text() if Path(pseudocode_path).exists() else None
        else:
            missing.append("Main Algorithms Pseudocode")
        
        # Check for constraints (optional)
        constraints_path = next((path for path in project_files.keys() if "constraints_and_anti_goals.md" in path), None)
        if constraints_path:
            constraints = Path(constraints_path).read_text() if Path(constraints_path).exists() else None
        
        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "comprehensive_spec": comprehensive_spec,
            "pseudocode_summary": pseudocode_summary,
            "constraints": constraints
        }
    
    async def _identify_created_documents(self) -> List[Dict[str, Any]]:
        """Identify which architecture documents were created"""
        docs_created = []
        
        architecture_files = [
            ("docs/architecture/system_design.md", "system_design", "Comprehensive system architecture design"),
            ("docs/architecture/component_interfaces.md", "component_interfaces", "Component interfaces and contracts"),
            ("docs/architecture/deployment_architecture.md", "deployment_architecture", "Deployment and infrastructure architecture"),
            ("docs/architecture/data_architecture.md", "data_architecture", "Data architecture and flow design"),
            ("docs/architecture/security_architecture.md", "security_architecture", "Security architecture and threat analysis")
        ]
        
        for path, doc_type, description in architecture_files:
            if Path(path).exists():
                docs_created.append({
                    "path": path,
                    "type": doc_type,
                    "description": description,
                    "memory_type": "architecture"
                })
        
        # Check for additional architecture files
        if Path("docs/architecture").exists():
            for arch_file in Path("docs/architecture").glob("*.md"):
                file_path = str(arch_file)
                if not any(doc["path"] == file_path for doc in docs_created):
                    docs_created.append({
                        "path": file_path,
                        "type": "additional_architecture",
                        "description": f"Additional architecture: {arch_file.name}",
                        "memory_type": "architecture"
                    })
        
        # Check for reports
        if Path("docs/reports").exists():
            for report_file in Path("docs/reports").glob("*architecture*.md"):
                docs_created.append({
                    "path": str(report_file),
                    "type": "architecture_report",
                    "description": f"Architecture analysis report: {report_file.name}",
                    "memory_type": "report"
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
                "rationale": "Created during architecture phase"
            })
        
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record architecture documents",
            task_context={
                "files_to_record": files_to_record,
                "phase": "architecture",
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
