#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase>=2.0.0",
#   "rich",
#   "pydantic",
#   "python-dotenv",
# ]
# ///

"""BMO System Model Synthesizer - System architect for reverse-engineering documentation"""

import json
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


class BMOSystemModelSynthesizer(BaseAgent):
    """Specialist system architect for reverse-engineering and documentation"""
    
    def __init__(self):
        super().__init__(
            agent_name="bmo-system-model-synthesizer",
            role_definition="You are a specialist system architect with expertise in reverse-engineering and documentation. Your function is to analyze the final, integrated codebase and produce a high-fidelity, human-readable document that accurately describes its structure, components, and data flows. Your output serves as the definitive 'Model' component of the BMO framework, representing the ground truth of what was actually built.",
            custom_instructions="""You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

You will be tasked by the BMO orchestrator. Your sole responsibility is to create an accurate model of the implemented system. You must use the use_mcp_tool to perform extensive queries on the project_memorys Supabase database to understand the complete, interconnected system, including all final classes, functions, API endpoints, and their relationships. Synthesize this wealth of information into a clear and comprehensive architectural document. Your AI-verifiable outcome is the creation of this document. You must use the write_to_file tool to save your work as docs/bmo/system_model.md. This document should serve as a clear blueprint of the final application's state, detailing how different parts of the system interact. Your attempt_completion summary must confirm the creation of the system model document and provide its full file path, stating that the 'Model' representation of the system is now ready for holistic verification."""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute system model synthesis"""
        
        # Build prompt using base class
        prompt = self._build_agent_prompt(task, context)
        
        # Add specific instructions for system model synthesis
        specific_prompt = f"""{prompt}

BMO SYSTEM MODEL SYNTHESIS MISSION:
You are now performing comprehensive system model synthesis. Your task is to:

1. COMPREHENSIVE SYSTEM ANALYSIS:
   - Query project_memorys database extensively
   - Analyze all final classes, functions, and components
   - Map API endpoints and their implementations
   - Understand data flows and component relationships
   - Identify integration points and dependencies
   - Analyze the complete system architecture

2. SYSTEM REVERSE-ENGINEERING:
   - Trace execution paths through the system
   - Document component interactions and communication
   - Identify design patterns and architectural decisions
   - Map data structures and their relationships
   - Analyze performance characteristics and bottlenecks
   - Document security measures and access controls

3. ARCHITECTURAL DOCUMENTATION:
   - Create clear system architecture diagrams
   - Document component responsibilities and interfaces
   - Explain data flow and processing pipelines
   - Describe integration patterns and communication protocols
   - Document configuration and deployment architecture
   - Explain error handling and recovery mechanisms

4. MODEL REPRESENTATION:
   - Create high-fidelity system model document
   - Use clear, human-readable language
   - Include visual diagrams and flowcharts
   - Provide detailed component specifications
   - Document system constraints and limitations
   - Include performance and scalability considerations

5. BMO FRAMEWORK INTEGRATION:
   - Serve as the definitive 'Model' component
   - Represent ground truth of implemented system
   - Enable comparison with user intent (Behavior)
   - Support oracle testing validation
   - Facilitate holistic verification process

6. SYSTEM MODEL DOCUMENT:
   - Save as docs/bmo/system_model.md
   - Include comprehensive system blueprint
   - Document actual implementation details
   - Provide clear interaction explanations
   - Ready for holistic verification

Remember: This model represents the ground truth of what was actually built, not what was planned.
"""
        
        # Use Claude via base class
        claude_response = await self._run_claude(specific_prompt)
        
        # Create system model document
        files_created = await self._create_system_model_outputs(claude_response)
        
        # Record with State Scribe
        if files_created:
            await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "system_model_synthesis": claude_response,
                "files_created": files_created
            },
            files_created=files_created,
            files_modified=[],
            next_steps=["Proceed with oracle test generation and holistic verification"]
        )
    
    async def _create_system_model_outputs(self, claude_response: str) -> List[str]:
        """Create system model document"""
        files_created = []
        
        try:
            # Create docs/bmo directory if it doesn't exist
            Path("docs/bmo").mkdir(parents=True, exist_ok=True)
            
            # Create system model document
            model_path = "docs/bmo/system_model.md"
            model_content = self._extract_system_model_content(claude_response)
            
            with open(model_path, 'w', encoding='utf-8') as f:
                f.write(model_content)
            
            files_created.append(model_path)
            
        except Exception as e:
            print(f"Error creating system model outputs: {str(e)}")
        
        return files_created
    
    def _extract_system_model_content(self, claude_response: str) -> str:
        """Extract system model content from Claude response"""
        header = f"""# System Model
Generated: {datetime.now().isoformat()}
Agent: {self.agent_name}

## Overview
This document represents the definitive 'Model' component of the BMO framework, providing a comprehensive blueprint of the final application's state and architecture.

## Model Synthesis Process
This model was created through extensive analysis of the project_memorys database, examining all final classes, functions, API endpoints, and their relationships to create an accurate representation of the implemented system.

## System Architecture

### High-Level Architecture
This section provides an overview of the system's architectural structure and design patterns.

### Component Overview
This section describes the major components and their responsibilities.

### Data Flow Architecture
This section explains how data flows through the system and between components.

### Integration Architecture
This section documents how different parts of the system integrate and communicate.

## Detailed System Model

### Core Components
Detailed documentation of all core system components.

### API Endpoints
Complete documentation of all API endpoints and their implementations.

### Data Models
Comprehensive documentation of all data structures and their relationships.

### Security Architecture
Documentation of security measures and access controls.

### Performance Characteristics
Analysis of system performance and scalability considerations.

### Error Handling
Documentation of error handling and recovery mechanisms.

## System Interactions

### Internal Component Communication
How components within the system communicate with each other.

### External Service Integration
How the system integrates with external services and APIs.

### Data Processing Pipelines
How data is processed and transformed throughout the system.

## Implementation Details

"""
        
        # Add Claude's response content
        return header + claude_response
    
    async def _record_files_with_state_scribe(self, files_created: List[str]) -> None:
        """Record created files with State Scribe"""
        if not files_created:
            return
        
        files_to_record = []
        for file_path in files_created:
            files_to_record.append({
                "file_path": file_path,
                "memory_type": "system_model",
                "brief_description": "Comprehensive system model document",
                "elements_description": "Complete architectural blueprint of the implemented system",
                "rationale": "Serves as the 'Model' component of BMO framework representing ground truth of the built system"
            })
        
        # Delegate to State Scribe
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record BMO system model files in project memory",
            task_context={
                "files_to_record": files_to_record,
                "phase": "bmo_system_model"
            }
        )

async def main():
    """Main execution function"""
    agent = BMOSystemModelSynthesizer()
    
    # Example task
    task = TaskPayload(
        task_id="bmo_system_model_synthesis",
        description="Synthesize comprehensive system model from implemented codebase",
        requirements=["Analyze final integrated codebase", "Create system model document"],
        ai_verifiable_outcomes=["Create docs/bmo/system_model.md"],
        phase="bmo_system_model",
        priority=2
    )
    
    result = await agent.execute(task)
    print(f"BMO System Model Synthesizer completed: {result.success}")
    if result.files_created:
        print(f"Files created: {', '.join(result.files_created)}")

if __name__ == "__main__":
    asyncio.run(main())

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
