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

"""Docs Writer Feature Agent - Creates feature documentation"""

import json
import asyncio
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
    
    @abstractmethod
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        pass

from lib.claude_runner import ClaudeRunner
from lib.utils import ensure_directory, format_file_for_memory

class DocsWriterFeatureAgent(BaseAgent):
    """Creates comprehensive feature documentation"""
    
    def __init__(self):
        super().__init__(
            agent_name="docs-writer-feature",
            role_definition="You are responsible for creating comprehensive feature documentation that explains how features work, their benefits, and how users can effectively use them.",
            custom_instructions="""
You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

Your task is to create clear, user-friendly documentation that:
- Explains features in simple, accessible language
- Provides practical examples and use cases
- Includes troubleshooting and FAQ sections
- Covers installation, configuration, and usage
- Maintains consistency with project goals and specifications

Create documentation in the 'docs/' directory with appropriate structure and organization.
"""
        )
        self.claude_runner = ClaudeRunner()
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute feature documentation writing using Claude"""
        
        # Ensure docs directory exists
        docs_dir = Path("docs")
        ensure_directory(docs_dir)
        
        # Get project context from memory
        project_context = await self.memory.get_project_state()
        
        # Determine documentation type and target
        doc_type = context.get("document_type", "feature")
        target_file = context.get("deliverable", "docs/feature_documentation.md")
        
        # Build documentation prompt for Claude
        docs_prompt = self._build_documentation_prompt(task, context, project_context, doc_type)
        
        # Use Claude to generate documentation
        claude_response = await self.claude_runner.run_claude_task(
            prompt=docs_prompt,
            task_context={
                "task_type": "documentation_writing",
                "document_type": doc_type,
                "target_file": target_file,
                "project_goal": task.description
            }
        )
        
        # Create documentation file
        files_created = await self._create_documentation_file(claude_response, target_file)
        
        # Record files with State Scribe
        await self._record_files_with_state_scribe(files_created, "documentation")
        
        return AgentResult(
            success=True,
            outputs={
                "documentation_created": len(files_created),
                "files": files_created,
                "document_type": doc_type,
                "message": f"Created {doc_type} documentation successfully"
            },
            files_created=files_created,
            files_modified=[],
            next_steps=[f"{doc_type.title()} documentation ready for review"]
        )
    
    def _build_documentation_prompt(self, task: TaskPayload, context: Dict[str, Any], 
                                   project_context: Dict[str, Any], doc_type: str) -> str:
        """Build a comprehensive prompt for Claude to generate documentation"""
        
        prompt_templates = {
            "feature": """
Create comprehensive feature documentation for this project:

PROJECT GOAL: {project_goal}

Create user-friendly documentation that includes:
- Feature overview and benefits
- Installation and setup instructions
- Usage examples and tutorials
- Configuration options
- Troubleshooting guide
- FAQ section
- Best practices

Use clear, accessible language suitable for end users.
""",
            "mutual_understanding": """
Create a Mutual Understanding Document that captures:

PROJECT GOAL: {project_goal}

Include:
- Project overview and objectives
- Key stakeholders and their roles
- Success criteria and metrics
- Assumptions and constraints
- Risks and mitigation strategies
- Communication plan
- Approval criteria

This document should establish clear mutual understanding between all parties.
""",
            "constraints_and_anti_goals": """
Create a Constraints and Anti-Goals document that defines:

PROJECT GOAL: {project_goal}

Include:
- Technical constraints and limitations
- Resource constraints (time, budget, team)
- Regulatory and compliance requirements
- Anti-goals (what we explicitly won't do)
- Trade-offs and decisions
- Boundary conditions
- Validation criteria

This document should clearly define project boundaries and limitations.
""",
            "api": """
Create comprehensive API documentation that includes:

PROJECT GOAL: {project_goal}

Include:
- API overview and architecture
- Authentication and authorization
- Endpoint documentation with examples
- Request/response formats
- Error handling and status codes
- Rate limiting and usage guidelines
- SDKs and client libraries
- Integration examples

Make it developer-friendly with clear examples.
"""
        }
        
        template = prompt_templates.get(doc_type, prompt_templates["feature"])
        
        return template.format(
            project_goal=task.description,
            context=json.dumps(context, indent=2),
            project_state=json.dumps(project_context, indent=2)
        )
    
    async def _create_documentation_file(self, claude_response: str, target_file: str) -> List[str]:
        """Create documentation file from Claude's response"""
        
        file_path = Path(target_file)
        ensure_directory(file_path.parent)
        
        # Write Claude's response to the file
        file_path.write_text(claude_response, encoding='utf-8')
        
        return [str(file_path)]
    
    async def _record_files_with_state_scribe(self, files_created: List[str], memory_type: str):
        """Record created files with State Scribe"""
        
        files_to_record = []
        for file_path in files_created:
            file_info = format_file_for_memory(
                Path(file_path),
                memory_type,
                f"Feature documentation: {Path(file_path).name}"
            )
            files_to_record.append(file_info)
        
        # Delegate to State Scribe
        if files_to_record:
            await self._delegate_task(
                to_agent="orchestrator-state-scribe",
                task_description="Record documentation files in project memory",
                task_context={"files_to_record": files_to_record},
                priority=8
            )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: uv run sparc/agents/writers/docs_writer_feature.py <task_json>")
        sys.exit(1)
    
    task_json = sys.argv[1]
    task = json.loads(task_json)
    
    task_payload = TaskPayload(
        description=task.get("description", ""),
        context=task.get("context", {}),
        priority=task.get("priority", 5)
    )
    
    agent = DocsWriterFeatureAgent()
    result = asyncio.run(agent._execute_task(task_payload, task.get("context", {})))
    print(json.dumps(result.dict(), indent=2))

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
