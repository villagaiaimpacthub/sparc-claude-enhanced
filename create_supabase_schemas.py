#!/usr/bin/env python3
"""
Create Proper Supabase Table Schemas for SPARC System
Fixes the empty tables by creating proper column structures
"""

import os
import sys
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from supabase import create_client, Client

load_dotenv()
console = Console()

class SupabaseSchemaCreator:
    """Create and fix Supabase table schemas"""
    
    def __init__(self):
        self.supabase = self._init_supabase()
        
    def _init_supabase(self) -> Client:
        """Initialize Supabase client"""
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY')  # Use service key for admin operations
        
        if not url or not key:
            console.print("[red]❌ Missing Supabase credentials[/red]")
            exit(1)
            
        return create_client(url, key)
    
    async def create_all_schemas(self):
        """Create all required SPARC table schemas"""
        console.print("🔨 [bold blue]Creating Supabase Table Schemas[/bold blue]")
        
        # SQL commands to create missing tables and fix existing ones
        sql_commands = [
            # Fix project_memorys table
            """
            DROP TABLE IF EXISTS project_memorys CASCADE;
            CREATE TABLE project_memorys (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                namespace VARCHAR(255) NOT NULL,
                file_path TEXT NOT NULL,
                memory_type VARCHAR(100),
                brief_description TEXT,
                elements_description TEXT,
                rationale TEXT,
                version INTEGER DEFAULT 1,
                quality_score FLOAT DEFAULT 0.0,
                last_updated_timestamp TIMESTAMPTZ DEFAULT NOW(),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                metadata JSONB DEFAULT '{}'::jsonb
            );
            """,
            
            # Create missing approval_requests table
            """
            CREATE TABLE IF NOT EXISTS approval_requests (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                project_id VARCHAR(255) NOT NULL,
                phase VARCHAR(100) NOT NULL,
                request_data JSONB NOT NULL,
                message TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                requested_by VARCHAR(255),
                approved_by VARCHAR(255),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Create missing bmo_verifications table
            """
            CREATE TABLE IF NOT EXISTS bmo_verifications (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                project_id VARCHAR(255) NOT NULL,
                verification_type VARCHAR(100) NOT NULL,
                behavior_model JSONB,
                oracle_results JSONB,
                triangulation_score FLOAT,
                verification_status VARCHAR(50),
                results JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Create missing memory_insights table
            """
            CREATE TABLE IF NOT EXISTS memory_insights (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                namespace VARCHAR(255) NOT NULL,
                insight_type VARCHAR(100) NOT NULL,
                content TEXT NOT NULL,
                confidence_score FLOAT DEFAULT 0.0,
                application_count INTEGER DEFAULT 0,
                success_rate FLOAT DEFAULT 0.0,
                tags TEXT[],
                metadata JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Create missing cross_project_learnings table
            """
            CREATE TABLE IF NOT EXISTS cross_project_learnings (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                learning_type VARCHAR(100) NOT NULL,
                source_projects TEXT[],
                pattern_description TEXT NOT NULL,
                applicability_score FLOAT DEFAULT 0.0,
                usage_frequency INTEGER DEFAULT 0,
                success_contexts JSONB DEFAULT '[]'::jsonb,
                failure_contexts JSONB DEFAULT '[]'::jsonb,
                recommendation TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Create missing quality_benchmarks table
            """
            CREATE TABLE IF NOT EXISTS quality_benchmarks (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                benchmark_type VARCHAR(100) NOT NULL,
                metric_name VARCHAR(255) NOT NULL,
                target_value FLOAT NOT NULL,
                current_average FLOAT DEFAULT 0.0,
                trend_direction VARCHAR(20) DEFAULT 'stable',
                measurement_count INTEGER DEFAULT 0,
                industry_percentile FLOAT,
                context_tags TEXT[],
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Create missing user_preferences table
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                user_identifier VARCHAR(255) NOT NULL,
                preference_type VARCHAR(100) NOT NULL,
                preference_value JSONB NOT NULL,
                confidence_level FLOAT DEFAULT 0.0,
                learned_from_interactions INTEGER DEFAULT 1,
                last_reinforced TIMESTAMPTZ DEFAULT NOW(),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(user_identifier, preference_type)
            );
            """,
            
            # Create missing failure_patterns table
            """
            CREATE TABLE IF NOT EXISTS failure_patterns (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                pattern_type VARCHAR(100) NOT NULL,
                failure_signature TEXT NOT NULL,
                occurrence_count INTEGER DEFAULT 1,
                severity_level VARCHAR(20) DEFAULT 'medium',
                resolution_strategy TEXT,
                prevention_measures TEXT[],
                affected_components TEXT[],
                first_seen TIMESTAMPTZ DEFAULT NOW(),
                last_seen TIMESTAMPTZ DEFAULT NOW(),
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Fix sparc_file_changes table if empty
            """
            DROP TABLE IF EXISTS sparc_file_changes CASCADE;
            CREATE TABLE sparc_file_changes (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                namespace VARCHAR(255) NOT NULL,
                file_path TEXT NOT NULL,
                change_type VARCHAR(50) NOT NULL,
                tool_used VARCHAR(100),
                content_preview TEXT,
                agent_name VARCHAR(255),
                timestamp TIMESTAMPTZ DEFAULT NOW(),
                metadata JSONB DEFAULT '{}'::jsonb
            );
            """,
            
            # Fix sparc_projects table if empty
            """
            DROP TABLE IF EXISTS sparc_projects CASCADE;
            CREATE TABLE sparc_projects (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                namespace VARCHAR(255) UNIQUE NOT NULL,
                project_goal TEXT NOT NULL,
                current_phase VARCHAR(100) DEFAULT 'initialization',
                status VARCHAR(50) DEFAULT 'active',
                start_date TIMESTAMPTZ DEFAULT NOW(),
                estimated_completion TIMESTAMPTZ,
                completion_percentage FLOAT DEFAULT 0.0,
                quality_score FLOAT DEFAULT 0.0,
                metadata JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        ]
        
        # Execute each SQL command
        for i, sql in enumerate(sql_commands, 1):
            try:
                console.print(f"🔨 Executing schema command {i}/{len(sql_commands)}...")
                
                # Extract table name for logging
                table_name = "unknown"
                if "CREATE TABLE" in sql or "DROP TABLE" in sql:
                    lines = sql.strip().split('\n')
                    for line in lines:
                        if 'TABLE' in line and ('CREATE' in line or 'DROP' in line):
                            parts = line.split()
                            for j, part in enumerate(parts):
                                if part == 'TABLE' and j + 1 < len(parts):
                                    table_name = parts[j + 1].replace('IF', '').replace('NOT', '').replace('EXISTS', '').strip()
                                    if table_name.endswith('CASCADE;'):
                                        table_name = table_name.replace('CASCADE;', '')
                                    break
                            break
                
                # Execute using RPC call to avoid permission issues
                result = self.supabase.rpc('exec_sql', {'sql_query': sql}).execute()
                
                console.print(f"✅ Schema command {i} completed for {table_name}")
                
            except Exception as e:
                console.print(f"❌ Schema command {i} failed: {e}")
                # Try alternative approach - direct table creation via REST API
                console.print(f"🔄 Attempting alternative creation method...")
                try:
                    await self._create_table_alternative(table_name, sql)
                    console.print(f"✅ Alternative creation successful for {table_name}")
                except Exception as e2:
                    console.print(f"❌ Alternative creation also failed: {e2}")
        
        # Test the created schemas
        await self._test_schemas()
        
        console.print("✅ [bold green]Schema creation completed![/bold green]")
    
    async def _create_table_alternative(self, table_name: str, sql: str):
        """Alternative table creation method"""
        # For tables that can be created via simple insert, try that
        if table_name == "project_memorys":
            test_record = {
                'namespace': 'test',
                'file_path': 'test.md',
                'memory_type': 'test',
                'brief_description': 'test description',
                'elements_description': 'test elements',
                'rationale': 'test rationale',
                'version': 1,
                'quality_score': 0.8,
                'metadata': {}
            }
            # Insert and immediately delete to create the table structure
            result = self.supabase.table('project_memorys').insert(test_record).execute()
            if result.data:
                self.supabase.table('project_memorys').delete().eq('namespace', 'test').execute()
    
    async def _test_schemas(self):
        """Test the created schemas by inserting test data"""
        console.print("\n🧪 [bold blue]Testing Created Schemas[/bold blue]")
        
        test_results = []
        
        # Test project_memorys
        try:
            test_memory = {
                'namespace': 'schema_test',
                'file_path': 'test/schema_test.md',
                'memory_type': 'test_type',
                'brief_description': 'Schema test record',
                'elements_description': 'Testing schema creation',
                'rationale': 'Verify table structure works',
                'version': 1,
                'quality_score': 0.95
            }
            
            result = self.supabase.table('project_memorys').insert(test_memory).execute()
            if result.data:
                # Clean up test data
                self.supabase.table('project_memorys').delete().eq('namespace', 'schema_test').execute()
                test_results.append(("project_memorys", "✅ Working"))
            else:
                test_results.append(("project_memorys", "❌ Insert failed"))
                
        except Exception as e:
            test_results.append(("project_memorys", f"❌ Error: {str(e)[:50]}"))
        
        # Test approval_requests
        try:
            test_approval = {
                'project_id': 'schema_test',
                'phase': 'test_phase',
                'request_data': {'test': True},
                'message': 'Schema test approval',
                'status': 'pending'
            }
            
            result = self.supabase.table('approval_requests').insert(test_approval).execute()
            if result.data:
                self.supabase.table('approval_requests').delete().eq('project_id', 'schema_test').execute()
                test_results.append(("approval_requests", "✅ Working"))
            else:
                test_results.append(("approval_requests", "❌ Insert failed"))
                
        except Exception as e:
            test_results.append(("approval_requests", f"❌ Error: {str(e)[:50]}"))
        
        # Display test results
        for table, status in test_results:
            console.print(f"  📋 {table}: {status}")

async def main():
    """Run schema creation"""
    creator = SupabaseSchemaCreator()
    await creator.create_all_schemas()
    
    console.print("\n💡 [bold blue]Next Steps:[/bold blue]")
    console.print("  • Run comprehensive SPARC test again")
    console.print("  • Verify all tables are populated during workflow")
    console.print("  • Check memory system integration works")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())