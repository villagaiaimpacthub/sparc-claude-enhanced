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

"""Goal Clarification Orchestrator"""

from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from agents.base_agent import BaseAgent, TaskPayload, AgentResult

class GoalClarificationOrchestrator(BaseAgent):
    """Orchestrator for the Goal Clarification phase"""
    
    def __init__(self):
        super().__init__(
            agent_name="orchestrator-goal-clarification",
            role_definition="You orchestrate the goal clarification phase, ensuring the project goal is thoroughly understood and documented before proceeding.",
            custom_instructions="""
You MUST:
1. Analyze the project goal thoroughly
2. Create a Mutual Understanding Document
3. Define constraints and anti-goals
4. Request human approval before proceeding
5. Delegate file recording to the State Scribe

Your outputs MUST include:
- docs/Mutual_Understanding_Document.md
- docs/specifications/constraints_and_anti_goals.md

You coordinate but do NOT write files directly. Instead:
1. Use Claude to analyze and create content
2. Have Claude write the files
3. Delegate to State Scribe for recording
4. Request human approval
"""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute goal clarification phase"""
        
        # Check if phase already completed
        existing_docs = await self._check_existing_documents(context)
        if existing_docs["has_mutual_understanding"] and existing_docs["has_constraints"]:
            return AgentResult(
                success=True,
                outputs={
                    "message": "Goal clarification already complete",
                    "documents": existing_docs
                },
                files_created=[],
                files_modified=[]
            )
        
        # Build comprehensive prompt for Claude
        clarification_prompt = self._build_clarification_prompt(task, context, existing_docs)
        
        # Run Claude to conduct discovery and create documents
        claude_response = await self._run_claude(clarification_prompt, max_tokens=100000)
        
        # Parse response and identify created documents
        documents_created = await self._identify_created_documents()
        
        if not documents_created:
            return AgentResult(
                success=False,
                outputs={"error": "No documents were created"},
                files_created=[],
                files_modified=[],
                errors=["Failed to create required documents"]
            )
        
        # Delegate to state scribe for recording
        await self._delegate_to_state_scribe(documents_created)
        
        # Request approval
        approval_id = await self._request_approval("goal-clarification", {
            "documents": documents_created,
            "phase": "goal-clarification",
            "timestamp": datetime.now().isoformat()
        }, "Goal clarification complete. Mutual Understanding Document and Constraints Document created. Please review and approve to proceed to specification phase.")
        
        return AgentResult(
            success=True,
            outputs={
                "phase": "goal-clarification",
                "documents_created": documents_created,
                "approval_requested": approval_id,
                "next_phase": "specification",
                "message": "Goal clarification phase completed, approval requested"
            },
            files_created=[doc["path"] for doc in documents_created],
            files_modified=[],
            next_steps=["Wait for human approval", "Proceed to specification phase"]
        )
    
    async def _check_existing_documents(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if goal clarification documents already exist"""
        project_files = context.get("project_state", {}).get("files", {})
        
        has_mutual = any("Mutual_Understanding_Document.md" in path for path in project_files.keys())
        has_constraints = any("constraints_and_anti_goals.md" in path for path in project_files.keys())
        
        return {
            "has_mutual_understanding": has_mutual,
            "has_constraints": has_constraints,
            "existing_files": list(project_files.keys())
        }
    
    def _build_clarification_prompt(self, task: TaskPayload, context: Dict[str, Any], 
                                   existing_docs: Dict[str, Any]) -> str:
        """Build comprehensive prompt for goal clarification"""
        project_goal = task.context.get('project_goal', task.description)
        
        return f"""
{self.role_definition}

{self.custom_instructions}

TASK: Conduct comprehensive goal clarification for this project.

PROJECT GOAL: {project_goal}

CURRENT CONTEXT:
- Project ID: {self.project_id}
- Phase: Goal Clarification
- Existing Documents: {existing_docs}

YOU MUST CREATE TWO DOCUMENTS:

1. **docs/Mutual_Understanding_Document.md**
   - Project overview and objectives
   - Success criteria (measurable and AI-verifiable)
   - Stakeholder analysis
   - Key assumptions and dependencies
   - Timeline and milestones
   - Technical requirements overview

2. **docs/specifications/constraints_and_anti_goals.md**
   - Technical constraints
   - Business constraints
   - Resource limitations
   - Anti-goals (what we explicitly do NOT want)
   - Risk factors
   - Compliance requirements

REQUIREMENTS FOR EACH DOCUMENT:
- Be extremely thorough and detailed
- Make every requirement measurable and AI-verifiable
- Include specific acceptance criteria
- Consider edge cases and failure modes
- Use clear, unambiguous language

ANALYSIS FRAMEWORK:
1. Decompose the goal into specific, measurable objectives
2. Identify all stakeholders and their needs
3. Define explicit success criteria
4. Document all constraints and limitations
5. Identify potential risks and mitigation strategies

Begin your comprehensive analysis and document creation now. Create both files with complete, detailed content.
"""
    
    async def _identify_created_documents(self) -> List[Dict[str, Any]]:
        """Identify which documents were created by Claude"""
        docs_created = []
        
        # Check for Mutual Understanding Document
        mutual_understanding_path = "docs/Mutual_Understanding_Document.md"
        if Path(mutual_understanding_path).exists():
            docs_created.append({
                "path": mutual_understanding_path,
                "type": "mutual_understanding",
                "description": "Comprehensive mutual understanding document",
                "memory_type": "specification"
            })
        
        # Check for Constraints Document
        constraints_path = "docs/specifications/constraints_and_anti_goals.md"
        if Path(constraints_path).exists():
            docs_created.append({
                "path": constraints_path,
                "type": "constraints",
                "description": "Project constraints and anti-goals",
                "memory_type": "specification"
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
                "rationale": "Created during goal clarification phase"
            })
        
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record goal clarification documents",
            task_context={
                "files_to_record": files_to_record,
                "phase": "goal-clarification",
                "requirements": ["Record all files in project_memorys table"],
                "ai_verifiable_outcomes": ["All files recorded with version 1"]
            },
            priority=8
        )