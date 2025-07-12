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

"""Completion Maintenance Orchestrator"""

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


class CompletionMaintenanceOrchestrator(BaseAgent):
    """Orchestrator for the Completion Maintenance phase"""
    
    def __init__(self):
        super().__init__(
            agent_name="orchestrator-sparc-completion-maintenance",
            role_definition="You orchestrate the completion maintenance phase, ensuring the delivered solution is maintainable, deployable, and ready for production. You coordinate the creation of operational documentation, deployment procedures, and maintenance frameworks.",
            custom_instructions="""
You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

You orchestrate the completion maintenance phase by:
1. Creating comprehensive deployment and operations documentation
2. Setting up monitoring, logging, and alerting systems
3. Establishing backup and disaster recovery procedures
4. Creating maintenance runbooks and troubleshooting guides
5. Setting up automated deployment and CI/CD pipelines
6. Documenting scaling and performance optimization procedures

Your primary outputs:
- docs/operations/deployment_guide.md (comprehensive deployment procedures)
- docs/operations/monitoring_setup.md (monitoring and alerting configuration)
- docs/operations/backup_recovery.md (backup and disaster recovery procedures)
- docs/operations/maintenance_runbook.md (operational maintenance procedures)
- docs/operations/troubleshooting_guide.md (issue resolution procedures)
- docs/operations/scaling_guide.md (scaling and performance procedures)
- deploy/ (deployment scripts and configurations)
- monitoring/ (monitoring and alerting configurations)

You delegate to:
- docs-writer-feature for operational documentation
- architect-highlevel-module for deployment architecture
- security-reviewer-module for operational security
- optimizer-module for performance and scaling guidance
- chaos-engineer for operational resilience testing

You coordinate but do NOT write files directly. You orchestrate the creation through delegation.
"""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute completion maintenance phase"""
        
        # Check if phase already completed
        existing_maintenance = await self._check_existing_maintenance(context)
        if existing_maintenance["has_deployment_guide"] and existing_maintenance["has_monitoring_setup"]:
            return AgentResult(
                success=True,
                outputs={
                    "message": "Completion maintenance phase already complete",
                    "maintenance": existing_maintenance
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
        
        # Step 1: Create comprehensive deployment guide
        deployment_guide_task_id = await self._delegate_task(
            to_agent="docs-writer-feature",
            task_description="Create comprehensive deployment and operations guide",
            task_context={
                "architecture_design": prereqs["architecture_design"],
                "implementation_summary": prereqs["implementation_summary"],
                "bmo_validation": prereqs.get("bmo_validation", ""),
                "feature_focus": "deployment_operations",
                "output_file": "docs/operations/deployment_guide.md",
                "requirements": [
                    "Document complete deployment procedures",
                    "Create environment setup instructions",
                    "Document configuration management",
                    "Create rollback and recovery procedures",
                    "Document security hardening steps"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/operations/deployment_guide.md",
                    "Deployment procedures documented",
                    "Environment setup instructions created",
                    "Configuration management documented",
                    "Rollback procedures defined"
                ]
            },
            priority=9
        )
        
        # Step 2: Create monitoring and alerting setup
        monitoring_setup_task_id = await self._delegate_task(
            to_agent="docs-writer-feature",
            task_description="Create monitoring, logging, and alerting setup guide",
            task_context={
                "architecture_design": prereqs["architecture_design"],
                "implementation_summary": prereqs["implementation_summary"],
                "feature_focus": "monitoring_alerting",
                "output_file": "docs/operations/monitoring_setup.md",
                "requirements": [
                    "Document monitoring system setup",
                    "Create logging configuration procedures",
                    "Define alerting rules and thresholds",
                    "Document performance metrics collection",
                    "Create dashboard and visualization setup"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/operations/monitoring_setup.md",
                    "Monitoring system documented",
                    "Logging procedures defined",
                    "Alerting rules documented",
                    "Performance metrics defined"
                ]
            },
            priority=9
        )
        
        # Step 3: Create backup and disaster recovery procedures
        backup_recovery_task_id = await self._delegate_task(
            to_agent="docs-writer-feature",
            task_description="Create backup and disaster recovery procedures",
            task_context={
                "architecture_design": prereqs["architecture_design"],
                "implementation_summary": prereqs["implementation_summary"],
                "feature_focus": "backup_disaster_recovery",
                "output_file": "docs/operations/backup_recovery.md",
                "requirements": [
                    "Document backup procedures and schedules",
                    "Create disaster recovery playbooks",
                    "Define RTO and RPO requirements",
                    "Document data restoration procedures",
                    "Create business continuity plans"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/operations/backup_recovery.md",
                    "Backup procedures documented",
                    "Disaster recovery playbooks created",
                    "RTO/RPO requirements defined",
                    "Restoration procedures documented"
                ]
            },
            priority=8
        )
        
        # Step 4: Create maintenance runbook
        maintenance_runbook_task_id = await self._delegate_task(
            to_agent="docs-writer-feature",
            task_description="Create operational maintenance runbook",
            task_context={
                "architecture_design": prereqs["architecture_design"],
                "implementation_summary": prereqs["implementation_summary"],
                "feature_focus": "maintenance_operations",
                "output_file": "docs/operations/maintenance_runbook.md",
                "requirements": [
                    "Document routine maintenance procedures",
                    "Create system health check procedures",
                    "Define maintenance schedules and windows",
                    "Document update and patching procedures",
                    "Create capacity planning guidelines"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/operations/maintenance_runbook.md",
                    "Maintenance procedures documented",
                    "Health check procedures defined",
                    "Maintenance schedules created",
                    "Update procedures documented"
                ]
            },
            priority=8
        )
        
        # Step 5: Create troubleshooting guide
        troubleshooting_task_id = await self._delegate_task(
            to_agent="docs-writer-feature",
            task_description="Create comprehensive troubleshooting guide",
            task_context={
                "architecture_design": prereqs["architecture_design"],
                "implementation_summary": prereqs["implementation_summary"],
                "feature_focus": "troubleshooting_support",
                "output_file": "docs/operations/troubleshooting_guide.md",
                "requirements": [
                    "Document common issues and solutions",
                    "Create diagnostic procedures",
                    "Define escalation procedures",
                    "Document log analysis techniques",
                    "Create performance troubleshooting guides"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/operations/troubleshooting_guide.md",
                    "Common issues documented",
                    "Diagnostic procedures created",
                    "Escalation procedures defined",
                    "Log analysis techniques documented"
                ]
            },
            priority=7
        )
        
        # Step 6: Create scaling and performance optimization guide
        scaling_optimization_task_id = await self._delegate_task(
            to_agent="optimizer-module",
            task_description="Create scaling and performance optimization guide",
            task_context={
                "architecture_design": prereqs["architecture_design"],
                "implementation_summary": prereqs["implementation_summary"],
                "optimization_focus": "scaling_performance",
                "output_file": "docs/operations/scaling_guide.md",
                "requirements": [
                    "Document scaling procedures and strategies",
                    "Create performance optimization guidelines",
                    "Define capacity planning procedures",
                    "Document load testing and monitoring",
                    "Create auto-scaling configuration guides"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/operations/scaling_guide.md",
                    "Scaling procedures documented",
                    "Performance optimization guidelines created",
                    "Capacity planning procedures defined",
                    "Auto-scaling configuration documented"
                ]
            },
            priority=7
        )
        
        # Step 7: Create deployment scripts and configurations
        deployment_automation_task_id = await self._delegate_task(
            to_agent="architect-highlevel-module",
            task_description="Create deployment automation and configuration",
            task_context={
                "architecture_design": prereqs["architecture_design"],
                "deployment_guide_task_id": deployment_guide_task_id,
                "architecture_focus": "deployment_automation",
                "output_directory": "deploy/",
                "requirements": [
                    "Create deployment scripts and automation",
                    "Generate configuration templates",
                    "Create CI/CD pipeline configurations",
                    "Generate infrastructure as code templates",
                    "Create environment-specific configurations"
                ],
                "ai_verifiable_outcomes": [
                    "Deployment scripts created in deploy/",
                    "Configuration templates generated",
                    "CI/CD pipeline configurations created",
                    "Infrastructure templates generated",
                    "Environment configs created"
                ]
            },
            priority=6
        )
        
        # Step 8: Create operational security hardening guide
        security_hardening_task_id = await self._delegate_task(
            to_agent="security-reviewer-module",
            task_description="Create operational security hardening guide",
            task_context={
                "architecture_design": prereqs["architecture_design"],
                "deployment_guide_task_id": deployment_guide_task_id,
                "security_focus": "operational_security",
                "output_file": "docs/operations/security_hardening.md",
                "requirements": [
                    "Document security hardening procedures",
                    "Create security monitoring setup",
                    "Define security update procedures",
                    "Document incident response procedures",
                    "Create security audit and compliance guides"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/operations/security_hardening.md",
                    "Security hardening procedures documented",
                    "Security monitoring setup defined",
                    "Security update procedures created",
                    "Incident response procedures documented"
                ]
            },
            priority=6
        )
        
        # Step 9: Create operational resilience testing
        resilience_testing_task_id = await self._delegate_task(
            to_agent="chaos-engineer",
            task_description="Create operational resilience testing procedures",
            task_context={
                "architecture_design": prereqs["architecture_design"],
                "monitoring_setup_task_id": monitoring_setup_task_id,
                "chaos_testing_focus": "operational_resilience",
                "output_file": "docs/operations/resilience_testing.md",
                "requirements": [
                    "Create operational chaos testing procedures",
                    "Design failure simulation scenarios",
                    "Create resilience validation tests",
                    "Document recovery time validation",
                    "Create operational stress testing guides"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/operations/resilience_testing.md",
                    "Chaos testing procedures created",
                    "Failure simulation scenarios defined",
                    "Resilience validation tests documented",
                    "Recovery time validation procedures created"
                ]
            },
            priority=5
        )
        
        # Wait for all tasks to complete
        all_tasks = [deployment_guide_task_id, monitoring_setup_task_id, backup_recovery_task_id, 
                    maintenance_runbook_task_id, troubleshooting_task_id, scaling_optimization_task_id,
                    deployment_automation_task_id, security_hardening_task_id, resilience_testing_task_id]
        completed_tasks = await self._wait_for_tasks(all_tasks)
        
        # Identify created documents
        documents_created = await self._identify_created_documents()
        
        if not documents_created:
            return AgentResult(
                success=False,
                outputs={"error": "No maintenance documents were created"},
                files_created=[],
                files_modified=[],
                errors=["Failed to create required maintenance documentation"]
            )
        
        # Delegate to state scribe for recording
        await self._delegate_to_state_scribe(documents_created)
        
        # Validate maintenance completeness
        maintenance_validation = await self._validate_maintenance_completeness(documents_created)
        
        return AgentResult(
            success=True,
            outputs={
                "phase": "completion-maintenance",
                "documents_created": documents_created,
                "completed_tasks": completed_tasks,
                "maintenance_validation": maintenance_validation,
                "next_phase": "documentation",
                "message": "Completion maintenance phase completed successfully"
            },
            files_created=[doc["path"] for doc in documents_created],
            files_modified=[],
            next_steps=["Proceed to documentation phase", "System ready for production deployment"]
        )
    
    async def _check_existing_maintenance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if maintenance documents already exist"""
        project_files = context.get("project_state", {}).get("files", {})
        
        has_deployment_guide = any("deployment_guide.md" in path for path in project_files.keys())
        has_monitoring_setup = any("monitoring_setup.md" in path for path in project_files.keys())
        has_backup_recovery = any("backup_recovery.md" in path for path in project_files.keys())
        has_maintenance_runbook = any("maintenance_runbook.md" in path for path in project_files.keys())
        has_troubleshooting = any("troubleshooting_guide.md" in path for path in project_files.keys())
        has_deploy_scripts = any("deploy/" in path for path in project_files.keys())
        
        return {
            "has_deployment_guide": has_deployment_guide,
            "has_monitoring_setup": has_monitoring_setup,
            "has_backup_recovery": has_backup_recovery,
            "has_maintenance_runbook": has_maintenance_runbook,
            "has_troubleshooting": has_troubleshooting,
            "has_deploy_scripts": has_deploy_scripts,
            "existing_files": list(project_files.keys())
        }
    
    async def _validate_prerequisites(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that BMO completion phase is complete"""
        project_files = context.get("project_state", {}).get("files", {})
        
        architecture_design = None
        implementation_summary = None
        bmo_validation = None
        missing = []
        
        # Check for architecture design
        arch_path = next((path for path in project_files.keys() if "system_design.md" in path), None)
        if arch_path:
            architecture_design = Path(arch_path).read_text() if Path(arch_path).exists() else None
        else:
            missing.append("System Architecture Design")
        
        # Check for implementation
        has_implementation = any("src/" in path for path in project_files.keys())
        if has_implementation:
            implementation_summary = "Implementation completed in src/ directory"
        else:
            missing.append("Implementation (src/ directory)")
        
        # Check for BMO validation (optional but recommended)
        bmo_path = next((path for path in project_files.keys() if "bmo_validation_report.md" in path), None)
        if bmo_path:
            bmo_validation = Path(bmo_path).read_text() if Path(bmo_path).exists() else None
        
        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "architecture_design": architecture_design,
            "implementation_summary": implementation_summary,
            "bmo_validation": bmo_validation
        }
    
    async def _identify_created_documents(self) -> List[Dict[str, Any]]:
        """Identify which maintenance documents were created"""
        docs_created = []
        
        # Operations documentation
        operations_docs = [
            ("docs/operations/deployment_guide.md", "deployment_guide", "Comprehensive deployment procedures"),
            ("docs/operations/monitoring_setup.md", "monitoring_setup", "Monitoring and alerting configuration"),
            ("docs/operations/backup_recovery.md", "backup_recovery", "Backup and disaster recovery procedures"),
            ("docs/operations/maintenance_runbook.md", "maintenance_runbook", "Operational maintenance procedures"),
            ("docs/operations/troubleshooting_guide.md", "troubleshooting_guide", "Issue resolution procedures"),
            ("docs/operations/scaling_guide.md", "scaling_guide", "Scaling and performance procedures"),
            ("docs/operations/security_hardening.md", "security_hardening", "Security hardening procedures"),
            ("docs/operations/resilience_testing.md", "resilience_testing", "Operational resilience testing procedures")
        ]
        
        for path, doc_type, description in operations_docs:
            if Path(path).exists():
                docs_created.append({
                    "path": path,
                    "type": doc_type,
                    "description": description,
                    "memory_type": "documentation"
                })
        
        # Deployment scripts and configurations
        deploy_directories = ["deploy/", "monitoring/", "scripts/"]
        for deploy_dir in deploy_directories:
            if Path(deploy_dir).exists():
                for deploy_file in Path(deploy_dir).rglob("*"):
                    if deploy_file.is_file():
                        docs_created.append({
                            "path": str(deploy_file),
                            "type": "deployment_config",
                            "description": f"Deployment configuration: {deploy_file.name}",
                            "memory_type": "configuration"
                        })
        
        # Additional operations files
        if Path("docs/operations").exists():
            for ops_file in Path("docs/operations").glob("*.md"):
                file_path = str(ops_file)
                if not any(doc["path"] == file_path for doc in docs_created):
                    docs_created.append({
                        "path": file_path,
                        "type": "operations_doc",
                        "description": f"Operations documentation: {ops_file.name}",
                        "memory_type": "documentation"
                    })
        
        return docs_created
    
    async def _validate_maintenance_completeness(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate maintenance documentation completeness"""
        doc_types = set(doc["type"] for doc in documents)
        
        required_types = {"deployment_guide", "monitoring_setup", "maintenance_runbook"}
        recommended_types = {"backup_recovery", "troubleshooting_guide", "scaling_guide", "security_hardening"}
        
        missing_required = required_types - doc_types
        missing_recommended = recommended_types - doc_types
        
        return {
            "complete": len(missing_required) == 0,
            "missing_required": list(missing_required),
            "missing_recommended": list(missing_recommended),
            "doc_types_present": list(doc_types),
            "total_operations_docs": len([doc for doc in documents if doc["memory_type"] == "documentation"]),
            "total_config_files": len([doc for doc in documents if doc["memory_type"] == "configuration"])
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
                "rationale": "Created during completion maintenance phase"
            })
        
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record maintenance documents",
            task_context={
                "files_to_record": files_to_record,
                "phase": "completion-maintenance",
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
