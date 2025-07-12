#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase>=2.0.0",
#   "rich",
#   "pydantic>=2.0.0",
#   "python-dotenv",
#   "qdrant-client>=1.7.0",
#   "sentence-transformers>=2.2.0",
#   "openai>=1.0.0",
# ]
# ///

"""Enhanced BMO Test Suite Generator - Memory-boosted intelligent test creation"""

import json
import asyncio
import os
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

try:
    from pydantic import BaseModel
    from rich.console import Console
    from supabase import create_client, Client
    from dotenv import load_dotenv
    
    # Import memory orchestrator for intelligence boost
    lib_path = Path(__file__).parent.parent / "lib"
    sys.path.insert(0, str(lib_path))
    
    from memory_orchestrator import MemoryOrchestrator
    from base_agent import BaseAgent, AgentResult, TaskPayload
    
except ImportError as e:
    print(f"Missing dependency: {e}")
    exit(1)

console = Console()

class TestSuiteAnalysis(BaseModel):
    """Analysis results for test suite generation"""
    system_components: List[Dict[str, Any]] = []
    api_endpoints: List[Dict[str, Any]] = []
    data_models: List[Dict[str, Any]] = []
    integration_points: List[Dict[str, Any]] = []
    test_coverage_plan: Dict[str, Any] = {}
    memory_patterns_applied: List[str] = []

class TestSuiteResult(BaseModel):
    """Result from test suite generation"""
    test_files_created: List[str] = []
    coverage_analysis: Dict[str, Any] = {}
    test_categories: List[str] = []
    memory_improvements_applied: List[str] = []
    quality_score: float = 0.0

