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

"""Uber Orchestrator - Master conductor of the SPARC workflow"""

from typing import Dict, Any, Optional, List
from pathlib import Path

from agents.base_agent import BaseAgent, TaskPayload, AgentResult
from lib.constants import PHASE_SEQUENCE, PHASE_ORCHESTRATORS, APPROVAL_REQUIRED_PHASES

class UberOrchestratorAgent(BaseAgent):
    """Master conductor of the entire SPARC workflow"""
    
    def __init__(self):
        super().__init__(
            agent_name="uber-orchestrator",
            role_definition="You are the master conductor of the entire project workflow. You understand the big picture and orchestrate the entire project from start to finish. You have the bird's-eye view of the project and ensure all phases are completed in the correct order with proper handoffs between orchestrators.",
            custom_instructions="""
You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

You coordinate all phases: goal-clarification, specification, pseudocode, architecture, refinement-testing, refinement-implementation, bmo-completion, maintenance, and documentation. You ensure each phase is completed before moving to the next. You have oversight of all 36 agents and ensure they work together cohesively. You maintain the project timeline and ensure deliverables meet quality standards.

Your workflow follows this sequence:
initialization → goal-clarification → specification → pseudocode → architecture → refinement-testing → refinement-implementation → bmo-completion → maintenance → documentation

At each phase, you must:
- Check if phase is complete by validating deliverables
- Request approval if required (goal-clarification, specification, architecture, bmo-completion)
- Delegate to next phase orchestrator
- Handle errors and retries
- Ensure quality gates are met
- Monitor all agent performance
- Maintain project coherence and vision
"""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Determine next phase and delegate to appropriate orchestrator"""
        
        # Get current project state
        current_phase = await self._determine_current_phase(context)
        next_phase = await self._determine_next_phase(current_phase, context)
        
        if not next_phase:
            return AgentResult(
                success=True,
                outputs={
                    "message": "All phases completed! Project is ready.",
                    "current_phase": current_phase,
                    "completion_status": "complete"
                },
                files_created=[],
                files_modified=[],
                next_steps=["Project completed successfully"]
            )
        
        # Check if approval is needed for current phase
        if current_phase and current_phase in APPROVAL_REQUIRED_PHASES:
            pending_approvals = await self.memory.check_pending_approvals()
            if pending_approvals:
                return AgentResult(
                    success=True,
                    outputs={
                        "message": f"Waiting for approval for {current_phase} phase",
                        "current_phase": current_phase,
                        "pending_approvals": len(pending_approvals)
                    },
                    files_created=[],
                    files_modified=[],
                    next_steps=["Wait for human approval"]
                )
        
        # Delegate to next phase orchestrator
        next_orchestrator = PHASE_ORCHESTRATORS.get(next_phase)
        if next_orchestrator:
            task_id = await self._delegate_task(
                to_agent=next_orchestrator,
                task_description=f"Execute {next_phase} phase",
                task_context={
                    "phase": next_phase,
                    "project_goal": task.context.get("project_goal", task.description),
                    "requirements": self._get_phase_requirements(next_phase),
                    "ai_verifiable_outcomes": self._get_phase_outcomes(next_phase),
                    "current_context": context
                },
                priority=10  # High priority for phase orchestrators
            )
            
            return AgentResult(
                success=True,
                outputs={
                    "delegated_to": next_orchestrator,
                    "phase": next_phase,
                    "task_id": task_id,
                    "message": f"Delegated to {next_orchestrator} for {next_phase} phase"
                },
                files_created=[],
                files_modified=[],
                next_steps=[f"Execute {next_phase} phase"]
            )
        
        return AgentResult(
            success=False,
            outputs={
                "error": f"No orchestrator found for phase: {next_phase}",
                "current_phase": current_phase,
                "next_phase": next_phase
            },
            files_created=[],
            files_modified=[],
            errors=[f"No orchestrator found for phase: {next_phase}"]
        )
    
    async def _determine_current_phase(self, context: Dict[str, Any]) -> Optional[str]:
        """Determine the current phase from project state"""
        try:
            # Query latest phase from contexts
            result = await self.memory.supabase.table("sparc_contexts").select("phase").eq(
                "project_id", self.project_id
            ).order(
                "created_at", desc=True
            ).limit(1).execute()
            
            if result.data:
                return result.data[0]["phase"]
            return None
        except Exception as e:
            print(f"Error determining current phase: {str(e)}")
            return None
    
    async def _determine_next_phase(self, current_phase: Optional[str], 
                                   context: Dict[str, Any]) -> Optional[str]:
        """Determine the next phase in the workflow"""
        if not current_phase:
            return "goal-clarification"
            
        # Check if current phase is complete
        if not await self._is_phase_complete(current_phase, context):
            return current_phase  # Continue current phase
            
        # Get next phase from sequence
        try:
            current_index = PHASE_SEQUENCE.index(current_phase)
            if current_index < len(PHASE_SEQUENCE) - 1:
                return PHASE_SEQUENCE[current_index + 1]
        except ValueError:
            pass
            
        return None
    
    async def _is_phase_complete(self, phase: str, context: Dict[str, Any]) -> bool:
        """Check if a phase is complete based on required artifacts"""
        # Define phase completion criteria
        completion_criteria = {
            "goal-clarification": ["docs/Mutual_Understanding_Document.md", "docs/specifications/constraints_and_anti_goals.md"],
            "specification": ["docs/specifications/comprehensive_spec.md"],
            "pseudocode": ["docs/pseudocode/"],
            "architecture": ["docs/architecture/system_design.md"],
            "refinement-testing": ["tests/"],
            "refinement-implementation": ["src/"],
            "bmo-completion": ["docs/bmo_validation_report.md"]
        }
        
        required_files = completion_criteria.get(phase, [])
        project_files = context.get("project_state", {}).get("files", {})
        
        # Check if required files exist
        for required_file in required_files:
            if required_file.endswith('/'):
                # Directory check
                if not any(path.startswith(required_file) for path in project_files.keys()):
                    return False
            else:
                # File check
                if required_file not in project_files:
                    return False
        
        return True
    
    def _get_phase_requirements(self, phase: str) -> List[str]:
        """Get requirements for a phase"""
        requirements_map = {
            "goal-clarification": [
                "Create Mutual Understanding Document",
                "Define constraints and anti-goals",
                "Get user approval for project direction"
            ],
            "specification": [
                "Create comprehensive technical specification",
                "Define all functional requirements",
                "Specify non-functional requirements"
            ],
            "pseudocode": [
                "Create detailed pseudocode for all components",
                "Define algorithm logic",
                "Specify data structures"
            ],
            "architecture": [
                "Design system architecture",
                "Define component interfaces",
                "Create deployment diagrams"
            ],
            "refinement-testing": [
                "Create comprehensive test suite",
                "Implement TDD approach",
                "Achieve target code coverage"
            ],
            "refinement-implementation": [
                "Implement all features",
                "Follow TDD principles",
                "Ensure code quality"
            ],
            "bmo-completion": [
                "Validate against original intent",
                "Verify all requirements met",
                "Generate final validation report"
            ]
        }
        return requirements_map.get(phase, [])
    
    def _get_phase_outcomes(self, phase: str) -> List[str]:
        """Get AI-verifiable outcomes for a phase"""
        outcomes_map = {
            "goal-clarification": [
                "File exists: docs/Mutual_Understanding_Document.md",
                "File exists: docs/specifications/constraints_and_anti_goals.md",
                "Approval record exists in database"
            ],
            "specification": [
                "File exists: docs/specifications/comprehensive_spec.md",
                "File contains functional requirements section",
                "File contains non-functional requirements section"
            ],
            "pseudocode": [
                "Directory exists: docs/pseudocode/",
                "Pseudocode files exist for all major components",
                "All algorithms have pseudocode representation"
            ],
            "architecture": [
                "File exists: docs/architecture/system_design.md",
                "Architecture diagrams present",
                "Component interfaces defined"
            ],
            "refinement-testing": [
                "Directory exists: tests/",
                "Test files exist for all components",
                "Test coverage meets target"
            ],
            "refinement-implementation": [
                "Directory exists: src/",
                "All features implemented",
                "Code passes all tests"
            ],
            "bmo-completion": [
                "File exists: docs/bmo_validation_report.md",
                "All requirements validated",
                "Final approval obtained"
            ]
        }
        return outcomes_map.get(phase, [])