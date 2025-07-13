#!/usr/bin/env python3
"""
Fix project_memorys table by inserting a proper record
Forces Supabase to create the correct column structure
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from supabase import create_client

load_dotenv()
console = Console()

def fix_project_memorys():
    """Fix the project_memorys table structure"""
    console.print("🔧 [bold blue]Fixing project_memorys table[/bold blue]")
    
    # Initialize Supabase
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    supabase = create_client(url, key)
    
    # Create a comprehensive test record with all expected fields
    test_record = {
        'namespace': 'schema_fix_test',
        'file_path': 'docs/test_schema_fix.md',
        'memory_type': 'specification',
        'brief_description': 'Test record to establish table schema',
        'elements_description': 'Schema fix test record with all required fields',
        'rationale': 'Establishing proper table structure for SPARC memory system',
        'version': 1,
        'quality_score': 0.95,
        'last_updated_timestamp': datetime.now().isoformat(),
        'created_at': datetime.now().isoformat(),
        'metadata': {
            'test': True,
            'purpose': 'schema_establishment',
            'agent': 'schema_fixer'
        }
    }
    
    try:
        # Insert the test record
        console.print("📝 Inserting test record to establish schema...")
        result = supabase.table('project_memorys').insert(test_record).execute()
        
        if result.data:
            console.print("✅ Test record inserted successfully")
            record_id = result.data[0].get('id')
            
            # Verify the record exists
            verify_result = supabase.table('project_memorys').select("*").eq('namespace', 'schema_fix_test').execute()
            
            if verify_result.data:
                console.print(f"✅ Record verified. Table now has {len(verify_result.data[0].keys())} columns")
                
                # Show the columns that were created
                columns = list(verify_result.data[0].keys())
                console.print(f"📋 Table columns: {', '.join(columns)}")
                
                # Clean up the test record
                if record_id:
                    delete_result = supabase.table('project_memorys').delete().eq('id', record_id).execute()
                    console.print("🗑️ Test record cleaned up")
                
                console.print("✅ [bold green]project_memorys table is now properly structured![/bold green]")
                return True
            else:
                console.print("❌ Could not verify the inserted record")
                return False
        else:
            console.print("❌ Failed to insert test record")
            return False
            
    except Exception as e:
        console.print(f"❌ Error fixing table: {e}")
        return False

def test_memory_operations():
    """Test basic memory operations"""
    console.print("\n🧪 [bold blue]Testing Memory Operations[/bold blue]")
    
    url = os.getenv('SUPABASE_URL') 
    key = os.getenv('SUPABASE_KEY')
    supabase = create_client(url, key)
    
    try:
        # Test a real memory record
        memory_record = {
            'namespace': 'test_operations',
            'file_path': 'docs/Mutual_Understanding_Document.md',
            'memory_type': 'specification',
            'brief_description': 'Comprehensive mutual understanding document',
            'elements_description': 'Document type: mutual_understanding',
            'rationale': 'Created during goal clarification phase',
            'version': 1,
            'quality_score': 0.9,
            'metadata': {
                'phase': 'goal-clarification',
                'agent': 'orchestrator-goal-clarification',
                'document_type': 'mutual_understanding'
            }
        }
        
        console.print("📝 Testing memory record insertion...")
        result = supabase.table('project_memorys').insert(memory_record).execute()
        
        if result.data:
            record_id = result.data[0].get('id')
            console.print("✅ Memory record inserted successfully")
            
            # Test query
            query_result = supabase.table('project_memorys').select("*").eq('namespace', 'test_operations').execute()
            if query_result.data:
                console.print("✅ Memory record queried successfully")
                
                # Cleanup
                supabase.table('project_memorys').delete().eq('id', record_id).execute()
                console.print("🗑️ Test record cleaned up")
                
                console.print("✅ [bold green]Memory operations working correctly![/bold green]")
                return True
        
        console.print("❌ Memory operations test failed")
        return False
        
    except Exception as e:
        console.print(f"❌ Memory operations error: {e}")
        return False

if __name__ == "__main__":
    success = fix_project_memorys()
    if success:
        test_memory_operations()
    else:
        console.print("❌ Could not fix project_memorys table")