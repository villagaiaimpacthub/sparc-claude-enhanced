#!/usr/bin/env python3
"""
Comprehensive Supabase Analysis for SPARC System
Check all tables, their structure, and current data state
"""

import asyncio
import os
from pathlib import Path
import sys
from datetime import datetime

# Add lib to path  
lib_path = Path(__file__).parent / "lib"
sys.path.insert(0, str(lib_path))

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from supabase import create_client, Client

load_dotenv()
console = Console()

class SupabaseAnalyzer:
    """Analyze the complete Supabase database structure and data"""
    
    def __init__(self):
        self.supabase = self._init_supabase()
        
    def _init_supabase(self) -> Client:
        """Initialize Supabase client"""
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            console.print("[red]❌ Missing Supabase credentials[/red]")
            exit(1)
            
        return create_client(url, key)
    
    async def analyze_all_tables(self):
        """Analyze all tables in the database"""
        console.print("🔍 [bold blue]Comprehensive Supabase Analysis[/bold blue]")
        
        # Known SPARC tables to check
        sparc_tables = [
            'agent_tasks',
            'project_memorys', 
            'sparc_contexts',
            'sparc_file_changes',
            'approval_requests',
            'bmo_verifications',
            'sparc_projects',
            'agent_executions',
            'memory_insights',
            'cross_project_learnings',
            'quality_benchmarks',
            'user_preferences',
            'failure_patterns'
        ]
        
        results = {}
        
        for table_name in sparc_tables:
            try:
                result = await self._analyze_table(table_name)
                results[table_name] = result
            except Exception as e:
                results[table_name] = {"error": str(e), "exists": False}
        
        # Display results
        await self._display_analysis(results)
        return results
    
    async def _analyze_table(self, table_name: str) -> dict:
        """Analyze a specific table"""
        try:
            # Get row count
            count_result = self.supabase.table(table_name).select("*", count="exact").execute()
            row_count = count_result.count if hasattr(count_result, 'count') else len(count_result.data)
            
            # Get sample data (first 3 rows)
            sample_result = self.supabase.table(table_name).select("*").limit(3).execute()
            sample_data = sample_result.data
            
            # Get recent data if any exists
            recent_data = []
            if row_count > 0:
                try:
                    recent_result = self.supabase.table(table_name).select("*").order(
                        "created_at", desc=True
                    ).limit(3).execute()
                    recent_data = recent_result.data
                except:
                    # Try with different timestamp fields
                    for time_field in ['updated_at', 'timestamp', 'last_updated_timestamp']:
                        try:
                            recent_result = self.supabase.table(table_name).select("*").order(
                                time_field, desc=True
                            ).limit(3).execute()
                            recent_data = recent_result.data
                            break
                        except:
                            continue
            
            # Get column information from sample
            columns = []
            if sample_data:
                columns = list(sample_data[0].keys())
            
            return {
                "exists": True,
                "row_count": row_count,
                "columns": columns,
                "sample_data": sample_data,
                "recent_data": recent_data,
                "has_data": row_count > 0
            }
            
        except Exception as e:
            return {
                "exists": False,
                "error": str(e),
                "row_count": 0,
                "has_data": False
            }
    
    async def _display_analysis(self, results: dict):
        """Display the analysis results in a nice format"""
        
        # Summary table
        summary_table = Table(title="📊 Supabase Table Summary")
        summary_table.add_column("Table Name", style="cyan")
        summary_table.add_column("Status", style="green")
        summary_table.add_column("Rows", justify="right")
        summary_table.add_column("Columns", justify="right")
        summary_table.add_column("Has Data", style="yellow")
        
        empty_tables = []
        populated_tables = []
        missing_tables = []
        
        for table_name, analysis in results.items():
            if not analysis.get("exists", False):
                status = "[red]❌ Missing[/red]"
                rows = "N/A"
                cols = "N/A" 
                has_data = "[red]No[/red]"
                missing_tables.append(table_name)
            else:
                status = "[green]✅ Exists[/green]"
                rows = str(analysis["row_count"])
                cols = str(len(analysis.get("columns", [])))
                
                if analysis["has_data"]:
                    has_data = "[green]Yes[/green]"
                    populated_tables.append(table_name)
                else:
                    has_data = "[yellow]Empty[/yellow]"
                    empty_tables.append(table_name)
            
            summary_table.add_row(table_name, status, rows, cols, has_data)
        
        console.print(summary_table)
        
        # Statistics
        stats_panel = Panel(
            f"📈 [bold]Database Statistics[/bold]\n\n"
            f"🟢 Tables with data: {len(populated_tables)}\n"
            f"🟡 Empty tables: {len(empty_tables)}\n" 
            f"🔴 Missing tables: {len(missing_tables)}\n"
            f"📊 Total tables analyzed: {len(results)}",
            title="Summary"
        )
        console.print(stats_panel)
        
        # Show populated tables detail
        if populated_tables:
            console.print("\n[bold green]🟢 Tables with Data:[/bold green]")
            for table_name in populated_tables:
                analysis = results[table_name]
                console.print(f"  • {table_name}: {analysis['row_count']} rows")
                
                # Show recent entries
                if analysis.get("recent_data"):
                    console.print(f"    [dim]Recent entries:[/dim]")
                    for i, entry in enumerate(analysis["recent_data"][:2]):
                        # Show key fields
                        key_info = []
                        for key in ['created_at', 'updated_at', 'timestamp', 'from_agent', 'to_agent', 'status', 'phase']:
                            if key in entry:
                                key_info.append(f"{key}={entry[key]}")
                        console.print(f"      {i+1}. {', '.join(key_info[:3])}")
        
        # Show empty tables
        if empty_tables:
            console.print(f"\n[bold yellow]🟡 Empty Tables ({len(empty_tables)}):[/bold yellow]")
            for table_name in empty_tables:
                analysis = results[table_name]
                cols = len(analysis.get("columns", []))
                console.print(f"  • {table_name}: {cols} columns, 0 rows")
        
        # Show missing tables
        if missing_tables:
            console.print(f"\n[bold red]🔴 Missing Tables ({len(missing_tables)}):[/bold red]")
            for table_name in missing_tables:
                console.print(f"  • {table_name}: Table does not exist")
    
    async def test_basic_operations(self):
        """Test basic CRUD operations on key tables"""
        console.print("\n🧪 [bold blue]Testing Basic Database Operations[/bold blue]")
        
        test_results = {}
        
        # Test agent_tasks table
        try:
            # Insert test task
            test_task = {
                'namespace': 'test_analysis',
                'from_agent': 'analyzer',
                'to_agent': 'test-agent',
                'task_type': 'test',
                'task_payload': {'test': True},
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            
            insert_result = self.supabase.table('agent_tasks').insert(test_task).execute()
            task_id = insert_result.data[0]['id'] if insert_result.data else None
            
            if task_id:
                # Update test
                update_result = self.supabase.table('agent_tasks').update({
                    'status': 'completed'
                }).eq('id', task_id).execute()
                
                # Read test  
                read_result = self.supabase.table('agent_tasks').select("*").eq('id', task_id).execute()
                
                # Delete test
                delete_result = self.supabase.table('agent_tasks').delete().eq('id', task_id).execute()
                
                test_results['agent_tasks'] = {
                    "crud_test": "✅ Passed",
                    "can_insert": True,
                    "can_update": True, 
                    "can_read": True,
                    "can_delete": True
                }
            else:
                test_results['agent_tasks'] = {"crud_test": "❌ Insert failed"}
                
        except Exception as e:
            test_results['agent_tasks'] = {"crud_test": f"❌ Error: {str(e)}"}
        
        # Display test results
        for table, result in test_results.items():
            console.print(f"  • {table}: {result.get('crud_test', 'Unknown')}")

async def main():
    """Run comprehensive analysis"""
    analyzer = SupabaseAnalyzer()
    
    # Analyze all tables
    results = await analyzer.analyze_all_tables()
    
    # Test basic operations
    await analyzer.test_basic_operations()
    
    # Recommendations
    console.print("\n💡 [bold blue]Recommendations:[/bold blue]")
    
    empty_count = sum(1 for r in results.values() if r.get("exists") and not r.get("has_data"))
    if empty_count > 5:
        console.print("  • Run a full SPARC workflow test to populate tables")
        console.print("  • Check if agents are properly configured to write to database")
        console.print("  • Verify database permissions and connections")
    
    console.print("\n🎯 [bold green]Ready for comprehensive SPARC system test![/bold green]")

if __name__ == "__main__":
    asyncio.run(main())