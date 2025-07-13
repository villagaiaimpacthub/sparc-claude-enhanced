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

"""Code Comprehension Assistant v2 - SPARC aligned code analysis specialist"""

import json
import asyncio
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from sparc.agents.base_agent import BaseAgent, TaskPayload, AgentResult

class CodeComprehensionAssistantV2(BaseAgent):
    """Analyzes codebase structure and behavior for comprehension reports"""
    
    def __init__(self):
        super().__init__(
            agent_name="code-comprehension-assistant-v2",
            role_definition="Your specific purpose is to analyze a designated area of the codebase to gain a thorough understanding of its static structure and dynamic behavior. You will analyze its functionality, underlying structure, and potential issues. This comprehension is a precursor to refinement or maintenance activities. The report you generate must be saved in the 'docs/reports' directory and crafted so that human programmers can quickly grasp the code's nature.",
            custom_instructions="""You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

Before you answer, you must think through this problem step by step. When you write documents, you must avoid every '|' character and substitute it with '--', and also avoid patterns like ':---'. You will receive paths to the code you need to analyze and all relevant context in your prompt. Your workflow begins by identifying the entry points and scope of the code, then meticulously analyzing the code structure and logic using the "read_file" tool. You must synthesize your findings into a comprehensive summary document. Your AI-verifiable outcome is the creation of this summary document at a specified path within 'docs/reports'. The report must cover the code's purpose, its main components, data flows, and potential areas for improvement or concern. After writing the report, you will use "attempt_completion". Your completion summary must be a full comprehensive natural language report detailing your comprehension process and findings, confirming the report's creation, and providing its file path. You should not produce any colon-separated signal text or structured signal proposals."""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute code comprehension analysis"""
        
        # Build prompt using base class
        prompt = self._build_agent_prompt(task, context)
        
        # Add specific instructions for code comprehension
        specific_prompt = f"""{prompt}

CODE COMPREHENSION ANALYSIS MISSION:
You are now performing a comprehensive code comprehension analysis. Your task is to:

1. ANALYSIS SCOPE:
   - Identify entry points and code boundaries
   - Understand the overall architecture and structure
   - Analyze data flows and dependencies
   - Examine functionality and behavior patterns

2. COMPREHENSIVE ANALYSIS AREAS:
   - Static structure: Classes, functions, modules, interfaces
   - Dynamic behavior: Control flow, data flow, interactions
   - Design patterns and architectural decisions
   - Code quality: Maintainability, readability, complexity
   - Performance considerations and bottlenecks
   - Security implications and vulnerabilities
   - Testing coverage and quality
   - Documentation accuracy and completeness

3. ANALYSIS PROCESS:
   - Read and analyze the specified code files
   - Map relationships between components
   - Identify critical paths and dependencies
   - Evaluate code quality and potential issues
   - Document findings in a structured manner

4. OUTPUT REQUIREMENTS:
   - Create a comprehensive code comprehension report
   - Save it in 'docs/reports' directory
   - Include visual diagrams where helpful
   - Provide actionable insights for improvement
   - Format for human programmer consumption

Remember: Focus on creating a clear, actionable report that helps human programmers understand the code's nature and identify areas for refinement.
"""
        
        # Use Claude via base class
        claude_response = await self._run_claude(specific_prompt)
        
        # Create comprehension report
        files_created = await self._create_comprehension_outputs(claude_response)
        
        # Record with State Scribe
        if files_created:
            await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "comprehension_analysis": claude_response,
                "files_created": files_created
            },
            files_created=files_created,
            files_modified=[],
            next_steps=["Review comprehension findings and plan refinement activities"]
        )
    
    async def _create_comprehension_outputs(self, claude_response: str) -> List[str]:
        """Create code comprehension report files"""
        files_created = []
        
        try:
            # Create docs/reports directory if it doesn't exist
            Path("docs/reports").mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = f"docs/reports/code_comprehension_report_{timestamp}.md"
            
            # Extract comprehension content from response
            comprehension_content = self._extract_comprehension_content(claude_response)
            
            # Write comprehension report
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(comprehension_content)
            
            files_created.append(report_path)
            
        except Exception as e:
            print(f"Error creating comprehension outputs: {str(e)}")
        
        return files_created
    
    def _extract_comprehension_content(self, claude_response: str) -> str:
        """Extract comprehension content from Claude response"""
        header = f"""# Code Comprehension Report
Generated: {datetime.now().isoformat()}
Agent: {self.agent_name}

## Executive Summary
This report provides a comprehensive analysis of the codebase structure, behavior, and quality to support refinement and maintenance activities.

## Analysis Methodology
1. Static Structure Analysis: Examined classes, functions, and modules
2. Dynamic Behavior Analysis: Analyzed control flow and data flow
3. Quality Assessment: Evaluated maintainability and potential issues
4. Recommendations: Identified areas for improvement

## Findings and Analysis

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
                "memory_type": "comprehension_report",
                "brief_description": "Code comprehension analysis report",
                "elements_description": "Comprehensive analysis of codebase structure, behavior, and quality",
                "rationale": "Provides understanding of code nature to support refinement and maintenance"
            })
        
        # Delegate to State Scribe
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record code comprehension analysis files in project memory",
            task_context={
                "files_to_record": files_to_record,
                "phase": "analysis"
            }
        )

async def main():
    """Main execution function"""
    agent = CodeComprehensionAssistantV2()
    
    # Example task
    task = TaskPayload(
        task_id="code_comprehension_analysis",
        description="Analyze codebase structure and behavior for comprehension report",
        requirements=["Analyze code structure, behavior, and quality"],
        ai_verifiable_outcomes=["Create detailed comprehension report in docs/reports"],
        phase="analysis",
        priority=3
    )
    
    result = await agent.execute(task)
    print(f"Code Comprehension Assistant v2 completed: {result.success}")
    if result.files_created:
        print(f"Files created: {', '.join(result.files_created)}")

if __name__ == "__main__":
    asyncio.run(main())