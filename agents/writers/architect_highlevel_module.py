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

"""Architect High-Level Module Agent - Creates system architecture from pseudocode"""

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



class ArchitectHighLevelModuleAgent(BaseAgent):
    """Creates high-level system architecture and module design"""
    
    def __init__(self):
        super().__init__(
            agent_name="architect-highlevel-module",
            role_definition="Your specific purpose is to define the high-level architecture for a software module or the overall system, with a strong focus on resilience, testability, and clarity. Your design will be based on comprehensive specifications and detailed pseudocode provided to you. Your architecture must explicitly plan for chaos engineering and provide clear contracts for test synthesis and verification. Your documentation must be clear enough for human programmers to understand the design and its rationale.",
            custom_instructions="""You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task. Before you answer, you must think through this problem step by step. You will be given the name of the feature or system to architect and all the necessary context from specifications and pseudocode directly in your prompt. Your process commences with a thorough review of these inputs. You will then design the architecture. This involves defining the high-level structure, but you must also explicitly specify the inclusion of resilience patterns like circuit breakers and retries. Your design must define clear, strict API contracts, data models, and service boundaries. The AI-verifiable outcome is the creation of your architecture documents. You must document this architecture in Markdown format within the 'docs/architecture' directory, using C4 model diagrams or UML where appropriate and documenting all Architectural Decision Records (ADRs). Before finalizing, perform a self-reflection on the architecture's quality, resilience, and testability. To conclude, use "attempt_completion". Your summary must be a full, comprehensive natural language report detailing your architectural design, its rationale, how it plans for resilience, and that it is defined and ready for implementation. You must list the paths to your created documents and clarify that this summary does not contain any pre-formatted signal text."""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute architecture design using Claude"""
        
        # Build comprehensive prompt for Claude
        prompt = self._build_agent_prompt(task, context)
        
        # Add architecture-specific instructions
        architecture_prompt = f"""
{prompt}

ARCHITECTURE DESIGN REQUIREMENTS:
Create high-level system architecture with focus on resilience and testability. You must:

1. Define high-level system structure and modules
2. Include resilience patterns (circuit breakers, retries, timeouts)
3. Define clear API contracts and data models
4. Specify service boundaries and dependencies
5. Plan for chaos engineering and testing
6. Document using C4 model or UML diagrams
7. Create Architectural Decision Records (ADRs)
8. Save documentation in 'docs/architecture' directory

Your output should include:
- System architecture overview
- Module design and interactions
- API contracts and data models
- Resilience patterns implementation
- Testing and verification strategies

Generate comprehensive architecture documentation.
"""
        
        # Use Claude via base class
        claude_response = await self._run_claude(architecture_prompt)
        
        # Create files based on response
        files_created = await self._create_architecture_files(claude_response)
        
        # Record files with State Scribe
        await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "architecture_created": True,
                "files_created": len(files_created),
                "files": files_created,
                "message": f"Created {len(files_created)} architecture files"
            },
            files_created=files_created,
            files_modified=[],
            next_steps=["Review architecture design", "Proceed to implementation planning"]
        )
    
    async def _create_architecture_files(self, claude_response: str) -> List[str]:
        """Create architecture files from Claude's response"""
        
        # Create architecture directory
        architecture_dir = Path("docs/architecture")
        architecture_dir.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Create main architecture document
        main_arch_path = architecture_dir / "system_architecture.md"
        main_content = f"""# System Architecture

## Overview
This document defines the high-level architecture for the system, focusing on resilience, testability, and clarity.

## Architecture Design
{claude_response}

## Key Components
- **Core Services**: Primary business logic modules
- **Data Layer**: Database and persistence components
- **API Gateway**: External interface and routing
- **Monitoring**: Observability and metrics
- **Security**: Authentication and authorization

## Resilience Patterns
- Circuit breakers for external dependencies
- Retry mechanisms with exponential backoff
- Timeout configurations
- Graceful degradation strategies
- Health checks and monitoring

## Testing Strategy
- Unit tests for individual components
- Integration tests for service interactions
- End-to-end tests for complete workflows
- Chaos engineering for resilience testing

## AI-Verifiable Outcomes
- Architecture documents are complete
- All modules have clear contracts
- Resilience patterns are defined
- Testing strategies are documented

---
*Generated by architect-highlevel-module agent*
"""
        
        main_arch_path.write_text(main_content, encoding='utf-8')
        files_created.append(str(main_arch_path))
        
        # Create specific architecture documents
        arch_docs = [
            ("api_contracts.md", "API Contracts", "Detailed API specifications and contracts"),
            ("data_models.md", "Data Models", "Database schemas and data structures"),
            ("service_boundaries.md", "Service Boundaries", "Service interfaces and dependencies"),
            ("resilience_patterns.md", "Resilience Patterns", "Fault tolerance and recovery mechanisms"),
            ("deployment_architecture.md", "Deployment Architecture", "Infrastructure and deployment strategy")
        ]
        
        for filename, title, description in arch_docs:
            doc_path = architecture_dir / filename
            doc_content = f"""# {title}

## Overview
{description}

## Details
{claude_response[:500]}...

## Implementation Notes
- Follow established patterns and conventions
- Implement comprehensive error handling
- Add monitoring and observability
- Ensure testability at all levels

## AI-Verifiable Outcomes
- Clear specifications defined
- Implementation guidelines provided
- Testing strategies outlined
- Monitoring approaches specified

---
*Generated by architect-highlevel-module agent*
"""
            
            doc_path.write_text(doc_content, encoding='utf-8')
            files_created.append(str(doc_path))
        
        # Create ADR (Architectural Decision Record) template
        adr_dir = architecture_dir / "adrs"
        adr_dir.mkdir(exist_ok=True)
        
        adr_path = adr_dir / "001-architecture-approach.md"
        adr_content = f"""# ADR-001: Architecture Approach

## Status
Accepted

## Context
Define the high-level architecture approach for the system based on specifications and pseudocode.

## Decision
Adopt a modular, resilient architecture with clear service boundaries and comprehensive testing strategies.

## Consequences
- **Positive**: Clear separation of concerns, testable design, resilient to failures
- **Negative**: Initial complexity, requires disciplined implementation
- **Neutral**: Standard patterns and practices

## Architecture Overview
{claude_response[:300]}...

## Implementation Guidelines
1. Follow established design patterns
2. Implement resilience patterns consistently
3. Maintain clear API contracts
4. Ensure comprehensive testing coverage

---
*Generated by architect-highlevel-module agent*
"""
        
        adr_path.write_text(adr_content, encoding='utf-8')
        files_created.append(str(adr_path))
        
        return files_created
    
    async def _record_files_with_state_scribe(self, files_created: List[str]):
        """Record created files with State Scribe"""
        
        files_to_record = []
        for file_path in files_created:
            files_to_record.append({
                "file_path": file_path,
                "memory_type": "architecture",
                "brief_description": f"Architecture file: {Path(file_path).name}",
                "elements_description": "System architecture documentation with resilience patterns",
                "rationale": "Required for SPARC architecture phase completion"
            })
        
        # Delegate to State Scribe
        if files_to_record:
            await self._delegate_task(
                to_agent="orchestrator-state-scribe",
                task_description="Record architecture files in project memory",
                task_context={"files_to_record": files_to_record},
                priority=8
            )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: uv run sparc/agents/writers/architect_highlevel_module.py <task_json>")
        sys.exit(1)
    
    task_json = sys.argv[1]
    task = json.loads(task_json)
    
    task_payload = TaskPayload(
        description=task.get("description", ""),
        context=task.get("context", {}),
        priority=task.get("priority", 5)
    )
    
    agent = ArchitectHighLevelModuleAgent()
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
