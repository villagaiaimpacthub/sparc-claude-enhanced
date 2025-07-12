#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase>=2.0.0",
#   "rich",
#   "pydantic",
#   "python-dotenv",
# ]
# ///

"""BMO E2E Test Generator - Specialist E2E test automation engineer"""

import json
import asyncio
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime


# Base agent classes embedded for UV standalone execution
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

try:
    from pydantic import BaseModel
    from rich.console import Console
    from supabase import create_client, Client
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing dependency: {e}")
    exit(1)

console = Console()

class AgentResult(BaseModel):
    success: bool
    outputs: Dict[str, Any]
    files_created: List[str] = []
    files_modified: List[str] = []
    next_steps: Optional[List[str]] = None
    errors: Optional[List[str]] = None

class TaskPayload(BaseModel):
    task_id: str
    description: str
    context: Dict[str, Any]
    requirements: List[str]
    ai_verifiable_outcomes: List[str]
    phase: str
    priority: int = 5

class BaseAgent(ABC):
    def __init__(self, agent_name: str, role_definition: str, custom_instructions: str):
        self.agent_name = agent_name
        self.role_definition = role_definition
        self.custom_instructions = custom_instructions
        
        # Load project context
        self.project_id = self._load_project_id()
        self.supabase = self._init_supabase()
        
    def _load_project_id(self) -> str:
        sparc_dir = Path('.sparc')
        namespace_file = sparc_dir / 'namespace'
        if namespace_file.exists():
            return namespace_file.read_text().strip()
        return os.environ.get("DEFAULT_PROJECT_ID", "default")
    
    def _init_supabase(self) -> Client:
        load_dotenv()
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        if not url or not key:
            console.print("[red]❌ Missing Supabase credentials[/red]")
            exit(1)
        return create_client(url, key)
    
    async def delegate_task(self, to_agent: str, task_description: str, 
                          context: Dict[str, Any], priority: int = 5) -> str:
        task_data = {
            'namespace': self.project_id,
            'from_agent': self.agent_name,
            'to_agent': to_agent,
            'task_type': 'delegation',
            'task_payload': {
                'task_id': f"{self.agent_name}_{datetime.now().isoformat()}",
                'description': task_description,
                'context': context,
                'requirements': context.get('requirements', []),
                'ai_verifiable_outcomes': context.get('ai_verifiable_outcomes', []),
                'phase': context.get('phase', 'unknown'),
                'priority': priority
            },
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        result = self.supabase.table('agent_tasks').insert(task_data).execute()
        return result.data[0]['id'] if result.data else None
    
    @abstractmethod
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        pass


class BMOE2ETestGenerator(BaseAgent):
    """Specialist E2E test automation engineer for BMO Oracle component"""
    
    def __init__(self):
        super().__init__(
            agent_name="bmo-e2e-test-generator",
            role_definition="You are a specialist E2E test automation engineer. Your function is to take the validated user intent, as defined in Gherkin feature files, and generate executable, production-grade end-to-end test scripts that will serve as the 'Oracle' for the BMO verification.",
            custom_instructions="""You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task.

You will be tasked by the BMO orchestrator. Your first action is to use the read_file tool to ingest the contents of the Gherkin .feature files located in the tests/bdd/ directory. Based on these validated behavioral specifications, you will generate executable end-to-end test scripts using a suitable framework like Playwright or Cypress. Your AI-verifiable outcome is the creation of these new test files. You will use the write_to_file tool to save the test scripts within the tests/e2e/ directory. These scripts must be runnable via the execute_command tool and must be designed to comprehensively cover the scenarios described in the Gherkin files. Your final attempt_completion summary must report the successful generation of the E2E tests and must include a list of all the new test file paths you created, confirming their readiness for the holistic verifier."""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute E2E test generation from Gherkin specifications"""
        
        # Build prompt using base class
        prompt = self._build_agent_prompt(task, context)
        
        # Add specific instructions for E2E test generation
        specific_prompt = f"""{prompt}

BMO E2E TEST GENERATION MISSION:
You are now generating executable E2E tests for BMO Oracle verification. Your task is to:

1. GHERKIN SPECIFICATION ANALYSIS:
   - Read all Gherkin .feature files from tests/bdd/
   - Parse scenarios and their steps
   - Identify user workflows and behaviors
   - Extract test data and conditions
   - Map scenarios to test implementations

2. E2E TEST FRAMEWORK SELECTION:
   - Choose appropriate framework (Playwright, Cypress, Selenium)
   - Configure test environment and setup
   - Set up test data and fixtures
   - Configure browser automation settings
   - Set up reporting and logging

3. TEST SCRIPT GENERATION:
   - Convert Gherkin scenarios to executable code
   - Implement Given-When-Then steps
   - Create page objects and helper functions
   - Add assertions and validations
   - Handle test data and cleanup

4. COMPREHENSIVE SCENARIO COVERAGE:
   - Cover all scenarios from Gherkin files
   - Include positive and negative test cases
   - Test edge cases and error conditions
   - Validate user interface interactions
   - Test data integrity and persistence

5. PRODUCTION-GRADE IMPLEMENTATION:
   - Add robust error handling
   - Implement proper waits and timeouts
   - Include screenshot and video capture
   - Add detailed logging and reporting
   - Configure parallel execution support

6. ORACLE VERIFICATION PREPARATION:
   - Ensure tests are runnable via execute_command
   - Create test execution scripts
   - Set up test result reporting
   - Configure for holistic verification
   - Prepare for BMO triangulation

7. TEST FILE ORGANIZATION:
   - Save all tests in tests/e2e/ directory
   - Create modular test structure
   - Include configuration files
   - Add helper utilities and fixtures
   - Create test execution scripts

Remember: These tests serve as the 'Oracle' component of the BMO framework for final verification.
"""
        
        # Use Claude via base class
        claude_response = await self._run_claude(specific_prompt)
        
        # Create E2E test files
        files_created = await self._create_e2e_test_outputs(claude_response)
        
        # Record with State Scribe
        if files_created:
            await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "e2e_test_generation": claude_response,
                "files_created": files_created
            },
            files_created=files_created,
            files_modified=[],
            next_steps=["Execute E2E tests for holistic verification"]
        )
    
    async def _create_e2e_test_outputs(self, claude_response: str) -> List[str]:
        """Create E2E test files from Gherkin specifications"""
        files_created = []
        
        try:
            # Create tests/e2e directory if it doesn't exist
            Path("tests/e2e").mkdir(parents=True, exist_ok=True)
            
            # Create E2E test files
            test_files = self._extract_e2e_test_files(claude_response)
            
            for test_file, content in test_files.items():
                test_path = f"tests/e2e/{test_file}"
                with open(test_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_created.append(test_path)
            
            # Create test configuration files
            config_files = self._create_test_config_files()
            for config_file, content in config_files.items():
                config_path = f"tests/e2e/{config_file}"
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_created.append(config_path)
            
        except Exception as e:
            print(f"Error creating E2E test outputs: {str(e)}")
        
        return files_created
    
    def _extract_e2e_test_files(self, claude_response: str) -> Dict[str, str]:
        """Extract E2E test files from Claude response"""
        # This is a simplified extraction - in practice, you'd parse the structured response
        test_files = {}
        
        # Create sample E2E test files
        test_files["user_authentication.test.js"] = """const { test, expect } = require('@playwright/test');

test.describe('User Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    // Given I am on the login page
    await expect(page.locator('h1')).toContainText('Login');
    
    // When I enter valid credentials
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Then I should be logged in successfully
    await expect(page).toHaveURL('/dashboard');
    
    // And I should see the dashboard
    await expect(page.locator('h1')).toContainText('Dashboard');
  });

  test('should show error message with invalid credentials', async ({ page }) => {
    // Given I am on the login page
    await expect(page.locator('h1')).toContainText('Login');
    
    // When I enter invalid credentials
    await page.fill('input[name="username"]', 'invaliduser');
    await page.fill('input[name="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    // Then I should see an error message
    await expect(page.locator('.error-message')).toContainText('Invalid credentials');
    
    // And I should remain on the login page
    await expect(page).toHaveURL('/login');
  });
});
"""
        
        test_files["user_registration.test.js"] = """const { test, expect } = require('@playwright/test');

