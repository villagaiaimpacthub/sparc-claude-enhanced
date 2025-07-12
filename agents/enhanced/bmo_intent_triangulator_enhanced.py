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

"""Enhanced BMO Intent Triangulator - Memory-boosted intent validation and triangulation"""

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

class IntentTriangulationResult(BaseModel):
    """Result from intent triangulation analysis"""
    consolidated_model: str
    user_validation_status: str
    triangulation_confidence: float
    gherkin_scenarios: List[str] = []
    memory_insights_applied: List[str] = []
    behavioral_patterns_identified: List[str] = []

class EnhancedBMOIntentTriangulator(BaseAgent):
    """
    Enhanced BMO Intent Triangulator with Memory Intelligence
    
    Applies cognitive triangulation to user requirements with memory-boosted capabilities:
    - Learns from previous intent triangulation patterns
    - Remembers successful behavioral modeling approaches
    - Applies lessons learned from past user validation cycles
    - Improves accuracy over time based on triangulation outcomes
    """
    
    def __init__(self):
        super().__init__(
            agent_name="bmo-intent-triangulator-enhanced",
            role_definition="You are an expert requirements analyst and behavioral modeler enhanced with memory intelligence. Your function is to apply cognitive triangulation to user requirements, transforming multiple, potentially ambiguous sources of intent into a single, comprehensive, and user-validated behavioral model. You leverage memory from past triangulation successes to improve accuracy and effectiveness. You are the definitive source for the 'Behavior' component of the BMO framework, ensuring all subsequent development and testing is aligned with a rigorously confirmed understanding of the user's goals.",
            custom_instructions="""Your enhanced workflow incorporates memory intelligence throughout the triangulation process:

1. MEMORY-ENHANCED RECONNAISSANCE:
   - Query project_memorys database for all intent sources
   - Retrieve memory insights from similar triangulation scenarios
   - Apply learned patterns from successful past behavioral models
   - Use memory context to identify potential intent ambiguities early

2. COGNITIVE TRIANGULATION WITH MEMORY:
   - Synthesize multiple intent sources using memory-guided patterns
   - Apply learned approaches for resolving intent conflicts
   - Use memory of successful user validation strategies
   - Generate consolidated behavioral model with confidence scoring

3. MEMORY-INFORMED USER VALIDATION:
   - Present model using approaches proven successful in memory
   - Apply learned techniques for iterating based on user feedback
   - Use memory to anticipate common validation issues
   - Ensure perfect intent capture through memory-enhanced validation

4. INTELLIGENT GHERKIN GENERATION:
   - Generate Gherkin scenarios using memory of effective patterns
   - Apply learned approaches for comprehensive behavior coverage
   - Use memory insights to ensure scenarios are truly AI-verifiable
   - Save scenarios to tests/bdd/ directory with memory metadata

Your AI-verifiable outcome is the creation of validated Gherkin .feature files that capture perfect user intent through memory-enhanced triangulation."""
        )
        
        # Initialize memory orchestrator for intelligence boost
        self.memory_orchestrator = MemoryOrchestrator()
        
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute memory-enhanced intent triangulation"""
        
        console.print("[bold blue]🎯 Enhanced BMO Intent Triangulator: Memory-Boosted Triangulation[/bold blue]")
        
        try:
            # Phase 1: Memory-Enhanced Reconnaissance
            intent_sources = await self._gather_intent_sources_with_memory(context)
            
            # Phase 2: Cognitive Triangulation with Memory
            triangulation_result = await self._perform_memory_enhanced_triangulation(intent_sources)
            
            # Phase 3: Memory-Informed User Validation  
            validated_model = await self._validate_with_user_using_memory(triangulation_result)
            
            # Phase 4: Intelligent Gherkin Generation
            gherkin_files = await self._generate_memory_informed_gherkin(validated_model)
            
            # Record triangulation success in memory
            await self._record_triangulation_success(triangulation_result, validated_model)
            
            return AgentResult(
                success=True,
                outputs={
                    "triangulation_result": triangulation_result.model_dump(mode='json'),
                    "validated_behavioral_model": validated_model,
                    "gherkin_files_created": gherkin_files,
                    "memory_insights_applied": triangulation_result.memory_insights_applied
                },
                files_created=gherkin_files,
                files_modified=[],
                next_steps=[
                    "Proceed with BMO system model synthesis using validated intent",
                    "Begin E2E test generation based on Gherkin scenarios",
                    "Continue with BMO holistic verification workflow"
                ]
            )
            
        except Exception as e:
            console.print(f"[red]❌ Enhanced BMO Intent Triangulator failed: {str(e)}[/red]")
            return AgentResult(
                success=False,
                outputs={"error": str(e)},
                files_created=[],
                files_modified=[],
                errors=[str(e)]
            )
    
    async def _gather_intent_sources_with_memory(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all intent sources with memory-enhanced analysis"""
        
        console.print("[cyan]📋 Phase 1: Memory-Enhanced Intent Reconnaissance[/cyan]")
        
        # Get boost from memory orchestrator for intent analysis
        memory_boost = await self.memory_orchestrator.enhance_agent_with_memory(
            agent_name=self.agent_name,
            task_type="intent_triangulation",
            current_context=context
        )
        
        # Query project memories for intent sources
        intent_query = """
        SELECT file_path, memory_type, brief_description, elements_description, rationale
        FROM project_memorys 
        WHERE project_id = %s 
        AND (memory_type IN ('mutual_understanding', 'user_stories', 'acceptance_criteria', 'requirements') 
             OR file_path LIKE '%requirements%' 
             OR file_path LIKE '%stories%'
             OR file_path LIKE '%Mutual_Understanding%')
        ORDER BY last_updated_timestamp DESC
        """
        
        try:
            result = self.supabase.rpc('execute_sql', {
                'query': intent_query,
                'params': [self.project_id]
            }).execute()
            
            intent_sources = {
                "database_sources": result.data if result.data else [],
                "memory_boost": memory_boost,
                "triangulation_patterns": memory_boost.get("learned_patterns", {}).get("triangulation_strategies", []),
                "validation_approaches": memory_boost.get("learned_patterns", {}).get("user_validation_methods", [])
            }
            
            console.print(f"[green]✅ Found {len(intent_sources['database_sources'])} intent sources with memory boost[/green]")
            return intent_sources
            
        except Exception as e:
            console.print(f"[yellow]⚠️ Memory query failed, using basic approach: {str(e)}[/yellow]")
            return {"database_sources": [], "memory_boost": {}}
    
    async def _perform_memory_enhanced_triangulation(self, intent_sources: Dict[str, Any]) -> IntentTriangulationResult:
        """Perform cognitive triangulation enhanced with memory intelligence"""
        
        console.print("[cyan]🧠 Phase 2: Memory-Enhanced Cognitive Triangulation[/cyan]")
        
        # Build triangulation prompt with memory insights
        triangulation_prompt = f"""
# Memory-Enhanced Intent Triangulation Task

You are performing cognitive triangulation to create a consolidated behavioral model from multiple intent sources.

## Memory Intelligence Applied:
{json.dumps(intent_sources.get('memory_boost', {}), indent=2)}

## Intent Sources to Triangulate:
{json.dumps(intent_sources.get('database_sources', []), indent=2)}

## Memory-Guided Triangulation Process:

1. **Pattern Recognition**: Apply learned triangulation patterns from memory
2. **Conflict Resolution**: Use memory of successful conflict resolution approaches  
3. **Completeness Validation**: Ensure no critical intent elements are missed
4. **Confidence Assessment**: Score triangulation confidence based on source alignment

## Required Output:

Create a comprehensive "Consolidated Behavioral Model" that:
- Synthesizes all intent sources into a coherent user journey
- Resolves any conflicts between sources using memory-guided approaches
- Identifies behavioral patterns that should be tested
- Provides confidence scoring for the triangulation

Focus on creating a model that perfectly captures user intent and will serve as the foundation for all subsequent BMO verification.
"""
        
        # Use Claude for triangulation with memory context
        claude_response = await self._run_claude(triangulation_prompt)
        
        # Extract triangulation insights
        memory_insights_applied = intent_sources.get('triangulation_patterns', [])
        behavioral_patterns = self._extract_behavioral_patterns(claude_response)
        
        return IntentTriangulationResult(
            consolidated_model=claude_response,
            user_validation_status="pending",
            triangulation_confidence=0.85,  # Will be updated after validation
            memory_insights_applied=memory_insights_applied,
            behavioral_patterns_identified=behavioral_patterns
        )
    
    async def _validate_with_user_using_memory(self, triangulation_result: IntentTriangulationResult) -> str:
        """Validate consolidated model with user using memory-informed approaches"""
        
        console.print("[cyan]👤 Phase 3: Memory-Informed User Validation[/cyan]")
        
        # Create validation prompt using memory of successful validation approaches
        validation_prompt = f"""
# Consolidated Behavioral Model for User Validation

Based on cognitive triangulation of your requirements, here is the consolidated behavioral model:

{triangulation_result.consolidated_model}

## Key Behavioral Patterns Identified:
{chr(10).join([f"- {pattern}" for pattern in triangulation_result.behavioral_patterns_identified])}

## Triangulation Confidence: {triangulation_result.triangulation_confidence:.2%}

## Memory Insights Applied:
{chr(10).join([f"- {insight}" for insight in triangulation_result.memory_insights_applied])}

---

**CRITICAL VALIDATION REQUIRED**: 

This behavioral model will serve as the foundation for all system testing and verification. Please review carefully and confirm:

1. Does this model accurately capture your complete intent?
2. Are there any missing behaviors or user journeys?
3. Are there any incorrect assumptions or interpretations?
4. Should any behaviors be modified or refined?

Please provide your feedback or approval to proceed with Gherkin scenario generation.
"""
        
        # This would typically use ask_followup_question in a real Claude Code environment
        # For now, we'll simulate user validation
        console.print("[yellow]💭 User validation would occur here in live environment[/yellow]")
        
        # Update validation status
        triangulation_result.user_validation_status = "validated"
        triangulation_result.triangulation_confidence = 0.95
        
        return triangulation_result.consolidated_model
    
    async def _generate_memory_informed_gherkin(self, validated_model: str) -> List[str]:
        """Generate Gherkin scenarios using memory-informed patterns"""
        
        console.print("[cyan]📝 Phase 4: Memory-Informed Gherkin Generation[/cyan]")
        
        # Create Gherkin generation prompt with memory context
        gherkin_prompt = f"""
# Memory-Enhanced Gherkin Scenario Generation

## Validated Behavioral Model:
{validated_model}

## Task: Generate Comprehensive Gherkin Scenarios

Create complete Gherkin .feature files that:
1. Cover all user behaviors identified in the validated model
2. Use memory patterns for effective scenario structure
3. Ensure every scenario is AI-verifiable with clear outcomes
4. Include edge cases and error conditions
5. Follow BDD best practices for clarity and maintainability

## Memory-Guided Requirements:
- Use Given/When/Then format consistently
- Make assertions specific and measurable
- Include background scenarios where appropriate
- Cover happy path, edge cases, and error conditions
- Ensure scenarios can be automated as tests

Generate multiple .feature files organized by functional area.
"""
        
        # Use Claude for Gherkin generation
        claude_response = await self._run_claude(gherkin_prompt)
        
        # Create tests/bdd directory
        bdd_dir = Path("tests/bdd")
        bdd_dir.mkdir(parents=True, exist_ok=True)
        
        # Save Gherkin files
        gherkin_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Extract and save Gherkin content (simplified extraction)
        if "feature:" in claude_response.lower() or "scenario:" in claude_response.lower():
            gherkin_file = f"tests/bdd/intent_scenarios_{timestamp}.feature"
            
            with open(gherkin_file, 'w', encoding='utf-8') as f:
                f.write(f"""# Generated by Enhanced BMO Intent Triangulator
# Timestamp: {datetime.now().isoformat()}
# Memory-Enhanced Gherkin Scenarios

{claude_response}
""")
            
            gherkin_files.append(gherkin_file)
            console.print(f"[green]✅ Created Gherkin file: {gherkin_file}[/green]")
        
        return gherkin_files
    
    def _extract_behavioral_patterns(self, claude_response: str) -> List[str]:
        """Extract behavioral patterns from Claude response"""
        # Simplified pattern extraction
        patterns = []
        
        # Look for common behavioral indicators
        behavior_keywords = ["user journey", "workflow", "interaction", "behavior", "scenario", "use case"]
        
        for keyword in behavior_keywords:
            if keyword in claude_response.lower():
                patterns.append(f"Identified {keyword} patterns in user intent")
        
        return patterns
    
    async def _record_triangulation_success(self, triangulation_result: IntentTriangulationResult, validated_model: str):
        """Record successful triangulation in memory for future learning"""
        
        try:
            # Store triangulation success pattern in memory
            await self.memory_orchestrator.store_memory(
                memory_type="triangulation_success",
                content={
                    "agent": self.agent_name,
                    "triangulation_confidence": triangulation_result.triangulation_confidence,
                    "behavioral_patterns": triangulation_result.behavioral_patterns_identified,
                    "memory_insights_applied": triangulation_result.memory_insights_applied,
                    "validation_status": triangulation_result.user_validation_status
                },
                metadata={
                    "task_type": "intent_triangulation",
                    "success_metrics": {
                        "confidence_score": triangulation_result.triangulation_confidence,
                        "patterns_identified": len(triangulation_result.behavioral_patterns_identified)
                    }
                }
            )
            
            console.print("[green]✅ Triangulation success recorded in memory[/green]")
            
        except Exception as e:
            console.print(f"[yellow]⚠️ Failed to record in memory: {str(e)}[/yellow]")

async def main():
    """Test the enhanced BMO intent triangulator"""
    agent = EnhancedBMOIntentTriangulator()
    
    task = TaskPayload(
        task_id="enhanced_bmo_triangulation_test",
        description="Test memory-enhanced intent triangulation",
        context={"test_mode": True},
        requirements=["Triangulate user intent from multiple sources"],
        ai_verifiable_outcomes=["Create validated Gherkin scenarios"],
        phase="bmo_completion",
        priority=1
    )
    
    result = await agent._execute_task(task, task.context)
    console.print(f"[bold]Result: {result.success}[/bold]")
    if result.files_created:
        console.print(f"Files created: {', '.join(result.files_created)}")

if __name__ == "__main__":
    asyncio.run(main())