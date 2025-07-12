#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase>=2.0.0",
#   "python-dotenv>=1.0.0",
#   "rich>=13.0.0",
#   "pydantic>=2.0.0",
# ]
# ///

"""
SPARC Enhanced PostToolUse Hook - Integrates Layer 2 Intelligence Components
Captures file changes and triggers intelligent autonomous workflow continuation
"""

import json
import sys
import os
import time
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

try:
    from supabase import create_client, Client
    from dotenv import load_dotenv
    from rich.console import Console
    
    # Import Layer 2 intelligence components
    lib_path = Path(__file__).parent.parent / 'lib'
    sys.path.insert(0, str(lib_path))
    
    from enhanced_hook_orchestrator import get_orchestrator_instance
    from bmo_intent_tracker import BMOIntentTracker
    from interactive_question_engine import InteractiveQuestionEngine
    
except ImportError as e:
    print(f"Missing dependency: {e}")
    sys.exit(1)

console = Console()

def load_project_namespace() -> str:
    """Load namespace from project .sparc directory"""
    sparc_dir = Path.cwd() / '.sparc'
    namespace_file = sparc_dir / 'namespace'
    
    if namespace_file.exists():
        return namespace_file.read_text().strip()
    return 'default'

def get_supabase_client() -> Client:
    """Initialize Supabase client"""
    load_dotenv()
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        console.print("[red]Missing Supabase credentials in .env file[/red]")
        sys.exit(1)
    
    return create_client(url, key)

def update_sparc_memory(hook_data: Dict[str, Any], namespace: str):
    """Enhanced SPARC memory update with Layer 2 intelligence integration"""
    try:
        supabase = get_supabase_client()
        
        tool_name = hook_data.get('tool_name')
        tool_input = hook_data.get('tool_input', {})
        
        # Always track file changes for memory
        if tool_name in ['Write', 'Edit', 'MultiEdit']:
            file_path = tool_input.get('file_path')
            
            if file_path:
                # Update project memory (existing functionality)
                memory_data = {
                    'namespace': namespace,
                    'file_path': file_path,
                    'tool_used': tool_name,
                    'timestamp': datetime.now().isoformat(),
                    'session_id': hook_data.get('session_id'),
                    'content_preview': tool_input.get('content', '')[:500] if tool_input.get('content') else None
                }
                
                supabase.table('sparc_file_changes').insert(memory_data).execute()
                console.print(f"[green]📝 SPARC: Updated memory for {file_path}[/green]")
        
        # NEW: Enhanced intelligence processing
        workflow_continuation = process_with_intelligence(hook_data, supabase, namespace)
        
        if workflow_continuation:
            console.print(f"[green]🧠 SPARC Intelligence: Triggered {workflow_continuation.next_agent}[/green]")
        else:
            # Fallback to original workflow triggering for compatibility  
            if tool_name in ['Write', 'Edit', 'MultiEdit']:
                trigger_next_workflow(supabase, namespace, tool_input.get('file_path'), tool_name)
    
    except Exception as e:
        console.print(f"[red]❌ SPARC enhanced processing failed: {e}[/red]")

def process_with_intelligence(hook_data: Dict[str, Any], supabase: Client, namespace: str) -> Optional[Any]:
    """Process hook event with Layer 2 intelligence components"""
    try:
        # Initialize intelligence components
        orchestrator = get_orchestrator_instance(supabase, namespace)
        intent_tracker = BMOIntentTracker(supabase, namespace)
        
        tool_name = hook_data.get('tool_name', '')
        tool_input = hook_data.get('tool_input', {})
        file_path = tool_input.get('file_path', '')
        content = tool_input.get('content', '')
        
        # Check for explicit SPARC triggers
        if is_sparc_workflow_file(file_path):
            console.print("[blue]🎯 SPARC workflow file detected[/blue]")
            return orchestrator.process_post_tool_use_hook(hook_data)
        
        # Check for implicit SPARC triggers (intelligent detection)
        if should_trigger_sparc_assistance(tool_name, content, file_path):
            console.print("[blue]🤖 Intelligent SPARC assistance trigger detected[/blue]")
            return trigger_intelligent_assistance(hook_data, orchestrator, intent_tracker, namespace)
        
        # Extract intents from user interactions for intent model building
        if tool_name in ['Write', 'Edit'] and content:
            asyncio.run(intent_tracker.extract_intents_from_interaction(
                content, 'claude_code_interaction', {'file_path': file_path}
            ))
        
        return None
        
    except Exception as e:
        console.print(f"[yellow]Warning: Intelligence processing failed: {e}[/yellow]")
        return None