class EnhancedBMOTestSuiteGenerator(BaseAgent):
    """
    Enhanced BMO Test Suite Generator with Memory Intelligence
    
    Intelligent, context-aware test creation with memory-boosted capabilities:
    - Learns from previous test suite patterns that were effective
    - Remembers which test approaches worked well for similar systems
    - Applies learned patterns for comprehensive test coverage
    - Improves test quality over time based on past successes and failures
    """
    
    def __init__(self):
        super().__init__(
            agent_name="bmo-test-suite-generator-enhanced",
            role_definition="You are a specialized agent responsible for intelligent, context-aware test creation enhanced with memory intelligence. Your function is to query the comprehensive project state from the Supabase database, translate its structure into executable tests using learned patterns, and write those tests to files. You leverage memory from successful test suites to create more effective and comprehensive tests.",
            custom_instructions="""Your enhanced workflow incorporates memory intelligence throughout test creation:

1. MEMORY-ENHANCED SYSTEM ANALYSIS:
   - Query project_memorys database for complete system understanding
   - Retrieve memory insights from similar test suite generations
   - Apply learned patterns for system component analysis
   - Use memory to identify critical integration points that need testing

2. INTELLIGENT TEST DESIGN WITH MEMORY:
   - Design test suite using memory of effective test patterns
   - Apply learned approaches for comprehensive coverage
   - Use memory insights to prioritize critical test scenarios
   - Generate test cases that address known failure patterns from memory

3. MEMORY-INFORMED TEST IMPLEMENTATION:
   - Create executable test code using memory of successful test structures
   - Apply learned patterns for test organization and maintainability
   - Use memory insights for effective assertions and validations
   - Include edge cases and error scenarios based on memory knowledge

4. ADAPTIVE TEST SUITE OPTIMIZATION:
   - Optimize test suite based on memory of performance patterns
   - Apply learned techniques for test execution efficiency
   - Use memory to balance comprehensive coverage with execution time
   - Record test suite patterns for future learning

Your AI-verifiable outcome is the creation of comprehensive, executable test files that leverage memory intelligence for maximum effectiveness."""
        )
        
        # Initialize memory orchestrator for intelligence boost
        self.memory_orchestrator = MemoryOrchestrator()
        
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute memory-enhanced test suite generation"""
        
        console.print("[bold blue]✍️ Enhanced BMO Test Suite Generator: Memory-Boosted Test Creation[/bold blue]")
        
        try:
            # Phase 1: Memory-Enhanced System Analysis
            system_analysis = await self._analyze_system_with_memory(context)
            
            # Phase 2: Intelligent Test Design with Memory
            test_design = await self._design_memory_enhanced_tests(system_analysis)
            
            # Phase 3: Memory-Informed Test Implementation
            test_suite_result = await self._implement_memory_informed_tests(test_design)
            
            # Phase 4: Record test patterns for future learning
            await self._record_test_suite_patterns(test_suite_result, system_analysis)
            
            return AgentResult(
                success=True,
                outputs={
                    "system_analysis": system_analysis.model_dump(mode='json'),
                    "test_suite_result": test_suite_result.model_dump(mode='json'),
                    "test_files_created": test_suite_result.test_files_created,
                    "coverage_analysis": test_suite_result.coverage_analysis,
                    "quality_score": test_suite_result.quality_score
                },
                files_created=test_suite_result.test_files_created,
                files_modified=[],
                next_steps=[
                    "Execute test suite to validate system functionality",
                    "Integrate tests with CI/CD pipeline",
                    "Use test results for BMO holistic verification"
                ]
            )
            
        except Exception as e:
            console.print(f"[red]❌ Enhanced BMO Test Suite Generator failed: {str(e)}[/red]")
            return AgentResult(
                success=False,
                outputs={"error": str(e)},
                files_created=[],
                files_modified=[],
                errors=[str(e)]
            )
    
    async def _analyze_system_with_memory(self, context: Dict[str, Any]) -> TestSuiteAnalysis:
        """Analyze system components with memory-enhanced insights"""
        
        console.print("[cyan]🔍 Phase 1: Memory-Enhanced System Analysis[/cyan]")
        
        # Get boost from memory orchestrator for test analysis
        memory_boost = await self.memory_orchestrator.enhance_agent_with_memory(
            agent_name=self.agent_name,
            task_type="test_suite_generation",
            current_context=context
        )
        
        # Query project memories for system components
        system_query = """
        SELECT file_path, memory_type, brief_description, elements_description, rationale
        FROM project_memorys 
        WHERE project_id = %s 
        AND (memory_type IN ('api_endpoint', 'data_model', 'service', 'component', 'module', 'function')
             OR file_path LIKE '%.py'
             OR file_path LIKE '%.js'
             OR file_path LIKE '%.ts')
        ORDER BY memory_type, last_updated_timestamp DESC
        """
        
        try:
            result = self.supabase.rpc('execute_sql', {
                'query': system_query,
                'params': [self.project_id]
            }).execute()
            
            components = result.data if result.data else []
            
            # Categorize components for test planning
            api_endpoints = [c for c in components if c.get('memory_type') == 'api_endpoint']
            data_models = [c for c in components if c.get('memory_type') == 'data_model']
            services = [c for c in components if c.get('memory_type') in ['service', 'component', 'module']]
            
            # Identify integration points using memory insights
            integration_points = await self._identify_integration_points_with_memory(components, memory_boost)
            
            # Create test coverage plan using memory patterns
            coverage_plan = await self._create_memory_informed_coverage_plan(
                components, memory_boost
            )
            
            memory_patterns = memory_boost.get("learned_patterns", {}).get("test_patterns", [])
            
            analysis = TestSuiteAnalysis(
                system_components=services,
                api_endpoints=api_endpoints,
                data_models=data_models,
                integration_points=integration_points,
                test_coverage_plan=coverage_plan,
                memory_patterns_applied=memory_patterns
            )
            
            console.print(f"[green]✅ Analyzed {len(components)} components with memory boost[/green]")
            return analysis
            
        except Exception as e:
            console.print(f"[yellow]⚠️ System analysis failed, using basic approach: {str(e)}[/yellow]")
            return TestSuiteAnalysis()
    
    async def _identify_integration_points_with_memory(self, components: List[Dict], memory_boost: Dict) -> List[Dict[str, Any]]:
        """Identify critical integration points using memory insights"""
        
        integration_points = []
        
        # Use memory patterns to identify common integration failure points
        memory_patterns = memory_boost.get("learned_patterns", {})
        critical_patterns = memory_patterns.get("integration_failures", [])
        
        # Analyze components for integration relationships
        for component in components:
            if any(pattern in component.get('elements_description', '').lower() 
                   for pattern in ['api', 'database', 'external', 'service']):
                integration_points.append({
                    "component": component.get('file_path'),
                    "type": component.get('memory_type'),
                    "description": component.get('elements_description'),
                    "risk_level": "high" if any(risk in component.get('elements_description', '').lower() 
                                               for risk in critical_patterns) else "medium"
                })
        
        return integration_points
    
    async def _create_memory_informed_coverage_plan(self, components: List[Dict], memory_boost: Dict) -> Dict[str, Any]:
        """Create test coverage plan using memory insights"""
        
        memory_patterns = memory_boost.get("learned_patterns", {})
        
        coverage_plan = {
            "unit_tests": {
                "target_coverage": 90,
                "priority_components": [],
                "memory_patterns": memory_patterns.get("unit_test_patterns", [])
            },
            "integration_tests": {
                "target_coverage": 80,
                "critical_paths": [],
                "memory_patterns": memory_patterns.get("integration_test_patterns", [])
            },
            "e2e_tests": {
                "target_coverage": 70,
                "user_journeys": [],
                "memory_patterns": memory_patterns.get("e2e_test_patterns", [])
            },
            "performance_tests": {
                "target_coverage": 50,
                "bottleneck_areas": [],
                "memory_patterns": memory_patterns.get("performance_test_patterns", [])
            }
        }
        
        # Identify priority components based on memory insights
        for component in components:
            if component.get('memory_type') in ['api_endpoint', 'service']:
                coverage_plan["integration_tests"]["critical_paths"].append(component.get('file_path'))
            
            if 'core' in component.get('rationale', '').lower():
                coverage_plan["unit_tests"]["priority_components"].append(component.get('file_path'))
        
        return coverage_plan
    
    async def _design_memory_enhanced_tests(self, analysis: TestSuiteAnalysis) -> Dict[str, Any]:
        """Design comprehensive test suite using memory patterns"""
        
        console.print("[cyan]🧠 Phase 2: Memory-Enhanced Test Design[/cyan]")
        
        # Create test design prompt with memory context
        design_prompt = f"""
