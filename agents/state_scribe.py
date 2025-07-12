#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase>=2.0.0",
#   "click>=8.1.0",
#   "rich>=13.0.0",
#   "python-dotenv>=1.0.0",
# ]
# ///

"""
SPARC State Scribe Agent
The sole, authoritative agent responsible for maintaining project state and memory
Records all file changes, maintains context, and coordinates project knowledge
"""

import os
import asyncio
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    import click
    from rich.console import Console
    from rich.table import Table
    from supabase import create_client, Client
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing dependency: {e}")
    exit(1)

console = Console()

class StateScribeAgent:
    """Authoritative agent for maintaining project state and memory"""
    
    def __init__(self, namespace: str):
        self.namespace = namespace
        self.agent_name = "orchestrator-state-scribe"
        self.supabase = self._init_supabase()
        
    def _init_supabase(self) -> Client:
        """Initialize Supabase client"""
        load_dotenv()
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            console.print("[red]❌ Missing Supabase credentials[/red]")
            exit(1)
            
        return create_client(url, key)
    
    async def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get pending tasks for state scribe"""
        try:
            result = self.supabase.table('agent_tasks').select('*').eq(
                'namespace', self.namespace
            ).eq(
                'to_agent', self.agent_name
            ).eq(
                'status', 'pending'
            ).order('priority', desc=True).order('created_at').execute()
            
            return result.data if result.data else []
        except Exception as e:
            console.print(f"[red]❌ Error fetching tasks: {e}[/red]")
            return []
    
    async def record_file_in_memory(self, file_path: str, context: Dict[str, Any]):
        """Record file in project memory (exclusive State Scribe authority)"""
        try:
            # Read file content
            file_content = ""
            file_size = 0
            
            if Path(file_path).exists():
                file_size = Path(file_path).stat().st_size
                if file_size < 100000:  # Only read files smaller than 100KB
                    try:
                        file_content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
                    except:
                        file_content = "[Binary or unreadable file]"
            
            # Generate file hash for deduplication
            content_hash = hashlib.md5(file_content.encode()).hexdigest()
            
            # Check if file already exists in memory
            existing = self.supabase.table('project_memorys').select('id, version').eq(
                'namespace', self.namespace
            ).eq('file_path', file_path).execute()
            
            if existing.data:
                # Update existing file
                current_version = existing.data[0]['version']
                new_version = current_version + 1
                
                self.supabase.table('project_memorys').update({
                    'content': file_content,
                    'file_size': file_size,
                    'content_hash': content_hash,
                    'version': new_version,
                    'last_modified': datetime.now().isoformat(),
                    'modification_context': context
                }).eq('id', existing.data[0]['id']).execute()
                
                console.print(f"[blue]📝 Updated file memory: {file_path} (v{new_version})[/blue]")
            else:
                # Create new file record
                file_record = {
                    'namespace': self.namespace,
                    'file_path': file_path,
                    'content': file_content,
                    'file_size': file_size,
                    'content_hash': content_hash,
                    'version': 1,
                    'created_at': datetime.now().isoformat(),
                    'last_modified': datetime.now().isoformat(),
                    'creation_context': context,
                    'file_type': self._determine_file_type(file_path),
                    'description': self._generate_file_description(file_path, file_content)
                }
                
                self.supabase.table('project_memorys').insert(file_record).execute()
                console.print(f"[green]📁 Recorded new file: {file_path}[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Error recording file: {e}[/red]")
    
    def _determine_file_type(self, file_path: str) -> str:
        """Determine file type from extension"""
        suffix = Path(file_path).suffix.lower()
        
        type_mapping = {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.md': 'markdown',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.txt': 'text',
            '.env': 'environment',
            '.cfg': 'config',
            '.ini': 'config'
        }
        
        return type_mapping.get(suffix, 'unknown')
    
    def _generate_file_description(self, file_path: str, content: str) -> str:
        """Generate intelligent file description"""
        file_name = Path(file_path).name
        file_type = self._determine_file_type(file_path)
        
        # Basic description based on file type and name
        descriptions = {
            'python': f"Python module: {file_name}",
            'javascript': f"JavaScript file: {file_name}",
            'typescript': f"TypeScript file: {file_name}",
            'html': f"HTML document: {file_name}",
            'css': f"CSS stylesheet: {file_name}",
            'markdown': f"Markdown document: {file_name}",
            'json': f"JSON configuration: {file_name}",
            'yaml': f"YAML configuration: {file_name}",
            'environment': f"Environment configuration: {file_name}",
            'config': f"Configuration file: {file_name}"
        }
        
        base_desc = descriptions.get(file_type, f"File: {file_name}")
        
        # Add content-based insights
        if content and len(content) > 0:
            lines = content.split('\n')
            line_count = len(lines)
            base_desc += f" ({line_count} lines)"
            
            # Look for key patterns
            if 'class ' in content:
                base_desc += " - Contains class definitions"
            if 'def ' in content or 'function ' in content:
                base_desc += " - Contains functions"
            if 'import ' in content or 'from ' in content:
                base_desc += " - Has imports"
            if 'test' in file_name.lower():
                base_desc += " - Test file"
        
        return base_desc
    
    async def update_project_statistics(self):
        """Update overall project statistics"""
        try:
            # Count files by type
            result = self.supabase.table('project_memorys').select(
                'file_type, file_size'
            ).eq('namespace', self.namespace).execute()
            
            if result.data:
                file_counts = {}
                total_size = 0
                
                for file_record in result.data:
                    file_type = file_record['file_type']
                    file_counts[file_type] = file_counts.get(file_type, 0) + 1
                    total_size += file_record.get('file_size', 0)
                
                # Update project state
                project_stats = {
                    'namespace': self.namespace,
                    'total_files': len(result.data),
                    'total_size': total_size,
                    'file_type_counts': file_counts,
                    'last_updated': datetime.now().isoformat()
                }
                
                # Upsert project statistics
                self.supabase.table('project_states').upsert(project_stats).execute()
                
                console.print(f"[green]📊 Updated project stats: {len(result.data)} files, {total_size} bytes[/green]")
                
        except Exception as e:
            console.print(f"[red]❌ Error updating statistics: {e}[/red]")
    
    async def execute_task(self, task: Dict[str, Any]):
        """Execute state scribe task"""
        task_payload = task['task_payload']
        description = task_payload['description']
        context = task_payload.get('context', {})
        
        console.print(f"[bold blue]📚 State Scribe: {description}[/bold blue]")
        
        # Mark task in progress
        self.supabase.table('agent_tasks').update({
            'status': 'in_progress',
            'started_at': datetime.now().isoformat()
        }).eq('id', task['id']).execute()
        
        try:
            # Handle different task types
            if 'file_change_trigger' in task['task_type']:
                # Handle file change recording
                changed_file = context.get('changed_file')
                if changed_file:
                    await self.record_file_in_memory(changed_file, context)
            
            elif 'record_files' in description.lower():
                # Record multiple files
                files = context.get('files', [])
                for file_path in files:
                    if Path(file_path).exists():
                        await self.record_file_in_memory(file_path, context)
            
            # Always update project statistics
            await self.update_project_statistics()
            
            # Complete task
            result = {
                'success': True,
                'files_recorded': context.get('files', [context.get('changed_file')] if context.get('changed_file') else []),
                'statistics_updated': True
            }
            
            self.supabase.table('agent_tasks').update({
                'status': 'completed',
                'completed_at': datetime.now().isoformat(),
                'result': result
            }).eq('id', task['id']).execute()
            
            console.print(f"[green]✅ State Scribe task completed[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Task execution failed: {e}[/red]")
            self.supabase.table('agent_tasks').update({
                'status': 'failed',
                'error': str(e),
                'completed_at': datetime.now().isoformat()
            }).eq('id', task['id']).execute()
    
    async def run_polling_loop(self):
        """Main agent polling loop"""
        console.print(f"[bold green]📚 State Scribe started for namespace: {self.namespace}[/bold green]")
        
        iteration = 0
        max_iterations = 1000  # State Scribe runs for longer
        
        while iteration < max_iterations:
            iteration += 1
            
            try:
                tasks = await self.get_pending_tasks()
                
                if not tasks:
                    await asyncio.sleep(3)  # Shorter wait for state scribe
                    continue
                
                for task in tasks:
                    await self.execute_task(task)
                    await asyncio.sleep(0.5)  # Brief pause between tasks
                
            except KeyboardInterrupt:
                console.print("\n[yellow]⏹️ State Scribe stopped by user[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]❌ Polling error: {e}[/red]")
                await asyncio.sleep(5)
        
        console.print("[yellow]State Scribe polling ended[/yellow]")

@click.command()
@click.option('--namespace', required=True, help='Project namespace')
@click.option('--single-run', is_flag=True, help='Process one batch of tasks and exit')
def main(namespace: str, single_run: bool):
    """SPARC State Scribe - Authoritative project memory manager"""
    
    agent = StateScribeAgent(namespace)
    
    async def run():
        if single_run:
            tasks = await agent.get_pending_tasks()
            if tasks:
                for task in tasks:
                    await agent.execute_task(task)
            else:
                console.print("[yellow]No pending tasks found[/yellow]")
        else:
            await agent.run_polling_loop()
    
    asyncio.run(run())

if __name__ == "__main__":
    main()