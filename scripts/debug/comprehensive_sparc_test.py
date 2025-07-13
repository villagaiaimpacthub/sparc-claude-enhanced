#!/usr/bin/env python3
"""
Comprehensive SPARC System Test
Run a complete workflow and monitor database activity
"""

import asyncio
import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

# Add lib to path
lib_path = Path(__file__).parent / "lib"
sys.path.insert(0, str(lib_path))

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, TaskID
from supabase import create_client, Client

load_dotenv()
console = Console()

class SPARCSystemTester:
    """Comprehensive SPARC system testing"""
    
    def __init__(self):
        self.supabase = self._init_supabase()
        self.test_namespace = f"test_sparc_{int(time.time())}"
        
    def _init_supabase(self) -> Client:
        """Initialize Supabase client"""
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            console.print("[red]❌ Missing Supabase credentials[/red]")
            exit(1)
            
        return create_client(url, key)
    
    async def run_comprehensive_test(self):
        """Run complete SPARC workflow test"""
        console.print("🚀 [bold blue]Comprehensive SPARC System Test[/bold blue]")
        console.print(f"🎯 Test namespace: {self.test_namespace}")
        
        # Phase 1: Initialize test project
        console.print("\n📋 [bold]Phase 1: Project Initialization[/bold]")
        await self._test_project_initialization()
        
        # Phase 2: Test goal clarification orchestrator directly
        console.print("\n🎯 [bold]Phase 2: Goal Clarification Agent[/bold]")
        await self._test_goal_clarification()
        
        # Phase 3: Monitor database activity
        console.print("\n📊 [bold]Phase 3: Database Activity Monitoring[/bold]")
        await self._monitor_database_activity()
        
        # Phase 4: Test individual agent execution
        console.print("\n🤖 [bold]Phase 4: Individual Agent Test[/bold]")
        await self._test_individual_agent()
        
        # Phase 5: Check memory system integration
        console.print("\n🧠 [bold]Phase 5: Memory System Integration[/bold]")
        await self._test_memory_integration()
        
        console.print("\n✅ [bold green]Comprehensive test completed![/bold green]")
    
    async def _test_project_initialization(self):
        """Test project initialization"""
        try:
            # Record baseline database state
            baseline = await self._get_database_state()
            console.print(f"📊 Baseline: {sum(baseline.values())} total records")
            
            # Initialize new project using orchestrator
            init_cmd = [
                'uv', 'run', 'orchestrator.py', 
                '--goal', 'Build a simple task management web app with user authentication',
                '--namespace', self.test_namespace
            ]
            
            console.print(f"🔧 Running: {' '.join(init_cmd)}")
            result = subprocess.run(init_cmd, capture_output=True, text=True, cwd=Path.cwd())
            
            if result.returncode == 0:
                console.print("✅ Project initialization successful")
                console.print(f"Output: {result.stdout[:200]}...")
            else:
                console.print(f"❌ Project initialization failed: {result.stderr}")
            
            # Check database changes
            new_state = await self._get_database_state()
            console.print(f"📊 After init: {sum(new_state.values())} total records")
            
            for table, count in new_state.items():
                if count > baseline.get(table, 0):
                    delta = count - baseline.get(table, 0)
                    console.print(f"  📈 {table}: +{delta} records")
                    
        except Exception as e:
            console.print(f"❌ Initialization test failed: {e}")
    
    async def _test_goal_clarification(self):
        """Test goal clarification orchestrator directly"""
        try:
            console.print("🎯 Testing goal clarification orchestrator...")
            
            # Run goal clarification agent directly
            agent_script = Path("agents/orchestrators/goal_clarification.py")
            if agent_script.exists():
                cmd = [
                    'uv', 'run', str(agent_script),
                    '--namespace', self.test_namespace,
                    '--goal', 'Build a simple task management web app'
                ]
                
                console.print(f"🔧 Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    console.print("✅ Goal clarification agent executed successfully")
                    console.print(f"Output: {result.stdout[-300:]}")
                else:
                    console.print(f"❌ Goal clarification failed: {result.stderr}")
            else:
                console.print(f"❌ Goal clarification agent not found: {agent_script}")
                
        except subprocess.TimeoutExpired:
            console.print("⏰ Goal clarification timed out after 60 seconds")
        except Exception as e:
            console.print(f"❌ Goal clarification test failed: {e}")
    
    async def _test_individual_agent(self):
        """Test a simple individual agent"""
        try:
            console.print("🤖 Testing individual agent execution...")
            
            # Try a simple research agent
            research_agent = Path("agents/researchers/research_planner_strategic.py")
            if research_agent.exists():
                cmd = [
                    'uv', 'run', str(research_agent),
                    '--namespace', self.test_namespace
                ]
                
                console.print(f"🔧 Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    console.print("✅ Individual agent executed successfully")
                    console.print(f"Output: {result.stdout[-200:]}")
                else:
                    console.print(f"❌ Individual agent failed: {result.stderr}")
            else:
                console.print(f"❌ Research agent not found: {research_agent}")
                
        except subprocess.TimeoutExpired:
            console.print("⏰ Individual agent timed out after 60 seconds")
        except Exception as e:
            console.print(f"❌ Individual agent test failed: {e}")
    
    async def _test_memory_integration(self):
        """Test memory system integration"""
        try:
            console.print("🧠 Testing memory system integration...")
            
            # Test storing a memory
            test_memory = {
                'namespace': self.test_namespace,
                'memory_type': 'test_pattern',
                'content': 'This is a test memory for comprehensive testing',
                'metadata': {'test': True, 'timestamp': datetime.now().isoformat()},
                'quality_score': 0.9,
                'created_at': datetime.now().isoformat()
            }
            
            # Try to insert into project_memorys if it exists
            try:
                memory_result = self.supabase.table('project_memorys').insert(test_memory).execute()
                if memory_result.data:
                    console.print("✅ Memory storage test successful")
                else:
                    console.print("❌ Memory storage returned no data")
            except Exception as e:
                console.print(f"⚠️  Memory storage test failed: {e}")
            
            # Test Mistral + Qdrant integration
            try:
                from mistral_embeddings import MistralEmbeddings
                from qdrant_client import QdrantClient
                from qdrant_client.http import models
                
                mistral = MistralEmbeddings()
                qdrant = QdrantClient(
                    host=os.getenv('QDRANT_HOST', 'localhost'),
                    port=int(os.getenv('QDRANT_PORT', '6336'))
                )
                
                # Test embedding + storage
                test_content = f"Comprehensive test memory for {self.test_namespace}"
                embedding = await mistral.get_embedding(test_content)
                
                test_point = models.PointStruct(
                    id=int(time.time()),  # Unique test ID
                    vector=embedding,
                    payload={
                        "namespace": self.test_namespace,
                        "content": test_content,
                        "test_type": "comprehensive_test"
                    }
                )
                
                qdrant.upsert(
                    collection_name="agent_memories",
                    points=[test_point]
                )
                
                console.print("✅ Mistral + Qdrant integration successful")
                
            except Exception as e:
                console.print(f"❌ Memory integration test failed: {e}")
                
        except Exception as e:
            console.print(f"❌ Memory integration test failed: {e}")
    
    async def _monitor_database_activity(self):
        """Monitor database activity during test"""
        try:
            console.print("📊 Monitoring database activity...")
            
            # Get current state
            current_state = await self._get_database_state()
            
            # Check for recent activity in agent_tasks
            recent_tasks = self.supabase.table('agent_tasks').select("*").eq(
                'namespace', self.test_namespace
            ).execute()
            
            console.print(f"📋 Found {len(recent_tasks.data)} tasks for test namespace")
            
            for task in recent_tasks.data[:3]:  # Show first 3
                console.print(f"  • {task.get('from_agent', 'unknown')} → {task.get('to_agent', 'unknown')}: {task.get('status', 'unknown')}")
            
            # Check agent executions
            executions = self.supabase.table('agent_executions').select("*").eq(
                'namespace', self.test_namespace
            ).execute()
            
            console.print(f"🤖 Found {len(executions.data)} agent executions for test namespace")
            
        except Exception as e:
            console.print(f"❌ Database monitoring failed: {e}")
    
    async def _get_database_state(self) -> dict:
        """Get current state of all tables"""
        state = {}
        
        tables = ['agent_tasks', 'sparc_contexts', 'agent_executions', 'project_memorys', 'sparc_file_changes']
        
        for table in tables:
            try:
                result = self.supabase.table(table).select("*", count="exact").execute()
                state[table] = result.count if hasattr(result, 'count') else len(result.data)
            except:
                state[table] = 0
        
        return state

async def main():
    """Run comprehensive test"""
    tester = SPARCSystemTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())