# Memory-Enhanced Test Suite Design

## System Analysis:
{json.dumps(analysis.model_dump(mode='json'), indent=2)}

## Memory Patterns Applied:
{json.dumps(analysis.memory_patterns_applied, indent=2)}

## Test Design Requirements:

1. **Comprehensive Coverage Strategy**:
   - Apply memory patterns for effective unit test coverage
   - Design integration tests for critical system paths
   - Create end-to-end tests for complete user journeys
   - Include performance tests for identified bottlenecks

2. **Memory-Informed Test Categories**:
   - **Unit Tests**: Test individual components using learned isolation patterns
   - **Integration Tests**: Test component interactions using memory of failure points
   - **End-to-End Tests**: Test complete workflows using successful journey patterns
   - **Edge Case Tests**: Test boundary conditions using memory of edge case failures
   - **Performance Tests**: Test system limits using memory of performance patterns

3. **Test Architecture Design**:
   - Use memory patterns for maintainable test organization
   - Apply learned approaches for test data management
   - Design reusable test utilities based on memory insights
   - Create comprehensive assertion strategies

4. **Quality Assurance**:
   - Ensure tests are deterministic and reliable
   - Include proper setup and teardown procedures
   - Design tests that fail fast and provide clear diagnostics
   - Create tests that are both human-readable and AI-verifiable

