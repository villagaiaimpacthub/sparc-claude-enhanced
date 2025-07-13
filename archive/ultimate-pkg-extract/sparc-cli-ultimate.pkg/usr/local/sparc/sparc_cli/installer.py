#!/usr/bin/env python3
"""
SPARC CLI Interactive Installer
Cross-platform installation and configuration system
"""

import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

from .docker_manager import DockerManager

app = typer.Typer(name="sparc-install")
console = Console()


class SPARCInstaller:
    """Interactive installer for SPARC CLI system"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.global_config_dir = Path.home() / ".sparc"
        self.config_file = self.global_config_dir / "config.json"
        self.docker_manager = DockerManager()
        
        # Ensure config directory exists
        self.global_config_dir.mkdir(exist_ok=True)
        
        # Installation steps
        self.steps = [
            "System Requirements Check",
            "Docker Installation",
            "Docker Configuration",
            "Supabase Configuration",
            "Agent System Setup",
            "Verification"
        ]
    
    def run_installation(self):
        """Run the complete installation process"""
        console.print(Panel.fit(
            "🚀 SPARC CLI Installation\n"
            "Global Autonomous Software Development System\n"
            "Setting up 36 AI agents for your development workflow",
            title="Welcome to SPARC",
            style="bold blue"
        ))
        
        console.print("\n📋 [cyan]Installation Steps:[/cyan]")
        for i, step in enumerate(self.steps, 1):
            console.print(f"  {i}. {step}")
        
        if not Confirm.ask("\n🚀 Ready to start installation?"):
            console.print("Installation cancelled.")
            return False
        
        # Run installation steps
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                
                # Step 1: System Requirements Check
                task = progress.add_task("Checking system requirements...", total=1)
                if not self._check_system_requirements():
                    return False
                progress.update(task, completed=1)
                
                # Step 2: Docker Installation
                task = progress.add_task("Setting up Docker...", total=1)
                if not self._setup_docker():
                    return False
                progress.update(task, completed=1)
                
                # Step 3: Docker Configuration
                task = progress.add_task("Configuring Docker containers...", total=1)
                if not self._configure_docker():
                    return False
                progress.update(task, completed=1)
                
                # Step 4: Supabase Configuration
                task = progress.add_task("Configuring Supabase...", total=1)
                if not self._configure_supabase():
                    return False
                progress.update(task, completed=1)
                
                # Step 5: Agent System Setup
                task = progress.add_task("Setting up agent system...", total=1)
                if not self._setup_agent_system():
                    return False
                progress.update(task, completed=1)
                
                # Step 6: Verification
                task = progress.add_task("Verifying installation...", total=1)
                if not self._verify_installation():
                    return False
                progress.update(task, completed=1)
            
            self._show_completion_message()
            return True
            
        except KeyboardInterrupt:
            console.print("\n❌ [red]Installation interrupted by user[/red]")
            return False
        except Exception as e:
            console.print(f"\n❌ [red]Installation failed: {e}[/red]")
            return False
    
    def _check_system_requirements(self) -> bool:
        """Check system requirements"""
        console.print("\n🔍 [cyan]Checking System Requirements...[/cyan]")
        
        requirements = {
            "Python": {"min_version": "3.11", "current": f"{sys.version_info.major}.{sys.version_info.minor}"},
            "Platform": {"supported": ["windows", "darwin", "linux"], "current": self.system},
            "Architecture": {"supported": ["x86_64", "arm64"], "current": platform.machine()},
        }
        
        # Check Python version
        if sys.version_info < (3, 11):
            console.print(f"❌ [red]Python 3.11+ required, found {sys.version_info.major}.{sys.version_info.minor}[/red]")
            return False
        
        # Check platform
        if self.system not in ["windows", "darwin", "linux"]:
            console.print(f"❌ [red]Unsupported platform: {self.system}[/red]")
            return False
        
        # Display requirements table
        table = Table(title="System Requirements")
        table.add_column("Component", style="cyan")
        table.add_column("Required", style="dim")
        table.add_column("Current", style="green")
        table.add_column("Status", style="bold")
        
        for component, info in requirements.items():
            if component == "Python":
                status = "✅ Pass" if sys.version_info >= (3, 11) else "❌ Fail"
            elif component == "Platform":
                status = "✅ Pass" if self.system in info["supported"] else "❌ Fail"
            elif component == "Architecture":
                status = "✅ Pass" if platform.machine() in info["supported"] else "⚠️  Check"
            else:
                status = "✅ Pass"
            
            table.add_row(
                component,
                str(info.get("min_version", ", ".join(info.get("supported", [])))),
                info["current"],
                status
            )
        
        console.print(table)
        
        console.print("✅ [green]System requirements check passed![/green]")
        return True
    
    def _setup_docker(self) -> bool:
        """Set up Docker installation"""
        console.print("\n🐳 [cyan]Setting up Docker...[/cyan]")
        
        # Check if Docker is already installed
        docker_status = self.docker_manager.check_docker_installation()
        
        if docker_status["docker_available"] and docker_status["docker_compose_available"]:
            console.print("✅ [green]Docker is already installed![/green]")
            console.print(f"Docker version: {docker_status['docker_version']}")
            console.print(f"Docker Compose version: {docker_status['docker_compose_version']}")
            return True
        
        # Docker not installed, provide installation instructions
        console.print("⚠️  [yellow]Docker not found. Installation required.[/yellow]")
        
        if not Confirm.ask("Would you like installation instructions?"):
            console.print("❌ [red]Docker is required for SPARC. Installation cancelled.[/red]")
            return False
        
        self.docker_manager.install_docker()
        
        # Wait for user to install Docker
        console.print("\n⏳ [blue]Please install Docker and return here.[/blue]")
        
        while True:
            if Confirm.ask("Have you installed Docker?"):
                # Re-check Docker installation
                docker_status = self.docker_manager.check_docker_installation()
                if docker_status["docker_available"] and docker_status["docker_compose_available"]:
                    console.print("✅ [green]Docker installation verified![/green]")
                    break
                else:
                    console.print("❌ [red]Docker still not detected. Please check your installation.[/red]")
                    if not Confirm.ask("Try again?"):
                        return False
            else:
                if not Confirm.ask("Docker is required. Continue waiting?"):
                    return False
        
        return True
    
    def _configure_docker(self) -> bool:
        """Configure Docker containers"""
        console.print("\n⚙️  [cyan]Configuring Docker containers...[/cyan]")
        
        # Set up Docker configuration
        if not self.docker_manager.setup_docker_config():
            console.print("❌ [red]Failed to set up Docker configuration[/red]")
            return False
        
        # Start containers
        console.print("🚀 [blue]Starting SPARC containers...[/blue]")
        if not self.docker_manager.start_containers():
            console.print("❌ [red]Failed to start Docker containers[/red]")
            
            # Offer to continue without Docker
            if Confirm.ask("Continue installation without Docker? (Some features will be limited)"):
                return True
            else:
                return False
        
        console.print("✅ [green]Docker containers configured and started![/green]")
        return True
    
    def _configure_supabase(self) -> bool:
        """Configure Supabase connection"""
        console.print("\n🗄️  [cyan]Configuring Supabase...[/cyan]")
        
        console.print("SPARC uses Supabase for cloud database and real-time features.")
        console.print("You'll need a Supabase account and project.")
        
        if not Confirm.ask("Do you have a Supabase account?"):
            console.print("📝 [blue]Please create a Supabase account:[/blue]")
            console.print("1. Go to https://supabase.com")
            console.print("2. Sign up for a free account")
            console.print("3. Create a new project")
            console.print("4. Return here with your project details")
            
            if not Confirm.ask("Have you created a Supabase project?"):
                console.print("⚠️  [yellow]Supabase configuration skipped. You can configure it later.[/yellow]")
                return True
        
        # Get Supabase configuration
        supabase_config = {}
        
        console.print("\n🔧 [blue]Enter your Supabase project details:[/blue]")
        
        supabase_config["project_url"] = Prompt.ask(
            "Supabase Project URL",
            default="https://your-project.supabase.co"
        )
        
        supabase_config["anon_key"] = Prompt.ask(
            "Supabase Anon Key",
            password=True
        )
        
        supabase_config["service_role_key"] = Prompt.ask(
            "Supabase Service Role Key (optional)",
            password=True,
            default=""
        )
        
        # Save configuration
        config = self._load_config()
        config["supabase"] = supabase_config
        self._save_config(config)
        
        console.print("✅ [green]Supabase configuration saved![/green]")
        return True
    
    def _setup_agent_system(self) -> bool:
        """Set up the agent system"""
        console.print("\n🤖 [cyan]Setting up agent system...[/cyan]")
        
        # Configure agent system settings
        agent_config = {
            "max_concurrent_agents": IntPrompt.ask(
                "Maximum concurrent agents",
                default=5,
                show_default=True
            ),
            "agent_timeout_minutes": IntPrompt.ask(
                "Agent timeout (minutes)",
                default=10,
                show_default=True
            ),
            "auto_phase_progression": Confirm.ask(
                "Enable automatic phase progression?",
                default=True
            ),
            "approval_required_phases": [
                "goal-clarification",
                "specification", 
                "architecture"
            ] if Confirm.ask("Require approval for critical phases?", default=True) else []
        }
        
        # Save agent configuration
        config = self._load_config()
        config["agent_system"] = agent_config
        self._save_config(config)
        
        console.print("✅ [green]Agent system configured![/green]")
        return True
    
    def _verify_installation(self) -> bool:
        """Verify the installation"""
        console.print("\n🔍 [cyan]Verifying installation...[/cyan]")
        
        verification_results = {}
        
        # Check global config
        config = self._load_config()
        verification_results["Global Config"] = "✅ Pass" if config else "❌ Fail"
        
        # Check Docker
        docker_status = self.docker_manager.check_docker_installation()
        verification_results["Docker"] = "✅ Pass" if docker_status["docker_available"] else "❌ Fail"
        
        # Check containers
        container_status = self.docker_manager.get_container_status()
        running_containers = sum(1 for info in container_status.values() 
                               if info.get("status") == "running")
        verification_results["Containers"] = f"✅ {running_containers} running" if running_containers > 0 else "⚠️  Not running"
        
        # Check Supabase config
        supabase_configured = "supabase" in config and config["supabase"].get("project_url")
        verification_results["Supabase"] = "✅ Configured" if supabase_configured else "⚠️  Not configured"
        
        # Display verification results
        table = Table(title="Installation Verification")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="bold")
        
        for component, status in verification_results.items():
            table.add_row(component, status)
        
        console.print(table)
        
        # Check if critical components are working
        critical_failures = [
            k for k, v in verification_results.items() 
            if v.startswith("❌") and k in ["Global Config", "Docker"]
        ]
        
        if critical_failures:
            console.print(f"❌ [red]Critical components failed: {', '.join(critical_failures)}[/red]")
            return False
        
        console.print("✅ [green]Installation verification passed![/green]")
        return True
    
    def _show_completion_message(self):
        """Show installation completion message"""
        console.print("\n" + "="*60)
        console.print(Panel.fit(
            "🎉 SPARC CLI Installation Complete!\n\n"
            "Your global autonomous development system is ready.\n"
            "You can now use SPARC in any project directory.\n\n"
            "Next steps:\n"
            "1. Navigate to a project directory\n"
            "2. Run: sparc init\n"
            "3. Use /sparc in Claude Code to start development\n\n"
            "For help: sparc --help",
            title="Installation Complete",
            style="bold green"
        ))
        
        console.print("\n📖 [cyan]Quick Start:[/cyan]")
        console.print("  cd your-project/")
        console.print("  sparc init")
        console.print("  # Then use /sparc in Claude Code")
        
        console.print("\n🔧 [cyan]Management Commands:[/cyan]")
        console.print("  sparc status       # Check system status")
        console.print("  sparc docker start # Start containers")
        console.print("  sparc config show  # View configuration")
        
        console.print("\n🆘 [cyan]Need help?[/cyan]")
        console.print("  sparc --help")
        console.print("  Documentation: https://sparc-cli.readthedocs.io")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load global configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Save global configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            console.print(f"❌ [red]Error saving config: {e}[/red]")
            return False


def install_claude_commands() -> bool:
    """Install Claude Code commands for SPARC"""
    try:
        # Get Claude Code commands directory
        claude_commands_dir = Path.home() / ".claude" / "commands"
        claude_commands_dir.mkdir(parents=True, exist_ok=True)
        
        # Get the package directory
        package_dir = Path(__file__).parent.parent
        source_commands_dir = package_dir / "claude-commands"
        
        if not source_commands_dir.exists():
            console.print("❌ [red]Claude commands directory not found in package[/red]")
            return False
        
        # Copy all command files
        commands_installed = 0
        for command_file in source_commands_dir.glob("*.md"):
            target_file = claude_commands_dir / command_file.name
            shutil.copy2(command_file, target_file)
            commands_installed += 1
        
        console.print(f"✅ [green]Installed {commands_installed} Claude Code commands[/green]")
        return True
        
    except Exception as e:
        console.print(f"❌ [red]Error installing Claude commands: {e}[/red]")
        return False


def check_installation() -> bool:
    """Check if SPARC is properly installed"""
    global_config_dir = Path.home() / ".sparc"
    config_file = global_config_dir / "config.json"
    
    if not config_file.exists():
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Check if basic configuration exists
        return bool(config.get("agent_system") or config.get("supabase"))
    except Exception:
        return False


@app.command()
def install():
    """Run interactive SPARC installation"""
    installer = SPARCInstaller()
    success = installer.run_installation()
    
    if not success:
        console.print("❌ [red]Installation failed or was cancelled[/red]")
        raise typer.Exit(1)


@app.command()
def check():
    """Check installation status"""
    console.print("🔍 [cyan]Checking SPARC installation...[/cyan]")
    
    if check_installation():
        console.print("✅ [green]SPARC is properly installed![/green]")
        
        # Show detailed status
        installer = SPARCInstaller()
        installer._verify_installation()
    else:
        console.print("❌ [red]SPARC is not properly installed[/red]")
        console.print("Run `sparc-install` to complete installation")
        raise typer.Exit(1)


@app.command()
def uninstall():
    """Uninstall SPARC CLI"""
    console.print("🗑️  [red]SPARC CLI Uninstallation[/red]")
    
    if not Confirm.ask("Are you sure you want to uninstall SPARC CLI?"):
        console.print("Uninstallation cancelled.")
        return
    
    # Remove global config
    global_config_dir = Path.home() / ".sparc"
    if global_config_dir.exists():
        shutil.rmtree(global_config_dir)
        console.print("✅ [green]Global configuration removed[/green]")
    
    # Stop Docker containers
    try:
        dm = DockerManager()
        dm.stop_containers()
        console.print("✅ [green]Docker containers stopped[/green]")
    except Exception:
        console.print("⚠️  [yellow]Could not stop Docker containers[/yellow]")
    
    console.print("✅ [green]SPARC CLI uninstalled successfully![/green]")
    console.print("Note: You may need to manually remove the Python package:")
    console.print("  pip uninstall sparc-cli")


def main():
    """Main entry point for sparc-install command"""
    app()


if __name__ == "__main__":
    main()