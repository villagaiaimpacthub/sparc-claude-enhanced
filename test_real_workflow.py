#!/usr/bin/env python3
"""
Test real SPARC workflow with properly structured database operations
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from supabase import create_client

load_dotenv()
console = Console()

def test_complete_workflow():
    """Test a complete SPARC workflow with proper database usage"""
    console.print("🚀 [bold blue]Testing Complete SPARC Workflow[/bold blue]")
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    supabase = create_client(url, key)
    
    test_namespace = f"workflow_test_{int(datetime.now().timestamp())}"
    console.print(f"🎯 Test namespace: {test_namespace}")
    
    # Step 1: Record project memory (with required fields)
    try:
        console.print("\n📝 Step 1: Recording project memory...")
        
        memory_record = {
            'namespace': test_namespace,
            'file_path': 'docs/Mutual_Understanding_Document.md',  # Required field
            'memory_type': 'specification',
            'brief_description': 'Comprehensive mutual understanding document',
            'elements_description': 'Project goals and requirements',
            'rationale': 'Created during goal clarification phase',
            'version': 1
        }
        
        memory_result = supabase.table('project_memorys').insert(memory_record).execute()
        
        if memory_result.data:
            console.print("✅ Project memory recorded successfully")
            memory_id = memory_result.data[0].get('id')
            console.print(f"  Memory ID: {memory_id}")
            
            # Show what columns are available
            columns = list(memory_result.data[0].keys())
            console.print(f"  Available columns: {', '.join(columns)}")
        else:
            console.print("❌ Failed to record project memory")
            return False
            
    except Exception as e:
        console.print(f"❌ Memory recording failed: {e}")
        return False
    
    # Step 2: Record file changes
    try:
        console.print("\n📂 Step 2: Recording file changes...")
        
        file_change = {
            'namespace': test_namespace,
            'file_path': 'docs/Mutual_Understanding_Document.md',
            'tool_used': 'goal_clarification_orchestrator',  # Required field
            'change_type': 'create',
            'content_preview': 'Created mutual understanding document with project goals...',
            'agent_name': 'orchestrator-goal-clarification'
        }
        
        file_result = supabase.table('sparc_file_changes').insert(file_change).execute()
        
        if file_result.data:
            console.print("✅ File change recorded successfully")
            file_id = file_result.data[0].get('id')
            console.print(f"  File change ID: {file_id}")
            
            # Show available columns
            columns = list(file_result.data[0].keys())
            console.print(f"  Available columns: {', '.join(columns)}")
        else:
            console.print("❌ Failed to record file change")
            
    except Exception as e:
        console.print(f"❌ File change recording failed: {e}")
    
    # Step 3: Test querying the data
    try:
        console.print("\n🔍 Step 3: Querying recorded data...")
        
        # Query memories
        memory_query = supabase.table('project_memorys').select("*").eq('namespace', test_namespace).execute()
        console.print(f"✅ Found {len(memory_query.data)} memory records")
        
        # Query file changes
        file_query = supabase.table('sparc_file_changes').select("*").eq('namespace', test_namespace).execute()
        console.print(f"✅ Found {len(file_query.data)} file change records")
        
        # Query agent tasks for this namespace
        task_query = supabase.table('agent_tasks').select("*").eq('namespace', test_namespace).execute()
        console.print(f"✅ Found {len(task_query.data)} agent task records")
        
    except Exception as e:
        console.print(f"❌ Data querying failed: {e}")
    
    # Step 4: Test the goal clarification orchestrator with database integration
    try:
        console.print("\n🎯 Step 4: Testing orchestrator with database...")
        
        import subprocess
        import sys
        from pathlib import Path
        
        cmd = [
            sys.executable, '-m', 'uv', 'run', 
            'agents/orchestrators/goal_clarification.py',
            '--namespace', test_namespace,
            '--goal', 'Build a real-time chat application with user authentication'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=Path.cwd())
        
        if result.returncode == 0:
            console.print("✅ Orchestrator executed successfully")
            
            # Check if new records were created
            final_memory_query = supabase.table('project_memorys').select("*").eq('namespace', test_namespace).execute()
            final_task_query = supabase.table('agent_tasks').select("*").eq('namespace', test_namespace).execute()
            
            console.print(f"📊 Final count - Memories: {len(final_memory_query.data)}, Tasks: {len(final_task_query.data)}")
            
        else:
            console.print(f"❌ Orchestrator failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        console.print("⏰ Orchestrator timed out")
    except Exception as e:
        console.print(f"❌ Orchestrator test failed: {e}")
    
    console.print("\n✅ [bold green]Workflow test completed![/bold green]")
    console.print(f"🗂️ All test data is under namespace: {test_namespace}")
    
    return True

def show_database_summary():
    """Show summary of all data in the database"""
    console.print("\n📊 [bold blue]Database Summary[/bold blue]")
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    supabase = create_client(url, key)
    
    tables = [
        'agent_tasks',
        'project_memorys', 
        'sparc_contexts',
        'sparc_file_changes',
        'agent_executions',
        'sparc_projects'
    ]
    
    for table in tables:
        try:
            result = supabase.table(table).select("*", count="exact").execute()
            count = result.count if hasattr(result, 'count') else len(result.data)
            console.print(f"  📋 {table}: {count} records")
            
            # Show recent activity
            if count > 0 and len(result.data) > 0:
                recent = result.data[:2]  # Show first 2
                for record in recent:
                    key_info = []
                    for key in ['namespace', 'from_agent', 'to_agent', 'phase', 'file_path', 'created_at']:
                        if key in record:
                            value = str(record[key])[:30]  # Truncate
                            key_info.append(f"{key}={value}")
                    console.print(f"    • {', '.join(key_info[:2])}")
            
        except Exception as e:
            console.print(f"  ❌ {table}: Error - {str(e)[:50]}")

if __name__ == "__main__":
    success = test_complete_workflow()
    if success:
        show_database_summary()