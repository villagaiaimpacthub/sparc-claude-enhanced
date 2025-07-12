#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "rich>=13.0.0",
# ]
# ///

"""
Generate Quality Review Agents
Batch generates additional quality review agents using template system
"""

import sys
from pathlib import Path

# Add lib path for imports
lib_path = Path(__file__).parent.parent / 'lib'
sys.path.insert(0, str(lib_path))

from agent_transformation_template import (
    AgentTransformationGenerator, AgentTemplate, AgentCategory, create_agent_generator
)
from rich.console import Console
from rich.panel import Panel

console = Console()

def create_quality_review_templates():
    """Create templates for quality review agents"""
    
    templates = [
        # Performance Review Agent
        AgentTemplate(
            agent_name="performance-reviewer-agent",
            category=AgentCategory.PERFORMANCE_AGENT,
            phase="performance-review",
            description="Performs comprehensive performance analysis and optimization recommendations using Layer 2 intelligence components",
            prerequisite_documents=[
                "src/main_implementation.py",
                "tests/performance_tests.py",
                "docs/architecture/system_architecture.md"
            ],
            prerequisite_phase="implementation phase",
            primary_task="Performance Review",
            clarification_focus="performance requirements and optimization targets",
            implementation_logic="Analyze implementation for performance bottlenecks and provide optimization strategies",
            output_directory="docs/performance",
            primary_artifact="performance_analysis_report.md",
            secondary_artifacts=["optimization_recommendations.md", "performance_benchmarks.md", "load_testing_results.md"],
            phase_specific_logic="""
    def _generate_performance_question(self, prerequisites: Dict[str, Any]) -> str:
        \"\"\"Generate initial performance clarification question\"\"\"
        
        return "What performance targets and optimization priorities should be evaluated? Please specify response time requirements, throughput targets, resource utilization limits, and scalability expectations."
    
    async def _simulate_performance_responses(self, question, implementation: str) -> List[str]:
        \"\"\"Simulate performance responses for testing\"\"\"
        
        return [
            "Performance targets: Sub-200ms API response times, 1000+ concurrent users, 99.9% uptime, efficient memory usage under 512MB per instance.",
            "Optimization priorities: Database query optimization, caching implementation, connection pooling, asynchronous processing for heavy operations.",
            "Scalability requirements: Horizontal scaling capability, load balancer compatibility, stateless design, efficient resource cleanup."
        ]
    
    def _extract_performance_details(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        \"\"\"Extract performance details from conversation history\"\"\"
        
        details = {
            'response_time_targets': [],
            'throughput_requirements': [],
            'resource_constraints': [],
            'scalability_expectations': [],
            'optimization_areas': []
        }
        
        for response in conversation_history:
            answer = response.get('selected_answer', '').lower()
            
            if 'response time' in answer or 'latency' in answer:
                details['response_time_targets'].append(answer)
            if 'throughput' in answer or 'concurrent' in answer:
                details['throughput_requirements'].append(answer)
            if 'memory' in answer or 'resource' in answer:
                details['resource_constraints'].append(answer)
            if 'scaling' in answer or 'scalability' in answer:
                details['scalability_expectations'].append(answer)
        
        return details"""
        ),
        
        # Code Quality Reviewer Agent
        AgentTemplate(
            agent_name="code-quality-reviewer-agent",
            category=AgentCategory.QUALITY_REVIEWER,
            phase="code-quality-review",
            description="Performs comprehensive code quality analysis and maintainability assessment using Layer 2 intelligence components",
            prerequisite_documents=[
                "src/main_implementation.py",
                "src/test_implementation.py"
            ],
            prerequisite_phase="implementation phase",
            primary_task="Code Quality Review",
            clarification_focus="code quality standards and maintainability requirements",
            implementation_logic="Analyze code for quality issues, maintainability, and adherence to best practices",
            output_directory="docs/quality",
            primary_artifact="code_quality_report.md",
            secondary_artifacts=["maintainability_analysis.md", "technical_debt_assessment.md", "refactoring_recommendations.md"],
            phase_specific_logic="""
    def _generate_code_quality_question(self, prerequisites: Dict[str, Any]) -> str:
        \"\"\"Generate initial code quality clarification question\"\"\"
        
        return "What code quality standards and maintainability requirements should be enforced? Please specify coding conventions, complexity limits, documentation requirements, and technical debt tolerance."
    
    async def _simulate_code_quality_responses(self, question, implementation: str) -> List[str]:
        \"\"\"Simulate code quality responses for testing\"\"\"
        
        return [
            "Quality standards: PEP 8 compliance, cyclomatic complexity under 10, function length under 50 lines, comprehensive docstrings for all public APIs.",
            "Maintainability requirements: Clear separation of concerns, minimal code duplication, consistent naming conventions, comprehensive test coverage above 90%.",
            "Technical debt management: Regular refactoring cycles, code review processes, automated quality checks in CI/CD, documentation updates with code changes."
        ]
    
    def _extract_code_quality_details(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        \"\"\"Extract code quality details from conversation history\"\"\"
        
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
        
        return details"""
        ),
        
        # Architecture Review Agent
        AgentTemplate(
            agent_name="architecture-reviewer-agent",
            category=AgentCategory.QUALITY_REVIEWER,
            phase="architecture-review",
            description="Performs comprehensive architectural analysis and design validation using Layer 2 intelligence components",
            prerequisite_documents=[
                "docs/architecture/system_architecture.md",
                "src/main_implementation.py"
            ],
            prerequisite_phase="implementation phase",
            primary_task="Architecture Review",
            clarification_focus="architectural quality and design principles",
            implementation_logic="Analyze architecture for design patterns, scalability, and adherence to principles",
            output_directory="docs/architecture_review",
            primary_artifact="architecture_review_report.md",
            secondary_artifacts=["design_pattern_analysis.md", "scalability_assessment.md", "architecture_recommendations.md"],
            phase_specific_logic="""
    def _generate_architecture_question(self, prerequisites: Dict[str, Any]) -> str:
        \"\"\"Generate initial architecture clarification question\"\"\"
        
        return "What architectural principles and design standards should be evaluated? Please specify design patterns, SOLID principles adherence, separation of concerns, and scalability requirements."
    
    async def _simulate_architecture_responses(self, question, architecture: str) -> List[str]:
        \"\"\"Simulate architecture responses for testing\"\"\"
        
        return [
            "Design principles: SOLID principles compliance, clean architecture patterns, dependency injection, clear layer separation between presentation, business, and data layers.",
            "Scalability requirements: Microservices compatibility, event-driven architecture support, horizontal scaling capability, database sharding readiness.",
            "Quality standards: Low coupling, high cohesion, consistent API design, proper error handling patterns, configuration management separation."
        ]
    
    def _extract_architecture_details(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        \"\"\"Extract architecture details from conversation history\"\"\"
        
        details = {
            'design_principles': [],
            'architecture_patterns': [],
            'scalability_requirements': [],
            'quality_attributes': [],
            'compliance_standards': []
        }
        
        for response in conversation_history:
            answer = response.get('selected_answer', '').lower()
            
            if 'solid' in answer or 'principle' in answer:
                details['design_principles'].append(answer)
            if 'pattern' in answer or 'architecture' in answer:
                details['architecture_patterns'].append(answer)
            if 'scalability' in answer or 'scaling' in answer:
                details['scalability_requirements'].append(answer)
            if 'quality' in answer or 'coupling' in answer:
                details['quality_attributes'].append(answer)
        
        return details"""
        )
    ]
    
    return templates

