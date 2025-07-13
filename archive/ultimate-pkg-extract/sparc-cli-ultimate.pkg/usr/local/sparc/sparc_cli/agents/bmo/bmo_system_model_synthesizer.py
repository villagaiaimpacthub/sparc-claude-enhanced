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

from sparc.agents.base_agent import BaseAgent, TaskPayload, AgentResult

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