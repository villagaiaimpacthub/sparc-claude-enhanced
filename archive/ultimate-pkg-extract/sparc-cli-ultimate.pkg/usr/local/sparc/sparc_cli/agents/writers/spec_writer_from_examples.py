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

"""Spec Writer From Examples Agent - Creates user stories from examples"""

import json
import asyncio
from typing import Dict, Any, List
from pathlib import Path

from sparc.agents.base_agent import BaseAgent, TaskPayload, AgentResult


class SpecWriterFromExamplesAgent(BaseAgent):
    """Creates comprehensive user stories from examples and fuzzy requirements"""
    
    def __init__(self):
        super().__init__(
            agent_name="spec-writer-from-examples",
            role_definition="You are an expert in extracting specifications from user examples and creating comprehensive user stories. Your function includes conducting deep recursive research on user interaction patterns, converting fuzzy requirements into measurable criteria, and generating clarifying questions for ambiguous specifications. You create user stories that serve as the foundation for defining acceptance criteria and high-level tests.",
            custom_instructions="""You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task. Before you answer, think through this problem step by step. You will be tasked by the specification orchestrator with all necessary context provided in your prompt. You must follow an internal quality assurance protocol to ensure your user stories are clear and have measurable, AI-verifiable criteria. Your primary AI-verifiable outcome is the creation of a 'user_stories.md' document in the 'docs/specifications/' directory. When you encounter vague requirements like 'user-friendly', you must convert them into measurable criteria such as 'primary action reachable in under 3 clicks' or 'page load time under 2 seconds'. Use "write_to_file" to create the 'user_stories.md' document. Each story must follow the format: As a [persona], I want to [goal], so that [benefit], with detailed, measurable acceptance criteria that an AI can later verify programmatically. Your "attempt_completion" summary must be a comprehensive report detailing the user stories you created, how fuzzy requirements were formalized, any clarifying questions generated, and the path to the file you created."""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute user story creation using Claude"""
        
        prompt = self._build_agent_prompt(task, context)
        
        user_story_prompt = f"""
{prompt}

USER STORY CREATION REQUIREMENTS:
Create comprehensive user stories from examples and requirements. You must:

1. Extract specifications from user examples
2. Convert fuzzy requirements into measurable criteria
3. Create user stories with format: As a [persona], I want to [goal], so that [benefit]
4. Include detailed, measurable acceptance criteria
5. Generate clarifying questions for ambiguous requirements
6. Save to 'docs/specifications/user_stories.md'
7. Ensure all criteria are AI-verifiable

Generate comprehensive user stories documentation.
"""
        
        claude_response = await self._run_claude(user_story_prompt)
        files_created = await self._create_user_story_files(claude_response)
        await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "user_stories_created": True,
                "files_created": len(files_created),
                "files": files_created,
                "message": f"Created {len(files_created)} user story files"
            },
            files_created=files_created,
            files_modified=[],
            next_steps=["Review user stories", "Create acceptance tests", "Validate with stakeholders"]
        )
    
    async def _create_user_story_files(self, claude_response: str) -> List[str]:
        """Create user story files from Claude's response"""
        
        specs_dir = Path("docs/specifications")
        specs_dir.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Create main user stories document
        user_stories_path = specs_dir / "user_stories.md"
        user_stories_content = f"""# User Stories

## Overview
This document contains comprehensive user stories extracted from examples and requirements, with measurable acceptance criteria.

## User Stories
{claude_response}

## Story Format
Each user story follows the format:
- **As a** [persona]
- **I want to** [goal]
- **So that** [benefit]

## Acceptance Criteria
All acceptance criteria are:
- Measurable and specific
- AI-verifiable
- Testable through automation
- Clear and unambiguous

## AI-Verifiable Outcomes
- User stories are complete and well-structured
- Acceptance criteria are measurable
- Fuzzy requirements have been formalized
- Stories are ready for test creation

---
*Generated by spec-writer-from-examples agent*
"""
        
        user_stories_path.write_text(user_stories_content, encoding='utf-8')
        files_created.append(str(user_stories_path))
        
        return files_created
    
    async def _record_files_with_state_scribe(self, files_created: List[str]):
        """Record created files with State Scribe"""
        
        files_to_record = []
        for file_path in files_created:
            files_to_record.append({
                "file_path": file_path,
                "memory_type": "user_story",
                "brief_description": f"User story file: {Path(file_path).name}",
                "elements_description": "User stories with measurable acceptance criteria",
                "rationale": "Required for SPARC specification phase completion"
            })
        
        if files_to_record:
            await self._delegate_task(
                to_agent="orchestrator-state-scribe",
                task_description="Record user story files in project memory",
                task_context={"files_to_record": files_to_record},
                priority=8
            )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: uv run sparc/agents/writers/spec_writer_from_examples.py <task_json>")
        sys.exit(1)
    
    task_json = sys.argv[1]
    task = json.loads(task_json)
    
    task_payload = TaskPayload(
        description=task.get("description", ""),
        context=task.get("context", {}),
        priority=task.get("priority", 5)
    )
    
    agent = SpecWriterFromExamplesAgent()
    result = asyncio.run(agent._execute_task(task_payload, task.get("context", {})))
    print(json.dumps(result.dict(), indent=2))