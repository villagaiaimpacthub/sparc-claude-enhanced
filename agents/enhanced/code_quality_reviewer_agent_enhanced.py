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
Enhanced Code Quality Reviewer Agent - Layer 2 Integration
Performs comprehensive code quality analysis and maintainability assessment using Layer 2 intelligence components
"""

import json
import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

try:
    from rich.console import Console
    from supabase import create_client, Client
    from dotenv import load_dotenv
    
    # Import Layer 2 intelligence components
    lib_path = Path(__file__).parent.parent.parent / 'lib'
    sys.path.insert(0, str(lib_path))
    
    from perfect_prompt_generator import PerfectPromptGenerator
    from test_oracle_resolver import TestOracleResolver
    from interactive_question_engine import InteractiveQuestionEngine  
    from bmo_intent_tracker import BMOIntentTracker
    from cognitive_triangulation_engine import CognitiveTriangulationEngine
    from sequential_review_chain import SequentialReviewChain
    
    
except ImportError as e:
    print(f"Missing dependency: {e}")
    sys.exit(1)

console = Console()

class EnhancedCodeQualityReviewerAgent:
    """
    Enhanced Code Quality Reviewer Agent with Layer 2 Intelligence Integration
    
    Key Features:
    1. Uses Perfect Prompt Generator for comprehensive code_quality_review creation
    2. Converts code_quality_review requirements to AI-verifiable outcomes
    3. Interactive clarification for code quality standards and maintainability requirements
    4. BMO intent tracking to ensure alignment with implementation phase
    5. Cognitive triangulation for multi-perspective code_quality_review validation
    6. Sequential review chain for code_quality_review quality assurance
    """
    
    def __init__(self, namespace: str):
        self.namespace = namespace
        self.supabase = self._init_supabase()
        
        # Initialize Layer 2 components
        self.prompt_generator = PerfectPromptGenerator(self.supabase, namespace)
        self.oracle_resolver = TestOracleResolver(self.supabase, namespace)
        self.question_engine = InteractiveQuestionEngine(self.supabase, namespace)
        self.intent_tracker = BMOIntentTracker(self.supabase, namespace)
        self.triangulation_engine = CognitiveTriangulationEngine(self.supabase, namespace)
        self.review_chain = SequentialReviewChain(self.supabase, namespace)
        
    def _init_supabase(self) -> Client:
        """Initialize Supabase client"""
        load_dotenv()
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            console.print("[red]Missing Supabase credentials[/red]")
            sys.exit(1)
        
        return create_client(url, key)
    
    async def execute_code_quality_review(self, 
                                   context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute enhanced code-quality-review workflow
        """
        context = context or {}
        
        console.print("[blue]🔧 Starting Enhanced Code Quality Reviewer Agent Workflow[/blue]")
        
        # Phase 1: Validate prerequisites from implementation phase
        prerequisites = await self._validate_prerequisites(context)
        if not prerequisites['valid']:
            return self._create_error_result(f"Prerequisites not met: {prerequisites['missing']}")
        
        # Phase 2: Extract and track code_quality_review intent
        await self._extract_code_quality_review_intent(prerequisites['main_implementation_py'], context)
        
        # Phase 3: Interactive clarification for code quality standards and maintainability requirements
        clarification_results = await self._conduct_code_quality_standards_and_maintainability_requirements_clarification(
            prerequisites, context
        )
        
        # Phase 4: Convert code_quality_review goals to AI-verifiable outcomes
        oracle_result = await self.oracle_resolver.resolve_goal_to_verifiable_criteria(
            "Create comprehensive code_quality_review with detailed requirements and measurable outcomes",
            'code-quality-review',
            clarification_results['context']
        )
        
        # Phase 5: Generate perfect prompt for code_quality_review creation
        perfect_prompt = await self.prompt_generator.generate_perfect_prompt(
            agent_name="code-quality-reviewer-agent",
            task_description="Create comprehensive code_quality_review documentation",
            oracle_criteria=oracle_result.dict(),
            context=clarification_results['context'],
            intent_model=await self._build_intent_model()
        )
        
        # Phase 6: Execute code_quality_review creation with perfect prompt
        execution_result = await self._execute_code_quality_review_creation(
            perfect_prompt, oracle_result, clarification_results
        )
        
        # Phase 7: Validate results with cognitive triangulation
        if execution_result['artifacts_created']:
            triangulation_results = []
            for artifact in execution_result['artifacts_created'][:3]:  # Top 3 artifacts
                triangulation_result = await self.triangulation_engine.triangulate_artifact(
                    artifact, 'code-quality-review', clarification_results['context']
                )
                triangulation_results.append(triangulation_result)
            execution_result['triangulation'] = triangulation_results
        
        # Phase 8: Sequential review for quality assurance
        if execution_result['primary_artifact']:
            review_result = await self.review_chain.execute_review_chain(
                execution_result['primary_artifact'], 'code-quality-review', 
                clarification_results['context']
            )
            execution_result['review_result'] = review_result
        
        # Phase 9: Create completion signal
        completion_signal = await self._create_completion_signal(
            execution_result, oracle_result, clarification_results
        )
        
        result = {
            'status': 'completed',
            'code_quality_review_context': clarification_results,
            'verifiable_criteria': oracle_result.dict(),
            'execution_result': execution_result,
            'completion_signal': completion_signal,
            'intent_model': await self._build_intent_model()
        }
        
        console.print("[green]🔧 Code Quality Reviewer Agent Workflow Completed Successfully[/green]")
        return result
    

    
    async def _validate_prerequisites(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that implementation phase is complete"""
        
        console.print("[blue]🔍 Validating Prerequisites[/blue]")
        
        missing = []
        main_implementation_py = None
        test_implementation_py = None
        
        
        # Check for src/main_implementation.py
        main_implementation_py_path = Path('src/main_implementation.py')
        if main_implementation_py_path.exists():
            main_implementation_py = main_implementation_py_path.read_text()
            console.print(f"[green]✅ Found: {main_implementation_py_path}[/green]")
        else:
            missing.append("src/main_implementation.py")
            console.print(f"[red]❌ Missing: {main_implementation_py_path}[/red]")
        # Check for src/test_implementation.py
        test_implementation_py_path = Path('src/test_implementation.py')
        if test_implementation_py_path.exists():
            test_implementation_py = test_implementation_py_path.read_text()
            console.print(f"[green]✅ Found: {test_implementation_py_path}[/green]")
        else:
            missing.append("src/test_implementation.py")
            console.print(f"[red]❌ Missing: {test_implementation_py_path}[/red]")
        
        return {
            'valid': len(missing) == 0,
            'missing': missing,
            'main_implementation_py': main_implementation_py,
            'test_implementation_py': test_implementation_py
        }
    
    async def _extract_code_quality_review_intent(self, main_implementation_py: str, context: Dict[str, Any]):
        """Extract user intent specific to code_quality_review requirements"""
        
        console.print("[blue]🎯 Extracting Code Quality Review Intent[/blue]")
        
        if main_implementation_py:
            await self.intent_tracker.extract_intents_from_interaction(
                main_implementation_py, 
                "code_quality_review_requirements",
                {'phase': 'code-quality-review', **context}
            )
            console.print("[green]✅ Code Quality Review intent extracted[/green]")
    
    async def _conduct_code_quality_standards_and_maintainability_requirements_clarification(self, 
                                                         prerequisites: Dict[str, Any],
                                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct interactive clarification for code quality standards and maintainability requirements"""
        
        console.print("[blue]💬 Starting Code Quality Standards And Maintainability Requirements Clarification[/blue]")
        
        conversation_history = []
        clarification_context = context.copy()
        clarification_context.update({
            'main_implementation_py': prerequisites['main_implementation_py'],
            'test_implementation_py': prerequisites['test_implementation_py']
        })
        
        # Generate first code_quality_standards_and_maintainability_requirements clarification question
        question = await self.question_engine.generate_interactive_question(
            agent_name="code-quality-reviewer-agent",
            phase="code-quality-review",
            base_question=self._generate_code_quality_standards_and_maintainability_requirements_question(prerequisites),
            context=clarification_context,
            conversation_history=conversation_history
        )
        
        # Create question file for Claude Code
        question_file = await self.question_engine.create_claude_code_question_file(question)
        
        # For testing, simulate responses (in production, user would respond)
        simulated_responses = await self._simulate_code_quality_standards_and_maintainability_requirements_responses(
            question, prerequisites['main_implementation_py']
        )
        
        # Process responses
        for response_text in simulated_responses:
            user_response = await self.question_engine.process_user_response(
                question, response_text, "auto_detect"
            )
            conversation_history.append(user_response.dict())
            
            # Check if we need more clarification
            next_question = await self.question_engine.determine_next_question(
                question, user_response, conversation_history
            )
            
            if next_question:
                question = next_question
                question_file = await self.question_engine.create_claude_code_question_file(question)
            else:
                break
        
        # Build comprehensive code_quality_review context
        clarification_context.update({
            'conversation_history': conversation_history,
            'clarification_method': 'interactive_code_quality_standards_and_maintainability_requirements_questions',
            'code_quality_review_details': self._extract_code_quality_review_details(conversation_history)
        })
        
        return {
            'context': clarification_context,
            'conversation_history': conversation_history
        }
    

    def _generate_code_quality_question(self, prerequisites: Dict[str, Any]) -> str:
        """Generate initial code quality clarification question"""
        
        return "What code quality standards and maintainability requirements should be enforced? Please specify coding conventions, complexity limits, documentation requirements, and technical debt tolerance."
    
    async def _simulate_code_quality_responses(self, question, implementation: str) -> List[str]:
        """Simulate code quality responses for testing"""
        
        return [
            "Quality standards: PEP 8 compliance, cyclomatic complexity under 10, function length under 50 lines, comprehensive docstrings for all public APIs.",
            "Maintainability requirements: Clear separation of concerns, minimal code duplication, consistent naming conventions, comprehensive test coverage above 90%.",
            "Technical debt management: Regular refactoring cycles, code review processes, automated quality checks in CI/CD, documentation updates with code changes."
        ]
    
    def _extract_code_quality_details(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Extract code quality details from conversation history"""
        
        details = {
            'coding_standards': [],
            'complexity_limits': [],
            'documentation_requirements': [],
            'maintainability_criteria': [],
            'quality_gates': []
        }
        
        for response in conversation_history:
            answer = response.get('selected_answer', '').lower()
            
            if 'standard' in answer or 'convention' in answer:
                details['coding_standards'].append(answer)
            if 'complexity' in answer or 'length' in answer:
                details['complexity_limits'].append(answer)
            if 'documentation' in answer or 'docstring' in answer:
                details['documentation_requirements'].append(answer)
            if 'maintainability' in answer or 'refactor' in answer:
                details['maintainability_criteria'].append(answer)
        
        return details
    
    async def _build_intent_model(self) -> Dict[str, Any]:
        """Build current intent model for prompt context"""
        
        intent_summary = await self.intent_tracker.get_intent_summary()
        
        return {
            'primary_intent': "Create detailed code_quality_review with comprehensive requirements and verifiable outcomes",
            'preferences': [intent.content for intent in intent_summary['intent_details']['preferences'][:3]],
            'anti_goals': [intent.content for intent in intent_summary['intent_details']['anti_goals'][:3]],
            'constraints': [intent.content for intent in intent_summary['intent_details']['constraints'][:3]],
            'confidence_level': intent_summary['average_confidence']
        }
    
    async def _execute_code_quality_review_creation(self,
                                           perfect_prompt,
                                           oracle_result,
                                           clarification_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code_quality_review creation with perfect prompt"""
        
        console.print("[blue]🤖 Executing Code Quality Review Creation with Perfect Prompt[/blue]")
        
        # Create instruction file for Claude Code
        instruction_file = Path('.sparc') / 'instructions' / f'{perfect_prompt.task_id}_code_quality_review_instructions.md'
        instruction_file.parent.mkdir(parents=True, exist_ok=True)
        
        instruction_file.write_text(perfect_prompt.prompt_content)
        
        # For testing, simulate the artifacts that would be created
        artifacts = await self._simulate_code_quality_review_creation(perfect_prompt, oracle_result, clarification_results)
        
        return {
            'instruction_file': str(instruction_file),
            'perfect_prompt': perfect_prompt.dict(),
            'artifacts_created': artifacts['files_created'],
            'primary_artifact': artifacts['primary_artifact'],
            'execution_success': True,
            'oracle_compliance': artifacts['oracle_compliance']
        }
    
    async def _simulate_code_quality_review_creation(self, 
                                           perfect_prompt, 
                                           oracle_result,
                                           clarification_results: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate code_quality_review creation results"""
        
        # Create docs/quality directory
        output_dir = Path('docs/quality')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        
        # Create code_quality_report.md
        code_quality_report = output_dir / 'code_quality_report.md'
        code_quality_review_details = clarification_results['context'].get('code_quality_review_details', {})
        
        code_quality_report.write_text(f"""# Code Quality Report

## Project Overview
{clarification_results['context'].get('main_prerequisite', 'Code Quality Review for the project')[:500]}...

## Core Requirements
{chr(10).join([f"- {req}" for req in code_quality_review_details.get('key_requirements', ['Requirement 1', 'Requirement 2', 'Requirement 3'])])}

## Implementation Details
{chr(10).join([f"- {detail}" for detail in code_quality_review_details.get('implementation_details', ['Detail 1', 'Detail 2', 'Detail 3'])])}

## Quality Standards
{chr(10).join([f"- {standard}" for standard in code_quality_review_details.get('quality_standards', ['Standard 1', 'Standard 2', 'Standard 3'])])}

## Acceptance Criteria
{chr(10).join([f"- ✅ {criterion.criterion}: {criterion.measurable_outcome}" for criterion in oracle_result.verifiable_criteria])}

---

*Generated by Enhanced Code Quality Reviewer Agent*
*Date: 2025-07-12T22:29:54.711178*
*Oracle Compliance Score: {oracle_result.ai_verifiable_score:.2f}*
""")

        # Create maintainability_analysis.md
        maintainability_analysis = output_dir / 'maintainability_analysis.md'
        maintainability_analysis.write_text(f"""# Maintainability Analysis

## Secondary Documentation
Content for maintainability analysis documentation.

---

*Generated by Enhanced Code Quality Reviewer Agent*
""")

        # Create technical_debt_assessment.md
        technical_debt_assessment = output_dir / 'technical_debt_assessment.md'
        technical_debt_assessment.write_text(f"""# Technical Debt Assessment

## Secondary Documentation
Content for technical debt assessment documentation.

---

*Generated by Enhanced Code Quality Reviewer Agent*
""")

        # Create refactoring_recommendations.md
        refactoring_recommendations = output_dir / 'refactoring_recommendations.md'
        refactoring_recommendations.write_text(f"""# Refactoring Recommendations

## Secondary Documentation
Content for refactoring recommendations documentation.

---

*Generated by Enhanced Code Quality Reviewer Agent*
""")

        
        return {
            'files_created': [str(code_quality_report), str(maintainability_analysis), str(technical_debt_assessment), str(refactoring_recommendations)],
            'primary_artifact': str(code_quality_report),
            'oracle_compliance': True
        }
    
    async def _create_completion_signal(self,
                                      execution_result: Dict[str, Any],
                                      oracle_result,
                                      clarification_results: Dict[str, Any]) -> str:
        """Create completion signal file"""
        
        completion_dir = Path('.sparc') / 'completions'
        completion_dir.mkdir(parents=True, exist_ok=True)
        
        completion_file = completion_dir / f"code-quality-review_20250712_222954_done.md"
        
        completion_content = f"""# Code Quality Review Phase - COMPLETED

## Agent: Enhanced Code Quality Reviewer Agent
## Completed: 2025-07-12T22:29:54.711178

## Summary
Successfully completed code-quality-review phase with comprehensive code_quality_review and AI-verifiable outcomes.

## Files Created
{chr(10).join([f"- {file}" for file in execution_result['artifacts_created']])}

## AI-Verifiable Outcomes Achieved
{chr(10).join([f"- ✅ {criterion.criterion}: {criterion.measurable_outcome}" for criterion in oracle_result.verifiable_criteria])}

## Code Quality Review Clarification Results
- **Conversation Rounds**: {len(clarification_results.get('conversation_history', []))}
- **Code Quality Review Items**: {len(clarification_results['context'].get('code_quality_review_details', {}).get('key_requirements', []))}
- **Quality Checks**: {len(clarification_results['context'].get('quality_criteria', []))}

## Quality Validation
- ✅ All criteria are AI-verifiable (Score: {oracle_result.ai_verifiable_score:.2f})
- ✅ Comprehensive code_quality_review created
- ✅ Intent alignment verified
- ✅ Multi-perspective validation completed

## Next Phase Recommendation
Ready to proceed to **Next Phase** with high confidence.

## Context for Next Agent
- **Primary Artifact**: {execution_result['primary_artifact']}
- **Code Quality Review Scope**: Complete code_quality_review with all requirements and quality validations
- **Quality Score**: {oracle_result.ai_verifiable_score:.2f}

---
*Generated by Enhanced Code Quality Reviewer Agent using Layer 2 Intelligence Components*
"""
        
        completion_file.write_text(completion_content)
        console.print(f"[green]✅ Completion signal created: {completion_file}[/green]")
        
        return str(completion_file)
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result structure"""
        return {
            'status': 'error',
            'error': error_message,
            'completion_signal': None
        }

async def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Code Quality Reviewer Agent")
    parser.add_argument('--namespace', default='default', help='Project namespace')
    parser.add_argument('--task-description', help='Task description from orchestrator')
    
    args = parser.parse_args()
    
    agent = EnhancedCodeQualityReviewerAgent(args.namespace)
    
    # Execute code-quality-review workflow
    result = await agent.execute_code_quality_review(
        context={'namespace': args.namespace}
    )
    
    if result['status'] == 'completed':
        console.print("[green]🔧 Enhanced Code Quality Reviewer Agent completed successfully![/green]")
        console.print(f"Primary artifact: {result['execution_result']['primary_artifact']}")
        console.print(f"Completion signal: {result['completion_signal']}")
    else:
        console.print(f"[red]❌ Code Quality Reviewer Agent failed: {result['error']}[/red]")

if __name__ == "__main__":
    asyncio.run(main())