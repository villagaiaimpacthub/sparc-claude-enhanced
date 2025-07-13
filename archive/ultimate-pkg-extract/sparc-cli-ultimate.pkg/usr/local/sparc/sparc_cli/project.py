"""
Project Management for SPARC CLI
Handles project initialization, configuration, and lifecycle
"""

import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import uuid

from rich.console import Console
from rich.prompt import Prompt, Confirm

console = Console()


class ProjectManager:
    """Manages SPARC projects and their configurations"""
    
    def __init__(self):
        self.global_config_dir = Path.home() / ".sparc"
        self.global_config_file = self.global_config_dir / "config.json"
        self.templates_dir = Path(__file__).parent / "templates"
        
        # Ensure global config directory exists
        self.global_config_dir.mkdir(exist_ok=True)
        
        # Load global configuration
        self.global_config = self._load_global_config()
    
    def _load_global_config(self) -> Dict[str, Any]:
        """Load global SPARC configuration"""
        if self.global_config_file.exists():
            try:
                with open(self.global_config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                console.print(f"⚠️  [yellow]Warning: Could not load global config: {e}[/yellow]")
                return {}
        return {}
    
    def _save_global_config(self) -> bool:
        """Save global SPARC configuration"""
        try:
            with open(self.global_config_file, 'w') as f:
                json.dump(self.global_config, f, indent=2)
            return True
        except Exception as e:
            console.print(f"❌ [red]Error saving global config: {e}[/red]")
            return False
    
    def init_project_with_namespace(self, project_name: str, namespace: str, force: bool = False) -> bool:
        """Initialize SPARC in the current directory with namespace support"""
        return self._init_project_internal(project_name, namespace, force)
    
    def init_project(self, project_id: Optional[str] = None, force: bool = False) -> bool:
        """Initialize SPARC in the current directory (legacy mode)"""
        # Legacy mode - generate a simple project ID
        current_dir = Path.cwd()
        project_name = current_dir.name
        if not project_id:
            project_id = f"sparc-{uuid.uuid4().hex[:8]}"
        
        # Use legacy namespace format
        namespace = project_id
        return self._init_project_internal(project_name, namespace, force, legacy_mode=True)
    
    def _init_project_internal(self, project_name: str, namespace: str, force: bool = False, legacy_mode: bool = False) -> bool:
        """Internal project initialization with namespace support"""
        current_dir = Path.cwd()
        sparc_dir = current_dir / ".sparc"
        claude_dir = current_dir / ".claude"
        
        # Check if already initialized
        if sparc_dir.exists() and not force:
            console.print("⚠️  [yellow]SPARC already initialized in this directory[/yellow]")
            if not Confirm.ask("Reinitialize?"):
                return False
        
        try:
            # Create .sparc directory and configuration
            sparc_dir.mkdir(exist_ok=True)
            
            project_config = {
                "project_name": project_name,
                "namespace": namespace,
                "name": project_name,
                "created_at": time.time(),
                "sparc_cli_version": "1.0.0",
                "legacy_mode": legacy_mode,
                "settings": {
                    "auto_phase_progression": True,
                    "approval_required_phases": ["goal-clarification", "specification", "architecture"],
                    "max_concurrent_agents": 5,
                    "agent_timeout_minutes": 10
                }
            }
            
            # Add legacy project_id for backward compatibility
            if legacy_mode:
                project_config["project_id"] = namespace
            
            # Save project configuration
            with open(sparc_dir / "project.json", 'w') as f:
                json.dump(project_config, f, indent=2)
            
            # Create Claude Code commands directory
            claude_commands_dir = claude_dir / "commands"
            claude_commands_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy command templates
            self._create_claude_commands(claude_commands_dir, namespace, project_name)
            
            # Create session state file
            session_state = {
                "active": False,
                "namespace": namespace,
                "project_name": project_name,
                "current_phase": "goal-clarification",
                "session_id": None,
                "context": {}
            }
            
            # Legacy compatibility
            if legacy_mode:
                session_state["project_id"] = namespace
            
            with open(sparc_dir / "session_state.json", 'w') as f:
                json.dump(session_state, f, indent=2)
            
            # Update global config with project (legacy support)
            if "projects" not in self.global_config:
                self.global_config["projects"] = {}
            
            self.global_config["projects"][namespace] = {
                "path": str(current_dir),
                "name": project_name,
                "namespace": namespace,
                "created_at": time.time()
            }
            
            self._save_global_config()
            
            return True
            
        except Exception as e:
            console.print(f"❌ [red]Error initializing project: {e}[/red]")
            return False
    
    def _create_claude_commands(self, commands_dir: Path, namespace: str, project_name: Optional[str] = None):
        """Create Claude Code command files using templates"""
        from jinja2 import Template
        
        if not project_name:
            project_name = Path.cwd().name
        sparc_cli_version = "1.0.0"
        timestamp = time.time()
        
        template_vars = {
            "namespace": namespace,
            "project_id": namespace,  # Legacy compatibility
            "project_name": project_name,
            "sparc_cli_version": sparc_cli_version,
            "timestamp": timestamp
        }
        
        # Get template directory
        template_dir = self.templates_dir / "claude_commands"
        
        # Create command files from templates
        template_files = [
            "sparc.md.template",
            "stopsparc.md.template", 
            "phase.md.template",
            "status.md.template",
            "agents.md.template"
        ]
        
        for template_file in template_files:
            template_path = template_dir / template_file
            output_file = commands_dir / template_file.replace('.template', '')
            
            if template_path.exists():
                try:
                    with open(template_path, 'r') as f:
                        template_content = f.read()
                    
                    template = Template(template_content)
                    rendered_content = template.render(**template_vars)
                    
                    with open(output_file, 'w') as f:
                        f.write(rendered_content)
                        
                except Exception as e:
                    console.print(f"⚠️  [yellow]Warning: Could not create {output_file}: {e}[/yellow]")
                    # Fall back to basic template
                    self._create_basic_command(output_file, template_file, template_vars)
            else:
                # Create basic command if template doesn't exist
                self._create_basic_command(output_file, template_file, template_vars)
    
    def _create_basic_command(self, output_file: Path, template_file: str, template_vars: Dict[str, Any]):
        """Create basic command file if template is not available"""
        namespace = template_vars["namespace"]
        project_id = template_vars["project_id"]  # For legacy compatibility
        
        if "sparc.md" in str(output_file):
            content = f"""---
description: "Enter SPARC development mode with 36-agent autonomous system"
allowed-tools: ["bash", "write", "read", "edit"]
---

# SPARC Development Mode

🚀 **Enter Autonomous Development Mode**

!sparc run --project-id {project_id} "{{{{ user_input }}}}"

**Available Commands:**
- Continue describing your development goals naturally
- `/phase` - Check current development phase
- `/status` - View project status
- `/agents` - Show agent activity
- `/stopsparc` - Exit SPARC mode
"""
        elif "stopsparc.md" in str(output_file):
            content = f"""---
description: "Exit SPARC development mode"
allowed-tools: ["bash", "write", "read"]
---

# Exit SPARC Mode

🛑 **Exiting SPARC Development Mode**

!sparc config set active false --project-id {project_id}

SPARC development mode has been deactivated.
"""
        elif "status.md" in str(output_file):
            content = f"""---
description: "View detailed SPARC project status and system information"
allowed-tools: ["bash", "read"]
---

# SPARC Project Status

📊 **System Status Overview**

!sparc status --project-id {project_id}

**Available Commands:**
- Continue describing your project naturally
- `/phase` - Check current phase
- `/agents` - Show active agents
- `/stopsparc` - Exit SPARC mode
"""
        elif "phase.md" in str(output_file):
            content = f"""---
description: "Check current SPARC development phase and progress"
allowed-tools: ["bash", "read"]
---

# SPARC Phase Status

📋 **Current Phase Information**

!sparc phase --project-id {project_id}

**Available Commands:**
- Continue with your development requests
- `/status` - View detailed project status
- `/agents` - Show active agents
- `/stopsparc` - Exit SPARC mode
"""
        elif "agents.md" in str(output_file):
            content = f"""---
description: "Show all 36 SPARC agents and their current activity status"
allowed-tools: ["bash", "read"]
---

# SPARC Agent Status

🤖 **36-Agent System Overview**

!sparc agents --project-id {project_id}

**Available Commands:**
- Continue with your development requests
- `/phase` - Check current phase
- `/status` - View project status
- `/stopsparc` - Exit SPARC mode
"""
        else:
            content = "# SPARC Command\n\nCommand not implemented yet."
        
        with open(output_file, 'w') as f:
            f.write(content)
    
    def load_project_config(self) -> Optional[Dict[str, Any]]:
        """Load project configuration from current directory"""
        sparc_dir = Path.cwd() / ".sparc"
        config_file = sparc_dir / "project.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                console.print(f"⚠️  [yellow]Warning: Could not load project config: {e}[/yellow]")
        
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system and project status"""
        status = {}
        
        # Project status
        project_config = self.load_project_config()
        if project_config:
            status["Project"] = {
                "status": "✅ Active",
                "details": f"ID: {project_config['project_id']}"
            }
        else:
            status["Project"] = {
                "status": "❌ Not initialized",
                "details": "Run `sparc init` to initialize"
            }
        
        # Docker status
        try:
            from .docker_manager import DockerManager
            dm = DockerManager()
            docker_status = dm.get_container_status()
            
            if docker_status:
                running_containers = sum(1 for info in docker_status.values() 
                                       if info.get("status") == "running")
                total_containers = len(docker_status)
                status["Docker"] = {
                    "status": f"✅ {running_containers}/{total_containers} running",
                    "details": ", ".join(docker_status.keys())
                }
            else:
                status["Docker"] = {
                    "status": "❌ Not running",
                    "details": "Run `sparc docker start`"
                }
        except Exception:
            status["Docker"] = {
                "status": "❓ Unknown",
                "details": "Docker not accessible"
            }
        
        # Global config status
        status["Global Config"] = {
            "status": "✅ Loaded" if self.global_config else "⚠️  Default",
            "details": f"Projects: {len(self.global_config.get('projects', {}))}"
        }
        
        return status
    
    def run_sparc_system(self, goal: str, namespace: str, phase: Optional[str] = None, 
                        session_id: Optional[str] = None) -> Dict[str, Any]:
        """Run the SPARC system with a development goal using namespace-based isolation"""
        try:
            # This would integrate with the existing SPARC orchestrator
            # For now, we'll create a placeholder that would call the actual system
            
            # Use the real SPARC orchestrator with all 36 agents
            package_root = Path(__file__).parent.parent
            cmd = [
                "python", "-c", f"""
import sys
sys.path.append('{package_root}')
from lib.sparc_orchestrator import SPARCOrchestrator
import asyncio

async def main():
    orchestrator = SPARCOrchestrator('{namespace}')
    await orchestrator.run_autonomous_development('{goal}', {repr(phase)})

asyncio.run(main())
"""
            ]
            
            if session_id:
                cmd.extend(["--session-id", session_id])
            
            # Run the command (this would be the actual SPARC system)
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_config(self) -> Dict[str, Any]:
        """Get all configuration values"""
        config = {}
        
        # Global config
        config.update(self.global_config)
        
        # Project config
        project_config = self.load_project_config()
        if project_config:
            config["project"] = project_config
        
        return config
    
    def set_config(self, key: str, value: str) -> bool:
        """Set a configuration value"""
        try:
            # Handle nested keys like "project.setting"
            if "." in key:
                keys = key.split(".")
                current = self.global_config
                
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                
                current[keys[-1]] = value
            else:
                self.global_config[key] = value
            
            return self._save_global_config()
            
        except Exception as e:
            console.print(f"❌ [red]Error setting config: {e}[/red]")
            return False
    
    def get_config_value(self, key: str) -> Any:
        """Get a specific configuration value"""
        try:
            if "." in key:
                keys = key.split(".")
                current = self.global_config
                
                for k in keys:
                    if k in current:
                        current = current[k]
                    else:
                        return None
                
                return current
            else:
                return self.global_config.get(key)
                
        except Exception:
            return None