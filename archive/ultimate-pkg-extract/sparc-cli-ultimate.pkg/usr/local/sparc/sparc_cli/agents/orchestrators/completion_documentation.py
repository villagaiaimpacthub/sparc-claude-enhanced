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

"""Completion Documentation Orchestrator"""

from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from sparc.agents.base_agent import BaseAgent, TaskPayload, AgentResult

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
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "implementation_summary": prereqs["implementation_summary"],
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
                "implementation_summary": prereqs["implementation_summary"],
                "architecture_design": prereqs.get("architecture_design", ""),
                "comprehensive_spec": prereqs["comprehensive_spec"],
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
                "implementation_summary": prereqs["implementation_summary"],
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
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "implementation_summary": prereqs["implementation_summary"],
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
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "implementation_summary": prereqs["implementation_summary"],
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
                "implementation_summary": prereqs["implementation_summary"],
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
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "implementation_summary": prereqs["implementation_summary"],
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
        """Validate that maintenance phase is complete"""
        project_files = context.get("project_state", {}).get("files", {})
        
        comprehensive_spec = None
        implementation_summary = None
        architecture_design = None
        operations_docs = None
        bmo_validation = None
        original_goal = None
        missing = []
        
        # Check for comprehensive specification
        spec_path = next((path for path in project_files.keys() if "comprehensive_spec.md" in path), None)
        if spec_path:
            comprehensive_spec = Path(spec_path).read_text() if Path(spec_path).exists() else None
        else:
            missing.append("Comprehensive Specification")
        
        # Check for implementation
        has_implementation = any("src/" in path for path in project_files.keys())
        if has_implementation:
            implementation_summary = "Implementation completed in src/ directory"
        else:
            missing.append("Implementation (src/ directory)")
        
        # Check for architecture design (optional)
        arch_path = next((path for path in project_files.keys() if "system_design.md" in path), None)
        if arch_path:
            architecture_design = Path(arch_path).read_text() if Path(arch_path).exists() else None
        
        # Check for operations documentation (optional)
        ops_path = next((path for path in project_files.keys() if "deployment_guide.md" in path), None)
        if ops_path:
            operations_docs = Path(ops_path).read_text() if Path(ops_path).exists() else None
        
        # Check for BMO validation (optional)
        bmo_path = next((path for path in project_files.keys() if "bmo_validation_report.md" in path), None)
        if bmo_path:
            bmo_validation = Path(bmo_path).read_text() if Path(bmo_path).exists() else None
        
        # Check for original goal (from mutual understanding)
        mutual_path = next((path for path in project_files.keys() if "Mutual_Understanding_Document.md" in path), None)
        if mutual_path:
            original_goal = Path(mutual_path).read_text() if Path(mutual_path).exists() else None
        
        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "comprehensive_spec": comprehensive_spec,
            "implementation_summary": implementation_summary,
            "architecture_design": architecture_design,
            "operations_docs": operations_docs,
            "bmo_validation": bmo_validation,
            "original_goal": original_goal,
            "all_project_files": list(project_files.keys())
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