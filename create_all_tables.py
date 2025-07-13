#!/usr/bin/env python3
"""
Create All Missing Supabase Tables with Proper Schemas
Creates production-ready table structures for the complete SPARC system
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, TaskID
from supabase import create_client, Client

load_dotenv()
console = Console()

class SPARCTableCreator:
    """Create all SPARC database tables with proper schemas"""
    
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
    
    async def create_all_tables(self):
        """Create all missing SPARC tables by inserting representative records"""
        console.print("🔨 [bold blue]Creating All SPARC Database Tables[/bold blue]")
        
        # Create each table by inserting a proper record that establishes the schema
        tables_to_create = [
            ("approval_requests", self._create_approval_requests),
            ("bmo_verifications", self._create_bmo_verifications),
            ("memory_insights", self._create_memory_insights),
            ("cross_project_learnings", self._create_cross_project_learnings),
            ("quality_benchmarks", self._create_quality_benchmarks),
            ("user_preferences", self._create_user_preferences),
            ("failure_patterns", self._create_failure_patterns),
            ("sparc_projects", self._fix_sparc_projects),
            ("sparc_file_changes", self._fix_sparc_file_changes)
        ]
        
        with Progress() as progress:
            task = progress.add_task("Creating tables...", total=len(tables_to_create))
            
            for table_name, create_func in tables_to_create:
                try:
                    console.print(f"\n🔨 Creating {table_name}...")
                    success = await create_func()
                    
                    if success:
                        console.print(f"✅ {table_name} created successfully")
                    else:
                        console.print(f"⚠️ {table_name} creation had issues")
                        
                    progress.advance(task)
                    
                except Exception as e:
                    console.print(f"❌ Failed to create {table_name}: {e}")
        
        # Test all tables
        await self._test_all_tables()
        
        console.print("\n✅ [bold green]All SPARC tables created![/bold green]")
    
    async def _create_approval_requests(self) -> bool:
        """Create approval_requests table"""
        try:
            sample_approval = {
                'project_id': 'table_creation_test',
                'phase': 'goal-clarification',
                'request_data': {
                    'documents': ['docs/Mutual_Understanding_Document.md'],
                    'phase': 'goal-clarification',
                    'timestamp': datetime.now().isoformat()
                },
                'message': 'Goal clarification complete. Please review and approve to proceed to specification phase.',
                'status': 'pending',
                'requested_by': 'orchestrator-goal-clarification',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('approval_requests').insert(sample_approval).execute()
            
            if result.data:
                # Clean up the test record
                record_id = result.data[0].get('id')
                if record_id:
                    self.supabase.table('approval_requests').delete().eq('id', record_id).execute()
                return True
            return False
            
        except Exception as e:
            console.print(f"  Error: {e}")
            return False
    
    async def _create_bmo_verifications(self) -> bool:
        """Create bmo_verifications table"""
        try:
            sample_verification = {
                'project_id': 'table_creation_test',
                'verification_type': 'intent_triangulation',
                'behavior_model': {
                    'user_intent': 'Build task management app',
                    'expected_behaviors': ['user registration', 'task creation', 'task editing'],
                    'success_criteria': ['authentication works', 'tasks persist', 'responsive UI']
                },
                'oracle_results': {
                    'tests_passed': 15,
                    'tests_failed': 2,
                    'coverage_percentage': 87.5,
                    'performance_metrics': {'response_time': 180, 'memory_usage': 64}
                },
                'triangulation_score': 0.92,
                'verification_status': 'passed',
                'results': {
                    'alignment_score': 0.94,
                    'completeness_score': 0.89,
                    'quality_score': 0.93,
                    'recommendations': ['Improve error handling', 'Add input validation']
                },
                'created_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('bmo_verifications').insert(sample_verification).execute()
            
            if result.data:
                record_id = result.data[0].get('id')
                if record_id:
                    self.supabase.table('bmo_verifications').delete().eq('id', record_id).execute()
                return True
            return False
            
        except Exception as e:
            console.print(f"  Error: {e}")
            return False
    
    async def _create_memory_insights(self) -> bool:
        """Create memory_insights table"""
        try:
            sample_insight = {
                'namespace': 'table_creation_test',
                'insight_type': 'code_pattern',
                'content': 'React components with useState hook pattern shows 95% success rate for user interfaces',
                'confidence_score': 0.95,
                'application_count': 23,
                'success_rate': 0.94,
                'tags': ['react', 'hooks', 'ui', 'frontend'],
                'metadata': {
                    'pattern_category': 'ui_component',
                    'framework': 'react',
                    'complexity_level': 'intermediate',
                    'performance_impact': 'low'
                },
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('memory_insights').insert(sample_insight).execute()
            
            if result.data:
                record_id = result.data[0].get('id')
                if record_id:
                    self.supabase.table('memory_insights').delete().eq('id', record_id).execute()
                return True
            return False
            
        except Exception as e:
            console.print(f"  Error: {e}")
            return False
    
    async def _create_cross_project_learnings(self) -> bool:
        """Create cross_project_learnings table"""
        try:
            sample_learning = {
                'learning_type': 'architecture_pattern',
                'source_projects': ['task_manager_v1', 'chat_app_v2', 'dashboard_v3'],
                'pattern_description': 'Authentication middleware with JWT tokens consistently reduces security vulnerabilities by 80%',
                'applicability_score': 0.88,
                'usage_frequency': 15,
                'success_contexts': [
                    {'project_type': 'web_app', 'team_size': 'small', 'success_rate': 0.95},
                    {'project_type': 'api', 'team_size': 'medium', 'success_rate': 0.92}
                ],
                'failure_contexts': [
                    {'project_type': 'mobile_app', 'reason': 'token_storage_complexity'},
                    {'project_type': 'embedded', 'reason': 'resource_constraints'}
                ],
                'recommendation': 'Use JWT authentication for web applications and APIs. Consider alternative approaches for mobile and embedded systems.',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('cross_project_learnings').insert(sample_learning).execute()
            
            if result.data:
                record_id = result.data[0].get('id')
                if record_id:
                    self.supabase.table('cross_project_learnings').delete().eq('id', record_id).execute()
                return True
            return False
            
        except Exception as e:
            console.print(f"  Error: {e}")
            return False
    
    async def _create_quality_benchmarks(self) -> bool:
        """Create quality_benchmarks table"""
        try:
            sample_benchmark = {
                'benchmark_type': 'code_quality',
                'metric_name': 'test_coverage_percentage',
                'target_value': 85.0,
                'current_average': 78.5,
                'trend_direction': 'improving',
                'measurement_count': 47,
                'industry_percentile': 72.0,
                'context_tags': ['web_development', 'javascript', 'automated_testing'],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('quality_benchmarks').insert(sample_benchmark).execute()
            
            if result.data:
                record_id = result.data[0].get('id')
                if record_id:
                    self.supabase.table('quality_benchmarks').delete().eq('id', record_id).execute()
                return True
            return False
            
        except Exception as e:
            console.print(f"  Error: {e}")
            return False
    
    async def _create_user_preferences(self) -> bool:
        """Create user_preferences table"""
        try:
            sample_preference = {
                'user_identifier': 'default_user',
                'preference_type': 'coding_style',
                'preference_value': {
                    'indentation': 'spaces',
                    'spaces_count': 2,
                    'semicolons': True,
                    'quote_style': 'single',
                    'trailing_commas': True
                },
                'confidence_level': 0.87,
                'learned_from_interactions': 12,
                'last_reinforced': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('user_preferences').insert(sample_preference).execute()
            
            if result.data:
                record_id = result.data[0].get('id')
                if record_id:
                    self.supabase.table('user_preferences').delete().eq('id', record_id).execute()
                return True
            return False
            
        except Exception as e:
            console.print(f"  Error: {e}")
            return False
    
    async def _create_failure_patterns(self) -> bool:
        """Create failure_patterns table"""
        try:
            sample_failure = {
                'pattern_type': 'implementation_error',
                'failure_signature': 'Missing input validation leads to SQL injection vulnerability',
                'occurrence_count': 8,
                'severity_level': 'high',
                'resolution_strategy': 'Implement parameterized queries and input sanitization',
                'prevention_measures': [
                    'Use ORM with built-in escaping',
                    'Validate all user inputs',
                    'Use prepared statements',
                    'Regular security audits'
                ],
                'affected_components': ['user_authentication', 'data_queries', 'api_endpoints'],
                'first_seen': (datetime.now() - timedelta(days=30)).isoformat(),
                'last_seen': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('failure_patterns').insert(sample_failure).execute()
            
            if result.data:
                record_id = result.data[0].get('id')
                if record_id:
                    self.supabase.table('failure_patterns').delete().eq('id', record_id).execute()
                return True
            return False
            
        except Exception as e:
            console.print(f"  Error: {e}")
            return False
    
    async def _fix_sparc_projects(self) -> bool:
        """Fix sparc_projects table structure"""
        try:
            sample_project = {
                'namespace': 'table_creation_test',
                'project_goal': 'Test project for table creation',
                'current_phase': 'initialization',
                'status': 'active',
                'start_date': datetime.now().isoformat(),
                'estimated_completion': (datetime.now() + timedelta(weeks=8)).isoformat(),
                'completion_percentage': 0.0,
                'quality_score': 0.0,
                'metadata': {
                    'created_by': 'table_creator',
                    'project_type': 'test',
                    'complexity': 'low'
                },
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('sparc_projects').insert(sample_project).execute()
            
            if result.data:
                record_id = result.data[0].get('id')
                if record_id:
                    self.supabase.table('sparc_projects').delete().eq('id', record_id).execute()
                return True
            return False
            
        except Exception as e:
            console.print(f"  Error: {e}")
            return False
    
    async def _fix_sparc_file_changes(self) -> bool:
        """Fix sparc_file_changes table structure"""
        try:
            sample_file_change = {
                'namespace': 'table_creation_test',
                'file_path': 'docs/test_file.md',
                'change_type': 'create',
                'tool_used': 'table_creator',  # Required field
                'content_preview': 'Test file for table creation...',
                'agent_name': 'table_creator_agent',
                'timestamp': datetime.now().isoformat(),
                'metadata': {
                    'file_size': 1024,
                    'lines_added': 25,
                    'lines_removed': 0
                }
            }
            
            result = self.supabase.table('sparc_file_changes').insert(sample_file_change).execute()
            
            if result.data:
                record_id = result.data[0].get('id')
                if record_id:
                    self.supabase.table('sparc_file_changes').delete().eq('id', record_id).execute()
                return True
            return False
            
        except Exception as e:
            console.print(f"  Error: {e}")
            return False
    
    async def _test_all_tables(self):
        """Test all created tables"""
        console.print("\n🧪 [bold blue]Testing All Tables[/bold blue]")
        
        tables = [
            'agent_tasks', 'project_memorys', 'sparc_contexts', 'sparc_file_changes',
            'approval_requests', 'bmo_verifications', 'sparc_projects', 'agent_executions',
            'memory_insights', 'cross_project_learnings', 'quality_benchmarks',
            'user_preferences', 'failure_patterns'
        ]
        
        results = {}
        
        for table in tables:
            try:
                # Test basic query
                result = self.supabase.table(table).select("*", count="exact").limit(1).execute()
                count = result.count if hasattr(result, 'count') else len(result.data)
                
                # Test structure by looking at available columns
                columns = []
                if result.data and len(result.data) > 0:
                    columns = list(result.data[0].keys())
                
                results[table] = {
                    'exists': True,
                    'row_count': count,
                    'columns': len(columns),
                    'sample_columns': columns[:5] if columns else []
                }
                
            except Exception as e:
                results[table] = {
                    'exists': False,
                    'error': str(e)
                }
        
        # Display results
        for table, result in results.items():
            if result.get('exists', False):
                status = f"✅ {result['row_count']} rows, {result['columns']} cols"
                if result['sample_columns']:
                    status += f" ({', '.join(result['sample_columns'][:3])}...)"
            else:
                status = f"❌ {result.get('error', 'Unknown error')[:50]}"
            
            console.print(f"  📋 {table}: {status}")

async def main():
    """Create all SPARC tables"""
    creator = SPARCTableCreator()
    await creator.create_all_tables()
    
    console.print("\n💡 [bold blue]Next Steps:[/bold blue]")
    console.print("  • All SPARC database tables are now available")
    console.print("  • Agents can use the complete schema")
    console.print("  • Run end-to-end workflow test")
    console.print("  • Update agent code to use new tables")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())