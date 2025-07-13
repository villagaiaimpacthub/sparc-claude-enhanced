#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase>=2.0.0",
#   "qdrant-client>=1.7.0",
#   "mistralai>=0.0.8",
#   "rich>=13.0.0",
#   "pydantic>=2.0.0",
#   "python-dotenv>=1.0.0",
# ]
# ///

"""Spec Writer Comprehensive Agent - Creates comprehensive specifications"""

import json
import asyncio
import os
from typing import Dict, Any, List
from pathlib import Path


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
    
    async def _build_agent_prompt(self, task: TaskPayload, context: Dict[str, Any]) -> str:
        """Build agent prompt from task and context"""
        return f"""
Task: {task.description}
Context: {context}
Phase: {task.phase}
Requirements: {task.requirements}
AI Verifiable Outcomes: {task.ai_verifiable_outcomes}
"""

    async def _run_claude(self, prompt: str) -> str:
        """Placeholder for Claude API call"""
        return f"Claude response for: {prompt[:100]}..."

    async def _delegate_task(self, to_agent: str, task_description: str, 
                           task_context: Dict[str, Any], priority: int = 5) -> str:
        """Delegate task to another agent"""
        return await self.delegate_task(to_agent, task_description, task_context, priority)

    @abstractmethod
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        pass



class SpecWriterComprehensiveAgent(BaseAgent):
    """Creates comprehensive and modular specification documents"""
    
    def __init__(self):
        super().__init__(
            agent_name="spec-writer-comprehensive",
            role_definition="You are responsible for creating comprehensive and modular specification documents. You formalize fuzzy requirements into measurable criteria and maintain traceability from requirements to the code and tests that will be created later.",
            custom_instructions="""
You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

Create comprehensive Markdown documents in the 'docs/specifications' directory that detail:
- Functional Requirements with measurable, AI-verifiable success criteria
- Non-Functional Requirements (performance, security, scalability)
- User Stories and Edge Cases
- Data Models and API specifications
- UI/UX flows and accessibility requirements
- Every single class with properties and methods
- Every standalone function with parameters, return types, and detailed descriptions

When you encounter fuzzy requirements, systematically convert them into measurable criteria.
Your specifications must be complete, clear, and verifiable for the next phases.
"""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute comprehensive specification writing using Claude"""
        
        # Build comprehensive prompt for Claude
        prompt = self._build_agent_prompt(task, context)
        
        # Add specification-specific instructions
        spec_prompt = f"""
{prompt}

SPECIFICATION REQUIREMENTS:
Create comprehensive specification documents in Markdown format. Save each as a separate file:

1. docs/specifications/functional_requirements.md
2. docs/specifications/non_functional_requirements.md  
3. docs/specifications/data_models.md
4. docs/specifications/api_specification.md
5. docs/specifications/class_definitions.md
6. docs/specifications/ui_ux_specification.md
7. docs/specifications/edge_cases.md
8. docs/specifications/traceability_matrix.md

For each specification:
- Use clear, measurable language
- Include AI-verifiable success criteria
- Formalize fuzzy requirements into concrete criteria
- Ensure completeness and clarity
- Define every class and function in detail

Create the files and provide the content for each specification area.
"""
        
        # Use Claude to generate specifications
        claude_response = await self._run_claude(spec_prompt)
        
        # Parse response and create files
        files_created = await self._create_specification_files(claude_response)
        
        # Record files with State Scribe
        await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "specifications_created": len(files_created),
                "files": files_created,
                "message": f"Created {len(files_created)} comprehensive specification documents"
            },
            files_created=files_created,
            files_modified=[],
            next_steps=["Specifications ready for pseudocode phase"]
        )
    
    async def _create_specification_files(self, claude_response: str) -> List[str]:
        """Create specification files from Claude's response"""
        
        # Ensure specs directory exists
        specs_dir = Path("docs/specifications")
        specs_dir.mkdir(parents=True, exist_ok=True)
        
        # Parse Claude's response to extract file contents
        # This is a simplified approach - in production you'd have more sophisticated parsing
        files_created = []
        
        spec_files = [
            "functional_requirements.md",
            "non_functional_requirements.md", 
            "data_models.md",
            "api_specification.md",
            "class_definitions.md",
            "ui_ux_specification.md",
            "edge_cases.md",
            "traceability_matrix.md"
        ]
        
        # For each file, extract relevant content from Claude's response
        for spec_file in spec_files:
            file_path = specs_dir / spec_file
            content = self._extract_file_content(claude_response, spec_file)
            
            if content:
                file_path.write_text(content, encoding='utf-8')
                files_created.append(str(file_path))
        
        return files_created
    
    def _extract_file_content(self, claude_response: str, filename: str) -> str:
        """Extract content for a specific file from Claude's response"""
        
        # This would be more sophisticated in production
        # For now, create structured content based on filename
        
        file_type = filename.replace('.md', '').replace('_', ' ').title()
        
        base_content = f"""# {file_type}

## Overview
This document contains the {file_type.lower()} for the project.

## Generated Content
{claude_response}

## AI-Verifiable Outcomes
- Document exists at correct path
- Content is structured and complete
- All requirements are clearly defined
- Traceability is maintained

---
*Generated by spec-writer-comprehensive agent*
"""
        
        return base_content
    
    async def _record_files_with_state_scribe(self, files_created: List[str]):
        """Record created files with State Scribe"""
        
        files_to_record = []
        for file_path in files_created:
            files_to_record.append({
                "file_path": file_path,
                "memory_type": "specification",
                "brief_description": f"Comprehensive specification: {Path(file_path).name}",
                "elements_description": "Detailed specification document with requirements and design",
                "rationale": "Required for SPARC specification phase completion"
            })
        
        # Delegate to State Scribe
        if files_to_record:
            await self._delegate_task(
                to_agent="orchestrator-state-scribe",
                task_description="Record specification files in project memory",
                task_context={"files_to_record": files_to_record},
                priority=8
            )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: uv run sparc/agents/writers/spec_writer_comprehensive.py <task_json>")
        sys.exit(1)
    
    task_json = sys.argv[1]
    task = json.loads(task_json)
    
    task_payload = TaskPayload(
        task_id=task.get("task_id", f"task_{datetime.now().isoformat()}"),
        description=task.get("description", ""),
        context=task.get("context", {}),
        requirements=task.get("requirements", []),
        ai_verifiable_outcomes=task.get("ai_verifiable_outcomes", []),
        phase=task.get("phase", "execution"),
        priority=task.get("priority", 5)
    )
    
    agent = SpecWriterComprehensiveAgent()
    result = asyncio.run(agent._execute_task(task_payload, task.get("context", {})))
    print(json.dumps(result.dict(), indent=2))

