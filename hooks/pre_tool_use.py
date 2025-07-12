#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "rich>=13.0.0",
# ]
# ///

"""
SPARC PreToolUse Hook - Provides context before tool execution
Runs before every tool operation in Claude Code
"""

import json
import sys
from pathlib import Path

try:
    from rich.console import Console
except ImportError:
    print("Missing dependency: rich")
    sys.exit(1)

console = Console()

def load_project_namespace() -> str:
    """Load namespace from project .sparc directory"""
    sparc_dir = Path.cwd() / '.sparc'
    namespace_file = sparc_dir / 'namespace'
    
    if namespace_file.exists():
        return namespace_file.read_text().strip()
    return None

def provide_sparc_context(hook_data: dict):
    """Provide SPARC context for the upcoming tool operation"""
    namespace = load_project_namespace()
    
    if namespace:
        tool_name = hook_data.get('tool_name')
        tool_input = hook_data.get('tool_input', {})
        
        # Log the upcoming operation
        if tool_name in ['Write', 'Edit', 'MultiEdit']:
            file_path = tool_input.get('file_path', 'unknown')
            console.print(f"[dim]🤖 SPARC: {tool_name} operation on {file_path}[/dim]")
        
        # Return approval (no blocking)
        return {"decision": "approve"}
    
    return {"decision": "approve"}

def main():
    """Main hook execution"""
    try:
        # Read hook data from stdin
        hook_data = json.loads(sys.stdin.read())
        
        # Provide context and return decision
        result = provide_sparc_context(hook_data)
        
        # Output decision for Claude Code
        if result:
            print(json.dumps(result))
        
    except json.JSONDecodeError:
        # Silent fail for invalid JSON
        print(json.dumps({"decision": "approve"}))
    except Exception:
        # Silent fail for any other errors
        print(json.dumps({"decision": "approve"}))

if __name__ == "__main__":
    main()