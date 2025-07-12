#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase>=2.0.0",
#   "python-dotenv>=1.0.0",
#   "rich>=13.0.0",
# ]
# ///

"""
SPARC PostToolUse Hook - Captures file changes and triggers agent workflows
Runs after every Write/Edit/MultiEdit operation in Claude Code
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

try:
    from supabase import create_client, Client
    from dotenv import load_dotenv
    from rich.console import Console
except ImportError as e:
    print(f"Missing dependency: {e}")
    sys.exit(1)

console = Console()

def load_project_namespace() -> str:
    """Load namespace from project .sparc directory"""
    sparc_dir = Path.cwd() / '.sparc'
    namespace_file = sparc_dir / 'namespace'
    
    if namespace_file.exists():
        return namespace_file.read_text().strip()
    return 'default'

def get_supabase_client() -> Client:
    """Initialize Supabase client"""
    load_dotenv()
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        console.print("[red]Missing Supabase credentials in .env file[/red]")
        sys.exit(1)
    
    return create_client(url, key)

def update_sparc_memory(hook_data: Dict[str, Any], namespace: str):
    """Update SPARC agent memory with file changes"""
    try:
        supabase = get_supabase_client()
        
        tool_name = hook_data.get('tool_name')
        tool_input = hook_data.get('tool_input', {})
        
        if tool_name in ['Write', 'Edit', 'MultiEdit']:
            file_path = tool_input.get('file_path')
            
            if file_path:
                # Update project memory
                memory_data = {
                    'namespace': namespace,
                    'file_path': file_path,
                    'tool_used': tool_name,
                    'timestamp': datetime.now().isoformat(),
                    'session_id': hook_data.get('session_id'),
                    'content_preview': tool_input.get('content', '')[:500] if tool_input.get('content') else None
                }
                
                supabase.table('sparc_file_changes').insert(memory_data).execute()
                
                # Trigger next agent workflow
                trigger_next_workflow(supabase, namespace, file_path, tool_name)
                
                console.print(f"[green]📝 SPARC: Updated memory for {file_path}[/green]")
    
    except Exception as e:
        console.print(f"[red]❌ SPARC memory update failed: {e}[/red]")

def trigger_next_workflow(supabase: Client, namespace: str, file_path: str, tool_name: str):
    """Trigger next agent in SPARC workflow based on file changes"""
    try:
        # Determine next agent based on file type and current project phase
        next_agent = determine_next_agent(file_path, tool_name)
        
        if next_agent:
            task_data = {
                'namespace': namespace,
                'from_agent': 'claude_code_hook',
                'to_agent': next_agent,
                'task_type': 'file_change_trigger',
                'task_payload': {
                    'task_id': f"hook_{datetime.now().isoformat()}",
                    'description': f"Process file change in {file_path}",
                    'context': {
                        'changed_file': file_path,
                        'tool_used': tool_name,
                        'trigger_type': 'file_change'
                    },
                    'phase': 'dynamic',
                    'priority': 7
                },
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            
            supabase.table('agent_tasks').insert(task_data).execute()
            console.print(f"[blue]🤖 SPARC: Triggered {next_agent} for {file_path}[/blue]")
    
    except Exception as e:
        console.print(f"[red]❌ Workflow trigger failed: {e}[/red]")

def determine_next_agent(file_path: str, tool_name: str) -> str:
    """Determine which agent should process this file change"""
    file_path = file_path.lower()
    
    # Code files -> State Scribe for memory recording
    if any(ext in file_path for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.rs']):
        return 'orchestrator-state-scribe'
    
    # Test files -> TDD Master
    elif 'test' in file_path or '.test.' in file_path:
        return 'tester-tdd-master'
    
    # Documentation -> Docs Writer
    elif any(ext in file_path for ext in ['.md', '.txt', '.rst']):
        return 'docs-writer-feature'
    
    # Config files -> Security Reviewer
    elif any(name in file_path for name in ['config', '.env', 'settings']):
        return 'security-reviewer-module'
    
    # Default to State Scribe for recording
    else:
        return 'orchestrator-state-scribe'

def main():
    """Main hook execution"""
    try:
        # Read hook data from stdin
        hook_data = json.loads(sys.stdin.read())
        
        # Load project namespace
        namespace = load_project_namespace()
        
        # Update SPARC memory and trigger workflows
        update_sparc_memory(hook_data, namespace)
        
    except json.JSONDecodeError:
        console.print("[red]❌ Invalid JSON input to SPARC hook[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ SPARC hook error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()