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
