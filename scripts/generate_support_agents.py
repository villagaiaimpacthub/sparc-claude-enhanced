#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "rich>=13.0.0",
# ]
# ///

"""
Generate Support Agents
Batch generates support agents for documentation, deployment, and monitoring using template system
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

def create_support_agent_templates():
    """Create templates for support agents"""
    
    templates = [
        # Documentation Agent
        AgentTemplate(
            agent_name="documentation-agent",
            category=AgentCategory.SUPPORT_AGENT,
            phase="documentation",
            description="Creates comprehensive project documentation and user guides using Layer 2 intelligence components",
            prerequisite_documents=[
                "src/main_implementation.py",
                "docs/specifications/comprehensive_spec.md",
                "docs/architecture/system_architecture.md"
            ],
            prerequisite_phase="completion phase",
            primary_task="Documentation",
            clarification_focus="documentation requirements and user guidance needs",
            implementation_logic="Generate comprehensive documentation including user guides, API docs, and technical documentation",
            output_directory="docs/final",
            primary_artifact="comprehensive_documentation.md",
            secondary_artifacts=["user_guide.md", "api_documentation.md", "deployment_guide.md", "troubleshooting_guide.md"],
            phase_specific_logic="""
    def _generate_documentation_question(self, prerequisites: Dict[str, Any]) -> str:
        \"\"\"Generate initial documentation clarification question\"\"\"
        
        return "What documentation components and detail levels are required? Please specify user guide requirements, API documentation needs, deployment instructions, troubleshooting sections, and target audience expertise levels."
    
    async def _simulate_documentation_responses(self, question, implementation: str) -> List[str]:
        \"\"\"Simulate documentation responses for testing\"\"\"
        
        return [
            "Documentation scope: Complete user guide for end users, comprehensive API documentation with examples, step-by-step deployment guide, troubleshooting section with common issues.",
            "Target audiences: End users (non-technical), developers (technical), system administrators (deployment), support teams (troubleshooting).",
            "Content requirements: Screenshots for user guide, code examples for API docs, command-line instructions for deployment, error code explanations for troubleshooting."
        ]
    
    def _extract_documentation_details(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        \"\"\"Extract documentation details from conversation history\"\"\"
        
        details = {
            'documentation_types': [],
            'target_audiences': [],
            'content_requirements': [],
            'detail_levels': [],
            'format_preferences': []
        }
        
        for response in conversation_history:
            answer = response.get('selected_answer', '').lower()
            
            if 'user guide' in answer or 'api doc' in answer or 'deployment' in answer:
                details['documentation_types'].append(answer)
            if 'user' in answer or 'developer' in answer or 'admin' in answer:
                details['target_audiences'].append(answer)
            if 'example' in answer or 'screenshot' in answer or 'instruction' in answer:
                details['content_requirements'].append(answer)
        
        return details"""
        ),
        
        # Deployment Agent
        AgentTemplate(
            agent_name="deployment-agent",
            category=AgentCategory.SUPPORT_AGENT,
            phase="deployment",
            description="Creates deployment packages and infrastructure configuration using Layer 2 intelligence components",
            prerequisite_documents=[
                "deliverables/project_completion_report.md",
                "src/refined/refined_implementation.py",
                "docs/architecture/system_architecture.md"
            ],
            prerequisite_phase="completion phase",
            primary_task="Deployment",
            clarification_focus="deployment targets and infrastructure requirements",
            implementation_logic="Create deployment packages, infrastructure configurations, and automated deployment scripts",
            output_directory="deployment",
            primary_artifact="deployment_package.zip",
            secondary_artifacts=["docker_compose.yml", "kubernetes_manifests.yaml", "deployment_script.sh", "infrastructure_config.tf"],
            phase_specific_logic="""
    def _generate_deployment_question(self, prerequisites: Dict[str, Any]) -> str:
        \"\"\"Generate initial deployment clarification question\"\"\"
        
        return "What deployment targets and infrastructure requirements should be supported? Please specify cloud platforms, containerization needs, orchestration requirements, and automation preferences."
    
    async def _simulate_deployment_responses(self, question, completion_report: str) -> List[str]:
        \"\"\"Simulate deployment responses for testing\"\"\"
        
        return [
            "Deployment targets: Docker containers for development, Kubernetes for production, support for AWS/GCP/Azure cloud platforms.",
            "Infrastructure requirements: Load balancer setup, database configuration, environment variable management, SSL certificate handling.",
            "Automation needs: CI/CD pipeline integration, automated testing before deployment, rollback capabilities, monitoring setup."
        ]
    
    def _extract_deployment_details(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        \"\"\"Extract deployment details from conversation history\"\"\"
        
        details = {
            'deployment_targets': [],
            'cloud_platforms': [],
            'containerization': [],
            'orchestration': [],
            'automation_requirements': []
        }
        
        for response in conversation_history:
            answer = response.get('selected_answer', '').lower()
            
            if 'docker' in answer or 'container' in answer:
                details['containerization'].append(answer)
            if 'kubernetes' in answer or 'orchestration' in answer:
                details['orchestration'].append(answer)
            if 'aws' in answer or 'gcp' in answer or 'azure' in answer:
                details['cloud_platforms'].append(answer)
            if 'ci/cd' in answer or 'automation' in answer:
                details['automation_requirements'].append(answer)
        
        return details"""
        ),
        
        # Monitoring Agent
        AgentTemplate(
            agent_name="monitoring-agent",
            category=AgentCategory.SUPPORT_AGENT,
            phase="monitoring",
            description="Sets up comprehensive monitoring, logging, and alerting systems using Layer 2 intelligence components",
            prerequisite_documents=[
                "deployment/deployment_package.zip",
                "docs/performance/performance_analysis_report.md",
                "src/main_implementation.py"
            ],
            prerequisite_phase="deployment phase",
            primary_task="Monitoring",
            clarification_focus="monitoring requirements and alerting preferences",
            implementation_logic="Configure monitoring dashboards, logging systems, and alerting mechanisms",
            output_directory="monitoring",
            primary_artifact="monitoring_configuration.yaml",
            secondary_artifacts=["dashboard_config.json", "alerting_rules.yaml", "logging_config.yaml", "health_checks.py"],
            phase_specific_logic="""
    def _generate_monitoring_question(self, prerequisites: Dict[str, Any]) -> str:
        \"\"\"Generate initial monitoring clarification question\"\"\"
        
        return "What monitoring metrics and alerting requirements should be implemented? Please specify performance metrics, error tracking, log aggregation needs, and notification preferences."
    
    async def _simulate_monitoring_responses(self, question, deployment_info: str) -> List[str]:
        \"\"\"Simulate monitoring responses for testing\"\"\"
        
        return [
            "Monitoring metrics: Response times, error rates, CPU/memory usage, database performance, user activity metrics, business KPIs.",
            "Alerting requirements: Critical error alerts via email/SMS, performance degradation warnings, capacity planning alerts, security incident notifications.",
            "Logging needs: Centralized log aggregation, structured logging format, log retention policies, searchable log interface, audit trail compliance."
        ]
    
    def _extract_monitoring_details(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        \"\"\"Extract monitoring details from conversation history\"\"\"
        
        details = {
            'metrics_to_track': [],
            'alerting_channels': [],
            'logging_requirements': [],
            'dashboard_preferences': [],
            'retention_policies': []
        }
        
        for response in conversation_history:
            answer = response.get('selected_answer', '').lower()
            
            if 'metric' in answer or 'performance' in answer or 'response time' in answer:
                details['metrics_to_track'].append(answer)
            if 'alert' in answer or 'email' in answer or 'notification' in answer:
                details['alerting_channels'].append(answer)
            if 'log' in answer or 'audit' in answer or 'retention' in answer:
                details['logging_requirements'].append(answer)
            if 'dashboard' in answer or 'visualization' in answer:
                details['dashboard_preferences'].append(answer)
        
        return details"""
        ),
        
        # Integration Agent
        AgentTemplate(
            agent_name="integration-agent",
            category=AgentCategory.INTEGRATION_AGENT,
            phase="integration",
            description="Manages system integrations and external service connections using Layer 2 intelligence components",
            prerequisite_documents=[
                "docs/architecture/system_architecture.md",
                "src/main_implementation.py"
            ],
            prerequisite_phase="implementation phase",
            primary_task="Integration",
            clarification_focus="integration requirements and external service dependencies",
            implementation_logic="Configure and validate external integrations, APIs, and service connections",
            output_directory="integrations",
            primary_artifact="integration_configuration.json",
            secondary_artifacts=["api_client_configs.py", "webhook_handlers.py", "integration_tests.py", "service_discovery.yaml"],
            phase_specific_logic="""
    def _generate_integration_question(self, prerequisites: Dict[str, Any]) -> str:
        \"\"\"Generate initial integration clarification question\"\"\"
        
        return "What external systems and services need integration? Please specify APIs to connect, authentication methods, data synchronization requirements, and error handling strategies."
    
    async def _simulate_integration_responses(self, question, architecture: str) -> List[str]:
        \"\"\"Simulate integration responses for testing\"\"\"
        
        return [
            "External services: Payment processing APIs, authentication providers (OAuth), email services, SMS gateways, analytics platforms.",
            "Integration patterns: RESTful API clients, webhook endpoints for real-time updates, message queue integration, database synchronization.",
            "Requirements: Secure credential management, retry mechanisms, circuit breaker patterns, integration health monitoring, data validation."
        ]
    
    def _extract_integration_details(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        \"\"\"Extract integration details from conversation history\"\"\"
        
        details = {
            'external_services': [],
            'integration_patterns': [],
            'authentication_methods': [],
            'error_handling': [],
            'data_synchronization': []
        }
        
        for response in conversation_history:
            answer = response.get('selected_answer', '').lower()
            
            if 'api' in answer or 'service' in answer or 'payment' in answer:
                details['external_services'].append(answer)
            if 'webhook' in answer or 'rest' in answer or 'queue' in answer:
                details['integration_patterns'].append(answer)
            if 'oauth' in answer or 'auth' in answer or 'credential' in answer:
                details['authentication_methods'].append(answer)
            if 'retry' in answer or 'error' in answer or 'circuit' in answer:
                details['error_handling'].append(answer)
        
        return details"""
        )
    ]
    
    return templates

def main():
    """Generate support agents"""
    
    console.print(Panel.fit(
        "[blue]🛠️ SPARC Support Agent Generation[/blue]\n\n"
        "Generating enhanced support agents using Layer 2 intelligence templates:\n"
        "• Documentation Agent\n"
        "• Deployment Agent\n"
        "• Monitoring Agent\n"
        "• Integration Agent",
        title="Support Agent Generation",
        border_style="blue"
    ))
    
    # Create generator
    generator = create_agent_generator()
    
    # Create templates
    templates = create_support_agent_templates()
    
    console.print(f"[cyan]Created {len(templates)} support agent templates[/cyan]")
    
    # Generate all agents
    generated_codes = generator.generate_batch(templates)
    
    console.print(Panel.fit(
        f"[green]✅ Successfully Generated {len(generated_codes)} Support Agents![/green]\n\n"
        f"All agents include:\n"
        f"• Complete Layer 2 intelligence integration\n"
        f"• Comprehensive support capabilities\n"
        f"• Agent communication system\n"
        f"• Project state management\n"
        f"• Interactive clarification with AI-verifiable outcomes\n\n"
        f"Total Enhanced Agents: 12 (previous) + {len(generated_codes)} (new) = {12 + len(generated_codes)} agents",
        title="Support Agent Generation Complete",
        border_style="green"
    ))
    
    return generated_codes

if __name__ == "__main__":
    main()