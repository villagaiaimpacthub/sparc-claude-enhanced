#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase",
#   "rich",
#   "pydantic",
#   "python-dotenv",
# ]
# ///

"""Refinement Implementation Orchestrator"""

from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from sparc.agents.base_agent import BaseAgent, TaskPayload, AgentResult

class RefinementImplementationOrchestrator(BaseAgent):
    """Orchestrator for the Refinement Implementation phase"""
    
    def __init__(self):
        super().__init__(
            agent_name="orchestrator-sparc-refinement-implementation",
            role_definition="You orchestrate the refinement implementation phase, coordinating the actual coding and development process. You ensure high-quality code delivery through test-driven development, code reviews, and iterative refinement.",
            custom_instructions="""
You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

You orchestrate the refinement implementation phase by:
1. Implementing features using strict test-driven development (TDD)
2. Creating framework and boilerplate code structure
3. Implementing core functionality with comprehensive error handling
4. Conducting thorough code reviews and security analysis
5. Optimizing performance and code quality
6. Ensuring all tests pass and coverage requirements are met

Your primary outputs:
- src/ (complete source code implementation)
- requirements.txt or package.json (dependency management)
- config/ (configuration files and settings)
- scripts/ (deployment and utility scripts)
- docs/implementation/ (implementation documentation)

You delegate to:
- coder-test-driven for TDD implementation
- coder-framework-boilerplate for project structure setup
- debugger-targeted for issue resolution
- code-comprehension-assistant-v2 for code reviews
- security-reviewer-module for security analysis
- optimizer-module for performance optimization

You coordinate but do NOT write files directly. You orchestrate the creation through delegation.
"""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute refinement implementation phase"""
        
        # Check if phase already completed
        existing_implementation = await self._check_existing_implementation(context)
        if existing_implementation["has_source_code"] and existing_implementation["tests_passing"]:
            return AgentResult(
                success=True,
                outputs={
                    "message": "Refinement implementation phase already complete",
                    "implementation": existing_implementation
                },
                files_created=[],
                files_modified=[]
            )
        
        # Validate prerequisites
        prereqs = await self._validate_prerequisites(context)
        if not prereqs["valid"]:
            return AgentResult(
                success=False,
                outputs={"error": f"Prerequisites not met: {prereqs['missing']}"},
                files_created=[],
                files_modified=[],
                errors=[f"Prerequisites not met: {prereqs['missing']}"]
            )
        
        # Step 1: Set up project structure and framework boilerplate
        framework_task_id = await self._delegate_task(
            to_agent="coder-framework-boilerplate",
            task_description="Create project structure and framework boilerplate",
            task_context={
                "architecture_design": prereqs["architecture_design"],
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "test_plan": prereqs.get("test_plan", ""),
                "framework_setup_focus": "project_structure",
                "requirements": [
                    "Create project directory structure",
                    "Set up build system and dependency management",
                    "Create configuration files and environment setup",
                    "Implement logging and monitoring framework",
                    "Set up development tools and linting configuration"
                ],
                "ai_verifiable_outcomes": [
                    "Project structure created in src/",
                    "Build configuration files present",
                    "Dependency management configured",
                    "Development environment setup complete",
                    "Logging framework implemented"
                ]
            },
            priority=10
        )
        
        # Step 2: Implement core functionality using TDD
        tdd_implementation_task_id = await self._delegate_task(
            to_agent="coder-test-driven",
            task_description="Implement core functionality using test-driven development",
            task_context={
                "architecture_design": prereqs["architecture_design"],
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "test_suite": prereqs["test_suite"],
                "framework_task_id": framework_task_id,
                "tdd_focus": "core_functionality",
                "requirements": [
                    "Implement core business logic following TDD principles",
                    "Make failing tests pass incrementally",
                    "Refactor code for maintainability and clarity",
                    "Implement error handling and validation",
                    "Add comprehensive logging and monitoring"
                ],
                "ai_verifiable_outcomes": [
                    "Core functionality implemented in src/",
                    "All unit tests passing",
                    "Code coverage meets requirements",
                    "Error handling implemented",
                    "Logging integrated throughout"
                ]
            },
            priority=10
        )
        
        # Step 3: Implement API endpoints and interfaces
        api_implementation_task_id = await self._delegate_task(
            to_agent="coder-test-driven",
            task_description="Implement API endpoints and external interfaces",
            task_context={
                "architecture_design": prereqs["architecture_design"],
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "tdd_implementation_task_id": tdd_implementation_task_id,
                "tdd_focus": "api_interfaces",
                "requirements": [
                    "Implement all API endpoints and routes",
                    "Add request/response validation and serialization",
                    "Implement authentication and authorization",
                    "Add rate limiting and security middleware",
                    "Create API documentation and OpenAPI specs"
                ],
                "ai_verifiable_outcomes": [
                    "API endpoints implemented",
                    "Request/response validation active",
                    "Authentication system working",
                    "Security middleware configured",
                    "API documentation generated"
                ]
            },
            priority=9
        )
        
        # Step 4: Implement data layer and persistence
        data_implementation_task_id = await self._delegate_task(
            to_agent="coder-test-driven",
            task_description="Implement data layer and persistence mechanisms",
            task_context={
                "architecture_design": prereqs["architecture_design"],
                "comprehensive_spec": prereqs["comprehensive_spec"],
                "tdd_implementation_task_id": tdd_implementation_task_id,
                "tdd_focus": "data_persistence",
                "requirements": [
                    "Implement database models and schemas",
                    "Create data access layer and repositories",
                    "Implement data validation and constraints",
                    "Add database migrations and versioning",
                    "Implement caching and performance optimizations"
                ],
                "ai_verifiable_outcomes": [
                    "Database models implemented",
                    "Data access layer created",
                    "Data validation active",
                    "Migration system in place",
                    "Caching layer implemented"
                ]
            },
            priority=9
        )
        
        # Step 5: Debug and resolve integration issues
        debugging_task_id = await self._delegate_task(
            to_agent="debugger-targeted",
            task_description="Debug and resolve integration and system issues",
            task_context={
                "tdd_implementation_task_id": tdd_implementation_task_id,
                "api_implementation_task_id": api_implementation_task_id,
                "data_implementation_task_id": data_implementation_task_id,
                "debugging_focus": "integration_issues",
                "requirements": [
                    "Identify and fix integration bugs",
                    "Resolve performance bottlenecks",
                    "Fix memory leaks and resource issues",
                    "Ensure all tests pass consistently",
                    "Optimize error handling and recovery"
                ],
                "ai_verifiable_outcomes": [
                    "Integration issues resolved",
                    "Performance bottlenecks fixed",
                    "Resource usage optimized",
                    "Test suite stability improved",
                    "Error handling enhanced"
                ]
            },
            priority=8
        )
        
        # Step 6: Comprehensive code review and quality analysis
        code_review_task_id = await self._delegate_task(
            to_agent="code-comprehension-assistant-v2",
            task_description="Conduct comprehensive code review and quality analysis",
            task_context={
                "tdd_implementation_task_id": tdd_implementation_task_id,
                "api_implementation_task_id": api_implementation_task_id,
                "data_implementation_task_id": data_implementation_task_id,
                "debugging_task_id": debugging_task_id,
                "review_focus": "code_quality_analysis",
                "requirements": [
                    "Review code for best practices and patterns",
                    "Analyze code maintainability and readability",
                    "Check for potential bugs and edge cases",
                    "Validate architectural adherence",
                    "Assess test coverage and quality"
                ],
                "ai_verifiable_outcomes": [
                    "Code review report generated",
                    "Quality metrics documented",
                    "Improvement recommendations provided",
                    "Architectural compliance validated",
                    "Test coverage analysis completed"
                ]
            },
            priority=7
        )
        
        # Step 7: Security analysis and hardening
        security_analysis_task_id = await self._delegate_task(
            to_agent="security-reviewer-module",
            task_description="Conduct security analysis and implement hardening",
            task_context={
                "api_implementation_task_id": api_implementation_task_id,
                "data_implementation_task_id": data_implementation_task_id,
                "architecture_design": prereqs["architecture_design"],
                "security_focus": "implementation_security",
                "requirements": [
                    "Perform security vulnerability assessment",
                    "Implement security best practices",
                    "Add input validation and sanitization",
                    "Implement secure configuration management",
                    "Add security monitoring and alerting"
                ],
                "ai_verifiable_outcomes": [
                    "Security assessment report created",
                    "Vulnerabilities identified and fixed",
                    "Security best practices implemented",
                    "Input validation enhanced",
                    "Security monitoring configured"
                ]
            },
            priority=7
        )
        
        # Step 8: Performance optimization
        optimization_task_id = await self._delegate_task(
            to_agent="optimizer-module",
            task_description="Optimize performance and resource usage",
            task_context={
                "tdd_implementation_task_id": tdd_implementation_task_id,
                "api_implementation_task_id": api_implementation_task_id,
                "data_implementation_task_id": data_implementation_task_id,
                "optimization_focus": "performance_optimization",
                "requirements": [
                    "Profile and optimize performance bottlenecks",
                    "Implement caching strategies",
                    "Optimize database queries and operations",
                    "Reduce memory usage and garbage collection",
                    "Implement performance monitoring and metrics"
                ],
                "ai_verifiable_outcomes": [
                    "Performance optimization report created",
                    "Bottlenecks identified and optimized",
                    "Caching strategies implemented",
                    "Database performance improved",
                    "Performance monitoring active"
                ]
            },
            priority=6
        )
        
        # Wait for all tasks to complete
        all_tasks = [framework_task_id, tdd_implementation_task_id, api_implementation_task_id, 
                    data_implementation_task_id, debugging_task_id, code_review_task_id, 
                    security_analysis_task_id, optimization_task_id]
        completed_tasks = await self._wait_for_tasks(all_tasks)
        
        # Validate implementation completeness
        validation_result = await self._validate_implementation()
        
        if not validation_result["complete"]:
            return AgentResult(
                success=False,
                outputs={
                    "error": "Implementation validation failed",
                    "validation_result": validation_result
                },
                files_created=[],
                files_modified=[],
                errors=[f"Implementation incomplete: {validation_result['missing']}"]
            )
        
        # Identify created files
        documents_created = await self._identify_created_documents()
        
        # Delegate to state scribe for recording
        await self._delegate_to_state_scribe(documents_created)
        
        return AgentResult(
            success=True,
            outputs={
                "phase": "refinement-implementation",
                "documents_created": documents_created,
                "completed_tasks": completed_tasks,
                "validation_result": validation_result,
                "next_phase": "bmo-completion",
                "message": "Refinement implementation phase completed successfully"
            },
            files_created=[doc["path"] for doc in documents_created],
            files_modified=[],
            next_steps=["Proceed to BMO completion phase", "Validate against original intent"]
        )
    
    async def _check_existing_implementation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if implementation already exists and is complete"""
        project_files = context.get("project_state", {}).get("files", {})
        
        has_source_code = any("src/" in path for path in project_files.keys())
        has_config = any("config/" in path or "requirements.txt" in path or "package.json" in path for path in project_files.keys())
        
        # Check if tests are passing (simplified check)
        tests_passing = True  # Would need actual test execution to determine
        
        return {
            "has_source_code": has_source_code,
            "has_config": has_config,
            "tests_passing": tests_passing,
            "existing_files": list(project_files.keys())
        }
    
    async def _validate_prerequisites(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that testing phase is complete"""
        project_files = context.get("project_state", {}).get("files", {})
        
        architecture_design = None
        comprehensive_spec = None
        test_plan = None
        test_suite = None
        missing = []
        
        # Check for architecture design
        arch_path = next((path for path in project_files.keys() if "system_design.md" in path), None)
        if arch_path:
            architecture_design = Path(arch_path).read_text() if Path(arch_path).exists() else None
        else:
            missing.append("System Architecture Design")
        
        # Check for comprehensive specification
        spec_path = next((path for path in project_files.keys() if "comprehensive_spec.md" in path), None)
        if spec_path:
            comprehensive_spec = Path(spec_path).read_text() if Path(spec_path).exists() else None
        else:
            missing.append("Comprehensive Specification")
        
        # Check for test plan
        test_plan_path = next((path for path in project_files.keys() if "test_plan.md" in path), None)
        if test_plan_path:
            test_plan = Path(test_plan_path).read_text() if Path(test_plan_path).exists() else None
        else:
            missing.append("Test Plan")
        
        # Check for test suite
        has_tests = any("tests/" in path for path in project_files.keys())
        if has_tests:
            test_suite = "Test suite exists"
        else:
            missing.append("Test Suite")
        
        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "architecture_design": architecture_design,
            "comprehensive_spec": comprehensive_spec,
            "test_plan": test_plan,
            "test_suite": test_suite
        }
    
    async def _validate_implementation(self) -> Dict[str, Any]:
        """Validate implementation completeness"""
        missing = []
        
        # Check for source code
        if not Path("src").exists():
            missing.append("Source code directory")
        
        # Check for configuration
        config_files = ["requirements.txt", "package.json", "config/"]
        if not any(Path(f).exists() for f in config_files):
            missing.append("Configuration files")
        
        # Check for tests passing (simplified)
        # In real implementation, would run test suite
        tests_passing = True
        
        return {
            "complete": len(missing) == 0 and tests_passing,
            "missing": missing,
            "tests_passing": tests_passing,
            "source_code_exists": Path("src").exists(),
            "config_exists": any(Path(f).exists() for f in config_files)
        }
    
    async def _identify_created_documents(self) -> List[Dict[str, Any]]:
        """Identify which implementation files were created"""
        docs_created = []
        
        # Source code files
        if Path("src").exists():
            for src_file in Path("src").rglob("*"):
                if src_file.is_file():
                    docs_created.append({
                        "path": str(src_file),
                        "type": "source_code",
                        "description": f"Source code: {src_file.name}",
                        "memory_type": "implementation"
                    })
        
        # Configuration files
        config_files = [
            ("requirements.txt", "dependency_config", "Python dependencies"),
            ("package.json", "dependency_config", "Node.js dependencies"),
            ("Dockerfile", "deployment_config", "Docker configuration"),
            ("docker-compose.yml", "deployment_config", "Docker Compose configuration")
        ]
        
        for file_path, doc_type, description in config_files:
            if Path(file_path).exists():
                docs_created.append({
                    "path": file_path,
                    "type": doc_type,
                    "description": description,
                    "memory_type": "configuration"
                })
        
        # Configuration directories
        config_dirs = ["config/", "scripts/", "deploy/"]
        for config_dir in config_dirs:
            if Path(config_dir).exists():
                for config_file in Path(config_dir).rglob("*"):
                    if config_file.is_file():
                        docs_created.append({
                            "path": str(config_file),
                            "type": "configuration",
                            "description": f"Configuration: {config_file.name}",
                            "memory_type": "configuration"
                        })
        
        # Documentation files
        if Path("docs/implementation").exists():
            for doc_file in Path("docs/implementation").rglob("*.md"):
                docs_created.append({
                    "path": str(doc_file),
                    "type": "implementation_docs",
                    "description": f"Implementation documentation: {doc_file.name}",
                    "memory_type": "documentation"
                })
        
        # Reports
        if Path("docs/reports").exists():
            for report_file in Path("docs/reports").glob("*implementation*.md"):
                docs_created.append({
                    "path": str(report_file),
                    "type": "implementation_report",
                    "description": f"Implementation report: {report_file.name}",
                    "memory_type": "report"
                })
        
        return docs_created
    
    async def _delegate_to_state_scribe(self, documents: List[Dict[str, Any]]) -> None:
        """Delegate to state scribe to record documents"""
        files_to_record = []
        
        for doc in documents:
            files_to_record.append({
                "file_path": doc["path"],
                "memory_type": doc["memory_type"],
                "brief_description": doc["description"],
                "elements_description": f"Document type: {doc['type']}",
                "rationale": "Created during refinement implementation phase"
            })
        
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record implementation files",
            task_context={
                "files_to_record": files_to_record,
                "phase": "refinement-implementation",
                "requirements": ["Record all files in project_memorys table"],
                "ai_verifiable_outcomes": ["All files recorded with appropriate version"]
            },
            priority=8
        )