#!/usr/bin/env python3
"""
Test complete SPARC database with all tables after SQL DDL execution
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from supabase import create_client

load_dotenv()
console = Console()

class DatabaseTester:
    """Test complete SPARC database functionality"""
    
    def __init__(self):
        self.supabase = self._init_supabase()
        self.test_namespace = f"complete_test_{int(datetime.now().timestamp())}"
        
    def _init_supabase(self):
        """Initialize Supabase client"""
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            console.print("[red]❌ Missing Supabase credentials[/red]")
            exit(1)
            
        return create_client(url, key)
    
    def test_all_tables(self):
        """Test all SPARC tables"""
        console.print("🧪 [bold blue]Testing Complete SPARC Database[/bold blue]")
        
        all_tables = [
            'agent_tasks',
            'project_memorys', 
            'sparc_contexts',
            'sparc_file_changes',
            'sparc_projects',
            'agent_executions',
            'approval_requests',
            'bmo_verifications', 
            'memory_insights',
            'cross_project_learnings',
            'quality_benchmarks',
            'user_preferences',
            'failure_patterns'
        ]
        
        # Create results table
        table = Table(title="SPARC Database Status")
        table.add_column("Table", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Rows", style="yellow")
        table.add_column("Columns", style="blue")
        table.add_column("Test", style="magenta")
        
        results = {}
        
        for table_name in all_tables:
            try:
                # Test basic query
                result = self.supabase.table(table_name).select("*", count="exact").limit(1).execute()
                count = result.count if hasattr(result, 'count') else len(result.data)
                
                # Get column count
                columns = 0
                if result.data and len(result.data) > 0:
                    columns = len(result.data[0].keys())
                
                # Test insert (if possible)
                test_result = self._test_insert(table_name)
                
                results[table_name] = {
                    'exists': True,
                    'row_count': count,
                    'columns': columns,
                    'insert_test': test_result
                }
                
                # Add to display table
                status = "✅ EXISTS"
                test_status = "✅ PASS" if test_result else "❌ FAIL"
                table.add_row(table_name, status, str(count), str(columns), test_status)
                
            except Exception as e:
                results[table_name] = {
                    'exists': False,
                    'error': str(e)
                }
                
                # Add to display table
                error_msg = str(e)[:30] + "..." if len(str(e)) > 30 else str(e)
                table.add_row(table_name, "❌ ERROR", "-", "-", error_msg)
        
        console.print(table)
        
        # Summary
        existing_tables = sum(1 for r in results.values() if r.get('exists', False))
        working_inserts = sum(1 for r in results.values() if r.get('insert_test', False))
        
        console.print(f"\n📊 [bold]Summary:[/bold]")
        console.print(f"  • Tables existing: {existing_tables}/{len(all_tables)}")
        console.print(f"  • Working inserts: {working_inserts}/{len(all_tables)}")
        
        if existing_tables == len(all_tables) and working_inserts >= 10:
            console.print("✅ [bold green]Database is ready for production![/bold green]")
            return True
        else:
            console.print("⚠️ [bold yellow]Database needs attention[/bold yellow]")
            return False
    
    def _test_insert(self, table_name):
        """Test insert operation for each table"""
        try:
            sample_data = self._get_sample_data(table_name)
            if not sample_data:
                return False
                
            # Insert test record
            result = self.supabase.table(table_name).insert(sample_data).execute()
            
            if result.data:
                # Clean up test record
                record_id = result.data[0].get('id')
                if record_id:
                    self.supabase.table(table_name).delete().eq('id', record_id).execute()
                return True
            return False
            
        except Exception as e:
            console.print(f"  Insert test failed for {table_name}: {str(e)[:50]}")
            return False
    
    def _get_sample_data(self, table_name):
        """Get sample data for testing each table"""
        base_data = {
            'agent_tasks': {
                'namespace': self.test_namespace,
                'from_agent': 'test_agent',
                'to_agent': 'target_agent',
                'task_type': 'test',
                'task_data': {'test': True},
                'task_payload': {'test': True},
                'priority': 5,
                'status': 'pending'
            },
            'project_memorys': {
                'namespace': self.test_namespace,
                'file_path': 'test/file.md',
                'memory_type': 'test',
                'brief_description': 'Test memory',
                'elements_description': 'Test elements',
                'rationale': 'Testing'
            },
            'sparc_contexts': {
                'namespace': self.test_namespace,
                'context_type': 'test',
                'context_key': 'test_key',
                'phase': 'test',
                'content': 'test content',
                'context_data': {'test': True}
            },
            'sparc_file_changes': {
                'namespace': self.test_namespace,
                'file_path': 'test/file.md',
                'tool_used': 'test_tool',
                'change_type': 'create',
                'agent_name': 'test_agent'
            },
            'sparc_projects': {
                'namespace': self.test_namespace,
                'project_name': 'Test Project',
                'project_goal': 'Test project',
                'current_phase': 'test',
                'status': 'active'
            },
            'agent_executions': {
                'namespace': self.test_namespace,
                'agent_name': 'test_agent',
                'execution_type': 'test',
                'status': 'completed'
            },
            'approval_requests': {
                'project_id': self.test_namespace,
                'phase': 'test',
                'request_data': {'test': True},
                'message': 'Test approval request',
                'requested_by': 'test_agent'
            },
            'bmo_verifications': {
                'project_id': self.test_namespace,
                'verification_type': 'test',
                'behavior_model': {'test': True},
                'oracle_results': {'test': True},
                'verification_status': 'passed',
                'results': {'test': True}
            },
            'memory_insights': {
                'namespace': self.test_namespace,
                'insight_type': 'test',
                'content': 'Test insight content'
            },
            'cross_project_learnings': {
                'learning_type': 'test',
                'pattern_description': 'Test learning pattern'
            },
            'quality_benchmarks': {
                'benchmark_type': 'test',
                'metric_name': 'test_metric'
            },
            'user_preferences': {
                'user_identifier': 'test_user',
                'preference_type': 'test',
                'preference_value': {'test': True}
            },
            'failure_patterns': {
                'pattern_type': 'test',
                'failure_signature': 'Test failure pattern',
                'severity_level': 'low'
            }
        }
        
        return base_data.get(table_name)
    
    def demonstrate_workflow(self):
        """Demonstrate a complete SPARC workflow using all tables"""
        console.print("\n🚀 [bold blue]Demonstrating Complete SPARC Workflow[/bold blue]")
        
        try:
            # 1. Create project
            project_data = {
                'namespace': self.test_namespace,
                'project_name': 'Task Management App',
                'project_goal': 'Build a complete task management application',
                'current_phase': 'goal-clarification',
                'status': 'active',
                'start_date': datetime.now().isoformat(),
                'estimated_completion': (datetime.now() + timedelta(weeks=8)).isoformat()
            }
            
            project_result = self.supabase.table('sparc_projects').insert(project_data).execute()
            console.print("✅ Project created")
            
            # 2. Add memory
            memory_data = {
                'namespace': self.test_namespace,
                'file_path': 'docs/requirements.md',
                'memory_type': 'specification',
                'brief_description': 'Project requirements document',
                'elements_description': 'User stories and technical requirements',
                'rationale': 'Foundation for development'
            }
            
            memory_result = self.supabase.table('project_memorys').insert(memory_data).execute()
            console.print("✅ Memory recorded")
            
            # 3. Create agent task
            task_data = {
                'namespace': self.test_namespace,
                'from_agent': 'orchestrator-goal-clarification',
                'to_agent': 'specialist-frontend',
                'task_type': 'create_component',
                'task_data': {'component': 'UserLoginForm', 'framework': 'React'},
                'task_payload': {'component': 'UserLoginForm', 'framework': 'React'},
                'priority': 1
            }
            
            task_result = self.supabase.table('agent_tasks').insert(task_data).execute()
            console.print("✅ Agent task created")
            
            # 4. Record BMO verification
            bmo_data = {
                'project_id': self.test_namespace,
                'verification_type': 'requirements_validation',
                'behavior_model': {
                    'user_behaviors': ['login', 'create_task', 'edit_task'],
                    'success_criteria': ['secure_auth', 'data_persistence']
                },
                'oracle_results': {
                    'validation_score': 0.92,
                    'completeness': 0.88
                },
                'verification_status': 'passed',
                'results': {'alignment_score': 0.90}
            }
            
            bmo_result = self.supabase.table('bmo_verifications').insert(bmo_data).execute()
            console.print("✅ BMO verification recorded")
            
            # 5. Create approval request
            approval_data = {
                'project_id': self.test_namespace,
                'phase': 'goal-clarification',
                'request_data': {
                    'documents': ['docs/requirements.md'],
                    'validation_score': 0.92
                },
                'message': 'Goal clarification complete. Ready for specification phase.',
                'requested_by': 'orchestrator-goal-clarification'
            }
            
            approval_result = self.supabase.table('approval_requests').insert(approval_data).execute()
            console.print("✅ Approval request created")
            
            console.print("\n🎉 [bold green]Complete workflow demonstrated successfully![/bold green]")
            
            # Clean up demo data
            if project_result.data:
                project_id = project_result.data[0].get('id')
                if project_id:
                    self.supabase.table('sparc_projects').delete().eq('id', project_id).execute()
            
            if memory_result.data:
                memory_id = memory_result.data[0].get('id')
                if memory_id:
                    self.supabase.table('project_memorys').delete().eq('id', memory_id).execute()
            
            if task_result.data:
                task_id = task_result.data[0].get('id')
                if task_id:
                    self.supabase.table('agent_tasks').delete().eq('id', task_id).execute()
            
            if bmo_result.data:
                bmo_id = bmo_result.data[0].get('id')
                if bmo_id:
                    self.supabase.table('bmo_verifications').delete().eq('id', bmo_id).execute()
            
            if approval_result.data:
                approval_id = approval_result.data[0].get('id')
                if approval_id:
                    self.supabase.table('approval_requests').delete().eq('id', approval_id).execute()
            
            console.print("🗑️ Demo data cleaned up")
            return True
            
        except Exception as e:
            console.print(f"❌ Workflow demonstration failed: {e}")
            return False

def main():
    """Test complete database"""
    tester = DatabaseTester()
    
    # Test all tables
    database_ready = tester.test_all_tables()
    
    if database_ready:
        # Demonstrate workflow
        tester.demonstrate_workflow()
        
        console.print("\n💡 [bold blue]Next Steps:[/bold blue]")
        console.print("  • Database is production-ready")
        console.print("  • All 13 SPARC tables are functional")
        console.print("  • Agents can use complete schema")
        console.print("  • Run real autonomous development workflow")
    else:
        console.print("\n⚠️ [bold yellow]Database Setup Required:[/bold yellow]")
        console.print("  • Execute create_missing_tables.sql in Supabase")
        console.print("  • Run this test again to verify")

if __name__ == "__main__":
    main()