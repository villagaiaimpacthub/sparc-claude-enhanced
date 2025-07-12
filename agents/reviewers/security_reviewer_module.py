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

"""Security Reviewer Module - SPARC aligned security auditing specialist"""

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


class SecurityReviewerModule(BaseAgent):
    """Audits code modules for security vulnerabilities and produces reports"""
    
    def __init__(self):
        super().__init__(
            agent_name="security-reviewer-module",
            role_definition="Your core responsibility is to audit a specific code module for security vulnerabilities and produce a report on your findings. You do not modify the project state.",
            custom_instructions="""You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

Before you answer, you must think through this problem step by step. You will receive the path to the module to review and all necessary context. Your workflow involves performing Static Application Security Testing (SAST). After your analysis, you will generate a security report in Markdown format and save it to 'docs/reports'. This is your AI-verifiable outcome. To conclude, use "attempt_completion". Your summary must be a comprehensive report detailing your findings and confirming that you have created the report file, providing its path."""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute security review of code module"""
        
        # Build prompt using base class
        prompt = self._build_agent_prompt(task, context)
        
        # Add specific instructions for security review
        specific_prompt = f"""{prompt}

SECURITY REVIEW MISSION:
You are now performing a comprehensive security audit of the specified code module. Your task is to:

1. STATIC APPLICATION SECURITY TESTING (SAST):
   - Analyze code for common security vulnerabilities
   - Identify potential attack vectors and exploitation points
   - Review input validation and sanitization
   - Examine authentication and authorization mechanisms
   - Check for cryptographic implementation issues

2. SECURITY VULNERABILITY CATEGORIES:
   - Injection vulnerabilities (SQL, XSS, Command injection)
   - Authentication and session management flaws
   - Cross-site scripting (XSS) and CSRF vulnerabilities
   - Insecure direct object references
   - Security misconfigurations
   - Sensitive data exposure
   - Insufficient logging and monitoring
   - Using components with known vulnerabilities
   - Unvalidated redirects and forwards

3. ANALYSIS AREAS:
   - Input validation and sanitization
   - Output encoding and escaping
   - Authentication mechanisms
   - Authorization controls
   - Session management
   - Cryptographic implementations
   - Error handling and information disclosure
   - Configuration security
   - Dependency vulnerabilities

4. SECURITY REPORT REQUIREMENTS:
   - Create comprehensive security audit report
   - Save it in 'docs/reports' directory
   - Include vulnerability severity ratings
   - Provide remediation recommendations
   - Include code examples where applicable
   - Follow security reporting best practices

Remember: Focus on identifying actual security vulnerabilities and providing actionable remediation guidance.
"""
        
        # Use Claude via base class
        claude_response = await self._run_claude(specific_prompt)
        
        # Create security report
        files_created = await self._create_security_outputs(claude_response)
        
        # Record with State Scribe
        if files_created:
            await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "security_analysis": claude_response,
                "files_created": files_created
            },
            files_created=files_created,
            files_modified=[],
            next_steps=["Review security findings and implement remediation measures"]
        )
    
    async def _create_security_outputs(self, claude_response: str) -> List[str]:
        """Create security audit report files"""
        files_created = []
        
        try:
            # Create docs/reports directory if it doesn't exist
            Path("docs/reports").mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = f"docs/reports/security_audit_report_{timestamp}.md"
            
            # Extract security content from response
            security_content = self._extract_security_content(claude_response)
            
            # Write security report
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(security_content)
            
            files_created.append(report_path)
            
        except Exception as e:
            print(f"Error creating security outputs: {str(e)}")
        
        return files_created
    
    def _extract_security_content(self, claude_response: str) -> str:
        """Extract security content from Claude response"""
        header = f"""# Security Audit Report
Generated: {datetime.now().isoformat()}
Agent: {self.agent_name}

## Executive Summary
This report contains a comprehensive security audit of the specified code module, identifying vulnerabilities and providing remediation recommendations.

## Security Analysis Methodology
1. Static Application Security Testing (SAST)
2. Common vulnerability pattern analysis
3. Input validation and sanitization review
4. Authentication and authorization assessment
5. Cryptographic implementation evaluation

## Vulnerability Assessment

### Legend
- **CRITICAL**: Immediate attention required, high risk of exploitation
- **HIGH**: Significant security risk, should be addressed promptly
- **MEDIUM**: Moderate risk, should be addressed in next development cycle
- **LOW**: Minor security concern, can be addressed when convenient
- **INFO**: Informational finding, no immediate action required

## Security Findings

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
                "memory_type": "security_report",
                "brief_description": "Security audit report for code module",
                "elements_description": "Comprehensive security vulnerability analysis with remediation recommendations",
                "rationale": "Identifies security vulnerabilities and provides guidance for secure coding practices"
            })
        
        # Delegate to State Scribe
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record security audit files in project memory",
            task_context={
                "files_to_record": files_to_record,
                "phase": "security_review"
            }
        )

async def main():
    """Main execution function"""
    agent = SecurityReviewerModule()
    
    # Example task
    task = TaskPayload(
        task_id="security_audit",
        description="Perform security audit of code module",
        requirements=["Analyze code for security vulnerabilities"],
        ai_verifiable_outcomes=["Create detailed security audit report in docs/reports"],
        phase="security_review",
        priority=2
    )
    
    result = await agent.execute(task)
    print(f"Security Reviewer Module completed: {result.success}")
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
