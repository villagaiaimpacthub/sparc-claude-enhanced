#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "rich>=13.0.0",
# ]
# ///

"""
SPARC Stop Hook - Runs when Claude Code finishes responding
Provides feedback and status updates for autonomous development
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

def announce_completion(hook_data: dict):
    """Announce Claude Code completion for SPARC project"""
    namespace = load_project_namespace()
    
    if namespace:
        console.print("[green]✅ SPARC: Claude Code session completed[/green]")
        console.print(f"[dim]📦 Project: {namespace}[/dim]")
        console.print("[dim]🔄 Autonomous agents continue working...[/dim]")
    else:
        console.print("[green]✅ All set and ready for your next step![/green]")

def main():
    """Main hook execution"""
    try:
        # Read hook data from stdin
        hook_data = json.loads(sys.stdin.read())
        
        # Announce completion
        announce_completion(hook_data)
        
    except json.JSONDecodeError:
        # Silent fail for invalid JSON
        pass
    except Exception:
        # Silent fail for any other errors
        pass

if __name__ == "__main__":
    main()