def is_sparc_workflow_file(file_path: str) -> bool:
    """Check if file is part of SPARC workflow"""
    return any(pattern in file_path for pattern in [
        '.sparc/questions/',
        '.sparc/responses/', 
        '.sparc/completions/',
        '/sparc',
        'sparc_'
    ])

def should_trigger_sparc_assistance(tool_name: str, content: str, file_path: str) -> bool:
    """Intelligent detection of when user might benefit from SPARC assistance"""
    
    if not isinstance(content, str) or len(content) < 20:
        return False
    
    content_lower = content.lower()
    
    # Don't trigger on read-only operations or system files
    if tool_name in ['Read', 'Glob', 'Grep', 'LS'] or 'node_modules' in file_path:
        return False
    
    # Strong indicators for SPARC assistance
    strong_triggers = [
        # User asking for help building things
        'help me build', 'help me create', 'help me implement',
        'i want to build', 'i need to create', 'how do i build',
        'how should i build', 'best way to build',
        
        # New project indicators
        'new project', 'start a project', 'create a project',
        'build an api', 'build a website', 'build an app',
        
        # User confusion/guidance needs
        'not sure how', 'how should i', 'what should i',
        'best approach', 'need guidance', 'help with architecture'
    ]
    
    # Project structure indicators
    structure_indicators = [
        'requirements.txt', 'package.json', 'dockerfile',
        'setup.py', 'pyproject.toml', '.gitignore'
    ]
    
    # Check for strong triggers
    if any(trigger in content_lower for trigger in strong_triggers):
        return True
    
    # Check for project structure creation
    if tool_name == 'Write' and any(indicator in file_path.lower() for indicator in structure_indicators):
        return True
    
    # Check for multiple related files being created (indicates new project)
    if tool_name == 'Write' and any(ext in file_path for ext in ['.py', '.js', '.ts']):
        # This is a code file - could indicate project start
        return 'main' in file_path.lower() or 'app' in file_path.lower() or 'index' in file_path.lower()
    
    return False

def trigger_intelligent_assistance(hook_data: Dict[str, Any], 
                                 orchestrator,
                                 intent_tracker: BMOIntentTracker,
                                 namespace: str) -> Optional[Any]:
    """Trigger intelligent SPARC assistance"""
    
    try:
        # Create SPARC directories if they don't exist
        sparc_dir = Path('.sparc')
        for subdir in ['questions', 'responses', 'completions']:
            (sparc_dir / subdir).mkdir(parents=True, exist_ok=True)
        
        # Generate intelligent assistance question
        question_content = generate_assistance_question(hook_data)
        
        # Create question file
        timestamp = int(datetime.now().timestamp())
        question_file = sparc_dir / 'questions' / f'auto_assist_{timestamp}.md'
        question_file.write_text(question_content)
        
        # Create synthetic hook data for the question
        question_hook_data = {
            'tool_name': 'Write',
            'tool_input': {
                'file_path': str(question_file),
                'content': question_content
            }
        }
        
        # Process through orchestrator
        return orchestrator.process_post_tool_use_hook(question_hook_data)
        
    except Exception as e:
        console.print(f"[red]Failed to trigger intelligent assistance: {e}[/red]")
        return None

