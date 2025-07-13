#!/usr/bin/env python3
"""
Interactive directory and project picker for SPARC CLI
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
import typer

console = Console()

class DirectoryPicker:
    """Interactive directory picker with arrow key navigation"""
    
    def __init__(self):
        self.current_path = Path.cwd()
        self.projects_base_path = None
        
    def pick_directory(self, start_path: Optional[Path] = None) -> Optional[Path]:
        """Interactive directory picker with projects base folder support"""
        console.print("📁 [bold blue]SPARC Directory Picker[/bold blue]")
        console.print()
        
        # Step 1: Ask for projects base directory
        projects_base = self._get_projects_base_directory()
        if not projects_base:
            return None
            
        # Step 2: Show projects in alphabetical order
        selected_project = self._select_project_from_base(projects_base)
        return selected_project
    
    def _get_projects_base_directory(self) -> Optional[Path]:
        """Get the base directory where all projects are stored"""
        console.print("🏠 [cyan]Projects Base Directory Setup[/cyan]")
        console.print("Please specify the base directory where your projects are organized.")
        console.print()
        
        # Suggest common locations
        suggestions = [
            Path.home() / "Projects",
            Path.home() / "Development", 
            Path.home() / "Code",
            Path.home() / "Workspace",
            Path.home() / "Desktop",
            Path("/Users") / os.getenv("USER", "user") / "Documents" / "Projects"
        ]
        
        console.print("💡 [yellow]Common project locations:[/yellow]")
        for i, suggestion in enumerate(suggestions, 1):
            exists_marker = "✅" if suggestion.exists() else "📁"
            console.print(f"  {i}. {exists_marker} {suggestion}")
        
        console.print(f"  {len(suggestions) + 1}. 📝 Enter custom path")
        console.print(f"  {len(suggestions) + 2}. ❌ Cancel")
        console.print()
        
        choice = Prompt.ask(
            "Select option",
            choices=[str(i) for i in range(1, len(suggestions) + 3)],
            default="1"
        )
        
        choice_num = int(choice)
        
        if choice_num <= len(suggestions):
            selected_path = suggestions[choice_num - 1]
        elif choice_num == len(suggestions) + 1:
            # Custom path
            custom_path = Prompt.ask("Enter the full path to your projects directory")
            if not custom_path:
                return None
            selected_path = Path(custom_path).expanduser()
        else:
            # Cancel
            return None
        
        # Validate the path
        if not selected_path.exists():
            console.print(f"❌ [red]Directory does not exist: {selected_path}[/red]")
            create = Confirm.ask("Would you like to create this directory?")
            if create:
                try:
                    selected_path.mkdir(parents=True, exist_ok=True)
                    console.print(f"✅ [green]Created directory: {selected_path}[/green]")
                except Exception as e:
                    console.print(f"❌ [red]Failed to create directory: {e}[/red]")
                    return None
            else:
                return None
        
        if not selected_path.is_dir():
            console.print(f"❌ [red]Path is not a directory: {selected_path}[/red]")
            return None
        
        console.print(f"✅ [green]Using projects base directory: {selected_path}[/green]")
        self.projects_base_path = selected_path
        return selected_path
    
    def _select_project_from_base(self, base_path: Path) -> Optional[Path]:
        """Select a project from the base directory"""
        console.print(f"\n📋 [cyan]Projects in {base_path}[/cyan]")
        
        try:
            # Get all directories (projects) and sort alphabetically
            projects = [item for item in base_path.iterdir() if item.is_dir()]
            projects.sort(key=lambda x: x.name.lower())  # Alphabetical, case-insensitive
            
            if not projects:
                console.print("📝 [yellow]No projects found in this directory.[/yellow]")
                create_new = Confirm.ask("Would you like to create a new project?")
                if create_new:
                    return self._create_new_project_in_base(base_path)
                return None
            
            # Display projects table
            table = Table(title=f"📂 Projects in {base_path.name}")
            table.add_column("#", width=4, style="cyan")
            table.add_column("Project Name", style="green")
            table.add_column("Type", style="dim")
            table.add_column("Last Modified", style="blue")
            
            for i, project in enumerate(projects, 1):
                # Detect project type
                project_type = self._detect_project_type(project)
                
                # Get last modified date
                try:
                    mtime = project.stat().st_mtime
                    last_modified = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
                except:
                    last_modified = "Unknown"
                
                table.add_row(str(i), project.name, project_type, last_modified)
            
            console.print(table)
            console.print()
            console.print(f"📊 [dim]Total projects: {len(projects)}[/dim]")
            console.print()
            
            # Add options for new project and navigation
            max_choice = len(projects) + 3
            console.print("Options:")
            console.print(f"  1-{len(projects)}. Select project")
            console.print(f"  {len(projects) + 1}. 🆕 Create new project")
            console.print(f"  {len(projects) + 2}. 🔄 Choose different base directory")
            console.print(f"  {len(projects) + 3}. ❌ Cancel")
            
            choice = Prompt.ask(
                "Select option",
                choices=[str(i) for i in range(1, max_choice + 1)]
            )
            
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(projects):
                selected_project = projects[choice_num - 1]
                console.print(f"✅ [green]Selected project: {selected_project.name}[/green]")
                return selected_project
            elif choice_num == len(projects) + 1:
                return self._create_new_project_in_base(base_path)
            elif choice_num == len(projects) + 2:
                return self.pick_directory()  # Start over
            else:
                return None
                
        except PermissionError:
            console.print(f"❌ [red]Permission denied accessing: {base_path}[/red]")
            return None
        except Exception as e:
            console.print(f"❌ [red]Error reading directory: {e}[/red]")
            return None
    
    def _detect_project_type(self, project_path: Path) -> str:
        """Detect the type of project based on files present"""
        type_indicators = {
            "package.json": "Node.js",
            "requirements.txt": "Python",
            "Pipfile": "Python (Pipenv)",
            "pyproject.toml": "Python (Modern)",
            "Cargo.toml": "Rust",
            "go.mod": "Go",
            "composer.json": "PHP",
            "pom.xml": "Java (Maven)",
            "build.gradle": "Java (Gradle)",
            "Gemfile": "Ruby",
            "mix.exs": "Elixir",
            "pubspec.yaml": "Dart/Flutter",
            "CLAUDE.md": "SPARC Project"
        }
        
        try:
            for file, project_type in type_indicators.items():
                if (project_path / file).exists():
                    return project_type
            
            # Check for common directories
            if (project_path / "src").exists():
                return "Source Code"
            elif (project_path / "app").exists():
                return "Application"
            elif (project_path / "docs").exists():
                return "Documentation"
            else:
                return "General"
                
        except:
            return "Unknown"
    
    def _create_new_project_in_base(self, base_path: Path) -> Optional[Path]:
        """Create a new project in the base directory"""
        console.print("\n🆕 [cyan]Create New Project[/cyan]")
        
        project_name = Prompt.ask("Enter project name")
        if not project_name:
            return None
        
        # Sanitize project name
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', project_name)
        if safe_name != project_name:
            console.print(f"💡 [yellow]Project name sanitized to: {safe_name}[/yellow]")
        
        new_project_path = base_path / safe_name
        
        if new_project_path.exists():
            console.print(f"❌ [red]Project '{safe_name}' already exists[/red]")
            return None
        
        try:
            new_project_path.mkdir(parents=True)
            console.print(f"✅ [green]Created new project: {safe_name}[/green]")
            return new_project_path
        except Exception as e:
            console.print(f"❌ [red]Failed to create project: {e}[/red]")
            return None
                
    def _show_directory_contents(self):
        """Show contents of current directory"""
        try:
            items = list(self.current_path.iterdir())
            directories = [item for item in items if item.is_dir()]
            files = [item for item in items if item.is_file()]
            
            table = Table(title=f"📂 {self.current_path}")
            table.add_column("Type", width=8)
            table.add_column("Name", style="cyan")
            table.add_column("Details", style="dim")
            
            # Add parent directory option
            if self.current_path.parent != self.current_path:
                table.add_row("📁", "..", "Parent directory")
            
            # Add directories
            for directory in sorted(directories):
                try:
                    item_count = len(list(directory.iterdir()))
                    table.add_row("📁", directory.name, f"{item_count} items")
                except PermissionError:
                    table.add_row("📁", directory.name, "Access denied")
            
            # Add files (limited)
            for file in sorted(files)[:5]:
                size = self._format_file_size(file.stat().st_size)
                table.add_row("📄", file.name, size)
                
            if len(files) > 5:
                table.add_row("📄", "...", f"and {len(files) - 5} more files")
            
            console.print(table)
            console.print()
            
            console.print("Actions:")
            console.print("• [cyan]select[/cyan] - Use this directory")
            console.print("• [cyan]parent[/cyan] - Go to parent directory") 
            console.print("• [cyan]enter[/cyan] - Enter a subdirectory")
            console.print("• [cyan]create[/cyan] - Create new directory")
            console.print("• [cyan]quit[/cyan] - Cancel")
            console.print()
            
        except PermissionError:
            console.print("❌ [red]Permission denied accessing this directory[/red]")
    
    def _select_subdirectory(self) -> Optional[Path]:
        """Select a subdirectory to enter"""
        try:
            directories = [item for item in self.current_path.iterdir() if item.is_dir()]
            
            if not directories:
                console.print("📁 [yellow]No subdirectories found[/yellow]")
                return None
            
            console.print("📁 [cyan]Available directories:[/cyan]")
            for i, directory in enumerate(directories, 1):
                console.print(f"  {i}. {directory.name}")
            
            choice = Prompt.ask(
                "Enter directory number (or 'back')",
                default="back"
            )
            
            if choice == "back":
                return None
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(directories):
                    return directories[index]
                else:
                    console.print("❌ [red]Invalid directory number[/red]")
                    return None
            except ValueError:
                console.print("❌ [red]Please enter a valid number[/red]")
                return None
                
        except PermissionError:
            console.print("❌ [red]Permission denied[/red]")
            return None
    
    def _create_directory(self) -> Optional[Path]:
        """Create a new directory"""
        name = Prompt.ask("Enter directory name")
        
        if not name:
            return None
        
        new_path = self.current_path / name
        
        if new_path.exists():
            console.print(f"❌ [red]Directory '{name}' already exists[/red]")
            return None
        
        try:
            new_path.mkdir(parents=True)
            console.print(f"✅ [green]Created directory '{name}'[/green]")
            return new_path
        except Exception as e:
            console.print(f"❌ [red]Failed to create directory: {e}[/red]")
            return None
    
    def _format_file_size(self, size: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class ProjectPicker:
    """Interactive project picker for existing SPARC projects"""
    
    def __init__(self, auth_manager):
        self.auth = auth_manager
        
    def pick_project(self) -> Optional[Tuple[str, str]]:
        """Pick an existing project or create new one"""
        console.print("🎯 [bold blue]SPARC Project Picker[/bold blue]")
        
        if not self.auth.is_authenticated():
            console.print("❌ [red]Not authenticated. Please run 'sparc auth login' first.[/red]")
            return None
        
        # Get existing projects
        projects = self.auth.list_projects()
        
        if projects:
            console.print("📋 [cyan]Your existing SPARC projects:[/cyan]")
            
            table = Table()
            table.add_column("#", width=3)
            table.add_column("Project Name", style="cyan")
            table.add_column("Namespace", style="dim")
            table.add_column("Path", style="green")
            
            project_list = list(projects.items())
            for i, (name, info) in enumerate(project_list, 1):
                table.add_row(
                    str(i),
                    info["name"],
                    info["namespace"],
                    info["path"]
                )
            
            console.print(table)
            console.print()
            
            choice = Prompt.ask(
                "Choose project number, 'new' for new project, or 'quit'",
                default="new"
            )
            
            if choice == "quit":
                return None
            elif choice == "new":
                return self._create_new_project()
            else:
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(project_list):
                        name, info = project_list[index]
                        return (info["name"], info["namespace"])
                    else:
                        console.print("❌ [red]Invalid project number[/red]")
                        return None
                except ValueError:
                    console.print("❌ [red]Please enter a valid number[/red]")
                    return None
        else:
            console.print("📝 [yellow]No existing projects found.[/yellow]")
            return self._create_new_project()
    
    def _create_new_project(self) -> Optional[Tuple[str, str]]:
        """Create a new project"""
        console.print("🆕 [cyan]Create New SPARC Project[/cyan]")
        
        project_name = Prompt.ask("Enter project name")
        if not project_name:
            return None
        
        namespace = self.auth.get_namespace(project_name)
        if not namespace:
            console.print("❌ [red]Failed to generate namespace[/red]")
            return None
        
        return (project_name, namespace)


def interactive_project_setup():
    """Interactive setup combining directory and project selection"""
    from .auth import AuthManager
    
    console.print(Panel.fit(
        "🚀 SPARC Interactive Setup\n"
        "Let's set up your autonomous development environment!",
        style="bold blue"
    ))
    
    # Step 1: Directory selection
    console.print("\n📁 [bold]Step 1: Choose Your Project Directory[/bold]")
    directory_picker = DirectoryPicker()
    selected_dir = directory_picker.pick_directory()
    
    if not selected_dir:
        console.print("❌ [red]Setup cancelled[/red]")
        return None
    
    # Step 2: Project selection
    console.print(f"\n🎯 [bold]Step 2: SPARC Project Configuration[/bold]")
    console.print(f"Selected directory: {selected_dir}")
    
    auth_manager = AuthManager()
    project_picker = ProjectPicker(auth_manager)
    project_info = project_picker.pick_project()
    
    if not project_info:
        console.print("❌ [red]Setup cancelled[/red]")
        return None
    
    project_name, namespace = project_info
    
    # Step 3: Confirm and initialize
    console.print(f"\n✅ [bold]Step 3: Confirmation[/bold]")
    console.print(f"Directory: {selected_dir}")
    console.print(f"Project: {project_name}")
    console.print(f"Namespace: {namespace}")
    
    if Confirm.ask("Initialize SPARC in this directory?"):
        return {
            "directory": selected_dir,
            "project_name": project_name,
            "namespace": namespace
        }
    else:
        console.print("❌ [red]Setup cancelled[/red]")
        return None


if __name__ == "__main__":
    result = interactive_project_setup()
    if result:
        console.print(f"🎉 [green]Setup complete! Use 'sparc init' in {result['directory']}[/green]")