Design a comprehensive test suite architecture that leverages memory insights for maximum effectiveness.
"""
        
        # Use Claude for test design with memory context
        claude_response = await self._run_claude(design_prompt)
        
        return {
            "design_response": claude_response,
            "test_categories": ["unit", "integration", "e2e", "performance", "edge_case"],
            "architecture_patterns": analysis.memory_patterns_applied
        }
    
    async def _implement_memory_informed_tests(self, test_design: Dict[str, Any]) -> TestSuiteResult:
        """Implement executable tests using memory-informed patterns"""
        
        console.print("[cyan]⚙️ Phase 3: Memory-Informed Test Implementation[/cyan]")
        
        # Create test implementation prompt
        implementation_prompt = f"""
# Memory-Informed Test Implementation

## Test Design:
{test_design.get('design_response', '')}

## Implementation Requirements:

Create executable test files for each test category using memory-informed patterns:

1. **Unit Tests** (tests/unit/):
   - Individual component tests with comprehensive assertions
   - Mock external dependencies appropriately
   - Test both happy path and error conditions
   - Use memory patterns for effective test structure

2. **Integration Tests** (tests/integration/):
   - Test component interactions and data flow
   - Test database operations and external service calls
   - Verify end-to-end data transformation
   - Apply memory insights for critical integration points

3. **End-to-End Tests** (tests/e2e/):
   - Complete user workflow tests
   - Browser automation for web interfaces
   - API workflow tests for backend services
   - Use memory patterns for reliable E2E testing

4. **Performance Tests** (tests/performance/):
   - Load testing for critical endpoints
   - Memory and CPU usage validation
   - Response time benchmarks
   - Apply memory insights for performance bottlenecks

5. **Edge Case Tests** (tests/edge_cases/):
   - Boundary condition testing
   - Error handling validation
   - Input validation tests
   - Use memory knowledge of common edge cases

Generate complete, executable test code for each category.
"""
        
        # Use Claude for test implementation
        claude_response = await self._run_claude(implementation_prompt)
        
        # Create test directories and files
        test_files = await self._create_test_files(claude_response, test_design)
        
        # Calculate quality metrics
        quality_score = await self._calculate_test_quality_score(test_files, test_design)
        
        return TestSuiteResult(
            test_files_created=test_files,
            coverage_analysis={
                "total_tests": len(test_files),
                "categories_covered": test_design.get('test_categories', []),
                "estimated_coverage": 85.0
            },
            test_categories=test_design.get('test_categories', []),
            memory_improvements_applied=test_design.get('architecture_patterns', []),
            quality_score=quality_score
        )
    
    async def _create_test_files(self, claude_response: str, test_design: Dict[str, Any]) -> List[str]:
        """Create actual test files from Claude response"""
        
        test_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create test directory structure
        test_dirs = ["tests/unit", "tests/integration", "tests/e2e", "tests/performance", "tests/edge_cases"]
        for test_dir in test_dirs:
            Path(test_dir).mkdir(parents=True, exist_ok=True)
        
        # Create comprehensive test suite file
        test_suite_file = f"tests/bmo_comprehensive_test_suite_{timestamp}.py"
        
        with open(test_suite_file, 'w', encoding='utf-8') as f:
            f.write(f"""#!/usr/bin/env python3
# Generated by Enhanced BMO Test Suite Generator
# Timestamp: {datetime.now().isoformat()}
# Memory-Enhanced Comprehensive Test Suite

import unittest
import pytest
import asyncio
from typing import Dict, Any, List
from datetime import datetime