def generate_assistance_question(hook_data: Dict[str, Any]) -> str:
    """Generate contextual assistance question based on user's action"""
    
    tool_input = hook_data.get('tool_input', {})
    content = tool_input.get('content', '')
    file_path = tool_input.get('file_path', '')
    
    content_lower = content.lower() if isinstance(content, str) else ''
    
    # Analyze context to generate appropriate question
    if any(keyword in content_lower for keyword in ['api', 'endpoint', 'fastapi', 'express']):
        project_type = "API"
        details = "I can help you build a complete REST API with proper authentication, validation, testing, and documentation."
        
    elif any(keyword in content_lower for keyword in ['website', 'frontend', 'react', 'vue', 'html']):
        project_type = "web application"
        details = "I can help you create a full web application with proper architecture, responsive design, and best practices."
        
    elif any(keyword in content_lower for keyword in ['database', 'model', 'schema', 'migration']):
        project_type = "database-driven application"
        details = "I can help you design proper database architecture, models, and data relationships."
        
    elif 'requirements.txt' in file_path or 'package.json' in file_path:
        project_type = "project"
        details = "I can help you structure your entire project with proper architecture, testing, and deployment setup."
        
    else:
        project_type = "development project"
        details = "I can help you build this with proper architecture, testing, security, and production readiness."
    
    return f"""# 🤖 SPARC Intelligent Assistance Detected

## Context Analysis
I detected that you're working on a **{project_type}** and might benefit from SPARC's autonomous development assistance.

## What I Observed
- **File**: `{file_path}`
- **Action**: {hook_data.get('tool_name', 'File operation')}
- **Context**: {content[:100]}{'...' if len(content) > 100 else ''}

## SPARC Can Provide
{details}

### Complete Development Assistance:
- 🎯 **Goal Clarification** - Define exact requirements with AI-verifiable outcomes
- 📋 **Technical Specifications** - Detailed specs with API documentation
- 🏗️ **System Architecture** - Scalable, maintainable design patterns
- 💻 **Implementation** - Production-ready code with best practices
- 🔒 **Security Review** - Vulnerability assessment and hardening
- ⚡ **Performance Optimization** - Speed and scalability improvements
- 🧪 **Testing Strategy** - Comprehensive test coverage
- 📚 **Documentation** - Complete API and user documentation

## Response Options

Please create a response file to let me know how you'd like to proceed:

**File**: `.sparc/responses/auto_assist_{int(datetime.now().timestamp())}_response.md`

```markdown
# SPARC Assistance Response

## Decision
[ ] Yes, start full SPARC autonomous development workflow
[ ] Yes, but just help with: [specify specific area]
[ ] No thanks, I'm good for now
[ ] Ask me later

## Project Details (if yes)
**What you're building**: [brief description]
**Primary goal**: [main objective]
**Timeline**: [any time constraints]
**Preferences**: [technology preferences, constraints, etc.]

## Immediate Priority (if yes)
[ ] Start with goal clarification and requirements
[ ] Help with architecture and design
[ ] Focus on implementation
[ ] Other: [specify]
```

---

**Note**: SPARC provides systematic, autonomous development while maintaining quality gates and ensuring all work aligns with your intentions.
"""

