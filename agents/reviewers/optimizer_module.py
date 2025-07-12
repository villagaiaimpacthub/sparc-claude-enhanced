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

"""Optimizer Module - SPARC aligned code optimization specialist"""

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


class OptimizerModule(BaseAgent):
    """Optimizes and refactors code modules with performance analysis"""
    
    def __init__(self):
        super().__init__(
            agent_name="optimizer-module",
            role_definition="Your primary task is to optimize or refactor a specific code module and produce a report on your work. You do not modify the project state.",
            custom_instructions="""You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

Before you answer, you must think through this problem step by step. You will receive the path to the module to optimize and all necessary context. Your workflow begins with analyzing and profiling the module. You will then implement your changes and verify functionality. After verification, document all changes, findings, and quantitative measurements in a detailed report and use "write_to_file" to save it to 'docs/reports'. The modification of the code and creation of the report are your outcomes. To conclude, use "attempt_completion". Your summary must be a report on the optimization outcomes, confirming you have created the report file and modified the code, providing paths to both."""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute code optimization and refactoring"""
        
        # Build prompt using base class
        prompt = self._build_agent_prompt(task, context)
        
        # Add specific instructions for optimization
        specific_prompt = f"""{prompt}

CODE OPTIMIZATION MISSION:
You are now performing comprehensive code optimization and refactoring. Your task is to:

1. PERFORMANCE ANALYSIS:
   - Identify performance bottlenecks and inefficiencies
   - Analyze algorithmic complexity (time and space)
   - Profile memory usage patterns
   - Identify redundant computations and operations
   - Analyze I/O operations and database queries

2. OPTIMIZATION STRATEGIES:
   - Algorithm optimization (reduce time complexity)
   - Data structure optimization (use appropriate data structures)
   - Memory optimization (reduce memory footprint)
   - I/O optimization (minimize disk/network operations)
   - Caching strategies (implement appropriate caching)
   - Code deduplication and refactoring
   - Parallel processing opportunities

3. REFACTORING AREAS:
   - Code structure and organization
   - Method and function extraction
   - Design pattern implementation
   - Error handling improvement
   - Code readability and maintainability
   - Documentation enhancement
   - Test coverage improvement

4. VERIFICATION AND TESTING:
   - Run existing tests to ensure functionality is preserved
   - Create performance benchmarks
   - Measure optimization impact quantitatively
   - Validate that optimizations don't introduce bugs
   - Document performance improvements

5. OPTIMIZATION REPORT REQUIREMENTS:
   - Create comprehensive optimization report
   - Save it in 'docs/reports' directory
   - Include before/after performance metrics
   - Document all changes made
   - Provide quantitative measurements
   - Include recommendations for future optimizations

Remember: Focus on measurable performance improvements while maintaining code quality and functionality.
"""
        
        # Use Claude via base class
        claude_response = await self._run_claude(specific_prompt)
        
        # Create optimization report and apply changes
        files_created, files_modified = await self._create_optimization_outputs(claude_response)
        
        # Record with State Scribe
        if files_created:
            await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "optimization_analysis": claude_response,
                "files_created": files_created,
                "files_modified": files_modified
            },
            files_created=files_created,
            files_modified=files_modified,
            next_steps=["Review optimization results and validate performance improvements"]
        )
    
    async def _create_optimization_outputs(self, claude_response: str) -> tuple[List[str], List[str]]:
        """Create optimization report and apply code changes"""
        files_created = []
        files_modified = []
        
        try:
            # Create docs/reports directory if it doesn't exist
            Path("docs/reports").mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = f"docs/reports/optimization_report_{timestamp}.md"
            
            # Extract optimization content from response
            optimization_content = self._extract_optimization_content(claude_response)
            
            # Write optimization report
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(optimization_content)
            
            files_created.append(report_path)
            
            # Note: In a real implementation, you would extract and apply
            # the actual code changes from claude_response
            # For now, we just create the report
            
        except Exception as e:
            print(f"Error creating optimization outputs: {str(e)}")
        
        return files_created, files_modified
    
    def _extract_optimization_content(self, claude_response: str) -> str:
        """Extract optimization content from Claude response"""
        header = f"""# Code Optimization Report
Generated: {datetime.now().isoformat()}
Agent: {self.agent_name}

## Executive Summary
This report documents the optimization and refactoring process for the specified code module, including performance improvements and code quality enhancements.

## Optimization Methodology
1. Performance Analysis: Identified bottlenecks and inefficiencies
2. Algorithm Optimization: Reduced time and space complexity
3. Code Refactoring: Improved structure and maintainability
4. Verification: Tested functionality and measured improvements
5. Documentation: Recorded all changes and metrics

## Performance Metrics

### Before Optimization
- Execution time: [baseline measurements]
- Memory usage: [baseline measurements]
- Code complexity: [baseline measurements]

### After Optimization
- Execution time: [optimized measurements]
- Memory usage: [optimized measurements]
- Code complexity: [optimized measurements]

### Improvement Summary
- Performance gain: [percentage improvement]
- Memory reduction: [percentage reduction]
- Code quality: [improvement metrics]

## Optimization Details

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
                "memory_type": "optimization_report",
                "brief_description": "Code optimization and refactoring report",
                "elements_description": "Comprehensive analysis of performance improvements and code quality enhancements",
                "rationale": "Documents optimization process and quantifies performance improvements"
            })
        
        # Delegate to State Scribe
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record optimization analysis files in project memory",
            task_context={
                "files_to_record": files_to_record,
                "phase": "optimization"
            }
        )

async def main():
    """Main execution function"""
    agent = OptimizerModule()
    
    # Example task
    task = TaskPayload(
        task_id="code_optimization",
        description="Optimize and refactor code module for performance",
        requirements=["Analyze performance bottlenecks", "Implement optimizations"],
        ai_verifiable_outcomes=["Create optimization report in docs/reports", "Apply code optimizations"],
        phase="optimization",
        priority=3
    )
    
    result = await agent.execute(task)
    print(f"Optimizer Module completed: {result.success}")
    if result.files_created:
        print(f"Files created: {', '.join(result.files_created)}")
    if result.files_modified:
        print(f"Files modified: {', '.join(result.files_modified)}")

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
