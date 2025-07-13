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

from agents.base_agent import BaseAgent, TaskPayload, AgentResult
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