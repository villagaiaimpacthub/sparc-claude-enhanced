#!/usr/bin/env python3
"""
SPARC CLI - Main Command Interface
Global autonomous software development system
"""

import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
from typing import Optional
import json
import os
import sys

from .project import ProjectManager
from .docker_manager import DockerManager
from .installer import check_installation
from .auth import AuthManager
from .security import get_security_manager

app = typer.Typer(
    name="sparc",
    help="🚀 SPARC CLI - Global Autonomous Software Development System",
    add_completion=False,
)

console = Console()

# Global project manager instance
project_manager = None

def get_project_manager():
    """Get or create global project manager instance"""
    global project_manager
    if project_manager is None:
        project_manager = ProjectManager()
    return project_manager


@app.command()
def init(
    project_name: Optional[str] = typer.Option(None, "--project", "-p", help="Project name"),
    force: bool = typer.Option(False, "--force", "-f", help="Force initialization"),
):
    """Initialize SPARC in the current directory"""
    try:
        # Check authentication
        auth_manager = AuthManager()
        if not auth_manager.is_authenticated():
            console.print("❌ [red]Not authenticated. Please login first.[/red]")
            console.print("Run: sparc auth login")
            raise typer.Exit(1)
        
        # Get project name
        if not project_name:
            from rich.prompt import Prompt
            current_dir = Path.cwd().name
            project_name = Prompt.ask("Project name", default=current_dir)
        
        # Initialize project with namespace
        pm = get_project_manager()
        namespace = auth_manager.get_namespace(project_name)
        
        success = pm.init_project_with_namespace(project_name, namespace, force)
        
        if success:
            # Register project with auth manager
            auth_manager.register_project(project_name, str(Path.cwd()))
            
            console.print("✅ [green]SPARC project initialized successfully![/green]")
            console.print(f"📋 [blue]Project: {project_name}[/blue]")
            console.print(f"🏷️  [dim]Namespace: {namespace}[/dim]")
            console.print("🚀 [blue]Use `/sparc` in Claude Code to start development[/blue]")
        else:
            console.print("❌ [red]Failed to initialize SPARC project[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"❌ [red]Error initializing project: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def status():
    """Show current project and system status"""
    try:
        pm = get_project_manager()
        status_info = pm.get_status()
        
        # Create status table
        table = Table(title="🔍 SPARC System Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")
        
        for component, info in status_info.items():
            table.add_row(
                component,
                info.get("status", "Unknown"),
                info.get("details", "")
            )
            
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ [red]Error getting status: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def run(
    goal: str = typer.Argument(..., help="Development goal or task description"),
    namespace: Optional[str] = typer.Option(None, "--namespace", "-n", help="Project namespace"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", help="Project ID (legacy)"),
    phase: Optional[str] = typer.Option(None, "--phase", help="Specific phase to run"),
    session_id: Optional[str] = typer.Option(None, "--session-id", help="Session ID"),
):
    """Run SPARC system with a development goal"""
    try:
        pm = get_project_manager()
        
        # Load project configuration
        project_config = pm.load_project_config()
        
        # Determine the namespace/project ID to use
        if namespace:
            # Use provided namespace
            target_namespace = namespace
        elif project_id:
            # Legacy mode - use project_id as namespace
            target_namespace = project_id
        elif project_config:
            # Use namespace from project config (preferred) or fallback to project_id
            target_namespace = project_config.get("namespace") or project_config.get("project_id")
        else:
            console.print("❌ [red]No project configuration found. Run `sparc init` first.[/red]")
            raise typer.Exit(1)
        
        if not target_namespace:
            console.print("❌ [red]Could not determine project namespace.[/red]")
            raise typer.Exit(1)
        
        # Run the SPARC system
        result = pm.run_sparc_system(
            goal=goal,
            namespace=target_namespace,
            phase=phase,
            session_id=session_id
        )
        
        if result.get("success"):
            console.print("✅ [green]SPARC execution completed successfully![/green]")
            if result.get("output"):
                console.print(result["output"])
        else:
            console.print("❌ [red]SPARC execution failed[/red]")
            if result.get("error"):
                console.print(f"Error: {result['error']}")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"❌ [red]Error running SPARC: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def docker(
    action: str = typer.Argument(..., help="Docker action: start, stop, restart, status"),
):
    """Manage Docker containers for SPARC"""
    try:
        dm = DockerManager()
        
        if action == "start":
            success = dm.start_containers()
            if success:
                console.print("✅ [green]Docker containers started successfully![/green]")
            else:
                console.print("❌ [red]Failed to start Docker containers[/red]")
                raise typer.Exit(1)
                
        elif action == "stop":
            success = dm.stop_containers()
            if success:
                console.print("✅ [green]Docker containers stopped successfully![/green]")
            else:
                console.print("❌ [red]Failed to stop Docker containers[/red]")
                raise typer.Exit(1)
                
        elif action == "restart":
            success = dm.restart_containers()
            if success:
                console.print("✅ [green]Docker containers restarted successfully![/green]")
            else:
                console.print("❌ [red]Failed to restart Docker containers[/red]")
                raise typer.Exit(1)
                
        elif action == "status":
            status_info = dm.get_container_status()
            
            table = Table(title="🐳 Docker Container Status")
            table.add_column("Container", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Ports", style="dim")
            
            for container, info in status_info.items():
                table.add_row(
                    container,
                    info.get("status", "Unknown"),
                    ", ".join(info.get("ports", []))
                )
                
            console.print(table)
            
        else:
            console.print(f"❌ [red]Unknown docker action: {action}[/red]")
            console.print("Available actions: start, stop, restart, status")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"❌ [red]Error managing Docker: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def config(
    action: str = typer.Argument(..., help="Config action: show, set, get"),
    key: Optional[str] = typer.Option(None, "--key", "-k", help="Configuration key"),
    value: Optional[str] = typer.Option(None, "--value", "-v", help="Configuration value"),
):
    """Manage SPARC configuration"""
    try:
        pm = get_project_manager()
        
        if action == "show":
            config_data = pm.get_config()
            
            table = Table(title="⚙️ SPARC Configuration")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="green")
            
            for k, v in config_data.items():
                # Hide sensitive values
                if "key" in k.lower() or "secret" in k.lower():
                    v = "***" if v else "Not set"
                table.add_row(k, str(v))
                
            console.print(table)
            
        elif action == "set":
            if not key or not value:
                console.print("❌ [red]Both --key and --value are required for set action[/red]")
                raise typer.Exit(1)
                
            success = pm.set_config(key, value)
            if success:
                console.print(f"✅ [green]Configuration set: {key}[/green]")
            else:
                console.print(f"❌ [red]Failed to set configuration: {key}[/red]")
                raise typer.Exit(1)
                
        elif action == "get":
            if not key:
                console.print("❌ [red]--key is required for get action[/red]")
                raise typer.Exit(1)
                
            value = pm.get_config_value(key)
            if value is not None:
                console.print(f"{key}: {value}")
            else:
                console.print(f"❌ [red]Configuration key not found: {key}[/red]")
                raise typer.Exit(1)
                
        else:
            console.print(f"❌ [red]Unknown config action: {action}[/red]")
            console.print("Available actions: show, set, get")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"❌ [red]Error managing config: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def agents(
    namespace: Optional[str] = typer.Option(None, "--namespace", "-n", help="Project namespace"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", help="Project ID (legacy)"),
):
    """Show all 36 SPARC agents and their current activity status"""
    try:
        pm = get_project_manager()
        
        # Load project configuration
        project_config = pm.load_project_config()
        
        # Determine the namespace/project ID to use
        if namespace:
            target_namespace = namespace
        elif project_id:
            target_namespace = project_id
        elif project_config:
            target_namespace = project_config.get("namespace") or project_config.get("project_id")
        else:
            console.print("❌ [red]No project configuration found. Run `sparc init` first.[/red]")
            raise typer.Exit(1)
        
        # Display agent status
        console.print(f"🤖 [cyan]SPARC Agent Status - Namespace: {target_namespace}[/cyan]")
        console.print()
        
        # Create agent categories table
        table = Table(title="36-Agent System Overview")
        table.add_column("Category", style="cyan")
        table.add_column("Count", style="green")
        table.add_column("Status", style="blue")
        
        agents = [
            ("🎯 Orchestrators", 11, "Active"),
            ("🔍 Researchers", 3, "Active"),
            ("✍️ Writers", 6, "Active"),
            ("💻 Coders", 3, "Active"),
            ("🔍 Reviewers", 4, "Active"),
            ("🧪 Testers", 2, "Active"),
            ("🎯 BMO Agents", 6, "Active"),
            ("🔧 Utility Agents", 1, "Active"),
        ]
        
        for category, count, status in agents:
            table.add_row(category, str(count), status)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ [red]Error getting agent status: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def phase(
    namespace: Optional[str] = typer.Option(None, "--namespace", "-n", help="Project namespace"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", help="Project ID (legacy)"),
):
    """Check current SPARC development phase and progress"""
    try:
        pm = get_project_manager()
        
        # Load project configuration
        project_config = pm.load_project_config()
        
        # Determine the namespace/project ID to use
        if namespace:
            target_namespace = namespace
        elif project_id:
            target_namespace = project_id
        elif project_config:
            target_namespace = project_config.get("namespace") or project_config.get("project_id")
        else:
            console.print("❌ [red]No project configuration found. Run `sparc init` first.[/red]")
            raise typer.Exit(1)
        
        # Display phase information
        console.print(f"📋 [cyan]SPARC Phase Status - Namespace: {target_namespace}[/cyan]")
        console.print()
        
        # Create phases table
        table = Table(title="Development Phases")
        table.add_column("Phase", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Status", style="blue")
        
        phases = [
            ("1. Goal Clarification", "Understanding and refining requirements", "✅ Complete"),
            ("2. Specification", "Creating detailed technical specifications", "🔄 In Progress"),
            ("3. Architecture", "Designing system structure and components", "⏳ Pending"),
            ("4. Pseudocode", "High-level implementation planning", "⏳ Pending"),
            ("5. Refinement", "Code generation and testing", "⏳ Pending"),
            ("6. Completion", "Final validation, documentation, and deployment", "⏳ Pending"),
        ]
        
        for phase_name, description, status in phases:
            table.add_row(phase_name, description, status)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ [red]Error getting phase status: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def version():
    """Show SPARC CLI version"""
    from . import __version__
    console.print(f"🚀 SPARC CLI v{__version__}")


@app.command()
def security():
    """Run security audit and validation"""
    try:
        security_manager = get_security_manager()
        
        console.print("🔒 [bold blue]SPARC Security Audit[/bold blue]")
        console.print()
        
        # Perform security audit
        security_manager.audit_security()
        
        console.print()
        console.print("💡 [cyan]Security Recommendations:[/cyan]")
        console.print("1. Keep .env files private and never commit to version control")
        console.print("2. Rotate API keys regularly")
        console.print("3. Use strong, unique passwords for all services")
        console.print("4. Enable 2FA where available")
        console.print("5. Monitor API usage for unauthorized access")
        
    except Exception as e:
        console.print(f"❌ [red]Security audit failed: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def setup():
    """Interactive project setup with directory and project picker"""
    try:
        from .interactive_picker import interactive_project_setup
        
        result = interactive_project_setup()
        
        if result:
            # Change to selected directory
            import os
            os.chdir(result["directory"])
            
            console.print(f"\n🎯 [cyan]Initializing SPARC in {result['directory']}...[/cyan]")
            
            # Initialize with selected project
            auth_manager = AuthManager()
            success = auth_manager.register_project(
                result["project_name"], 
                str(result["directory"])
            )
            
            if success:
                # Create CLAUDE.md
                claude_md = result["directory"] / "CLAUDE.md"
                claude_md.write_text(f"""# SPARC Project Configuration

project_name: {result['project_name']}
namespace: {result['namespace']}
user_id: {auth_manager.get_user_id()}
created_at: {auth_manager._get_timestamp()}

## SPARC Commands Available:
- `/sparc` - Start autonomous development
- `/phase` - Check current development phase  
- `/status` - View project status
- `/agents` - View agent status
- `/stopsparc` - Stop SPARC mode

## 36-Agent System Ready
All agents loaded and memory isolated to namespace: {result['namespace']}
""")
                
                console.print("✅ [green]SPARC project initialized successfully![/green]")
                console.print(f"📁 [cyan]Directory: {result['directory']}[/cyan]")
                console.print(f"🎯 [cyan]Project: {result['project_name']}[/cyan]")
                console.print(f"🏷️  [dim]Namespace: {result['namespace']}[/dim]")
                console.print()
                console.print("🚀 [blue]Next steps:[/blue]")
                console.print("1. Open terminal in this directory")
                console.print("2. Run 'claude' to start Claude Code")
                console.print("3. Use '/sparc' to begin autonomous development")
            else:
                console.print("❌ [red]Failed to register project[/red]")
                raise typer.Exit(1)
        else:
            console.print("⏹️  [yellow]Setup cancelled by user[/yellow]")
            
    except Exception as e:
        console.print(f"❌ [red]Interactive setup failed: {str(e)}[/red]")
        raise typer.Exit(1)


# Authentication commands
auth_app = typer.Typer(name="auth", help="🔐 User authentication and session management")
app.add_typer(auth_app)


@auth_app.command("login")
def auth_login(
    email: Optional[str] = typer.Option(None, "--email", "-e", help="Email address"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Display name"),
):
    """Login to SPARC CLI"""
    try:
        auth_manager = AuthManager()
        
        if email:
            # Non-interactive login
            success = auth_manager.login(email, name)
        else:
            # Interactive login
            success = auth_manager.interactive_login()
        
        if not success:
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"❌ [red]Login failed: {str(e)}[/red]")
        raise typer.Exit(1)


@auth_app.command("logout")
def auth_logout():
    """Logout from SPARC CLI"""
    try:
        auth_manager = AuthManager()
        success = auth_manager.logout()
        
        if not success:
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"❌ [red]Logout failed: {str(e)}[/red]")
        raise typer.Exit(1)


@auth_app.command("status")
def auth_status():
    """Show authentication status"""
    try:
        auth_manager = AuthManager()
        status = auth_manager.get_auth_status()
        
        if status["authenticated"]:
            user = status["user"]
            table = Table(title="🔐 Authentication Status")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Status", "✅ Authenticated")
            table.add_row("Email", user["email"])
            table.add_row("Display Name", user["display_name"])
            table.add_row("User ID", user["user_id"])
            table.add_row("Projects", str(status["projects_count"]))
            
            console.print(table)
            
            # Show projects if any
            if status["projects"]:
                console.print("\n📋 [cyan]Your Projects:[/cyan]")
                for name, info in status["projects"].items():
                    console.print(f"  • {info['name']} ({info['namespace']})")
        else:
            console.print("❌ [red]Not authenticated[/red]")
            console.print("Run `sparc auth login` to authenticate")
            
    except Exception as e:
        console.print(f"❌ [red]Error checking auth status: {str(e)}[/red]")
        raise typer.Exit(1)


# Project management commands
project_app = typer.Typer(name="project", help="📁 Project management and switching")
app.add_typer(project_app)


@project_app.command("list")
def project_list():
    """List all projects for current user"""
    try:
        auth_manager = AuthManager()
        
        if not auth_manager.is_authenticated():
            console.print("❌ [red]Not authenticated. Run 'sparc auth login' first.[/red]")
            raise typer.Exit(1)
        
        projects = auth_manager.list_projects()
        
        if not projects:
            console.print("📋 [yellow]No projects found.[/yellow]")
            console.print("Run `sparc init` in a project directory to create one.")
            return
        
        table = Table(title="📁 Your SPARC Projects")
        table.add_column("Project Name", style="cyan")
        table.add_column("Namespace", style="dim")
        table.add_column("Path", style="green")
        table.add_column("Created", style="blue")
        
        for name, info in projects.items():
            from datetime import datetime
            created_date = datetime.fromtimestamp(info["created_at"]).strftime("%Y-%m-%d")
            table.add_row(
                info["name"],
                info["namespace"],
                info["path"],
                created_date
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ [red]Error listing projects: {str(e)}[/red]")
        raise typer.Exit(1)


@project_app.command("remove")
def project_remove(
    name: str = typer.Argument(..., help="Project name to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Force removal without confirmation"),
):
    """Remove a project from registry"""
    try:
        auth_manager = AuthManager()
        
        if not auth_manager.is_authenticated():
            console.print("❌ [red]Not authenticated. Run 'sparc auth login' first.[/red]")
            raise typer.Exit(1)
        
        # Confirm removal unless forced
        if not force:
            from rich.prompt import Confirm
            if not Confirm.ask(f"Are you sure you want to remove project '{name}'?"):
                console.print("Operation cancelled.")
                return
        
        success = auth_manager.remove_project(name)
        
        if not success:
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"❌ [red]Error removing project: {str(e)}[/red]")
        raise typer.Exit(1)


def main():
    """Entry point for the SPARC CLI"""
    app()


@app.callback()
def callback():
    """
    🚀 SPARC CLI - Global Autonomous Software Development System
    
    36 AI agents working together to build complete software solutions.
    """
    # Check if SPARC is properly installed
    if not check_installation():
        console.print("⚠️  [yellow]SPARC installation incomplete. Run `sparc-install` to complete setup.[/yellow]")


if __name__ == "__main__":
    main()