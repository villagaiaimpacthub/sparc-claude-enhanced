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

"""Goal Clarification Orchestrator"""

import os
import asyncio
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
        
        # For testing, simulate document creation (in production this would call Claude)
        console.print("[blue]🤖 Creating goal clarification documents...[/blue]")
        await self._create_goal_documents(task, context)
        
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
        
        has_mutual = self._check_namespaced_file("docs/Mutual_Understanding_Document.md")
        has_constraints = self._check_namespaced_file("docs/specifications/constraints_and_anti_goals.md")
        
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

IMPORTANT: As part of goal clarification, you MUST ask the user for:
1. GitHub repository name for this project (suggest: {project_goal.lower().replace(' ', '-')})
2. Whether to create a new repo or use existing one
3. Repository visibility (public/private)

Store this information in the mutual understanding document.

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
        mutual_understanding_path = self._get_namespaced_path("docs/Mutual_Understanding_Document.md")
        if Path(mutual_understanding_path).exists():
            docs_created.append({
                "path": mutual_understanding_path,
                "type": "mutual_understanding",
                "description": "Comprehensive mutual understanding document",
                "memory_type": "specification"
            })
        
        # Check for Constraints Document
        constraints_path = self._get_namespaced_path("docs/specifications/constraints_and_anti_goals.md")
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
        
        await self.delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record goal clarification documents",
            context={
                "files_to_record": files_to_record,
                "phase": "goal-clarification",
                "requesting_agent": self.agent_name,
                "requirements": ["Record all files in project_memorys table"],
                "ai_verifiable_outcomes": ["All files recorded with version 1"]
            },
            priority=8
        )
    
    async def _create_goal_documents(self, task: TaskPayload, context: Dict[str, Any]):
        """Create goal clarification documents"""
        console.print("[blue]📝 Creating goal clarification documents...[/blue]")
        
        project_goal = task.context.get('project_goal', task.description)
        
        # Create namespaced directories
        docs_dir = Path(self._get_namespaced_path("docs"))
        specs_dir = docs_dir / 'specifications'
        docs_dir.mkdir(parents=True, exist_ok=True)
        specs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create Mutual Understanding Document
        mutual_doc = Path(self._get_namespaced_path("docs")) / 'Mutual_Understanding_Document.md'
        mutual_content = f"""# Mutual Understanding Document

## Project Overview
**Goal:** {project_goal}

## Project Objectives
- Build a user-friendly web application
- Implement secure user authentication system
- Create task management functionality
- Ensure responsive design for mobile and desktop

## Success Criteria
1. Users can register and log in securely
2. Users can create, edit, and delete tasks
3. Tasks can be organized and prioritized
4. Application loads in under 2 seconds
5. Mobile-responsive design works on all devices

## Key Stakeholders
- End users (task management needs)
- Development team (technical implementation)
- Product owner (business requirements)

## Technical Requirements Overview
- Web-based application
- User authentication and authorization
- Task CRUD operations
- Responsive UI/UX design
- Data persistence

## Timeline and Milestones
- Phase 1: User authentication (Week 1-2)
- Phase 2: Task management core (Week 3-4)
- Phase 3: UI/UX refinement (Week 5-6)
- Phase 4: Testing and deployment (Week 7-8)

---
*Generated by Goal Clarification Orchestrator*
*Date: {datetime.now().isoformat()}*
"""
        
        mutual_doc.write_text(mutual_content)
        console.print(f"✅ Created: {mutual_doc}")
        
        # Create Constraints and Anti-goals Document
        constraints_doc = Path(self._get_namespaced_path("docs/specifications")) / 'constraints_and_anti_goals.md'
        constraints_content = f"""# Constraints and Anti-Goals

## Technical Constraints
- Must work in modern web browsers (Chrome, Firefox, Safari, Edge)
- Database must be relational (PostgreSQL or MySQL)
- Frontend must be responsive (mobile-first design)
- API must be RESTful
- Must use HTTPS in production

## Business Constraints
- Development budget: Limited to open-source technologies
- Timeline: Maximum 8 weeks for MVP
- Team size: 1-3 developers
- Hosting: Cloud-based deployment preferred

## Resource Limitations
- No budget for premium third-party services
- Limited to standard web technologies
- Must be maintainable by small team

## Anti-Goals (What We Explicitly Do NOT Want)
- Complex enterprise features (workflows, approvals)
- Real-time collaboration (for MVP)
- Mobile native apps (web-only for now)
- Advanced reporting and analytics
- Multi-tenant architecture
- Integration with external calendar systems

## Risk Factors
- Authentication security vulnerabilities
- Data loss due to poor backup strategy
- Performance issues with large task lists
- Cross-browser compatibility problems
- Mobile usability challenges

## Compliance Requirements
- Basic GDPR compliance for user data
- Secure password storage (hashing)
- Data export capability for users
- Privacy policy and terms of service

---
*Generated by Goal Clarification Orchestrator*
*Date: {datetime.now().isoformat()}*
"""
        
        constraints_doc.write_text(constraints_content)
        console.print(f"✅ Created: {constraints_doc}")
    
    async def _request_approval(self, phase: str, data: Dict[str, Any], message: str) -> str:
        """Request approval for phase completion"""
        # For testing, simulate approval request
        console.print(f"[yellow]🔍 Requesting approval for {phase} phase[/yellow]")
        console.print(f"[yellow]📋 {message}[/yellow]")
        return f"approval_request_{phase}_{datetime.now().isoformat()}"
    
    async def _wait_for_tasks(self, task_ids: List[str]) -> List[str]:
        """Wait for delegated tasks to complete"""
        # For testing, simulate task completion
        console.print(f"[blue]⏳ Waiting for {len(task_ids)} tasks to complete...[/blue]")
        await asyncio.sleep(1)  # Simulate processing time
        console.print("[green]✅ All delegated tasks completed[/green]")
        return task_ids

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
    agent = GoalClarificationOrchestrator()
    
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
