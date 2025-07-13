#!/usr/bin/env python3
"""
Debug why the 36-agent workflow stopped after goal clarification
"""

import os
from dotenv import load_dotenv
from rich.console import Console
from supabase import create_client

load_dotenv()
console = Console()

def debug_workflow():
    """Debug the workflow state"""
    console.print("🔍 [bold blue]Debugging SPARC Workflow State[/bold blue]")
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    supabase = create_client(url, key)
    
    namespace = "test_sparc_1752415022"
    
    # Check agent tasks
    console.print("\n📋 [bold]Agent Tasks in Queue:[/bold]")
    tasks_result = supabase.table('agent_tasks').select("*").eq('namespace', namespace).execute()
    
    if tasks_result.data:
        for task in tasks_result.data:
            console.print(f"  • {task.get('from_agent')} → {task.get('to_agent')}")
            console.print(f"    Task: {task.get('task_type')}")
            console.print(f"    Status: {task.get('status')}")
            console.print(f"    Priority: {task.get('priority')}")
            console.print(f"    Created: {task.get('created_at')}")
            console.print()
    else:
        console.print("  No agent tasks found")
    
    # Check approval requests
    console.print("\n📝 [bold]Approval Requests:[/bold]")
    approval_result = supabase.table('approval_requests').select("*").eq('project_id', namespace).execute()
    
    if approval_result.data:
        for approval in approval_result.data:
            console.print(f"  • Phase: {approval.get('phase')}")
            console.print(f"    Status: {approval.get('status')}")
            console.print(f"    Message: {approval.get('message')}")
            console.print(f"    Requested by: {approval.get('requested_by')}")
            console.print()
    else:
        console.print("  No approval requests found")
    
    # Check project state
    console.print("\n🏗️ [bold]Project State:[/bold]")
    projects_result = supabase.table('sparc_projects').select("*").eq('namespace', namespace).execute()
    
    if projects_result.data:
        for project in projects_result.data:
            console.print(f"  • Status: {project.get('status')}")
            console.print(f"    Phase: {project.get('current_phase')}")
            console.print(f"    Goal: {project.get('project_goal')}")
            console.print()
    else:
        console.print("  No project records found")
    
    # Check agent executions
    console.print("\n🤖 [bold]Agent Executions:[/bold]")
    exec_result = supabase.table('agent_executions').select("*").eq('namespace', namespace).execute()
    
    if exec_result.data:
        for execution in exec_result.data:
            console.print(f"  • Agent: {execution.get('agent_name')}")
            console.print(f"    Type: {execution.get('execution_type')}")
            console.print(f"    Status: {execution.get('status')}")
            console.print(f"    Phase: {execution.get('phase')}")
            console.print()
    else:
        console.print("  No agent executions found")

def simulate_next_phase():
    """Manually trigger the next phase to continue workflow"""
    console.print("\n🚀 [bold blue]Manually Triggering Specification Phase[/bold blue]")
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    supabase = create_client(url, key)
    
    namespace = "test_sparc_1752415022"
    
    # Create a new agent task for specification phase
    new_task = {
        'namespace': namespace,
        'from_agent': 'orchestrator-goal-clarification',
        'to_agent': 'orchestrator-specification-phase',
        'task_type': 'phase_transition',
        'task_data': {'next_phase': 'specification'},
        'task_payload': {'next_phase': 'specification', 'trigger': 'manual'},
        'priority': 1,
        'status': 'pending'
    }
    
    result = supabase.table('agent_tasks').insert(new_task).execute()
    
    if result.data:
        console.print("✅ Created specification phase task")
        task_id = result.data[0].get('id')
        console.print(f"  Task ID: {task_id}")
    else:
        console.print("❌ Failed to create task")

if __name__ == "__main__":
    debug_workflow()
    simulate_next_phase()