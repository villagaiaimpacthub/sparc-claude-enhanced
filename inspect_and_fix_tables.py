#!/usr/bin/env python3
"""
Inspect current table structure and fix using available columns
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from supabase import create_client

load_dotenv()
console = Console()

def inspect_table_structure():
    """Inspect what columns actually exist in tables"""
    console.print("🔍 [bold blue]Inspecting Table Structures[/bold blue]")
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    supabase = create_client(url, key)
    
    tables = ['project_memorys', 'sparc_file_changes', 'sparc_projects']
    
    for table in tables:
        try:
            console.print(f"\n📋 [bold]{table}[/bold]")
            
            # Try to get any existing records to see structure
            result = supabase.table(table).select("*").limit(1).execute()
            
            if result.data and len(result.data) > 0:
                columns = list(result.data[0].keys())
                console.print(f"  Existing columns: {', '.join(columns)}")
                console.print(f"  Sample data: {result.data[0]}")
            else:
                console.print(f"  No data in {table}, trying minimal insert...")
                
                # Try minimal insert to discover structure
                if table == 'project_memorys':
                    minimal_record = {'namespace': 'test'}
                elif table == 'sparc_file_changes':
                    minimal_record = {'namespace': 'test', 'file_path': 'test.md'}
                elif table == 'sparc_projects':
                    minimal_record = {'namespace': 'test', 'project_goal': 'test goal'}
                
                try:
                    test_result = supabase.table(table).insert(minimal_record).execute()
                    if test_result.data:
                        columns = list(test_result.data[0].keys())
                        console.print(f"  Discovered columns: {', '.join(columns)}")
                        
                        # Clean up test record
                        record_id = test_result.data[0].get('id')
                        if record_id:
                            supabase.table(table).delete().eq('id', record_id).execute()
                            console.print("  🗑️ Test record cleaned up")
                    else:
                        console.print(f"  ❌ Could not insert test record")
                        
                except Exception as e:
                    console.print(f"  ❌ Insert failed: {e}")
                    
        except Exception as e:
            console.print(f"  ❌ Error inspecting {table}: {e}")

def test_working_with_existing_structure():
    """Test operations with the existing table structure"""
    console.print("\n🧪 [bold blue]Testing with Existing Structure[/bold blue]")
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    supabase = create_client(url, key)
    
    # Test project_memorys with minimal data
    try:
        console.print("📝 Testing project_memorys with basic structure...")
        
        # Try the simplest possible record
        basic_memory = {
            'namespace': 'structure_test'
        }
        
        result = supabase.table('project_memorys').insert(basic_memory).execute()
        
        if result.data:
            console.print("✅ Basic project_memorys record works")
            record_id = result.data[0].get('id')
            
            # Show what columns were actually created
            columns = list(result.data[0].keys())
            console.print(f"  Available columns: {', '.join(columns)}")
            
            # Test query
            query_result = supabase.table('project_memorys').select("*").eq('namespace', 'structure_test').execute()
            if query_result.data:
                console.print("✅ Query works")
                
            # Cleanup
            if record_id:
                supabase.table('project_memorys').delete().eq('id', record_id).execute()
                console.print("🗑️ Cleaned up")
        else:
            console.print("❌ Basic insert failed")
            
    except Exception as e:
        console.print(f"❌ project_memorys test failed: {e}")
    
    # Test sparc_file_changes
    try:
        console.print("\n📝 Testing sparc_file_changes...")
        
        basic_file_change = {
            'namespace': 'structure_test',
            'file_path': 'test/file.md'
        }
        
        result = supabase.table('sparc_file_changes').insert(basic_file_change).execute()
        
        if result.data:
            console.print("✅ Basic file_changes record works")
            record_id = result.data[0].get('id')
            columns = list(result.data[0].keys())
            console.print(f"  Available columns: {', '.join(columns)}")
            
            # Cleanup
            if record_id:
                supabase.table('sparc_file_changes').delete().eq('id', record_id).execute()
                console.print("🗑️ Cleaned up")
        else:
            console.print("❌ Basic file_changes insert failed")
            
    except Exception as e:
        console.print(f"❌ sparc_file_changes test failed: {e}")

def create_memory_with_available_columns():
    """Create a real memory record using only available columns"""
    console.print("\n💾 [bold blue]Creating Real Memory Record[/bold blue]")
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    supabase = create_client(url, key)
    
    try:
        # Create a memory record for our test documents
        memory_record = {
            'namespace': 'test_sparc_1752415022'  # From our earlier test
        }
        
        result = supabase.table('project_memorys').insert(memory_record).execute()
        
        if result.data:
            console.print("✅ Real memory record created successfully")
            console.print(f"  Record ID: {result.data[0].get('id')}")
            console.print(f"  Namespace: {result.data[0].get('namespace')}")
            
            # Don't clean up - leave it as real data
            console.print("📊 Memory record kept for testing")
            return True
        else:
            console.print("❌ Failed to create real memory record")
            return False
            
    except Exception as e:
        console.print(f"❌ Real memory creation failed: {e}")
        return False

if __name__ == "__main__":
    inspect_table_structure()
    test_working_with_existing_structure()
    create_memory_with_available_columns()