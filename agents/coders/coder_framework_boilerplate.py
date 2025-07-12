#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase>=2.0.0",
#   "qdrant-client>=1.7.0",
#   "mistralai>=0.0.8",
#   "rich>=13.0.0",
#   "pydantic>=2.0.0",
#   "python-dotenv>=1.0.0",
# ]
# ///

"""Coder Framework Boilerplate Agent - Creates boilerplate code for projects"""

import json
import asyncio
from typing import Dict, Any, List
from pathlib import Path


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



class CoderFrameworkBoilerplateAgent(BaseAgent):
    """Creates boilerplate code for project frameworks and modules"""
    
    def __init__(self):
        super().__init__(
            agent_name="coder-framework-boilerplate",
            role_definition="Your specific task is to create boilerplate code for a project's framework or a particular module, ensuring the output supports an AI-verifiable and test-driven development process. The generated code and accompanying summary should be clear enough for human programmers to build upon. Your AI-verifiable outcome is the creation of specified boilerplate files at designated paths.",
            custom_instructions="""You MUST do select * from project_memorys where project_id = 'yjnrxnacpxdvseyetsgi' before every task. Before you answer, you must think through this problem step by step. When you write documents, you must avoid every '|' character and substitute it with '--', and also avoid patterns like ':---'. You will receive a description of the boilerplate task and a list of expected output file names in your prompt. Your task is to generate the necessary directory structure and code files. In addition to the basic structure, you must include comments and stubs that encourage best practices for testability and resilience, such as placeholders for TDD test files or comments indicating where error handling logic should go. As you create these files, you must save them to the correct paths. The creation of these files is your AI-verifiable outcome. To conclude, use \"attempt_completion\". Your summary must be a full, comprehensive natural language report detailing what you have accomplished, including a narrative of how you generated the boilerplate. It must list all the files that were created and state that it is now ready for further development. You must not use any colon-separated signal text."""
        )
    
    async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
        """Execute boilerplate code generation using Claude"""
        
        # Build comprehensive prompt for Claude
        prompt = self._build_agent_prompt(task, context)
        
        # Add boilerplate-specific instructions
        boilerplate_prompt = f"""
{prompt}

BOILERPLATE CODE GENERATION REQUIREMENTS:
Create boilerplate code for the project framework or module. You must:

1. Generate necessary directory structure and code files
2. Include comments and stubs that encourage TDD best practices
3. Add placeholders for test files and error handling logic
4. Ensure code supports AI-verifiable and test-driven development
5. Make code clear enough for human programmers to build upon
6. Avoid using '|' characters and ':---' patterns in documents

Your output should include:
- Clean, well-structured boilerplate code
- Comments indicating where specific logic should be added
- Stubs for testing and error handling
- Clear file organization and naming conventions

Generate the complete boilerplate code structure.
"""
        
        # Use Claude via base class
        claude_response = await self._run_claude(boilerplate_prompt)
        
        # Create files based on response
        files_created = await self._create_boilerplate_files(claude_response)
        
        # Record files with State Scribe
        await self._record_files_with_state_scribe(files_created)
        
        return AgentResult(
            success=True,
            outputs={
                "boilerplate_created": True,
                "files_created": len(files_created),
                "files": files_created,
                "message": f"Created {len(files_created)} boilerplate files"
            },
            files_created=files_created,
            files_modified=[],
            next_steps=["Review boilerplate structure", "Add specific business logic", "Create corresponding tests"]
        )
    
    async def _create_boilerplate_files(self, claude_response: str) -> List[str]:
        """Create boilerplate files from Claude's response"""
        
        files_created = []
        
        # Common boilerplate files to create
        boilerplate_files = [
            ("src/main.py", "main"),
            ("src/config.py", "config"),
            ("src/models.py", "models"),
            ("src/utils.py", "utils"),
            ("src/exceptions.py", "exceptions"),
            ("tests/test_main.py", "test_main"),
            ("tests/test_config.py", "test_config"),
            ("tests/test_models.py", "test_models"),
            ("tests/test_utils.py", "test_utils"),
            ("requirements.txt", "requirements"),
            ("README.md", "readme"),
            (".gitignore", "gitignore")
        ]
        
        for file_path, file_type in boilerplate_files:
            full_path = Path(file_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            content = self._generate_file_content(file_type, claude_response)
            full_path.write_text(content, encoding='utf-8')
            files_created.append(str(full_path))
        
        return files_created
    
    def _generate_file_content(self, file_type: str, claude_response: str) -> str:
        """Generate content for specific file types"""
        
        if file_type == "main":
            return f"""#!/usr/bin/env python3
\"\"\"
Main application entry point
Generated by coder-framework-boilerplate agent
\"\"\"

import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from models import *
from utils import *
from exceptions import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class Application:
    \"\"\"Main application class\"\"\"
    
    def __init__(self):
        self.config = Config()
        logger.info("Application initialized")
    
    def run(self):
        \"\"\"Run the application\"\"\"
        try:
            logger.info("Starting application...")
            # TODO: Add main application logic here
            
            # Claude Response Context:
            # {claude_response[:200]}...
            
            logger.info("Application running successfully")
            
        except Exception as e:
            logger.error(f"Application error: {{e}}")
            raise
    
    def shutdown(self):
        \"\"\"Shutdown the application\"\"\"
        logger.info("Shutting down application...")
        # TODO: Add cleanup logic here

def main():
    \"\"\"Main entry point\"\"\"
    app = Application()
    
    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Fatal error: {{e}}")
        sys.exit(1)
    finally:
        app.shutdown()

if __name__ == "__main__":
    main()
"""
        
        elif file_type == "config":
            return f"""#!/usr/bin/env python3
\"\"\"
Configuration management
Generated by coder-framework-boilerplate agent
\"\"\"

import os
from pathlib import Path
from typing import Dict, Any

class Config:
    \"\"\"Application configuration\"\"\"
    
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        \"\"\"Load configuration from environment and files\"\"\"
        
        # Environment variables
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Database configuration
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///app.db")
        
        # API configuration
        self.api_host = os.getenv("API_HOST", "localhost")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        
        # Security configuration
        self.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
        
        # Logging configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Claude Response Context:
        # {claude_response[:200]}...
        
        # TODO: Add more configuration options as needed
    
    def get_database_config(self) -> Dict[str, Any]:
        \"\"\"Get database configuration\"\"\"
        return {{
            "url": self.database_url,
            "echo": self.debug
        }}
    
    def get_api_config(self) -> Dict[str, Any]:
        \"\"\"Get API configuration\"\"\"
        return {{
            "host": self.api_host,
            "port": self.api_port,
            "debug": self.debug
        }}
    
    def is_production(self) -> bool:
        \"\"\"Check if running in production\"\"\"
        return self.environment == "production"
    
    def validate(self):
        \"\"\"Validate configuration\"\"\"
        if self.is_production() and self.secret_key == "dev-secret-key":
            raise ValueError("Production environment requires proper secret key")
        
        # TODO: Add more validation logic
"""
        
        elif file_type == "models":
            return f"""#!/usr/bin/env python3
\"\"\"
Data models
Generated by coder-framework-boilerplate agent
\"\"\"

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class BaseModel:
    \"\"\"Base model with common fields\"\"\"
    
    id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        \"\"\"Convert model to dictionary\"\"\"
        return {{
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }}
    
    def update_timestamp(self):
        \"\"\"Update the updated_at timestamp\"\"\"
        self.updated_at = datetime.now()

@dataclass
class User(BaseModel):
    \"\"\"User model\"\"\"
    
    username: str = ""
    email: str = ""
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        \"\"\"Convert user to dictionary\"\"\"
        data = super().to_dict()
        data.update({{
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active
        }})
        return data

@dataclass
class Task(BaseModel):
    \"\"\"Task model\"\"\"
    
    title: str = ""
    description: str = ""
    completed: bool = False
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        \"\"\"Convert task to dictionary\"\"\"
        data = super().to_dict()
        data.update({{
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "user_id": self.user_id
        }})
        return data

# Claude Response Context:
# {claude_response[:200]}...

# TODO: Add more models as needed
"""
        
        elif file_type == "utils":
            return f"""#!/usr/bin/env python3
\"\"\"
Utility functions
Generated by coder-framework-boilerplate agent
\"\"\"

import json
import hashlib
import uuid
from typing import Any, Dict, Optional
from datetime import datetime

def generate_id() -> str:
    \"\"\"Generate unique ID\"\"\"
    return str(uuid.uuid4())

def hash_password(password: str) -> str:
    \"\"\"Hash password for secure storage\"\"\"
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    \"\"\"Verify password against hash\"\"\"
    return hash_password(password) == hashed

def serialize_json(data: Any) -> str:
    \"\"\"Serialize data to JSON string\"\"\"
    try:
        return json.dumps(data, default=str, indent=2)
    except Exception as e:
        raise ValueError(f"Failed to serialize JSON: {{e}}")

def deserialize_json(json_str: str) -> Any:
    \"\"\"Deserialize JSON string to data\"\"\"
    try:
        return json.loads(json_str)
    except Exception as e:
        raise ValueError(f"Failed to deserialize JSON: {{e}}")

def format_datetime(dt: datetime) -> str:
    \"\"\"Format datetime for display\"\"\"
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def validate_email(email: str) -> bool:
    \"\"\"Basic email validation\"\"\"
    return "@" in email and "." in email

def sanitize_input(input_str: str) -> str:
    \"\"\"Sanitize user input\"\"\"
    # TODO: Add proper input sanitization
    return input_str.strip()

def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    \"\"\"Log error with context\"\"\"
    import logging
    logger = logging.getLogger(__name__)
    
    error_msg = f"Error: {{error}}"
    if context:
        error_msg += f" Context: {{context}}"
    
    logger.error(error_msg)

# Claude Response Context:
# {claude_response[:200]}...

# TODO: Add more utility functions as needed
"""
        
        elif file_type == "exceptions":
            return f"""#!/usr/bin/env python3
\"\"\"
Custom exceptions
Generated by coder-framework-boilerplate agent
\"\"\"

class ApplicationError(Exception):
    \"\"\"Base application exception\"\"\"
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "APP_ERROR"

class ValidationError(ApplicationError):
    \"\"\"Validation error exception\"\"\"
    
    def __init__(self, message: str, field: str = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field

class AuthenticationError(ApplicationError):
    \"\"\"Authentication error exception\"\"\"
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTH_ERROR")

class AuthorizationError(ApplicationError):
    \"\"\"Authorization error exception\"\"\"
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, "AUTHZ_ERROR")

class NotFoundError(ApplicationError):
    \"\"\"Resource not found exception\"\"\"
    
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{{resource}} not found", "NOT_FOUND")

class DatabaseError(ApplicationError):
    \"\"\"Database operation error\"\"\"
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DB_ERROR")

class ExternalServiceError(ApplicationError):
    \"\"\"External service error\"\"\"
    
    def __init__(self, service: str, message: str = "External service error"):
        super().__init__(f"{{service}}: {{message}}", "EXTERNAL_ERROR")
        self.service = service

# Claude Response Context:
# {claude_response[:200]}...

# TODO: Add more custom exceptions as needed
"""
        
        elif file_type.startswith("test_"):
            module_name = file_type.replace("test_", "")
            return f"""#!/usr/bin/env python3
\"\"\"
Tests for {module_name}
Generated by coder-framework-boilerplate agent
\"\"\"

import unittest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class Test{module_name.title()}(unittest.TestCase):
    \"\"\"Test cases for {module_name}\"\"\"
    
    def setUp(self):
        \"\"\"Set up test fixtures\"\"\"
        pass
    
    def tearDown(self):
        \"\"\"Clean up after tests\"\"\"
        pass
    
    def test_placeholder(self):
        \"\"\"Placeholder test - replace with actual tests\"\"\"
        # Claude Response Context:
        # {claude_response[:200]}...
        
        # TODO: Add actual test cases
        self.assertTrue(True, "Placeholder test")
    
    def test_error_handling(self):
        \"\"\"Test error handling\"\"\"
        # TODO: Add error handling tests
        pass
    
    def test_edge_cases(self):
        \"\"\"Test edge cases\"\"\"
        # TODO: Add edge case tests
        pass

if __name__ == '__main__':
    unittest.main()
"""
        
        elif file_type == "requirements":
            return f"""# Requirements file
# Generated by coder-framework-boilerplate agent

# Core dependencies
requests>=2.25.1
python-dotenv>=0.19.0
pydantic>=1.8.2

# Database
sqlalchemy>=1.4.0
alembic>=1.7.0

# Testing
pytest>=6.2.5
pytest-asyncio>=0.15.1
pytest-cov>=2.12.1

# Development
black>=21.9.0
flake8>=3.9.2
mypy>=0.910

# Claude Response Context:
# {claude_response[:200]}...

# TODO: Add project-specific dependencies
"""
        
        elif file_type == "readme":
            return f"""# Project

Generated by coder-framework-boilerplate agent

## Overview

This project provides a basic framework structure with boilerplate code designed to support test-driven development and AI-verifiable outcomes.

## Structure

```
src/
├── main.py          # Main application entry point
├── config.py        # Configuration management
├── models.py        # Data models
├── utils.py         # Utility functions
└── exceptions.py    # Custom exceptions

tests/
├── test_main.py     # Tests for main module
├── test_config.py   # Tests for config module
├── test_models.py   # Tests for models module
└── test_utils.py    # Tests for utils module
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python src/main.py
   ```

3. Run tests:
   ```bash
   pytest tests/
   ```

## Development

This boilerplate follows TDD principles:
- Write tests first
- Implement minimal code to pass tests
- Refactor while keeping tests green

## Claude Response Context
{claude_response[:300]}...

## TODO

- Add specific business logic
- Implement database models
- Add API endpoints
- Configure CI/CD pipeline
- Add more comprehensive tests
"""
        
        elif file_type == "gitignore":
            return f"""# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Generated by coder-framework-boilerplate agent
# Claude Response Context: {claude_response[:100]}...
"""
        
        else:
            return f"""# Generated by coder-framework-boilerplate agent
# File type: {file_type}
# Claude Response Context: {claude_response[:200]}...

# TODO: Add specific content for this file type
"""
    
    async def _record_files_with_state_scribe(self, files_created: List[str]):
        """Record created files with State Scribe"""
        
        files_to_record = []
        for file_path in files_created:
            files_to_record.append({
                "file_path": file_path,
                "memory_type": "boilerplate",
                "brief_description": f"Boilerplate file: {Path(file_path).name}",
                "elements_description": "Framework boilerplate code with TDD structure",
                "rationale": "Required for SPARC architecture phase completion"
            })
        
        # Delegate to State Scribe
        if files_to_record:
            await self._delegate_task(
                to_agent="orchestrator-state-scribe",
                task_description="Record boilerplate files in project memory",
                task_context={"files_to_record": files_to_record},
                priority=8
            )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: uv run sparc/agents/coders/coder_framework_boilerplate.py <task_json>")
        sys.exit(1)
    
    task_json = sys.argv[1]
    task = json.loads(task_json)
    
    task_payload = TaskPayload(
        description=task.get("description", ""),
        context=task.get("context", {}),
        priority=task.get("priority", 5)
    )
    
    agent = CoderFrameworkBoilerplateAgent()
    result = asyncio.run(agent._execute_task(task_payload, task.get("context", {})))
    print(json.dumps(result.dict(), indent=2))

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
