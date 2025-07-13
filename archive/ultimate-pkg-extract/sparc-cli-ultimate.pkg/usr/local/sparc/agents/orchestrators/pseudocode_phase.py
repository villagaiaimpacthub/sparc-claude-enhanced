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

"""Pseudocode Phase Orchestrator"""

from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from agents.base_agent import BaseAgent, TaskPayload, AgentResult

class PseudocodePhaseOrchestrator(BaseAgent):
    """Orchestrator for the Pseudocode phase"""
    
    def __init__(self):
        super().__init__(
            agent_name="orchestrator-sparc-pseudocode-phase",
            role_definition="You orchestrate the pseudocode phase, creating detailed algorithmic blueprints for all system components. You translate specifications into step-by-step pseudocode that will guide the implementation phase.",
            custom_instructions="""
You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

You orchestrate the pseudocode phase by:
1. Analyzing the comprehensive specification and requirements
2. Breaking down the system into logical components and modules
3. Delegating to pseudocode writers for detailed algorithm design
4. Creating pseudocode for all major functions and data structures
5. Ensuring pseudocode is complete, unambiguous, and implementable
6. Validating pseudocode against requirements and constraints

Your primary outputs:
- docs/pseudocode/main_algorithms.md (core system algorithms)
- docs/pseudocode/data_structures.md (data models and structures)
- docs/pseudocode/api_endpoints.md (API logic if applicable)
- docs/pseudocode/business_logic.md (business rules and workflows)
- docs/pseudocode/error_handling.md (error scenarios and handling)

You delegate to:
- pseudocode-writer for main algorithm creation
- researcher-high-level-tests for test-driven pseudocode analysis
- devils-advocate-critical-evaluator for pseudocode validation
- edge-case-synthesizer for edge case pseudocode coverage

You coordinate but do NOT write files directly. You orchestrate the creation through delegation.
"""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute pseudocode phase"""
        
        # Check if phase already completed
        existing_pseudocode = await self._check_existing_pseudocode(context)
        if existing_pseudocode["has_main_algorithms"]:
            return AgentResult(
                success=True,
                outputs={
                    "message": "Pseudocode phase already complete",
                    "pseudocode": existing_pseudocode
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
        
        # Step 1: Analyze specifications for test-driven pseudocode approach
        test_analysis_task_id = await self._delegate_task(
            to_agent="researcher-high-level-tests",
            task_description="Analyze specifications for test-driven pseudocode development",
            task_context={
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "examples_spec": prereqs.get("examples_spec", ""),
                "research_focus": "test_driven_pseudocode_analysis",
                "requirements": [
                    "Identify all functions and methods that need pseudocode",
                    "Define test scenarios for each algorithm",
                    "Analyze input/output requirements",
                    "Document expected behavior and edge cases"
                ],
                "ai_verifiable_outcomes": [
                    "Test scenarios documented for all algorithms",
                    "Input/output specifications defined",
                    "Edge cases identified and catalogued"
                ]
            },
            priority=9
        )
        
        # Step 2: Create main system pseudocode
        main_pseudocode_task_id = await self._delegate_task(
            to_agent="pseudocode-writer",
            task_description="Create main system algorithms pseudocode",
            task_context={
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "test_analysis_task_id": test_analysis_task_id,
                "output_file": "docs/pseudocode/main_algorithms.md",
                "pseudocode_focus": "core_algorithms",
                "requirements": [
                    "Create pseudocode for all core algorithms",
                    "Define data structures and their operations",
                    "Specify control flow and decision logic",
                    "Document algorithm complexity and performance",
                    "Include error handling pseudocode"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/pseudocode/main_algorithms.md",
                    "All core algorithms have pseudocode",
                    "Data structures operations defined",
                    "Control flow clearly specified"
                ]
            },
            priority=9
        )
        
        # Step 3: Create data structures pseudocode
        data_structures_task_id = await self._delegate_task(
            to_agent="pseudocode-writer",
            task_description="Create data structures and models pseudocode",
            task_context={
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "main_pseudocode_task_id": main_pseudocode_task_id,
                "output_file": "docs/pseudocode/data_structures.md",
                "pseudocode_focus": "data_structures",
                "requirements": [
                    "Define all data structures and their properties",
                    "Specify data validation and constraints",
                    "Document data relationships and dependencies",
                    "Create serialization/deserialization pseudocode",
                    "Define database schema pseudocode if applicable"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/pseudocode/data_structures.md",
                    "All data structures defined",
                    "Data validation rules specified",
                    "Relationships documented"
                ]
            },
            priority=8
        )
        
        # Step 4: Create API/interface pseudocode
        api_pseudocode_task_id = await self._delegate_task(
            to_agent="pseudocode-writer",
            task_description="Create API endpoints and interfaces pseudocode",
            task_context={
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "main_pseudocode_task_id": main_pseudocode_task_id,
                "output_file": "docs/pseudocode/api_endpoints.md",
                "pseudocode_focus": "api_interfaces",
                "requirements": [
                    "Define all API endpoints and their logic",
                    "Specify request/response handling",
                    "Document authentication and authorization",
                    "Create middleware and interceptor pseudocode",
                    "Define error response formatting"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/pseudocode/api_endpoints.md",
                    "All API endpoints defined",
                    "Request/response handling specified",
                    "Authentication logic documented"
                ]
            },
            priority=8
        )
        
        # Step 5: Analyze edge cases for pseudocode coverage
        edge_case_task_id = await self._delegate_task(
            to_agent="edge-case-synthesizer",
            task_description="Analyze edge cases and create corresponding pseudocode",
            task_context={
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "main_pseudocode_task_id": main_pseudocode_task_id,
                "output_file": "docs/pseudocode/edge_cases.md",
                "requirements": [
                    "Identify all edge cases and boundary conditions",
                    "Create pseudocode for edge case handling",
                    "Define fallback and recovery mechanisms",
                    "Document error propagation strategies",
                    "Specify validation and sanitization pseudocode"
                ],
                "ai_verifiable_outcomes": [
                    "File exists: docs/pseudocode/edge_cases.md",
                    "All edge cases identified",
                    "Edge case handling pseudocode created",
                    "Recovery mechanisms defined"
                ]
            },
            priority=7
        )
        
        # Step 6: Critical validation of pseudocode
        validation_task_id = await self._delegate_task(
            to_agent="devils-advocate-critical-evaluator",
            task_description="Validate pseudocode completeness and correctness",
            task_context={
                "main_pseudocode_task_id": main_pseudocode_task_id,
                "data_structures_task_id": data_structures_task_id,
                "api_pseudocode_task_id": api_pseudocode_task_id,
                "edge_case_task_id": edge_case_task_id,
                "evaluation_focus": "pseudocode_validation",
                "requirements": [
                    "Validate pseudocode against specifications",
                    "Check for logical inconsistencies",
                    "Verify completeness of algorithm coverage",
                    "Assess implementability of pseudocode",
                    "Identify missing components or gaps"
                ],
                "ai_verifiable_outcomes": [
                    "Pseudocode validation report created",
                    "Logical inconsistencies identified",
                    "Coverage assessment completed",
                    "Implementation gaps documented"
                ]
            },
            priority=7
        )
        
        # Wait for all tasks to complete
        all_tasks = [test_analysis_task_id, main_pseudocode_task_id, data_structures_task_id, 
                    api_pseudocode_task_id, edge_case_task_id, validation_task_id]
        completed_tasks = await self._wait_for_tasks(all_tasks)
        
        # Identify created documents
        documents_created = await self._identify_created_documents()
        
        if not documents_created:
            return AgentResult(
                success=False,
                outputs={"error": "No pseudocode documents were created"},
                files_created=[],
                files_modified=[],
                errors=["Failed to create required pseudocode documents"]
            )
        
        # Delegate to state scribe for recording
        await self._delegate_to_state_scribe(documents_created)
        
        return AgentResult(
            success=True,
            outputs={
                "phase": "pseudocode",
                "documents_created": documents_created,
                "completed_tasks": completed_tasks,
                "next_phase": "architecture",
                "message": "Pseudocode phase completed successfully"
            },
            files_created=[doc["path"] for doc in documents_created],
            files_modified=[],
            next_steps=["Proceed to architecture phase"]
        )
    
    async def _check_existing_pseudocode(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if pseudocode documents already exist"""
        project_files = context.get("project_state", {}).get("files", {})
        
        has_main_algorithms = any("main_algorithms.md" in path for path in project_files.keys())
        has_data_structures = any("data_structures.md" in path for path in project_files.keys())
        has_api_endpoints = any("api_endpoints.md" in path for path in project_files.keys())
        
        return {
            "has_main_algorithms": has_main_algorithms,
            "has_data_structures": has_data_structures,
            "has_api_endpoints": has_api_endpoints,
            "existing_files": list(project_files.keys())
        }
    
    async def _validate_prerequisites(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that specification phase is complete"""
        project_files = context.get("project_state", {}).get("files", {})
        
        comprehensive_spec = None
        examples_spec = None
        missing = []
        
        # Check for comprehensive specification
        spec_path = next((path for path in project_files.keys() if "comprehensive_spec.md" in path), None)
        if spec_path:
            comprehensive_spec = Path(spec_path).read_text() if Path(spec_path).exists() else None
        else:
            missing.append("Comprehensive Specification")
        
        # Check for examples specification (optional)
        examples_path = next((path for path in project_files.keys() if "examples_and_use_cases.md" in path), None)
        if examples_path:
            examples_spec = Path(examples_path).read_text() if Path(examples_path).exists() else None
        
        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "comprehensive_spec": comprehensive_spec,
            "examples_spec": examples_spec
        }
    
    async def _identify_created_documents(self) -> List[Dict[str, Any]]:
        """Identify which pseudocode documents were created"""
        docs_created = []
        
        pseudocode_files = [
            ("docs/pseudocode/main_algorithms.md", "main_algorithms", "Core system algorithms pseudocode"),
            ("docs/pseudocode/data_structures.md", "data_structures", "Data structures and models pseudocode"),
            ("docs/pseudocode/api_endpoints.md", "api_endpoints", "API endpoints and interfaces pseudocode"),
            ("docs/pseudocode/edge_cases.md", "edge_cases", "Edge cases and error handling pseudocode")
        ]
        
        for path, doc_type, description in pseudocode_files:
            if Path(path).exists():
                docs_created.append({
                    "path": path,
                    "type": doc_type,
                    "description": description,
                    "memory_type": "pseudocode"
                })
        
        # Check for any additional pseudocode files
        if Path("docs/pseudocode").exists():
            for pseudocode_file in Path("docs/pseudocode").glob("*.md"):
                file_path = str(pseudocode_file)
                if not any(doc["path"] == file_path for doc in docs_created):
                    docs_created.append({
                        "path": file_path,
                        "type": "additional_pseudocode",
                        "description": f"Additional pseudocode: {pseudocode_file.name}",
                        "memory_type": "pseudocode"
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
                "rationale": "Created during pseudocode phase"
            })
        
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record pseudocode documents",
            task_context={
                "files_to_record": files_to_record,
                "phase": "pseudocode",
                "requirements": ["Record all files in project_memorys table"],
                "ai_verifiable_outcomes": ["All files recorded with appropriate version"]
            },
            priority=8
        )