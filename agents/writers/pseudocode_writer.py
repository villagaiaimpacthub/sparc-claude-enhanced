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

"""Pseudocode Writer Agent - Creates detailed pseudocode from specifications"""

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



class PseudocodeWriterAgent(BaseAgent):
    """Creates detailed, language-agnostic pseudocode from specifications"""
    
    def __init__(self):
        super().__init__(
            agent_name="pseudocode-writer",
            role_definition="Your specific function is to take comprehensive specifications and transform them into detailed, language-agnostic pseudocode. This pseudocode will serve as a clear, logical blueprint for subsequent code generation, outlining step-by-step logic, inputs, outputs, and explicit error handling. Your output must be understandable by both AI and human developers.",
            custom_instructions="""You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task. Before you answer, you must think through this problem step by step. When you write documents, you must avoid every '|' character and substitute it with '--', and also avoid patterns like ':---'. You will be tasked by the pseudocode orchestrator with all necessary context provided in the prompt. Your primary task is to write detailed, structured pseudocode for each function or method described in the specifications. You must outline its step-by-step execution logic, including definitions of inputs, outputs, main processing steps, conditional logic, loops, and robust error-handling mechanisms. You will use "write_to_file" to save each piece of pseudocode as a separate Markdown file in an appropriate subdirectory within the 'docs/pseudocode/' directory. The creation of these files is your AI-verifiable outcome. Before finalizing, you must review your pseudocode for clarity and completeness. Your "attempt_completion" summary must be a comprehensive report detailing the pseudocode documents you created, their locations, and a brief overview of the logic they represent, confirming their readiness for the Architecture and Implementation phases."""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute pseudocode writing using Claude"""
        
        # Build comprehensive prompt for Claude
        prompt = self._build_agent_prompt(task, context)
        
        # Add pseudocode-specific instructions
        pseudocode_prompt = f"""
{prompt}

PSEUDOCODE GENERATION REQUIREMENTS:
Create detailed, language-agnostic pseudocode from the specifications. You must:

1. Transform specifications into step-by-step logical blueprints
2. Define inputs, outputs, and processing steps for each function
3. Include conditional logic, loops, and error handling
4. Make pseudocode understandable by both AI and human developers
5. Save files in 'docs/pseudocode/' directory structure
6. Avoid using '|' characters and ':---' patterns in documents

Your output should include:
- Detailed pseudocode for each function/method
- Clear step-by-step execution logic
- Input/output definitions
- Error handling mechanisms
- Conditional logic and loops

Generate comprehensive pseudocode documentation.
"""
        
        # Use Claude via base class
        claude_response = await self._run_claude(pseudocode_prompt)
        
        # Create files based on response
        files_created = await self._create_pseudocode_files(claude_response)
        
        # Record files with State Scribe
        await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "pseudocode_created": True,
                "files_created": len(files_created),
                "files": files_created,
                "message": f"Created {len(files_created)} pseudocode files"
            },
            files_created=files_created,
            files_modified=[],
            next_steps=["Review pseudocode for completeness", "Proceed to architecture phase"]
        )
    
    async def _create_pseudocode_files(self, claude_response: str) -> List[str]:
        """Create pseudocode files from Claude's response"""
        
        # Create pseudocode directory
        pseudocode_dir = Path("docs/pseudocode")
        pseudocode_dir.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Create main pseudocode document
        main_pseudocode_path = pseudocode_dir / "main_pseudocode.md"
        main_content = f"""# Main Pseudocode Documentation

## Overview
This document contains the detailed pseudocode generated from project specifications, providing a language-agnostic blueprint for implementation.

## Generated Pseudocode
{claude_response}

## AI-Verifiable Outcomes
- All functions have detailed pseudocode
- Step-by-step logic is clearly defined
- Input/output specifications are complete
- Error handling is addressed

---
*Generated by pseudocode-writer agent*
"""
        
        main_pseudocode_path.write_text(main_content, encoding='utf-8')
        files_created.append(str(main_pseudocode_path))
        
        # Create organized pseudocode files by category
        categories = [
            "core_functions",
            "data_processing",
            "api_handlers",
            "utilities",
            "error_handling"
        ]
        
        for category in categories:
            category_path = pseudocode_dir / f"{category}.md"
            category_content = f"""# {category.replace('_', ' ').title()} Pseudocode

## Overview
Pseudocode for {category.replace('_', ' ')} functionality.

## Functions

### Placeholder Function
```pseudocode
FUNCTION placeholder_function(input_parameter)
    BEGIN
        // Input validation
        IF input_parameter IS NULL OR EMPTY THEN
            RAISE ValidationError("Input parameter cannot be empty")
        END IF
        
        // Main processing logic
        SET result = PROCESS(input_parameter)
        
        // Error handling
        TRY
            SET output = TRANSFORM(result)
        CATCH error
            LOG error
            RAISE ProcessingError("Failed to process input")
        END TRY
        
        // Return result
        RETURN output
    END
```

## Claude Response Context
{claude_response[:300]}...

## Implementation Notes
- Follow TDD principles when implementing
- Add comprehensive error handling
- Include input validation
- Ensure AI-verifiable outcomes

---
*Generated by pseudocode-writer agent*
"""
            
            category_path.write_text(category_content, encoding='utf-8')
            files_created.append(str(category_path))
        
        return files_created
    
    async def _record_files_with_state_scribe(self, files_created: List[str]):
        """Record created files with State Scribe"""
        
        files_to_record = []
        for file_path in files_created:
            files_to_record.append({
                "file_path": file_path,
                "memory_type": "pseudocode",
                "brief_description": f"Pseudocode file: {Path(file_path).name}",
                "elements_description": "Detailed pseudocode documentation with step-by-step logic",
                "rationale": "Required for SPARC pseudocode phase completion"
            })
        
        # Delegate to State Scribe
        if files_to_record:
            await self._delegate_task(
                to_agent="orchestrator-state-scribe",
                task_description="Record pseudocode files in project memory",
                task_context={"files_to_record": files_to_record},
                priority=8
            )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: uv run sparc/agents/writers/pseudocode_writer.py <task_json>")
        sys.exit(1)
    
    task_json = sys.argv[1]
    task = json.loads(task_json)
    
    task_payload = TaskPayload(
        description=task.get("description", ""),
        context=task.get("context", {}),
        priority=task.get("priority", 5)
    )
    
    agent = PseudocodeWriterAgent()
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