def trigger_next_workflow(supabase: Client, namespace: str, file_path: str, tool_name: str):
    """Trigger next agent in SPARC workflow based on file changes"""
    try:
        # Determine next agent based on file type and current project phase
        next_agent = determine_next_agent(file_path, tool_name)
        
        if next_agent:
            task_data = {
                'namespace': namespace,
                'from_agent': 'claude_code_hook',
                'to_agent': next_agent,
                'task_type': 'file_change_trigger',
                'task_payload': {
                    'task_id': f"hook_{datetime.now().isoformat()}",
                    'description': f"Process file change in {file_path}",
                    'context': {
                        'changed_file': file_path,
                        'tool_used': tool_name,
                        'trigger_type': 'file_change'
                    },
                    'phase': 'dynamic',
                    'priority': 7
                },
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            
            supabase.table('agent_tasks').insert(task_data).execute()
            console.print(f"[blue]🤖 SPARC: Triggered {next_agent} for {file_path}[/blue]")
    
    except Exception as e:
        console.print(f"[red]❌ Workflow trigger failed: {e}[/red]")

def determine_next_agent(file_path: str, tool_name: str) -> str:
    """Determine which agent should process this file change"""
    file_path = file_path.lower()
    
    # Code files -> State Scribe for memory recording
    if any(ext in file_path for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.rs']):
        return 'orchestrator-state-scribe'
    
    # Test files -> TDD Master
    elif 'test' in file_path or '.test.' in file_path:
        return 'tester-tdd-master'
    
    # Documentation -> Docs Writer
    elif any(ext in file_path for ext in ['.md', '.txt', '.rst']):
        return 'docs-writer-feature'
    
    # Config files -> Security Reviewer
    elif any(name in file_path for name in ['config', '.env', 'settings']):
        return 'security-reviewer-module'
    
    # Default to State Scribe for recording
    else:
        return 'orchestrator-state-scribe'

def main():
    """Main hook execution with production-ready error handling"""
    
    # Set up error logging
    error_log = setup_error_logging()
    
    try:
        # Validate environment first
        if not validate_environment():
            return  # Fail silently if SPARC not configured
        
        # Read and validate hook data
        hook_data = read_and_validate_hook_data()
        if not hook_data:
            return
        
        # Load project namespace with fallback
        namespace = load_project_namespace_safe()
        
        # Execute with comprehensive error handling
        execute_sparc_workflow_safe(hook_data, namespace, error_log)
        
    except Exception as e:
        handle_critical_error(e, error_log)

def setup_error_logging():
    """Setup error logging for production"""
    log_dir = Path('.sparc/logs')
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f'hook_errors_{datetime.now().strftime("%Y%m%d")}.log'
    return log_file

def validate_environment() -> bool:
    """Validate SPARC environment is properly configured"""
    try:
        # Check for required environment variables
        if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_KEY'):
            return False
        
        # Test database connection
        supabase = get_supabase_client()
        supabase.table('sparc_projects').select('id').limit(1).execute()
        
        return True
        
    except Exception:
        return False  # Fail silently if not configured

def read_and_validate_hook_data() -> Optional[Dict[str, Any]]:
    """Read and validate hook data with error handling"""
    try:
        # Read with timeout to prevent hanging
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Hook data read timeout")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)  # 5 second timeout
        
        try:
            raw_data = sys.stdin.read()
        finally:
            signal.alarm(0)  # Cancel timeout
        
        if not raw_data.strip():
            return None
        
        hook_data = json.loads(raw_data)
        
        # Validate required fields
        if not isinstance(hook_data, dict):
            return None
        
        if 'tool_name' not in hook_data:
            return None
        
        return hook_data
        
    except (json.JSONDecodeError, TimeoutError, ValueError):
        return None

def load_project_namespace_safe() -> str:
    """Load namespace with safe fallbacks"""
    try:
        sparc_dir = Path.cwd() / '.sparc'
        namespace_file = sparc_dir / 'namespace'
        
        if namespace_file.exists():
            namespace = namespace_file.read_text().strip()
            if namespace and len(namespace) > 0:
                return namespace
        
        # Fallback to directory name
        cwd_name = Path.cwd().name
        if cwd_name and cwd_name != '/':
            return f"project_{cwd_name}"
        
        return 'default'
        
    except Exception:
        return 'default'

def execute_sparc_workflow_safe(hook_data: Dict[str, Any], namespace: str, error_log: Path):
    """Execute SPARC workflow with comprehensive error handling"""
    try:
        # Update SPARC memory and trigger workflows
        update_sparc_memory_safe(hook_data, namespace, error_log)
        
    except Exception as e:
        log_workflow_error(e, hook_data, namespace, error_log)

def update_sparc_memory_safe(hook_data: Dict[str, Any], namespace: str, error_log: Path):
    """Enhanced SPARC memory update with production error handling"""
    try:
        supabase = get_supabase_client()
        
        tool_name = hook_data.get('tool_name')
        tool_input = hook_data.get('tool_input', {})
        
        # Always track file changes for memory (with error handling)
        if tool_name in ['Write', 'Edit', 'MultiEdit']:
            file_path = tool_input.get('file_path')
            
            if file_path and isinstance(file_path, str):
                try:
                    store_file_change_safe(supabase, namespace, hook_data, file_path, tool_name)
                except Exception as e:
                    log_error(f"Failed to store file change: {e}", error_log)
        
        # Enhanced intelligence processing with error isolation
        try:
            workflow_continuation = process_with_intelligence_safe(hook_data, supabase, namespace, error_log)
            
            if workflow_continuation:
                console.print(f"[green]🧠 SPARC: Triggered {workflow_continuation.next_agent}[/green]")
            else:
                # Fallback to original workflow triggering
                if tool_name in ['Write', 'Edit', 'MultiEdit'] and tool_input.get('file_path'):
                    trigger_next_workflow_safe(supabase, namespace, tool_input.get('file_path'), tool_name, error_log)
        
        except Exception as e:
            log_error(f"Intelligence processing failed: {e}", error_log)
            # Continue with basic workflow triggering
            if tool_name in ['Write', 'Edit', 'MultiEdit'] and tool_input.get('file_path'):
                trigger_next_workflow_safe(supabase, namespace, tool_input.get('file_path'), tool_name, error_log)
    
    except Exception as e:
        log_error(f"Memory update failed: {e}", error_log)

def store_file_change_safe(supabase: Client, namespace: str, hook_data: Dict[str, Any], file_path: str, tool_name: str):
    """Store file change with retry logic"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            memory_data = {
                'namespace': namespace,
                'file_path': file_path,
                'tool_used': tool_name,
                'timestamp': datetime.now().isoformat(),
                'session_id': hook_data.get('session_id'),
                'content_preview': str(hook_data.get('tool_input', {}).get('content', ''))[:500]
            }
            
            supabase.table('sparc_file_changes').insert(memory_data).execute()
            console.print(f"[green]📝 SPARC: Stored {file_path}[/green]")
            return
            
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(0.5 * (attempt + 1))  # Exponential backoff

def process_with_intelligence_safe(hook_data: Dict[str, Any], supabase: Client, namespace: str, error_log: Path) -> Optional[Any]:
    """Process with intelligence components with error isolation"""
    try:
        # Initialize components with error handling
        components = initialize_intelligence_components_safe(supabase, namespace, error_log)
        if not components:
            return None
        
        orchestrator, intent_tracker = components
        
        tool_name = hook_data.get('tool_name', '')
        tool_input = hook_data.get('tool_input', {})
        file_path = tool_input.get('file_path', '')
        content = tool_input.get('content', '')
        
        # Check for explicit SPARC triggers
        if is_sparc_workflow_file(file_path):
            console.print("[blue]🎯 SPARC workflow file detected[/blue]")
            return orchestrator.process_post_tool_use_hook(hook_data)
        
        # Check for implicit SPARC triggers with error handling
        try:
            if should_trigger_sparc_assistance(tool_name, content, file_path):
                console.print("[blue]🤖 Intelligent assistance trigger detected[/blue]")
                return trigger_intelligent_assistance_safe(hook_data, orchestrator, intent_tracker, namespace, error_log)
        except Exception as e:
            log_error(f"Trigger detection failed: {e}", error_log)
        
        # Extract intents with error handling
        try:
            if tool_name in ['Write', 'Edit'] and content and isinstance(content, str):
                # Run async intent extraction safely
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Create new thread for async operation
                        import threading
                        result = [None]
                        def run_intent_extraction():
                            new_loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(new_loop)
                            result[0] = new_loop.run_until_complete(
                                intent_tracker.extract_intents_from_interaction(
                                    content, 'claude_code_interaction', {'file_path': file_path}
                                )
                            )
                            new_loop.close()
                        
                        thread = threading.Thread(target=run_intent_extraction)
                        thread.start()
                        thread.join(timeout=5)  # 5 second timeout
                    else:
                        asyncio.run(intent_tracker.extract_intents_from_interaction(
                            content, 'claude_code_interaction', {'file_path': file_path}
                        ))
                except Exception:
                    pass  # Intent extraction is not critical
        except Exception as e:
            log_error(f"Intent extraction failed: {e}", error_log)
        
        return None
        
    except Exception as e:
        log_error(f"Intelligence processing error: {e}", error_log)
        return None

def initialize_intelligence_components_safe(supabase: Client, namespace: str, error_log: Path) -> Optional[Tuple[Any, Any]]:
    """Initialize intelligence components with error handling"""
    try:
        from enhanced_hook_orchestrator import get_orchestrator_instance
        from bmo_intent_tracker import BMOIntentTracker
        
        orchestrator = get_orchestrator_instance(supabase, namespace)
        intent_tracker = BMOIntentTracker(supabase, namespace)
        
        return (orchestrator, intent_tracker)
        
    except ImportError as e:
        log_error(f"Failed to import intelligence components: {e}", error_log)
        return None
    except Exception as e:
        log_error(f"Failed to initialize intelligence components: {e}", error_log)
        return None

def trigger_intelligent_assistance_safe(hook_data: Dict[str, Any], 
                                       orchestrator,
                                       intent_tracker,
                                       namespace: str,
                                       error_log: Path) -> Optional[Any]:
    """Trigger intelligent assistance with comprehensive error handling"""
    try:
        # Create SPARC directories safely
        sparc_dir = Path('.sparc')
        for subdir in ['questions', 'responses', 'completions']:
            try:
                (sparc_dir / subdir).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                log_error(f"Failed to create directory {subdir}: {e}", error_log)
                return None
        
        # Generate assistance question safely
        try:
            question_content = generate_assistance_question(hook_data)
        except Exception as e:
            log_error(f"Failed to generate assistance question: {e}", error_log)
            return None
        
        # Create question file safely
        try:
            timestamp = int(datetime.now().timestamp())
            question_file = sparc_dir / 'questions' / f'auto_assist_{timestamp}.md'
            question_file.write_text(question_content)
        except Exception as e:
            log_error(f"Failed to create question file: {e}", error_log)
            return None
        
        # Process through orchestrator safely
        try:
            question_hook_data = {
                'tool_name': 'Write',
                'tool_input': {
                    'file_path': str(question_file),
                    'content': question_content
                }
            }
            
            return orchestrator.process_post_tool_use_hook(question_hook_data)
        except Exception as e:
            log_error(f"Failed to process through orchestrator: {e}", error_log)
            return None
        
    except Exception as e:
        log_error(f"Intelligent assistance trigger failed: {e}", error_log)
        return None

def trigger_next_workflow_safe(supabase: Client, namespace: str, file_path: str, tool_name: str, error_log: Path):
    """Trigger next workflow with error handling"""
    try:
        next_agent = determine_next_agent(file_path, tool_name)
        
        if next_agent:
            task_data = {
                'namespace': namespace,
                'from_agent': 'claude_code_hook',
                'to_agent': next_agent,
                'task_type': 'file_change_trigger',
                'task_payload': {
                    'task_id': f"hook_{datetime.now().isoformat()}",
                    'description': f"Process file change in {file_path}",
                    'context': {
                        'changed_file': file_path,
                        'tool_used': tool_name,
                        'trigger_type': 'file_change'
                    },
                    'phase': 'dynamic',
                    'priority': 7
                },
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            
            supabase.table('agent_tasks').insert(task_data).execute()
            console.print(f"[blue]🤖 SPARC: Queued {next_agent} for {file_path}[/blue]")
    
    except Exception as e:
        log_error(f"Workflow trigger failed: {e}", error_log)

def log_error(message: str, error_log: Path):
    """Log error with timestamp"""
    try:
        timestamp = datetime.now().isoformat()
        error_entry = f"[{timestamp}] {message}\n"
        
        with open(error_log, 'a') as f:
            f.write(error_entry)
    except Exception:
        pass  # Can't log if logging fails

def log_workflow_error(error: Exception, hook_data: Dict[str, Any], namespace: str, error_log: Path):
    """Log workflow-specific errors"""
    try:
        error_details = {
            'error': str(error),
            'error_type': type(error).__name__,
            'hook_data': hook_data,
            'namespace': namespace,
            'timestamp': datetime.now().isoformat()
        }
        
        log_error(f"Workflow Error: {json.dumps(error_details, indent=2)}", error_log)
    except Exception:
        log_error(f"Workflow Error: {str(error)}", error_log)

def handle_critical_error(error: Exception, error_log: Path):
    """Handle critical errors that prevent hook execution"""
    try:
        log_error(f"CRITICAL ERROR: {str(error)}", error_log)
        
        # Try to create a failure signal
        try:
            failure_dir = Path('.sparc/failures')
            failure_dir.mkdir(parents=True, exist_ok=True)
            
            failure_file = failure_dir / f'hook_failure_{int(datetime.now().timestamp())}.log'
            failure_file.write_text(f"Hook execution failed: {str(error)}\nTimestamp: {datetime.now().isoformat()}")
        except Exception:
            pass
        
    except Exception:
        pass  # Ultimate fallback - fail silently

if __name__ == "__main__":
    main()