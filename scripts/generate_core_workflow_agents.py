#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "rich>=13.0.0",
# ]
# ///

"""
Generate Core Workflow Agents
Batch generates the remaining core SPARC workflow agents using template system
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

def create_core_workflow_templates():
    """Create templates for core workflow agents"""
    
    templates = [
        # Implementation Phase Agent
        AgentTemplate(
            agent_name="implementation-phase-agent",
            category=AgentCategory.PHASE_ORCHESTRATOR,
            phase="implementation",
            description="Creates production-ready code implementations using Layer 2 intelligence components",
            prerequisite_documents=[
                "docs/pseudocode/main_implementation.md",
                "docs/pseudocode/algorithms_and_data_structures.md",
                "docs/architecture/system_architecture.md"
            ],
            prerequisite_phase="pseudocode phase",
            primary_task="Implementation",
            clarification_focus="implementation approach and coding standards",
            implementation_logic="Convert pseudocode to production-ready code with comprehensive error handling and testing",
            output_directory="src",
            primary_artifact="main_implementation.py",
            secondary_artifacts=["test_implementation.py", "implementation_docs.md", "api_endpoints.py"],
            phase_specific_logic="""
    def _generate_implementation_question(self, prerequisites: Dict[str, Any]) -> str:
        \"\"\"Generate initial implementation clarification question\"\"\"
        
        pseudocode = prerequisites.get('main_implementation', '')
        
        if 'api' in pseudocode.lower():
            return "What specific programming language, framework, and development standards should be used for the API implementation? Please detail the project structure, dependency management, error handling patterns, and testing approach."
        
        elif 'web' in pseudocode.lower():
            return "What frontend framework and development approach should be used? Please specify the component architecture, state management, build tools, testing framework, and deployment strategy."
        
        elif 'database' in pseudocode.lower():
            return "What database technology and ORM should be used for implementation? Please detail the migration strategy, query optimization approach, connection management, and backup procedures."
        
        else:
            return "What programming language, frameworks, and development patterns should be used for implementation? Please specify code organization, dependency management, testing strategy, and deployment approach."
    
    async def _simulate_implementation_responses(self, question, pseudocode: str) -> List[str]:
        \"\"\"Simulate implementation responses for testing\"\"\"
        
        if 'api' in pseudocode.lower():
            return [
                "Use Python with FastAPI framework. Project structure: /src for main code, /tests for tests, /docs for documentation. Use Poetry for dependency management and pytest for testing.",
                "Implement comprehensive error handling with custom exception classes, structured logging with correlation IDs, input validation with Pydantic models, and rate limiting.",
                "Testing approach: Unit tests with 90%+ coverage, integration tests for API endpoints, performance tests for load requirements, security tests for auth flows."
            ]
        
        elif 'web' in pseudocode.lower():
            return [
                "Use React with TypeScript. Component architecture with functional components and hooks. Redux Toolkit for state management. Vite for build tools and Vitest for testing.",
                "Code organization: /src/components for reusable components, /src/pages for page components, /src/hooks for custom hooks, /src/utils for utilities.",
                "Development standards: ESLint + Prettier for code formatting, Husky for git hooks, Jest for unit testing, Cypress for E2E testing."
            ]
        
        else:
            return [
                "Use modern development practices with clean architecture, dependency injection, comprehensive testing, and proper error handling.",
                "Implement logging and monitoring, configuration management, security best practices, and performance optimization.",
                "Follow coding standards with linting, formatting, documentation, and automated testing throughout development."
            ]
    
    def _extract_implementation_details(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        \"\"\"Extract implementation details from conversation history\"\"\"
        
        details = {
            'programming_language': [],
            'frameworks': [],
            'project_structure': [],
            'testing_approach': [],
            'development_standards': [],
            'deployment_strategy': []
        }
        
        for response in conversation_history:
            answer = response.get('selected_answer', '').lower()
            
            # Extract programming languages
            languages = ['python', 'javascript', 'typescript', 'java', 'go', 'rust']
            for lang in languages:
                if lang in answer:
                    details['programming_language'].append(lang)
            
            # Extract frameworks
            frameworks = ['fastapi', 'react', 'vue', 'django', 'express', 'spring']
            for framework in frameworks:
                if framework in answer:
                    details['frameworks'].append(framework)
            
            # Extract testing approaches
            if any(term in answer for term in ['test', 'pytest', 'jest', 'vitest']):
                test_terms = [word for word in answer.split() if any(t in word for t in ['test', 'pytest', 'jest', 'coverage'])]
                details['testing_approach'].extend(test_terms)
        
        return details"""
        ),
        
        # Refinement Phase Agent
        AgentTemplate(
            agent_name="refinement-phase-agent",
            category=AgentCategory.PHASE_ORCHESTRATOR,
            phase="refinement",
            description="Iteratively improves and optimizes implementations using Layer 2 intelligence components",
            prerequisite_documents=[
                "src/main_implementation.py",
                "src/test_implementation.py",
                "docs/security/security_analysis.md"
            ],
            prerequisite_phase="implementation phase",
            primary_task="Refinement",
            clarification_focus="optimization priorities and quality improvements",
            implementation_logic="Analyze implementation for improvements and apply systematic refinements",
            output_directory="src/refined",
            primary_artifact="refined_implementation.py",
            secondary_artifacts=["optimization_report.md", "performance_improvements.md", "refactoring_notes.md"],
            phase_specific_logic="""
    def _generate_refinement_question(self, prerequisites: Dict[str, Any]) -> str:
        \"\"\"Generate initial refinement clarification question\"\"\"
        
        implementation = prerequisites.get('main_implementation', '')
        
        return "What specific aspects of the implementation should be prioritized for refinement? Please detail performance optimization targets, code quality improvements, security enhancements, and maintainability upgrades needed."
    
    async def _simulate_refinement_responses(self, question, implementation: str) -> List[str]:
        \"\"\"Simulate refinement responses for testing\"\"\"
        
        return [
            "Priority 1: Performance optimization - improve response times by 30%, optimize database queries, implement caching where appropriate.",
            "Priority 2: Code quality - refactor duplicate code, improve error handling, add comprehensive logging and monitoring.",
            "Priority 3: Security hardening - address any security findings, implement rate limiting, add input sanitization, update dependencies."
        ]
    
    def _extract_refinement_details(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        \"\"\"Extract refinement details from conversation history\"\"\"
        
        details = {
            'performance_targets': [],
            'quality_improvements': [],
            'security_enhancements': [],
            'maintainability_upgrades': [],
            'optimization_areas': []
        }
        
        for response in conversation_history:
            answer = response.get('selected_answer', '').lower()
            
            if 'performance' in answer:
                details['performance_targets'].append(answer)
            if 'quality' in answer:
                details['quality_improvements'].append(answer)
            if 'security' in answer:
                details['security_enhancements'].append(answer)
            if 'maintain' in answer:
                details['maintainability_upgrades'].append(answer)
        
        return details"""
        ),
        
        # Completion Phase Agent
        AgentTemplate(
            agent_name="completion-phase-agent",
            category=AgentCategory.PHASE_ORCHESTRATOR,
            phase="completion",
            description="Finalizes project deliverables and prepares for deployment using Layer 2 intelligence components",
            prerequisite_documents=[
                "src/refined/refined_implementation.py",
                "docs/specifications/comprehensive_spec.md",
                "docs/architecture/system_architecture.md"
            ],
            prerequisite_phase="refinement phase",
            primary_task="Completion",
            clarification_focus="final deliverables and deployment readiness",
            implementation_logic="Package all deliverables, validate completeness, and prepare deployment artifacts",
            output_directory="deliverables",
            primary_artifact="project_completion_report.md",
            secondary_artifacts=["deployment_package.zip", "documentation_bundle.md", "quality_certification.md"],
            phase_specific_logic="""
    def _generate_completion_question(self, prerequisites: Dict[str, Any]) -> str:
        \"\"\"Generate initial completion clarification question\"\"\"
        
        return "What final deliverables and deployment artifacts are required for project completion? Please specify packaging requirements, documentation needs, deployment configuration, and handover procedures."
    
    async def _simulate_completion_responses(self, question, implementation: str) -> List[str]:
        \"\"\"Simulate completion responses for testing\"\"\"
        
        return [
            "Required deliverables: Complete source code package, comprehensive documentation, deployment scripts, configuration files, test suites, and user manuals.",
            "Deployment artifacts: Docker containers, environment configurations, database migration scripts, monitoring setup, backup procedures.",
            "Handover requirements: Technical documentation, operational runbooks, maintenance procedures, support contact information, SLA documentation."
        ]
    
    def _extract_completion_details(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        \"\"\"Extract completion details from conversation history\"\"\"
        
        details = {
            'deliverables': [],
            'deployment_artifacts': [],
            'documentation_requirements': [],
            'handover_items': [],
            'quality_gates': []
        }
        
        for response in conversation_history:
            answer = response.get('selected_answer', '')
            
            if 'deliverable' in answer.lower():
                details['deliverables'].append(answer)
            if 'deployment' in answer.lower():
                details['deployment_artifacts'].append(answer)
            if 'documentation' in answer.lower():
                details['documentation_requirements'].append(answer)
            if 'handover' in answer.lower():
                details['handover_items'].append(answer)
        
        return details"""
        ),
        
        # Testing Master Agent
        AgentTemplate(
            agent_name="testing-master-agent",
            category=AgentCategory.TESTING_AGENT,
            phase="testing",
            description="Creates comprehensive test suites and validation frameworks using Layer 2 intelligence components",
            prerequisite_documents=[
                "src/main_implementation.py",
                "docs/specifications/functional_requirements.md"
            ],
            prerequisite_phase="implementation phase",
            primary_task="Testing",
            clarification_focus="testing strategy and coverage requirements",
            implementation_logic="Generate comprehensive test suites covering unit, integration, and system testing",
            output_directory="tests",
            primary_artifact="test_suite_comprehensive.py",
            secondary_artifacts=["integration_tests.py", "performance_tests.py", "test_coverage_report.md"],
            phase_specific_logic="""
    def _generate_testing_question(self, prerequisites: Dict[str, Any]) -> str:
        \"\"\"Generate initial testing clarification question\"\"\"
        
        return "What testing strategy and coverage requirements should be implemented? Please specify unit test coverage targets, integration test scenarios, performance test criteria, and automated testing pipeline requirements."
    
    async def _simulate_testing_responses(self, question, implementation: str) -> List[str]:
        \"\"\"Simulate testing responses for testing\"\"\"
        
        return [
            "Testing strategy: 90%+ unit test coverage, comprehensive integration tests for all API endpoints, performance tests for load requirements, security tests for authentication flows.",
            "Test automation: CI/CD pipeline with automated test execution, test report generation, coverage tracking, and quality gate enforcement.",
            "Test types: Unit tests with mocking, integration tests with test databases, E2E tests with real scenarios, load tests with performance benchmarks."
        ]
    
    def _extract_testing_details(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        \"\"\"Extract testing details from conversation history\"\"\"
        
        details = {
            'test_types': [],
            'coverage_requirements': [],
            'automation_strategy': [],
            'performance_criteria': [],
            'quality_gates': []
        }
        
        for response in conversation_history:
            answer = response.get('selected_answer', '').lower()
            
            if 'unit' in answer or 'integration' in answer or 'e2e' in answer:
                details['test_types'].append(answer)
            if 'coverage' in answer:
                details['coverage_requirements'].append(answer)
            if 'automation' in answer or 'ci/cd' in answer:
                details['automation_strategy'].append(answer)
            if 'performance' in answer:
                details['performance_criteria'].append(answer)
        
        return details"""
        ),
        
        # Security Reviewer Agent
        AgentTemplate(
            agent_name="security-reviewer-agent",
            category=AgentCategory.SECURITY_AGENT,
            phase="security-review",
            description="Performs comprehensive security analysis and vulnerability assessment using Layer 2 intelligence components",
            prerequisite_documents=[
                "src/main_implementation.py",
                "docs/architecture/system_architecture.md"
            ],
            prerequisite_phase="implementation phase",
            primary_task="Security Review",
            clarification_focus="security requirements and threat assessment",
            implementation_logic="Analyze implementation for security vulnerabilities and provide hardening recommendations",
            output_directory="docs/security",
            primary_artifact="security_analysis_report.md",
            secondary_artifacts=["vulnerability_assessment.md", "security_recommendations.md", "threat_model.md"],
            phase_specific_logic="""
    def _generate_security_question(self, prerequisites: Dict[str, Any]) -> str:
        \"\"\"Generate initial security clarification question\"\"\"
        
        return "What security standards and threat model should be applied for the security review? Please specify compliance requirements, security testing criteria, vulnerability assessment scope, and risk tolerance levels."
    
    async def _simulate_security_responses(self, question, implementation: str) -> List[str]:
        \"\"\"Simulate security responses for testing\"\"\"
        
        return [
            "Security standards: OWASP Top 10 compliance, input validation on all endpoints, authentication with JWT tokens, authorization with role-based access control.",
            "Threat model: Analyze authentication bypass, injection attacks, data exposure, privilege escalation, and denial of service vulnerabilities.",
            "Security testing: Static code analysis, dependency vulnerability scanning, penetration testing for critical paths, security configuration review."
        ]
    
    def _extract_security_details(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        \"\"\"Extract security details from conversation history\"\"\"
        
        details = {
            'security_standards': [],
            'threat_categories': [],
            'vulnerability_types': [],
            'testing_methods': [],
            'compliance_requirements': []
        }
        
        for response in conversation_history:
            answer = response.get('selected_answer', '').lower()
            
            if 'owasp' in answer or 'standard' in answer:
                details['security_standards'].append(answer)
            if 'threat' in answer:
                details['threat_categories'].append(answer)
            if 'vulnerability' in answer or 'attack' in answer:
                details['vulnerability_types'].append(answer)
            if 'testing' in answer or 'scan' in answer:
                details['testing_methods'].append(answer)
        
        return details"""
        )
    ]
    
    return templates

def main():
    """Generate core workflow agents"""
    
    console.print(Panel.fit(
        "[blue]🚀 SPARC Core Workflow Agent Generation[/blue]\n\n"
        "Generating enhanced agents using Layer 2 intelligence templates:\n"
        "• Implementation Phase Agent\n"
        "• Refinement Phase Agent\n" 
        "• Completion Phase Agent\n"
        "• Testing Master Agent\n"
        "• Security Reviewer Agent",
        title="Core Workflow Generation",
        border_style="blue"
    ))
    
    # Create generator
    generator = create_agent_generator()
    
    # Create templates
    templates = create_core_workflow_templates()
    
    console.print(f"[cyan]Created {len(templates)} agent templates[/cyan]")
    
    # Generate all agents
    generated_codes = generator.generate_batch(templates)
    
    console.print(Panel.fit(
        f"[green]✅ Successfully Generated {len(generated_codes)} Core Workflow Agents![/green]\n\n"
        f"All agents include:\n"
        f"• Complete Layer 2 intelligence integration\n"
        f"• Comprehensive error handling\n"
        f"• Agent communication system\n"
        f"• Project state management\n"
        f"• Interactive clarification with AI-verifiable outcomes\n\n"
        f"Total Enhanced Agents: 4 (previous) + {len(generated_codes)} (new) = {4 + len(generated_codes)} agents",
        title="Generation Complete",
        border_style="green"
    ))
    
    return generated_codes

if __name__ == "__main__":
    main()