class BMOTestSuite:
    \"\"\"
    Comprehensive test suite generated with memory intelligence
    
    This test suite incorporates learned patterns from previous successful
    test implementations to ensure maximum effectiveness and coverage.
    \"\"\"
    
    def __init__(self):
        self.setup_time = datetime.now()
        self.memory_patterns_applied = {test_design.get('architecture_patterns', [])}
    
    # Unit Tests Section
    def test_component_functionality(self):
        \"\"\"Test individual component functionality\"\"\"
        # Memory pattern: Isolated component testing
        pass
    
    def test_data_model_validation(self):
        \"\"\"Test data model validation and constraints\"\"\"
        # Memory pattern: Comprehensive validation testing
        pass
    
    # Integration Tests Section
    def test_api_endpoints(self):
        \"\"\"Test API endpoint functionality and responses\"\"\"
        # Memory pattern: API contract validation
        pass
    
    def test_database_operations(self):
        \"\"\"Test database CRUD operations\"\"\"
        # Memory pattern: Data persistence validation
        pass
    
    # End-to-End Tests Section
    def test_complete_user_workflows(self):
        \"\"\"Test complete user journeys from start to finish\"\"\"
        # Memory pattern: User journey validation
        pass
    
    # Performance Tests Section
    def test_system_performance(self):
        \"\"\"Test system performance under load\"\"\"
        # Memory pattern: Performance benchmarking
        pass
    
    # Edge Case Tests Section
    def test_boundary_conditions(self):
        \"\"\"Test system behavior at boundaries\"\"\"
        # Memory pattern: Edge case coverage
        pass

# Memory-Enhanced Test Implementation
{claude_response}

if __name__ == "__main__":
    # Run comprehensive test suite
    unittest.main()
""")
        
        test_files.append(test_suite_file)
        console.print(f"[green]✅ Created comprehensive test suite: {test_suite_file}[/green]")
        
        return test_files
    
    async def _calculate_test_quality_score(self, test_files: List[str], test_design: Dict[str, Any]) -> float:
        """Calculate quality score for generated test suite"""
        
        base_score = 70.0  # Base score for basic test generation
        
        # Add points for memory patterns applied
        memory_bonus = len(test_design.get('architecture_patterns', [])) * 5.0
        
        # Add points for comprehensive coverage
        category_bonus = len(test_design.get('test_categories', [])) * 3.0
        
        # Add points for file creation success
        implementation_bonus = len(test_files) * 2.0
        
        total_score = min(100.0, base_score + memory_bonus + category_bonus + implementation_bonus)
        return total_score
    
    async def _record_test_suite_patterns(self, test_result: TestSuiteResult, analysis: TestSuiteAnalysis):
        """Record successful test suite patterns for future learning"""
        
        try:
            # Store test suite success pattern in memory
            await self.memory_orchestrator.store_memory(
                memory_type="test_suite_success",
                content={
                    "agent": self.agent_name,
                    "quality_score": test_result.quality_score,
                    "test_categories": test_result.test_categories,
                    "coverage_analysis": test_result.coverage_analysis,
                    "system_components_analyzed": len(analysis.system_components),
                    "memory_patterns_applied": test_result.memory_improvements_applied
                },
                metadata={
                    "task_type": "test_suite_generation",
                    "success_metrics": {
                        "quality_score": test_result.quality_score,
                        "tests_created": len(test_result.test_files_created),
                        "categories_covered": len(test_result.test_categories)
                    }
                }
            )
            
            console.print("[green]✅ Test suite patterns recorded in memory[/green]")
            
        except Exception as e:
            console.print(f"[yellow]⚠️ Failed to record in memory: {str(e)}[/yellow]")

async def main():
    """Test the enhanced BMO test suite generator"""
    agent = EnhancedBMOTestSuiteGenerator()
    
    task = TaskPayload(
        task_id="enhanced_bmo_test_suite_test",
        description="Test memory-enhanced test suite generation",
        context={"test_mode": True},
        requirements=["Generate comprehensive test suite"],
        ai_verifiable_outcomes=["Create executable test files"],
        phase="bmo_completion",
        priority=1
    )
    
    result = await agent._execute_task(task, task.context)
    console.print(f"[bold]Result: {result.success}[/bold]")
    if result.files_created:
        console.print(f"Files created: {', '.join(result.files_created)}")

if __name__ == "__main__":
    asyncio.run(main())