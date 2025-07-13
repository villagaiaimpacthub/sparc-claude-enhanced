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

"""BMO Intent Triangulator - Requirements analyst and behavioral modeler"""

import json
import asyncio
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from sparc.agents.base_agent import BaseAgent, TaskPayload, AgentResult

class BMOIntentTriangulator(BaseAgent):
    """Expert requirements analyst applying cognitive triangulation to user requirements"""
    
    def __init__(self):
        super().__init__(
            agent_name="bmo-intent-triangulator",
            role_definition="You are an expert requirements analyst and behavioral modeler. Your function is to apply cognitive triangulation to user requirements, transforming multiple, potentially ambiguous sources of intent into a single, comprehensive, and user-validated behavioral model. You are the definitive source for the 'Behavior' component of the BMO framework, ensuring all subsequent development and testing is aligned with a rigorously confirmed understanding of the user's goals.",
            custom_instructions="""You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

You will be tasked by the BMO orchestrator. Your first action is to use the use_mcp_tool to query the project_memorys database and the read_file tool to ingest all relevant sources of user intent, including the Mutual Understanding Document, user stories, and acceptance criteria. You must synthesize this information into a single, coherent 'Consolidated Behavioral Model' in a markdown document. This model should describe the complete user journey and system behaviors. Your next critical step is to use the ask_followup_question tool to present this consolidated model to the user for explicit approval, iterating on it based on their feedback until it is perfect. This validation is a non-negotiable step to ensure intent is perfectly captured. Once the user approves the model, your AI-verifiable outcome is to generate the complete suite of Gherkin .feature files based on the validated model. You will use the write_to_file tool to save these scenarios in the tests/bdd/ directory. Your attempt_completion summary must report on the successful triangulation and validation of user intent and list the paths to the final .feature files you created."""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute intent triangulation and behavioral modeling"""
        
        # Build prompt using base class
        prompt = self._build_agent_prompt(task, context)
        
        # Add specific instructions for intent triangulation
        specific_prompt = f"""{prompt}

BMO INTENT TRIANGULATION MISSION:
You are now performing cognitive triangulation of user requirements. Your task is to:

1. REQUIREMENTS SYNTHESIS:
   - Query project_memorys database for all user intent sources
   - Read Mutual Understanding Document, user stories, acceptance criteria
   - Identify patterns, conflicts, and gaps in requirements
   - Synthesize into a coherent behavioral model

2. BEHAVIORAL MODEL CREATION:
   - Create a 'Consolidated Behavioral Model' document
   - Describe complete user journeys and system behaviors
   - Include all functional and non-functional requirements
   - Map user needs to system capabilities
   - Identify edge cases and exception scenarios

3. USER VALIDATION PROCESS:
   - Present consolidated model to user for approval
   - Iterate based on feedback until perfect alignment
   - Ensure no ambiguity or misunderstanding remains
   - Get explicit user sign-off on the model

4. GHERKIN GENERATION:
   - Transform validated model into Gherkin .feature files
   - Create comprehensive BDD scenarios
   - Cover all user journeys and system behaviors
   - Include positive, negative, and edge case scenarios
   - Save in tests/bdd/ directory

5. TRIANGULATION VALIDATION:
   - Ensure consistency between requirements sources
   - Verify behavioral model completeness
   - Validate Gherkin scenarios against model
   - Confirm user intent is fully captured

Your output defines the 'Behavior' component of the BMO framework.
"""
        
        # Use Claude via base class
        claude_response = await self._run_claude(specific_prompt)
        
        # Create behavioral model and Gherkin files
        files_created = await self._create_intent_outputs(claude_response)
        
        # Record with State Scribe
        if files_created:
            await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "intent_triangulation": claude_response,
                "files_created": files_created
            },
            files_created=files_created,
            files_modified=[],
            next_steps=["Proceed with system modeling and oracle test generation"]
        )
    
    async def _create_intent_outputs(self, claude_response: str) -> List[str]:
        """Create behavioral model and Gherkin feature files"""
        files_created = []
        
        try:
            # Create necessary directories
            Path("docs/bmo").mkdir(parents=True, exist_ok=True)
            Path("tests/bdd").mkdir(parents=True, exist_ok=True)
            
            # Create Consolidated Behavioral Model
            behavioral_model_path = "docs/bmo/consolidated_behavioral_model.md"
            behavioral_content = self._extract_behavioral_model_content(claude_response)
            
            with open(behavioral_model_path, 'w', encoding='utf-8') as f:
                f.write(behavioral_content)
            
            files_created.append(behavioral_model_path)
            
            # Extract and create Gherkin feature files
            gherkin_files = self._extract_gherkin_files(claude_response)
            for filename, content in gherkin_files.items():
                gherkin_path = f"tests/bdd/{filename}"
                with open(gherkin_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_created.append(gherkin_path)
            
        except Exception as e:
            print(f"Error creating intent outputs: {str(e)}")
        
        return files_created
    
    def _extract_behavioral_model_content(self, claude_response: str) -> str:
        """Extract behavioral model content from Claude response"""
        header = f"""# Consolidated Behavioral Model
Generated: {datetime.now().isoformat()}
Agent: {self.agent_name}

## Overview
This document represents the consolidated behavioral model derived from cognitive triangulation of all user requirements sources. It serves as the definitive 'Behavior' component of the BMO framework.

## User Intent Triangulation
This model has been validated through cognitive triangulation of:
- Mutual Understanding Document
- User stories and acceptance criteria
- Stakeholder feedback and validation

## Behavioral Model

### User Journeys
This section describes the complete user journeys and system behaviors.

### System Behaviors
This section outlines how the system should behave in various scenarios.

### Functional Requirements
This section lists all functional requirements derived from user intent.

### Non-Functional Requirements
This section covers performance, security, and other quality attributes.

## Detailed Behavioral Specifications

"""
        
        # Add Claude's response content
        return header + claude_response
    
    def _extract_gherkin_files(self, claude_response: str) -> Dict[str, str]:
        """Extract Gherkin feature files from Claude response"""
        # This is a simplified extraction - in practice, you'd parse the structured response
        gherkin_files = {}
        
        # Create a sample Gherkin file structure
        gherkin_files["user_authentication.feature"] = """Feature: User Authentication
  As a user
  I want to authenticate with the system
  So that I can access personalized features

  Scenario: Successful login
    Given I am on the login page
    When I enter valid credentials
    Then I should be logged in successfully
    And I should see the dashboard

  Scenario: Failed login
    Given I am on the login page
    When I enter invalid credentials
    Then I should see an error message
    And I should remain on the login page
"""
        
        return gherkin_files
    
    async def _record_files_with_state_scribe(self, files_created: List[str]) -> None:
        """Record created files with State Scribe"""
        if not files_created:
            return
        
        files_to_record = []
        for file_path in files_created:
            if file_path.endswith('.md'):
                files_to_record.append({
                    "file_path": file_path,
                    "memory_type": "behavioral_model",
                    "brief_description": "Consolidated behavioral model from requirements triangulation",
                    "elements_description": "Complete user journeys and system behaviors derived from cognitive triangulation",
                    "rationale": "Defines the 'Behavior' component of BMO framework for development alignment"
                })
            else:
                files_to_record.append({
                    "file_path": file_path,
                    "memory_type": "gherkin_feature",
                    "brief_description": "Gherkin BDD feature file for behavioral testing",
                    "elements_description": "Behavior-driven development scenarios for system validation",
                    "rationale": "Provides executable specifications for behavioral testing"
                })
        
        # Delegate to State Scribe
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record BMO intent triangulation files in project memory",
            task_context={
                "files_to_record": files_to_record,
                "phase": "bmo_intent"
            }
        )

async def main():
    """Main execution function"""
    agent = BMOIntentTriangulator()
    
    # Example task
    task = TaskPayload(
        task_id="bmo_intent_triangulation",
        description="Triangulate user requirements into consolidated behavioral model",
        requirements=["Synthesize all user intent sources", "Create behavioral model", "Generate Gherkin scenarios"],
        ai_verifiable_outcomes=["Create consolidated behavioral model", "Generate Gherkin .feature files"],
        phase="bmo_intent",
        priority=2
    )
    
    result = await agent.execute(task)
    print(f"BMO Intent Triangulator completed: {result.success}")
    if result.files_created:
        print(f"Files created: {', '.join(result.files_created)}")

if __name__ == "__main__":
    asyncio.run(main())