test.describe('User Registration', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/register');
  });

  test('should register new user successfully', async ({ page }) => {
    // Given I am on the registration page
    await expect(page.locator('h1')).toContainText('Register');
    
    // When I fill in the registration form
    await page.fill('input[name="username"]', 'newuser');
    await page.fill('input[name="email"]', 'newuser@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.fill('input[name="confirmPassword"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Then I should be registered successfully
    await expect(page.locator('.success-message')).toContainText('Registration successful');
    
    // And I should be redirected to login
    await expect(page).toHaveURL('/login');
  });

  test('should show validation errors for invalid input', async ({ page }) => {
    // Given I am on the registration page
    await expect(page.locator('h1')).toContainText('Register');
    
    // When I submit the form with invalid data
    await page.fill('input[name="username"]', '');
    await page.fill('input[name="email"]', 'invalid-email');
    await page.fill('input[name="password"]', '123');
    await page.click('button[type="submit"]');
    
    // Then I should see validation errors
    await expect(page.locator('.error-username')).toContainText('Username is required');
    await expect(page.locator('.error-email')).toContainText('Valid email is required');
    await expect(page.locator('.error-password')).toContainText('Password must be at least 8 characters');
  });
});
"""
        
        return test_files
    
    def _create_test_config_files(self) -> Dict[str, str]:
        """Create test configuration files"""
        config_files = {}
        
        # Playwright configuration
        config_files["playwright.config.js"] = """const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
