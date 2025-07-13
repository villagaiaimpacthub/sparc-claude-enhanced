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

"""Completion Documentation Orchestrator"""

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


class CompletionDocumentationOrchestrator(BaseAgent):
    """Orchestrator for the Completion Documentation phase"""
    
    def __init__(self):
        super().__init__(
            agent_name="orchestrator-sparc-completion-documentation",
            role_definition="You orchestrate the final completion documentation phase, creating comprehensive user-facing documentation, API documentation, and project completion reports. You ensure all documentation is complete, accurate, and ready for end users and stakeholders.",
            custom_instructions="""
You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

You orchestrate the completion documentation phase by:
1. Creating comprehensive user documentation and guides
2. Generating API documentation and developer guides
3. Creating project completion reports and summaries
4. Organizing all documentation into a coherent structure
5. Ensuring documentation quality and consistency
6. Creating final project deliverables and handover materials

Your primary outputs:
- docs/user/ (comprehensive user documentation)
- docs/api/ (API documentation and developer guides)
- docs/developer/ (developer documentation and guides)
- docs/project/ (project completion reports and summaries)
- README.md (project overview and getting started guide)
- CHANGELOG.md (project history and version information)
- docs/final_project_report.md (comprehensive project completion report)

You delegate to:
- docs-writer-feature for user and developer documentation
- code-comprehension-assistant-v2 for API documentation generation
- research-planner-strategic for project completion analysis
- devils-advocate-critical-evaluator for documentation quality review

You coordinate but do NOT write files directly. You orchestrate the creation through delegation.
"""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute completion documentation phase"""
        
        # Check if phase already completed
        existing_documentation = await self._check_existing_documentation(context)
        if existing_documentation["has_user_docs"] and existing_documentation["has_api_docs"] and existing_documentation["has_readme"]:
            return AgentResult(
                success=True,
                outputs={
                    "message": "Completion documentation phase already complete",
                    "documentation": existing_documentation
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
        
        # Step 1: Create comprehensive user documentation
        user_docs_task_id = await self._delegate_task(
            to_agent="docs-writer-feature",
            task_description="Create comprehensive user documentation",
            task_context={
                "prerequisites_valid": prereqs["valid"],
                "bmo_validation": prereqs.get("bmo_validation", ""),
                "feature_focus": "user_documentation",
                "output_directory": "docs/user/",
                "requirements": [
                    "Create user guide and getting started documentation",
                    "Document all features and functionality",
                    "Create tutorials and examples",
                    "Document configuration and customization",
                    "Create FAQ and troubleshooting for users"
                ],
                "ai_verifiable_outcomes": [
                    "User documentation created in docs/user/",
                    "Getting started guide created",
                    "Feature documentation completed",
                    "Tutorials and examples provided",
                    "User FAQ created"
                ]
            },
            priority=9
        )
        
        # Step 2: Generate API documentation and developer guides
        api_docs_task_id = await self._delegate_task(
            to_agent="code-comprehension-assistant-v2",
            task_description="Generate API documentation and developer guides",
            task_context={
                "prerequisites_valid": prereqs["valid"],
                "analysis_focus": "api_documentation",
                "output_directory": "docs/api/",
                "requirements": [
                    "Generate comprehensive API documentation",
                    "Create developer integration guides",
                    "Document code examples and SDKs",
                    "Create API reference documentation",
                    "Document authentication and security"
                ],
                "ai_verifiable_outcomes": [
                    "API documentation created in docs/api/",
                    "Developer guides created",
                    "Code examples documented",
                    "API reference completed",
                    "Authentication documentation provided"
                ]
            },
            priority=9
        )
        
        # Step 3: Create developer documentation and guides
        developer_docs_task_id = await self._delegate_task(
            to_agent="docs-writer-feature",
            task_description="Create developer documentation and contribution guides",
            task_context={
                "prerequisites_valid": prereqs["valid"],
                "architecture_design": prereqs.get("architecture_design", ""),
                "operations_docs": prereqs.get("operations_docs", ""),
                "feature_focus": "developer_documentation",
                "output_directory": "docs/developer/",
                "requirements": [
                    "Create developer setup and contribution guide",
                    "Document code architecture and patterns",
                    "Create testing and debugging guides",
                    "Document build and deployment processes",
                    "Create code style and contribution guidelines"
                ],
                "ai_verifiable_outcomes": [
                    "Developer documentation created in docs/developer/",
                    "Setup and contribution guide created",
                    "Architecture documentation provided",
                    "Testing guides created",
                    "Build and deployment docs completed"
                ]
            },
            priority=8
        )
        
        # Step 4: Create project README and overview
        readme_task_id = await self._delegate_task(
            to_agent="docs-writer-feature",
            task_description="Create project README and overview documentation",
            task_context={
                "original_goal": prereqs.get("original_goal", ""),
                "prerequisites_valid": prereqs["valid"],
                "bmo_validation": prereqs.get("bmo_validation", ""),
                "feature_focus": "project_overview",
                "output_file": "README.md",
                "requirements": [
                    "Create compelling project overview and description",
                    "Document installation and quick start guide",
                    "Provide usage examples and screenshots",
                    "Document key features and benefits",
                    "Include contribution and support information"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: README.md",
                    "Project overview created",
                    "Installation guide provided",
                    "Usage examples included",
                    "Key features documented"
                ]
            },
            priority=9
        )
        
        # Step 5: Create project completion report
        completion_report_task_id = await self._delegate_task(
            to_agent="research-planner-strategic",
            task_description="Create comprehensive project completion report",
            task_context={
                "original_goal": prereqs.get("original_goal", ""),
                "prerequisites_valid": prereqs["valid"],
                "bmo_validation": prereqs.get("bmo_validation", ""),
                "all_project_files": prereqs.get("all_project_files", []),
                "research_focus": "project_completion_analysis",
                "output_file": "docs/final_project_report.md",
                "requirements": [
                    "Analyze project completion against original goals",
                    "Document all deliverables and achievements",
                    "Create project timeline and milestone summary",
                    "Document lessons learned and recommendations",
                    "Create final project metrics and statistics"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/final_project_report.md",
                    "Project completion analysis completed",
                    "Deliverables documented",
                    "Timeline and milestones summarized",
                    "Lessons learned documented"
                ]
            },
            priority=8
        )
        
        # Step 6: Create changelog and version history
        changelog_task_id = await self._delegate_task(
            to_agent="docs-writer-feature",
            task_description="Create changelog and version history documentation",
            task_context={
                "prerequisites_valid": prereqs["valid"],
                "all_project_files": prereqs.get("all_project_files", []),
                "feature_focus": "changelog_history",
                "output_file": "CHANGELOG.md",
                "requirements": [
                    "Document project development history",
                    "Create version history and release notes",
                    "Document major changes and improvements",
                    "Create migration guides if applicable",
                    "Document breaking changes and deprecations"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: CHANGELOG.md",
                    "Development history documented",
                    "Version history created",
                    "Major changes documented",
                    "Migration guides provided if needed"
                ]
            },
            priority=7
        )
        
        # Step 7: Create project handover documentation
        handover_docs_task_id = await self._delegate_task(
            to_agent="docs-writer-feature",
            task_description="Create project handover and transition documentation",
            task_context={
                "prerequisites_valid": prereqs["valid"],
                "operations_docs": prereqs.get("operations_docs", ""),
                "bmo_validation": prereqs.get("bmo_validation", ""),
                "feature_focus": "project_handover",
                "output_directory": "docs/project/",
                "requirements": [
                    "Create project handover documentation",
                    "Document knowledge transfer materials",
                    "Create stakeholder summary reports",
                    "Document project governance and ownership",
                    "Create future roadmap and recommendations"
                ],
                "ai_verifiable_outcomes": [
                    "Project handover docs created in docs/project/",
                    "Knowledge transfer materials documented",
                    "Stakeholder reports created",
                    "Project governance documented",
                    "Future roadmap provided"
                ]
            },
            priority=7
        )
        
        # Step 8: Quality review and consistency check
        quality_review_task_id = await self._delegate_task(
            to_agent="devils-advocate-critical-evaluator",
            task_description="Review documentation quality and consistency",
            task_context={
                "user_docs_task_id": user_docs_task_id,
                "api_docs_task_id": api_docs_task_id,
                "developer_docs_task_id": developer_docs_task_id,
                "readme_task_id": readme_task_id,
                "completion_report_task_id": completion_report_task_id,
                "evaluation_focus": "documentation_quality",
                "requirements": [
                    "Review documentation for completeness and accuracy",
                    "Check consistency across all documentation",
                    "Validate examples and code snippets",
                    "Review documentation structure and navigation",
                    "Identify gaps and improvement opportunities"
                ],
                "ai_verifiable_outcomes": [
                    "Documentation quality review completed",
                    "Consistency issues identified",
                    "Examples and code validated",
                    "Structure and navigation reviewed",
                    "Improvement recommendations provided"
                ]
            },
            priority=6
        )
        
        # Step 9: Create documentation index and organization
        documentation_index_task_id = await self._delegate_task(
            to_agent="docs-writer-feature",
            task_description="Create documentation index and organization structure",
            task_context={
                "user_docs_task_id": user_docs_task_id,
                "api_docs_task_id": api_docs_task_id,
                "developer_docs_task_id": developer_docs_task_id,
                "quality_review_task_id": quality_review_task_id,
                "feature_focus": "documentation_organization",
                "output_file": "docs/index.md",
                "requirements": [
                    "Create comprehensive documentation index",
                    "Organize documentation into logical structure",
                    "Create navigation and cross-references",
                    "Generate table of contents for all sections",
                    "Create documentation search and discovery aids"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/index.md",
                    "Documentation index created",
                    "Logical structure implemented",
                    "Navigation and cross-references added",
                    "Table of contents generated"
                ]
            },
            priority=5
        )
        
        # Wait for all tasks to complete
        all_tasks = [user_docs_task_id, api_docs_task_id, developer_docs_task_id, readme_task_id, 
                    completion_report_task_id, changelog_task_id, handover_docs_task_id, 
                    quality_review_task_id, documentation_index_task_id]
        completed_tasks = await self._wait_for_tasks(all_tasks)
        
        # Identify created documents
        documents_created = await self._identify_created_documents()
        
        if not documents_created:
            return AgentResult(
                success=False,
                outputs={"error": "No documentation was created"},
                files_created=[],
                files_modified=[],
                errors=["Failed to create required documentation"]
            )
        
        # Delegate to state scribe for recording
        await self._delegate_to_state_scribe(documents_created)
        
        # Validate documentation completeness
        documentation_validation = await self._validate_documentation_completeness(documents_created)
        
        # Generate final project summary
        project_summary = await self._generate_project_summary(prereqs, documents_created)
        
        return AgentResult(
            success=True,
            outputs={
                "phase": "completion-documentation",
                "documents_created": documents_created,
                "completed_tasks": completed_tasks,
                "documentation_validation": documentation_validation,
                "project_summary": project_summary,
                "message": "Completion documentation phase completed successfully - PROJECT COMPLETE!"
            },
            files_created=[doc["path"] for doc in documents_created],
            files_modified=[],
            next_steps=["Project is complete and ready for delivery", "All documentation is finalized"]
        )
    
    async def _check_existing_documentation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if documentation already exists"""
        project_files = context.get("project_state", {}).get("files", {})
        
        has_user_docs = any("docs/user/" in path for path in project_files.keys())
        has_api_docs = any("docs/api/" in path for path in project_files.keys())
        has_developer_docs = any("docs/developer/" in path for path in project_files.keys())
        has_readme = any("README.md" in path for path in project_files.keys())
        has_changelog = any("CHANGELOG.md" in path for path in project_files.keys())
        has_final_report = any("final_project_report.md" in path for path in project_files.keys())
        
        return {
            "has_user_docs": has_user_docs,
            "has_api_docs": has_api_docs,
            "has_developer_docs": has_developer_docs,
            "has_readme": has_readme,
            "has_changelog": has_changelog,
            "has_final_report": has_final_report,
            "existing_files": list(project_files.keys())
        }
    
    async def _validate_prerequisites(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that implementation and testing phases are complete - FIXED VERSION"""
        
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
        
        # Check for implementation (src/ directory or any code files)
        impl_paths = [
            Path("src/"),
            Path("app/"),
            Path("lib/"),
            Path("implementation/")
        ]
        impl_exists = any(path.exists() and path.is_dir() for path in impl_paths)
        if not impl_exists:
            # Also check for any source code files
            code_files = list(Path(".").glob("**/*.py")) + list(Path(".").glob("**/*.js")) + list(Path(".").glob("**/*.ts"))
            if not code_files:
                missing.append("Implementation (src/ directory)")
        
        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "message": "All prerequisites met" if len(missing) == 0 else f"Missing: {', '.join(missing)}"
        }
    
    async def _identify_created_documents(self) -> List[Dict[str, Any]]:
        """Identify which documentation was created"""
        docs_created = []
        
        # Root level documentation
        root_docs = [
            ("README.md", "readme", "Project overview and getting started guide"),
            ("CHANGELOG.md", "changelog", "Project history and version information"),
            ("docs/index.md", "documentation_index", "Documentation index and organization"),
            ("docs/final_project_report.md", "final_project_report", "Comprehensive project completion report")
        ]
        
        for path, doc_type, description in root_docs:
            if Path(path).exists():
                docs_created.append({
                    "path": path,
                    "type": doc_type,
                    "description": description,
                    "memory_type": "documentation"
                })
        
        # Documentation directories
        doc_directories = [
            ("docs/user/", "user_documentation", "User documentation"),
            ("docs/api/", "api_documentation", "API documentation"),
            ("docs/developer/", "developer_documentation", "Developer documentation"),
            ("docs/project/", "project_documentation", "Project documentation")
        ]
        
        for doc_dir, doc_type, description in doc_directories:
            if Path(doc_dir).exists():
                for doc_file in Path(doc_dir).rglob("*.md"):
                    docs_created.append({
                        "path": str(doc_file),
                        "type": doc_type,
                        "description": f"{description}: {doc_file.name}",
                        "memory_type": "documentation"
                    })
        
        # Additional documentation files
        additional_doc_dirs = ["docs/guides/", "docs/tutorials/", "docs/examples/"]
        for doc_dir in additional_doc_dirs:
            if Path(doc_dir).exists():
                for doc_file in Path(doc_dir).rglob("*.md"):
                    docs_created.append({
                        "path": str(doc_file),
                        "type": "additional_documentation",
                        "description": f"Additional documentation: {doc_file.name}",
                        "memory_type": "documentation"
                    })
        
        return docs_created
    
    async def _validate_documentation_completeness(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate documentation completeness"""
        doc_types = set(doc["type"] for doc in documents)
        
        required_types = {"readme", "user_documentation", "api_documentation"}
        recommended_types = {"developer_documentation", "changelog", "final_project_report", "documentation_index"}
        
        missing_required = required_types - doc_types
        missing_recommended = recommended_types - doc_types
        
        return {
            "complete": len(missing_required) == 0,
            "missing_required": list(missing_required),
            "missing_recommended": list(missing_recommended),
            "doc_types_present": list(doc_types),
            "total_documentation_files": len(documents)
        }
    
    async def _generate_project_summary(self, prereqs: Dict[str, Any], documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate final project summary"""
        return {
            "project_complete": True,
            "total_files_created": len(documents),
            "documentation_types": len(set(doc["type"] for doc in documents)),
            "has_original_goal": prereqs.get("original_goal") is not None,
            "has_implementation": prereqs.get("implementation_summary") is not None,
            "has_bmo_validation": prereqs.get("bmo_validation") is not None,
            "completion_timestamp": datetime.now().isoformat()
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
                "rationale": "Created during completion documentation phase"
            })
        
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record final documentation",
            task_context={
                "files_to_record": files_to_record,
                "phase": "completion-documentation",
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