def main():
    """Generate quality review agents"""
    
    console.print(Panel.fit(
        "[blue]🔍 SPARC Quality Review Agent Generation[/blue]\n\n"
        "Generating enhanced quality review agents using Layer 2 intelligence templates:\n"
        "• Performance Reviewer Agent\n"
        "• Code Quality Reviewer Agent\n"
        "• Architecture Reviewer Agent",
        title="Quality Review Generation",
        border_style="blue"
    ))
    
    # Create generator
    generator = create_agent_generator()
    
    # Create templates
    templates = create_quality_review_templates()
    
    console.print(f"[cyan]Created {len(templates)} quality review agent templates[/cyan]")
    
    # Generate all agents
    generated_codes = generator.generate_batch(templates)
    
    console.print(Panel.fit(
        f"[green]✅ Successfully Generated {len(generated_codes)} Quality Review Agents![/green]\n\n"
        f"All agents include:\n"
        f"• Complete Layer 2 intelligence integration\n"
        f"• Comprehensive quality analysis capabilities\n"
        f"• Agent communication system\n"
        f"• Project state management\n"
        f"• Interactive clarification with AI-verifiable outcomes\n\n"
        f"Total Enhanced Agents: 9 (previous) + {len(generated_codes)} (new) = {9 + len(generated_codes)} agents",
        title="Quality Review Generation Complete",
        border_style="green"
    ))
    
    return generated_codes

if __name__ == "__main__":
    main()