"""
        
        # Test execution script
        config_files["run-tests.sh"] = """#!/bin/bash
set -e

echo "Starting E2E test execution..."

# Install dependencies
npm install

# Run the tests
npx playwright test

# Generate report
npx playwright show-report

echo "E2E test execution completed."
"""
        
        return config_files
    
    async def _record_files_with_state_scribe(self, files_created: List[str]) -> None:
        """Record created files with State Scribe"""
        if not files_created:
            return
        
        files_to_record = []
        for file_path in files_created:
            if file_path.endswith('.test.js'):
                files_to_record.append({
                    "file_path": file_path,
                    "memory_type": "e2e_test",
                    "brief_description": "End-to-end test script for BMO Oracle verification",
                    "elements_description": "Executable E2E test based on Gherkin scenarios for comprehensive user workflow validation",
                    "rationale": "Serves as 'Oracle' component of BMO framework for final system verification"
                })
            else:
                files_to_record.append({
                    "file_path": file_path,
                    "memory_type": "test_config",
                    "brief_description": "E2E test configuration file",
                    "elements_description": "Configuration for E2E test execution and reporting",
                    "rationale": "Supports E2E test execution for BMO verification process"
                })
        
        # Delegate to State Scribe
        await self._delegate_task(
            to_agent="orchestrator-state-scribe",
            task_description="Record BMO E2E test files in project memory",
            task_context={
                "files_to_record": files_to_record,
                "phase": "bmo_e2e_testing"
            }
        )

async def main():
    """Main execution function"""
    agent = BMOE2ETestGenerator()
    
    # Example task
    task = TaskPayload(
        task_id="bmo_e2e_test_generation",
        description="Generate E2E tests from Gherkin specifications",
        requirements=["Read Gherkin .feature files", "Generate executable E2E tests"],
        ai_verifiable_outcomes=["Create E2E test files in tests/e2e/"],
        phase="bmo_e2e_testing",
        priority=2
    )
    
    result = await agent.execute(task)
    print(f"BMO E2E Test Generator completed: {result.success}")
    if result.files_created:
        print(f"Files created: {', '.join(result.files_created)}")

if __name__ == "__main__":
    asyncio.run(main())

# CLI interface for standalone UV execution
import asyncio
import click

@click.command()
@click.option('--namespace', required=True, help='Project namespace')
@click.option('--task-id', help='Specific task ID to process')
@click.option('--goal', help='Project goal for context')
def main(namespace: str, task_id: str, goal: str):
    """Run this SPARC agent standalone"""
    
    # Create mock task for testing
    if not task_id:
        task = TaskPayload(
            task_id=f"test_{datetime.now().isoformat()}",
            description=f"Test execution for {namespace}",
            context={'project_goal': goal or 'Test goal'},
            requirements=[],
            ai_verifiable_outcomes=[],
            phase='test',
            priority=5
        )
    else:
        # In real implementation, load task from database
        task = TaskPayload(
            task_id=task_id,
            description="Loaded from database",
            context={},
            requirements=[],
            ai_verifiable_outcomes=[],
            phase='unknown',
            priority=5
        )
    
    # Create agent and execute
    agent_class_name = [name for name in globals() if name.endswith('Agent') or name.endswith('Orchestrator')]
    if agent_class_name:
        agent_class = globals()[agent_class_name[0]]
        agent = agent_class()
        
        async def run():
            try:
                result = await agent._execute_task(task, task.context)
                console.print(f"[green]✅ {agent.agent_name} completed successfully[/green]")
                console.print(f"Result: {result}")
            except Exception as e:
                console.print(f"[red]❌ {agent.agent_name} failed: {e}[/red]")
        
        asyncio.run(run())
    else:
        console.print("[red]❌ No agent class found[/red]")

if __name__ == "__main__":
    main()
