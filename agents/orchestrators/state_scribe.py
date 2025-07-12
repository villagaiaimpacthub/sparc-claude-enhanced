#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase",
#   "rich",
#   "pydantic",
#   "python-dotenv",
# ]
# ///

"""State Scribe - The ONLY agent that writes to project_memorys table"""

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


class StateScribeAgent(BaseAgent):
    """The sole, authoritative agent responsible for maintaining project state"""
    
    def __init__(self):
        super().__init__(
            agent_name="orchestrator-state-scribe",
            role_definition="You are the sole, authoritative agent responsible for maintaining the project's state in a central Supabase database. You are the ONLY agent allowed to write to the project_memorys table.",
            custom_instructions="""
You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

You are the ONLY agent that can:
- INSERT into project_memorys table
- UPDATE existing records in project_memorys table
- DELETE orphaned records from project_memorys table
- Maintain file versioning and metadata

Your core responsibilities:
1. Record all file artifacts in the project_memorys table with comprehensive metadata
2. Maintain accurate version control for all files (increment version on updates)
3. Ensure data integrity and consistency across all records
4. Never duplicate records - always check for existing entries first
5. Provide clear, descriptive metadata for all files including brief_description, elements_description, and rationale
6. Clean up orphaned records for files that no longer exist
7. Generate project state summaries and reports
8. Maintain token counts for all files
9. Coordinate with Qdrant for semantic indexing of file contents

You are triggered by:
- File creation events from other agents
- File modification events
- Manual requests for project state updates
- Cleanup operations for orphaned records

Never create, modify, or delete actual files - only maintain their records in the database.
"""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Record file artifacts in the project_memorys table"""
        
        files_to_record = task.context.get("files_to_record", [])
        if not files_to_record:
            return AgentResult(
                success=True,
                outputs={"message": "No files to record"},
                files_created=[],
                files_modified=[]
            )
        
        inserted = 0
        updated = 0
        errors = []
        
        for file_info in files_to_record:
            try:
                file_path = file_info["file_path"]
                
                # Validate file exists
                if not Path(file_path).exists():
                    errors.append(f"File does not exist: {file_path}")
                    continue
                
                # Check if record exists
                existing = await self.memory.supabase.table("project_memorys").select("*").eq(
                    "project_id", self.project_id
                ).eq(
                    "file_path", file_path
                ).execute()
                
                if existing.data:
                    # Update existing record
                    await self.memory.supabase.table("project_memorys").update({
                        "memory_type": file_info.get("memory_type", "unknown"),
                        "brief_description": file_info.get("brief_description", ""),
                        "elements_description": file_info.get("elements_description", ""),
                        "rationale": file_info.get("rationale", ""),
                        "version": existing.data[0]["version"] + 1,
                        "last_updated_timestamp": "now()",
                        "token_count": self._estimate_file_tokens(file_path)
                    }).eq(
                        "project_id", self.project_id
                    ).eq(
                        "file_path", file_path
                    ).execute()
                    updated += 1
                else:
                    # Insert new record
                    await self.memory.supabase.table("project_memorys").insert({
                        "project_id": self.project_id,
                        "file_path": file_path,
                        "memory_type": file_info.get("memory_type", "unknown"),
                        "brief_description": file_info.get("brief_description", ""),
                        "elements_description": file_info.get("elements_description", ""),
                        "rationale": file_info.get("rationale", ""),
                        "version": 1,
                        "token_count": self._estimate_file_tokens(file_path)
                    }).execute()
                    inserted += 1
                
                # Also index the file for semantic search
                await self.memory.index_file(file_path)
                
            except Exception as e:
                errors.append(f"Error processing {file_info.get('file_path', 'unknown')}: {str(e)}")
        
        # Generate summary
        summary = f"Processed {len(files_to_record)} files: {inserted} inserted, {updated} updated"
        if errors:
            summary += f", {len(errors)} errors"
        
        return AgentResult(
            success=len(errors) == 0,
            outputs={
                "summary": summary,
                "records_inserted": inserted,
                "records_updated": updated,
                "total_processed": len(files_to_record),
                "errors": errors
            },
            files_created=[],
            files_modified=[],
            next_steps=["Files successfully recorded in project memory"] if len(errors) == 0 else None,
            errors=errors if errors else None
        )
    
    def _estimate_file_tokens(self, file_path: str) -> int:
        """Estimate token count for a file"""
        try:
            content = Path(file_path).read_text(encoding='utf-8')
            return len(content) // 4  # Rough estimate
        except Exception:
            return 0
    
    async def _cleanup_orphaned_records(self) -> int:
        """Clean up records for files that no longer exist"""
        try:
            # Get all records for this project
            result = await self.memory.supabase.table("project_memorys").select("*").eq(
                "project_id", self.project_id
            ).execute()
            
            orphaned = 0
            for record in result.data:
                file_path = record["file_path"]
                if not Path(file_path).exists():
                    # Delete orphaned record
                    await self.memory.supabase.table("project_memorys").delete().eq(
                        "id", record["id"]
                    ).execute()
                    orphaned += 1
            
            return orphaned
        except Exception as e:
            print(f"Error cleaning up orphaned records: {str(e)}")
            return 0
    
    async def get_project_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the project state"""
        try:
            result = await self.memory.supabase.table("project_memorys").select("*").eq(
                "project_id", self.project_id
            ).execute()
            
            if not result.data:
                return {"total_files": 0, "by_type": {}, "last_updated": None}
            
            # Analyze by memory type
            by_type = {}
            for record in result.data:
                memory_type = record["memory_type"]
                if memory_type not in by_type:
                    by_type[memory_type] = 0
                by_type[memory_type] += 1
            
            # Get last updated
            last_updated = max(record["last_updated_timestamp"] for record in result.data)
            
            return {
                "total_files": len(result.data),
                "by_type": by_type,
                "last_updated": last_updated,
                "project_id": self.project_id
            }
        except Exception as e:
            print(f"Error getting project summary: {str(e)}")
            return {"total_files": 0, "by_type": {}, "last_updated": None}

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
