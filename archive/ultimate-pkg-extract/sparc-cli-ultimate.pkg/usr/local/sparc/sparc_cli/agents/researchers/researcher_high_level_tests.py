#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase",
#   "qdrant-client",
#   "mistralai",
#   "rich",
#   "pydantic",
#   "python-dotenv",
# ]
# ///

"""Researcher High-Level Tests Agent - High-Level Test Strategy Specialist"""

import os
import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from ..base_agent import BaseAgent, AgentResult
from ...memory.manager import TaskPayload

class ResearcherHighLevelTestsAgent(BaseAgent):
    """
    Researcher High-Level Tests Agent
    
    A specialized deep researcher tasked with defining the optimal strategy for 
    high level acceptance tests for the project. Research will be based on a 
    complete understanding of all available project documentation and will 
    leverage an MCP search tool for in depth investigation.
    """
    
    def __init__(self):
        role_definition = """You are a specialized deep researcher tasked with defining the optimal strategy for high level acceptance tests for the project. Your research will be based on a complete understanding of all available project documentation and will leverage an MCP search tool for in depth investigation into best practices and methodologies. Your goal is to produce a research report that outlines a comprehensive high level testing suite designed to ensure the entire system works perfectly if all tests pass."""
        
        custom_instructions = """You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task. Before you answer, you must think through this problem step by step. You will be delegated this task by the orchestrator-sparc-specification-phase with all necessary context provided in the prompt. You will use an MCP search tool like Perplexity to conduct deep research on identifying the best possible ways to set up high-level tests tailored to the project. Your proposed testing strategy must lead to a suite of tests that, if passed, provide extremely high confidence in the system's correctness. Every test concept you propose must ultimately be AI-verifiable. Your primary output, and your AI-verifiable outcome, is a detailed research report document, for example named 'docs/research/high_level_test_strategy_report.md'. This report must be comprehensive and clearly articulate the recommended high-level testing strategy and must explain how each part of the strategy is AI-verifiable. Upon completion of the report, you will use "attempt_completion". Your completion summary must describe the research process, the key findings, and confirm that the report outlines a comprehensive, AI-verifiable testing strategy, and provide the path to the report."""
        
        super().__init__(
            agent_name="researcher-high-level-tests",
            role_definition=role_definition,
            custom_instructions=custom_instructions
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute high-level test strategy research"""
        
        # Ensure research directory exists
        research_dir = Path("docs/research")
        research_dir.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        try:
            # Load project context and requirements
            project_context = await self._analyze_project_context(task, context)
            
            # Research testing methodologies
            testing_methodologies = await self._research_testing_methodologies(project_context)
            
            # Design comprehensive test strategy
            test_strategy = await self._design_test_strategy(project_context, testing_methodologies)
            
            # Create detailed research report
            report_path = research_dir / "high_level_test_strategy_report.md"
            await self._create_research_report(report_path, project_context, testing_methodologies, test_strategy)
            files_created.append(str(report_path))
            
            # Create supplementary documentation
            supplementary_files = await self._create_supplementary_docs(research_dir, test_strategy)
            files_created.extend(supplementary_files)
            
            # Delegate to state-scribe for recording
            await self._delegate_task(
                to_agent="orchestrator-state-scribe",
                task_description=f"Record high-level test strategy research documentation for project {self.project_id}",
                task_context={
                    "files_created": files_created,
                    "phase": "research",
                    "summary": f"High-level test strategy research completed for {task.description}"
                }
            )
            
            return AgentResult(
                success=True,
                outputs={
                    "research_report": str(report_path),
                    "testing_strategy": test_strategy,
                    "ai_verifiable_concepts": self._extract_ai_verifiable_concepts(test_strategy)
                },
                files_created=files_created,
                files_modified=[],
                next_steps=[
                    "Review research report for testing strategy insights",
                    "Use findings to inform acceptance test plan creation",
                    "Validate test strategy against project requirements"
                ]
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                outputs={},
                files_created=files_created,
                files_modified=[],
                errors=[f"High-level test research failed: {str(e)}"]
            )
    
    async def _analyze_project_context(self, task: TaskPayload, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project context to understand testing requirements"""
        
        return {
            "project_type": context.get("project_type", "web_application"),
            "architecture": context.get("architecture", "microservices"),
            "frameworks": context.get("frameworks", ["python", "fastapi"]),
            "requirements": task.requirements,
            "success_criteria": task.ai_verifiable_outcomes,
            "complexity_level": self._assess_complexity(task, context),
            "testing_priorities": self._identify_testing_priorities(task, context)
        }
    
    async def _research_testing_methodologies(self, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Research testing methodologies using MCP search tool"""
        
        # Simulate MCP search tool research
        # In real implementation, would use actual search tool
        
        return {
            "black_box_testing": {
                "description": "Testing without knowledge of internal implementation",
                "benefits": ["User-focused", "Integration validation", "Behavior verification"],
                "ai_verifiable": True,
                "methods": ["API testing", "UI testing", "End-to-end scenarios"]
            },
            "acceptance_testing": {
                "description": "Testing against business requirements",
                "benefits": ["Requirements validation", "User story verification", "Business logic validation"],
                "ai_verifiable": True,
                "methods": ["BDD scenarios", "User journey testing", "Business rule validation"]
            },
            "integration_testing": {
                "description": "Testing component interactions",
                "benefits": ["Interface validation", "Data flow verification", "System coherence"],
                "ai_verifiable": True,
                "methods": ["API integration", "Database integration", "External service integration"]
            },
            "system_testing": {
                "description": "Testing complete system functionality",
                "benefits": ["Full system validation", "Performance verification", "Security testing"],
                "ai_verifiable": True,
                "methods": ["Load testing", "Security scanning", "Performance benchmarking"]
            },
            "regression_testing": {
                "description": "Testing to ensure changes don't break existing functionality",
                "benefits": ["Change validation", "Quality assurance", "Stability verification"],
                "ai_verifiable": True,
                "methods": ["Automated test suites", "Continuous integration", "Smoke testing"]
            }
        }
    
    async def _design_test_strategy(self, project_context: Dict[str, Any], methodologies: Dict[str, Any]) -> Dict[str, Any]:
        """Design comprehensive test strategy based on research"""
        
        return {
            "strategy_overview": {
                "approach": "Layered testing pyramid with comprehensive coverage",
                "focus": "AI-verifiable outcomes with maximum confidence",
                "principles": ["Test early", "Test often", "Test thoroughly"]
            },
            "test_layers": {
                "acceptance_tests": {
                    "purpose": "Validate business requirements and user stories",
                    "coverage": "All major user journeys and business rules",
                    "ai_verifiable": "Pass/fail status, requirement traceability",
                    "tools": ["Pytest", "Behave", "Selenium"]
                },
                "integration_tests": {
                    "purpose": "Validate component interactions and data flows",
                    "coverage": "All API endpoints, database operations, external services",
                    "ai_verifiable": "Response validation, data integrity checks",
                    "tools": ["Pytest", "Requests", "TestContainers"]
                },
                "system_tests": {
                    "purpose": "Validate complete system functionality",
                    "coverage": "End-to-end scenarios, performance, security",
                    "ai_verifiable": "System metrics, performance benchmarks",
                    "tools": ["Locust", "OWASP ZAP", "Docker"]
                },
                "smoke_tests": {
                    "purpose": "Validate core functionality after changes",
                    "coverage": "Critical paths and essential features",
                    "ai_verifiable": "Quick pass/fail indicators",
                    "tools": ["Pytest", "Curl", "Health checks"]
                }
            },
            "ai_verification_strategy": {
                "automated_assertions": "All tests must have clear pass/fail criteria",
                "metric_collection": "Quantitative measures for performance and quality",
                "result_reporting": "Structured test results with detailed feedback",
                "traceability": "Link test results to requirements and user stories"
            },
            "implementation_phases": {
                "phase_1": "Core acceptance tests for primary user journeys",
                "phase_2": "Integration tests for all API endpoints",
                "phase_3": "System tests for performance and security",
                "phase_4": "Regression test suite for continuous validation"
            }
        }
    
    async def _create_research_report(self, report_path: Path, project_context: Dict[str, Any], 
                                    methodologies: Dict[str, Any], test_strategy: Dict[str, Any]):
        """Create comprehensive research report"""
        
        report_content = f"""# High-Level Test Strategy Research Report

## Executive Summary

This report outlines a comprehensive high-level testing strategy designed to ensure maximum system reliability and user satisfaction. The strategy emphasizes AI-verifiable outcomes and provides extremely high confidence in system correctness when all tests pass.

## Project Context Analysis

### Project Characteristics
- **Type**: {project_context['project_type']}
- **Architecture**: {project_context['architecture']}
- **Frameworks**: {', '.join(project_context['frameworks'])}
- **Complexity Level**: {project_context['complexity_level']}

### Testing Requirements
- **Primary Requirements**: {', '.join(project_context['requirements'])}
- **Success Criteria**: {', '.join(project_context['success_criteria'])}
- **Testing Priorities**: {', '.join(project_context['testing_priorities'])}

## Research Methodology

### Information Sources
- Industry best practices and standards
- Framework-specific testing documentation
- Academic research on testing methodologies
- Case studies from similar projects

### Research Focus Areas
- Black-box testing approaches
- Acceptance testing methodologies
- Integration testing strategies
- System testing techniques
- Regression testing practices

## Testing Methodology Analysis

### Black-Box Testing
- **Purpose**: Test system behavior without implementation knowledge
- **AI-Verifiable**: Yes - clear input/output validation
- **Benefits**: User-focused, integration validation, behavior verification
- **Implementation**: API testing, UI testing, end-to-end scenarios

### Acceptance Testing
- **Purpose**: Validate business requirements and user stories
- **AI-Verifiable**: Yes - requirement traceability and pass/fail status
- **Benefits**: Requirements validation, user story verification, business logic validation
- **Implementation**: BDD scenarios, user journey testing, business rule validation

### Integration Testing
- **Purpose**: Validate component interactions and data flows
- **AI-Verifiable**: Yes - response validation and data integrity checks
- **Benefits**: Interface validation, data flow verification, system coherence
- **Implementation**: API integration, database integration, external service integration

### System Testing
- **Purpose**: Test complete system functionality
- **AI-Verifiable**: Yes - system metrics and performance benchmarks
- **Benefits**: Full system validation, performance verification, security testing
- **Implementation**: Load testing, security scanning, performance benchmarking

### Regression Testing
- **Purpose**: Ensure changes don't break existing functionality
- **AI-Verifiable**: Yes - automated test suite results
- **Benefits**: Change validation, quality assurance, stability verification
- **Implementation**: Automated test suites, continuous integration, smoke testing

## Recommended Testing Strategy

### Strategy Overview
The recommended approach follows a layered testing pyramid with comprehensive coverage at each level. This strategy provides maximum confidence in system correctness while maintaining efficiency and maintainability.

### Test Layers

#### 1. Acceptance Tests
- **Purpose**: Validate business requirements and user stories
- **Coverage**: All major user journeys and business rules
- **AI-Verifiable Outcomes**: 
  - Pass/fail status for each user story
  - Requirement traceability matrix
  - Business rule validation results
- **Tools**: Pytest, Behave, Selenium
- **Success Criteria**: All acceptance criteria met for each user story

#### 2. Integration Tests
- **Purpose**: Validate component interactions and data flows
- **Coverage**: All API endpoints, database operations, external services
- **AI-Verifiable Outcomes**:
  - API response validation
  - Database integrity checks
  - External service integration status
- **Tools**: Pytest, Requests, TestContainers
- **Success Criteria**: All interfaces function correctly with expected data flows

#### 3. System Tests
- **Purpose**: Validate complete system functionality
- **Coverage**: End-to-end scenarios, performance, security
- **AI-Verifiable Outcomes**:
  - System performance metrics
  - Security vulnerability scan results
  - Load testing benchmarks
- **Tools**: Locust, OWASP ZAP, Docker
- **Success Criteria**: System meets all performance and security requirements

#### 4. Smoke Tests
- **Purpose**: Validate core functionality after changes
- **Coverage**: Critical paths and essential features
- **AI-Verifiable Outcomes**:
  - Quick pass/fail indicators
  - Health check results
  - Critical path validation
- **Tools**: Pytest, Curl, Health checks
- **Success Criteria**: All critical functionality remains operational

### AI-Verification Strategy

#### Automated Assertions
All tests must include clear, measurable assertions that can be evaluated programmatically:
- Boolean pass/fail results
- Quantitative performance metrics
- Structured error reporting
- Requirement traceability links

#### Metric Collection
Comprehensive metrics collection ensures objective evaluation:
- Response time measurements
- Error rate tracking
- Resource utilization monitoring
- User experience metrics

#### Result Reporting
Structured test results provide detailed feedback:
- Test execution summaries
- Pass/fail statistics
- Performance benchmarks
- Failure analysis reports

#### Traceability
Clear links between tests and requirements:
- Test-to-requirement mapping
- User story coverage reports
- Business rule validation status
- Change impact analysis

## Implementation Plan

### Phase 1: Core Acceptance Tests
- Implement tests for primary user journeys
- Create basic BDD scenarios
- Establish test execution framework
- **Duration**: 2-3 sprints
- **AI-Verifiable Outcome**: All primary user stories have passing acceptance tests

### Phase 2: Integration Tests
- Develop API endpoint tests
- Create database integration tests
- Implement external service mocks
- **Duration**: 2-3 sprints
- **AI-Verifiable Outcome**: All integrations validated with automated tests

### Phase 3: System Tests
- Implement performance testing
- Create security testing suite
- Develop load testing scenarios
- **Duration**: 2-3 sprints
- **AI-Verifiable Outcome**: System meets all performance and security requirements

### Phase 4: Regression Test Suite
- Consolidate all tests into CI/CD pipeline
- Implement automated test execution
- Create test result reporting
- **Duration**: 1-2 sprints
- **AI-Verifiable Outcome**: Automated regression testing operational

## Quality Assurance

### Test Quality Metrics
- Test coverage percentage
- Test execution success rate
- Test maintenance effort
- Defect detection rate

### Continuous Improvement
- Regular test strategy review
- Test effectiveness analysis
- Performance optimization
- New testing technique adoption

## Risk Assessment

### Technical Risks
- Test environment stability
- Test data management
- Tool compatibility issues
- Performance testing scalability

### Process Risks
- Test execution time constraints
- Resource allocation challenges
- Skill gap in testing techniques
- Change management complexity

### Mitigation Strategies
- Robust test infrastructure
- Automated test execution
- Comprehensive training programs
- Clear change management processes

## Conclusion

This high-level testing strategy provides a comprehensive framework for ensuring system quality and reliability. By emphasizing AI-verifiable outcomes and following established testing methodologies, this strategy will provide extremely high confidence in system correctness when all tests pass.

The layered approach ensures comprehensive coverage while maintaining efficiency, and the phased implementation plan provides a clear path to full testing capability. Regular monitoring and continuous improvement will ensure the strategy remains effective as the system evolves.

## References

- IEEE 829-2008 Standard for Software Test Documentation
- ISO/IEC 25010 Software Quality Model
- ISTQB Foundation Level Syllabus
- Agile Testing Practices and Principles
- Test-Driven Development Best Practices

## Appendices

### Appendix A: Test Framework Comparison
### Appendix B: Tool Selection Criteria
### Appendix C: Test Environment Requirements
### Appendix D: Sample Test Cases
"""
        
        with open(report_path, "w") as f:
            f.write(report_content)
    
    async def _create_supplementary_docs(self, research_dir: Path, test_strategy: Dict[str, Any]) -> List[str]:
        """Create supplementary documentation"""
        
        files_created = []
        
        # Create test framework comparison
        framework_comparison = f"""# Test Framework Comparison

## API Testing Frameworks

### Pytest
- **Strengths**: Flexible, extensive plugin ecosystem, easy setup
- **Weaknesses**: Learning curve for advanced features
- **AI-Verifiable**: Excellent assertion capabilities
- **Recommendation**: Primary choice for Python projects

### Requests
- **Strengths**: Simple HTTP library, excellent for API testing
- **Weaknesses**: Limited to HTTP requests
- **AI-Verifiable**: Clear response validation
- **Recommendation**: Use with Pytest for API tests

### TestContainers
- **Strengths**: Isolated test environments, real database testing
- **Weaknesses**: Docker dependency, slower execution
- **AI-Verifiable**: Reliable test isolation
- **Recommendation**: Use for integration tests

## UI Testing Frameworks

### Selenium
- **Strengths**: Browser automation, cross-browser support
- **Weaknesses**: Slow execution, brittle tests
- **AI-Verifiable**: Element validation, screenshot comparison
- **Recommendation**: Use for critical UI workflows

### Playwright
- **Strengths**: Fast execution, modern browser support
- **Weaknesses**: Newer tool, smaller community
- **AI-Verifiable**: Excellent assertion capabilities
- **Recommendation**: Consider for new projects

## Performance Testing

### Locust
- **Strengths**: Python-based, scalable, user-friendly
- **Weaknesses**: Limited protocol support
- **AI-Verifiable**: Clear performance metrics
- **Recommendation**: Primary choice for load testing
"""
        
        framework_path = research_dir / "test_framework_comparison.md"
        with open(framework_path, "w") as f:
            f.write(framework_comparison)
        files_created.append(str(framework_path))
        
        # Create tool selection criteria
        tool_criteria = f"""# Tool Selection Criteria

## Primary Criteria

### AI-Verifiability
- Clear pass/fail indicators
- Quantitative metrics
- Structured result reporting
- Programmatic result analysis

### Integration Capabilities
- CI/CD pipeline support
- Test result reporting
- Artifact generation
- Notification systems

### Maintainability
- Code readability
- Test organization
- Documentation quality
- Community support

## Secondary Criteria

### Performance
- Execution speed
- Resource usage
- Scalability
- Parallel execution

### Flexibility
- Test customization
- Framework integration
- Plugin ecosystem
- Configuration options

### Reliability
- Test stability
- Error handling
- Recovery mechanisms
- Debugging capabilities

## Evaluation Matrix

| Tool | AI-Verifiable | Integration | Maintainability | Performance | Flexibility | Reliability |
|------|---------------|-------------|-----------------|-------------|-------------|-------------|
| Pytest | Excellent | Good | Excellent | Good | Excellent | Excellent |
| Selenium | Good | Good | Good | Poor | Good | Good |
| Locust | Excellent | Good | Good | Excellent | Good | Good |
| TestContainers | Good | Good | Good | Poor | Good | Excellent |
"""
        
        criteria_path = research_dir / "tool_selection_criteria.md"
        with open(criteria_path, "w") as f:
            f.write(tool_criteria)
        files_created.append(str(criteria_path))
        
        return files_created
    
    def _assess_complexity(self, task: TaskPayload, context: Dict[str, Any]) -> str:
        """Assess project complexity level"""
        
        complexity_indicators = 0
        
        # Check for complex requirements
        if len(task.requirements) > 5:
            complexity_indicators += 1
        
        # Check for multiple integrations
        if "external_services" in context and len(context["external_services"]) > 2:
            complexity_indicators += 1
        
        # Check for performance requirements
        if any("performance" in req.lower() for req in task.requirements):
            complexity_indicators += 1
        
        # Check for security requirements
        if any("security" in req.lower() for req in task.requirements):
            complexity_indicators += 1
        
        if complexity_indicators >= 3:
            return "High"
        elif complexity_indicators >= 1:
            return "Medium"
        else:
            return "Low"
    
    def _identify_testing_priorities(self, task: TaskPayload, context: Dict[str, Any]) -> List[str]:
        """Identify testing priorities based on requirements"""
        
        priorities = []
        
        # Analyze requirements for testing priorities
        requirements_text = " ".join(task.requirements).lower()
        
        if "user" in requirements_text or "interface" in requirements_text:
            priorities.append("User Experience Testing")
        
        if "performance" in requirements_text or "speed" in requirements_text:
            priorities.append("Performance Testing")
        
        if "security" in requirements_text or "auth" in requirements_text:
            priorities.append("Security Testing")
        
        if "integration" in requirements_text or "api" in requirements_text:
            priorities.append("Integration Testing")
        
        if "data" in requirements_text or "database" in requirements_text:
            priorities.append("Data Integrity Testing")
        
        # Default priorities if none identified
        if not priorities:
            priorities = ["Functional Testing", "Integration Testing", "User Acceptance Testing"]
        
        return priorities
    
    def _extract_ai_verifiable_concepts(self, test_strategy: Dict[str, Any]) -> List[str]:
        """Extract AI-verifiable concepts from test strategy"""
        
        concepts = []
        
        for layer_name, layer_info in test_strategy.get("test_layers", {}).items():
            ai_verifiable = layer_info.get("ai_verifiable", "")
            if ai_verifiable:
                concepts.append(f"{layer_name}: {ai_verifiable}")
        
        return concepts


# Entry point for direct execution
if __name__ == "__main__":
    import asyncio
    from ...memory.manager import TaskPayload
    
    async def main():
        agent = ResearcherHighLevelTestsAgent()
        
        # Example task
        task = TaskPayload(
            task_id="test_research",
            description="Research high-level testing strategy for todo API",
            context={"project_type": "web_api", "frameworks": ["python", "fastapi"]},
            requirements=["Comprehensive testing", "AI-verifiable outcomes", "Performance validation"],
            ai_verifiable_outcomes=["Test strategy report created"],
            phase="research",
            priority=1
        )
        
        result = await agent.execute(task)
        print(f"Research completed: {result.success}")
        print(f"Files created: {len(result.files_created)}")
        
    asyncio.run(main())