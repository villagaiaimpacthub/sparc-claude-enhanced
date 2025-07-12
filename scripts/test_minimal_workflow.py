#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase>=2.0.0",
#   "rich>=13.0.0",
#   "pydantic>=2.0.0",
#   "python-dotenv>=1.0.0",
# ]
# ///

"""
Minimal SPARC Workflow Test - No Database Required
Tests the core logic without database dependencies
"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from unittest.mock import Mock, AsyncMock

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from dotenv import load_dotenv
    
    # Import Layer 2 components
    lib_path = Path(__file__).parent.parent / 'lib'
    sys.path.insert(0, str(lib_path))
    
    from test_oracle_resolver import TestOracleResolver, VerifiableCriteria
    from bmo_intent_tracker import BMOIntentTracker, Intent, IntentType, IntentSource
    from perfect_prompt_generator import PerfectPromptGenerator
    from interactive_question_engine import InteractiveQuestionEngine
    
except ImportError as e:
    print(f"Missing dependency: {e}")
    sys.exit(1)

console = Console()

class MockSupabase:
    """Mock Supabase client for testing without database"""
    
    def __init__(self):
        self.last_table = None
        self.last_operation = None
        self.last_data = None
    
    def table(self, table_name: str):
        self.last_table = table_name
        return self
    
    def insert(self, data: dict):
        self.last_operation = 'insert'
        self.last_data = data
        return self
    
    def update(self, data: dict):
        self.last_operation = 'update'
        self.last_data = data
        return self
    
    def select(self, columns: str = '*'):
        self.last_operation = 'select'
        return self
    
    def eq(self, column: str, value: Any):
        return self
    
    def limit(self, count: int):
        return self
    
    def execute(self):
        # Return mock successful result
        mock_result = Mock()
        mock_result.data = []
        return mock_result
    
    def rpc(self, function_name: str, params: dict = None):
        return self

class MinimalWorkflowTester:
    """Test SPARC workflow without database dependencies"""
    
    def __init__(self):
        self.supabase = MockSupabase()
        self.namespace = "test"
        
        # Initialize components with mock supabase
        self.oracle_resolver = TestOracleResolver(self.supabase, self.namespace)
        self.intent_tracker = BMOIntentTracker(self.supabase, self.namespace)
        self.prompt_generator = PerfectPromptGenerator(self.supabase, self.namespace)
        self.question_engine = InteractiveQuestionEngine(self.supabase, self.namespace)
    
    async def test_oracle_resolver(self) -> bool:
        """Test oracle resolver functionality"""
        
        console.print("[blue]🔍 Testing Oracle Resolver...[/blue]")
        
        try:
            # Test goal to verifiable criteria conversion
            result = await self.oracle_resolver.resolve_goal_to_verifiable_criteria(
                goal="Build a REST API for user management",
                phase="implementation",
                context={"features": ["authentication", "CRUD operations"]}
            )
            
            console.print(f"[green]✅ Oracle resolved {len(result.verifiable_criteria)} criteria[/green]")
            
            # Display criteria
            for i, criterion in enumerate(result.verifiable_criteria, 1):
                console.print(f"  {i}. {criterion.criterion}")
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Oracle resolver failed: {e}[/red]")
            return False
    
    async def test_intent_tracker(self) -> bool:
        """Test intent tracking functionality"""
        
        console.print("[blue]🎯 Testing Intent Tracker...[/blue]")
        
        try:
            # Extract intents from user goal
            intents = await self.intent_tracker.extract_intents_from_interaction(
                interaction_content="Build a REST API for user management with authentication",
                interaction_type="goal_statement",
                context={"phase": "goal_clarification"}
            )
            
            console.print(f"[green]✅ Extracted {len(intents)} intents[/green]")
            
            # Display intents
            for intent in intents:
                intent_type_display = intent.intent_type.value if hasattr(intent.intent_type, 'value') else intent.intent_type
                console.print(f"  • {intent_type_display}: {intent.content}")
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Intent tracker failed: {e}[/red]")
            return False
    
    async def test_prompt_generator(self) -> bool:
        """Test perfect prompt generation"""
        
        console.print("[blue]🚀 Testing Prompt Generator...[/blue]")
        
        try:
            # Create mock oracle criteria
            mock_criteria = [
                VerifiableCriteria(
                    criterion="API endpoints respond with correct status codes",
                    verification_method="Test HTTP responses",
                    success_example="GET /users returns 200 OK",
                    failure_example="GET /users returns 500 error",
                    measurable_outcome="All endpoints return appropriate status codes"
                )
            ]
            
            # Generate perfect prompt
            prompt = await self.prompt_generator.generate_perfect_prompt(
                agent_name="implementation-agent",
                task_description="Create REST API implementation",
                oracle_criteria={"verifiable_criteria": [c.model_dump() for c in mock_criteria]},
                context={"goal": "Build REST API"},
                intent_model={"primary_intent": "Build working API"}
            )
            
            console.print(f"[green]✅ Generated prompt (length: {len(prompt.prompt_content)})[/green]")
            console.print(f"  Task ID: {prompt.task_id}")
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Prompt generator failed: {e}[/red]")
            return False
    
    async def test_question_engine(self) -> bool:
        """Test interactive question generation"""
        
        console.print("[blue]💬 Testing Question Engine...[/blue]")
        
        try:
            # Generate interactive question
            question = await self.question_engine.generate_interactive_question(
                agent_name="goal-clarification-agent",
                phase="goal_clarification",
                base_question="What type of API do you want to build?",
                context={"goal": "Build REST API"},
                conversation_history=[]
            )
            
            console.print(f"[green]✅ Generated question with {len(question.suggested_answers)} options[/green]")
            console.print(f"  Question: {question.question_text[:100]}...")
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Question engine failed: {e}[/red]")
            return False
    
    async def run_comprehensive_test(self):
        """Run comprehensive workflow test"""
        
        console.print(Panel.fit(
            "[bold blue]🧪 SPARC Minimal Workflow Test[/bold blue]\n\n"
            "Testing Layer 2 intelligence components without database:\n"
            "• Oracle Resolver (goals → verifiable criteria)\n"
            "• Intent Tracker (extract user intentions)\n"
            "• Perfect Prompt Generator (create optimized prompts)\n"
            "• Interactive Question Engine (clarification workflows)",
            title="Workflow Test"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            test_task = progress.add_task("Running tests...", total=4)
            
            results = []
            
            # Test each component
            progress.update(test_task, description="Testing Oracle Resolver...")
            results.append(await self.test_oracle_resolver())
            progress.advance(test_task)
            
            progress.update(test_task, description="Testing Intent Tracker...")
            results.append(await self.test_intent_tracker())
            progress.advance(test_task)
            
            progress.update(test_task, description="Testing Prompt Generator...")
            results.append(await self.test_prompt_generator())
            progress.advance(test_task)
            
            progress.update(test_task, description="Testing Question Engine...")
            results.append(await self.test_question_engine())
            progress.advance(test_task)
        
        # Results summary
        passed = sum(results)
        total = len(results)
        
        if passed == total:
            console.print(Panel.fit(
                f"[bold green]🎉 All Tests Passed! ({passed}/{total})[/bold green]\n\n"
                "Core SPARC workflow logic is working correctly.\n"
                "Ready to proceed with database setup and full integration.",
                title="Success"
            ))
        else:
            console.print(Panel.fit(
                f"[bold red]❌ Some Tests Failed ({passed}/{total})[/bold red]\n\n"
                "Core logic issues need to be resolved before database integration.",
                title="Issues Found"
            ))
        
        return passed == total

async def main():
    """Main test execution"""
    
    try:
        tester = MinimalWorkflowTester()
        success = await tester.run_comprehensive_test()
        
        if success:
            console.print("\n[bold green]Next Steps:[/bold green]")
            console.print("1. Run database setup: `uv run scripts/init_database.py`")
            console.print("2. Test full workflow: `uv run sparc_orchestrator_minimal.py --goal 'Build an API'`")
        else:
            console.print("\n[bold red]Fix the failing tests before proceeding.[/bold red]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Test cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Test failed with error: {e}[/red]")

if __name__ == "__main__":
    asyncio.run(main())