#!/usr/bin/env python3
"""
SPARC Project Initializer
Handles project detection, database setup, and namespace isolation
"""

import os
import hashlib
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel

from .memory.manager import MemoryManager
from supabase import create_client
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, CreateCollection

console = Console()

class SPARCProjectInitializer:
    """Handles SPARC project initialization with database setup"""
    
    def __init__(self):
        self.console = console
        self.supabase = None
        self.qdrant = None
        self.project_namespace = None
        self.project_path = None
        
    def generate_project_namespace(self, project_path: str) -> str:
        """Generate a unique namespace for the project based on its path"""
        # Use the absolute path and create a deterministic hash
        abs_path = str(Path(project_path).resolve())
        project_name = Path(abs_path).name
        
        # Create a short hash of the full path for uniqueness
        path_hash = hashlib.md5(abs_path.encode()).hexdigest()[:8]
        
        # Combine project name with hash for readable but unique namespace
        namespace = f"{project_name}_{path_hash}"
        
        # Ensure namespace is database-safe
        namespace = namespace.replace('-', '_').replace(' ', '_').lower()
        
        return namespace
    
    def detect_project_type(self, project_path: Path) -> Dict[str, Any]:
        """Detect if this is a new project or existing project"""
        
        project_info = {
            "is_new_project": False,
            "is_sparc_project": False,
            "has_code": False,
            "project_type": "unknown",
            "existing_files": [],
            "sparc_phase": None
        }
        
        if not project_path.exists():
            project_info["is_new_project"] = True
            return project_info
            
        # Check if it's an existing SPARC project
        claude_md = project_path / "CLAUDE.md"
        if claude_md.exists():
            content = claude_md.read_text()
            if "project_id:" in content:
                project_info["is_sparc_project"] = True
                # Extract phase if present
                for line in content.split('\n'):
                    if line.startswith('Phase:'):
                        project_info["sparc_phase"] = line.split(':', 1)[1].strip()
        
        # Check for existing files
        try:
            files = list(project_path.iterdir())
            project_info["existing_files"] = [f.name for f in files if f.is_file()]
            
            # Determine if it's empty or has content
            if not files:
                project_info["is_new_project"] = True
            elif len(files) == 1 and files[0].name in ['.DS_Store', '.gitkeep']:
                project_info["is_new_project"] = True
            else:
                project_info["has_code"] = True
                
                # Detect project type
                if (project_path / "package.json").exists():
                    project_info["project_type"] = "nodejs"
                elif (project_path / "pyproject.toml").exists() or (project_path / "requirements.txt").exists():
                    project_info["project_type"] = "python"
                elif (project_path / "Cargo.toml").exists():
                    project_info["project_type"] = "rust"
                elif (project_path / "pom.xml").exists():
                    project_info["project_type"] = "java"
                elif any(f.name.endswith(('.js', '.jsx', '.ts', '.tsx')) for f in files):
                    project_info["project_type"] = "javascript"
                elif any(f.name.endswith(('.py',)) for f in files):
                    project_info["project_type"] = "python"
                    
        except PermissionError:
            console.print(f"[red]Permission denied accessing {project_path}[/red]")
            
        return project_info
    
    async def initialize_databases(self, namespace: str) -> bool:
        """Initialize Supabase and Qdrant for the project namespace"""
        
        try:
            # Initialize Supabase
            console.print(f"[cyan]🗄️  Initializing Supabase for namespace: {namespace}[/cyan]")
            
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            
            if not supabase_url or not supabase_key:
                console.print("[red]❌ Supabase credentials not found in environment[/red]")
                console.print("[yellow]Please set SUPABASE_URL and SUPABASE_KEY environment variables[/yellow]")
                return False
            
            self.supabase = create_client(supabase_url, supabase_key)
            
            # Test connection
            try:
                result = self.supabase.table("project_memorys").select("id").limit(1).execute()
                console.print("[green]✅ Supabase connection successful[/green]")
            except Exception as e:
                console.print(f"[red]❌ Supabase connection failed: {str(e)}[/red]")
                return False
            
            # Initialize Qdrant
            console.print(f"[cyan]🔍 Initializing Qdrant for namespace: {namespace}[/cyan]")
            
            self.qdrant = QdrantClient(host="localhost", port=6333)
            
            # Test connection
            try:
                collections = self.qdrant.get_collections()
                console.print("[green]✅ Qdrant connection successful[/green]")
            except Exception as e:
                console.print(f"[red]❌ Qdrant connection failed: {str(e)}[/red]")
                console.print("[yellow]Make sure Qdrant is running: docker-compose up -d[/yellow]")
                return False
            
            # Create project-specific collections
            await self._create_project_collections(namespace)
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Database initialization failed: {str(e)}[/red]")
            return False
    
    async def _create_project_collections(self, namespace: str):
        """Create Qdrant collections for the project namespace"""
        
        collections_to_create = [
            f"{namespace}_files",      # Complete files
            f"{namespace}_chunks",     # Code chunks (functions, classes)
            f"{namespace}_docs",       # Documentation
            f"{namespace}_decisions"   # Agent decisions/outputs
        ]
        
        for collection_name in collections_to_create:
            try:
                # Check if collection already exists
                existing_collections = self.qdrant.get_collections()
                collection_names = [col.name for col in existing_collections.collections]
                
                if collection_name not in collection_names:
                    self.qdrant.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=1024,  # Mistral embedding size
                            distance=Distance.COSINE
                        )
                    )
                    console.print(f"[green]✅ Created Qdrant collection: {collection_name}[/green]")
                else:
                    console.print(f"[yellow]📦 Collection already exists: {collection_name}[/yellow]")
                    
            except Exception as e:
                console.print(f"[red]❌ Failed to create collection {collection_name}: {str(e)}[/red]")
    
    async def setup_project(self, project_path: str, goal: Optional[str] = None) -> Dict[str, Any]:
        """Complete project setup with database initialization"""
        
        project_path = Path(project_path).resolve()
        self.project_path = project_path
        
        console.print(Panel.fit(
            f"🚀 SPARC Project Setup\n"
            f"Path: {project_path}\n"
            f"Goal: {goal or 'To be defined'}",
            style="bold blue"
        ))
        
        # Generate namespace
        namespace = self.generate_project_namespace(str(project_path))
        self.project_namespace = namespace
        
        console.print(f"[cyan]📦 Project namespace: {namespace}[/cyan]")
        
        # Detect project type
        project_info = self.detect_project_type(project_path)
        
        console.print(f"[dim]Project analysis: {project_info}[/dim]")
        
        # Create directory if it doesn't exist
        if project_info["is_new_project"]:
            console.print(f"[yellow]📁 Creating new project directory: {project_path}[/yellow]")
            project_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize databases
        console.print(f"[cyan]🗄️  Setting up databases for namespace: {namespace}[/cyan]")
        db_success = await self.initialize_databases(namespace)
        
        if not db_success:
            console.print("[red]❌ Database setup failed - continuing without databases[/red]")
        
        # Create CLAUDE.md
        claude_content = self._generate_claude_md(namespace, goal, project_info)
        claude_path = project_path / "CLAUDE.md"
        claude_path.write_text(claude_content)
        
        console.print(f"[green]✅ Created CLAUDE.md with project configuration[/green]")
        
        # Create basic project structure
        await self._create_project_structure(project_path, project_info)
        
        # Initialize memory manager
        memory_manager = MemoryManager(namespace)
        
        setup_result = {
            "success": True,
            "namespace": namespace,
            "project_path": str(project_path),
            "project_info": project_info,
            "database_initialized": db_success,
            "claude_md_path": str(claude_path),
            "memory_manager": memory_manager
        }
        
        console.print(Panel.fit(
            f"✅ SPARC Project Setup Complete!\n\n"
            f"Namespace: {namespace}\n"
            f"Path: {project_path}\n"
            f"Databases: {'✅ Ready' if db_success else '❌ Not connected'}\n\n"
            f"Ready to start autonomous development!",
            style="bold green"
        ))
        
        return setup_result
    
    def _generate_claude_md(self, namespace: str, goal: Optional[str], project_info: Dict[str, Any]) -> str:
        """Generate CLAUDE.md content for the project"""
        
        timestamp = datetime.now().isoformat()
        
        claude_content = f"""# SPARC Project

project_id: {namespace}

## Project Information
- **Namespace**: {namespace}
- **Created**: {timestamp}
- **Project Type**: {project_info.get('project_type', 'unknown')}
- **Is New Project**: {project_info.get('is_new_project', False)}

## Goal
{goal or 'To be defined during goal clarification phase'}

## Current Status
- **Phase**: initialization
- **Started**: {timestamp}
- **Databases**: {'✅ Initialized' if self.supabase and self.qdrant else '⚠️ Not connected'}

## SPARC Workflow
This project follows the SPARC methodology:
1. **Goal Clarification** - Define requirements and constraints
2. **Specification** - Create detailed technical specifications  
3. **Pseudocode** - Design algorithms and logic
4. **Architecture** - Design system architecture
5. **Refinement** - Implement and test features
6. **Completion** - Final validation and deployment

## Memory System
- **Namespace Isolation**: Each project has its own isolated memory space
- **Vector Database**: Qdrant collections for semantic search
- **Structured Data**: Supabase tables for project state and context
- **Unlimited Context**: No token limits on project memory

## Usage
- Use `/sparc-init` to initialize or continue development
- Use `/agents` to view all 36 SPARC agents
- Use `/phase` to check current development phase
- Use `/status` to view project status

---
*This project is powered by SPARC (Specification, Pseudocode, Architecture, Refinement, Completion)*
*36 AI agents working together for autonomous software development*
"""
        
        return claude_content
    
    async def _create_project_structure(self, project_path: Path, project_info: Dict[str, Any]):
        """Create basic project structure"""
        
        if project_info["is_new_project"]:
            # Create standard directories
            dirs_to_create = [
                "docs",
                "docs/specifications",
                "docs/architecture", 
                "docs/pseudocode",
                "docs/research",
                "src",
                "tests",
                "tests/unit",
                "tests/integration"
            ]
            
            for dir_name in dirs_to_create:
                dir_path = project_path / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)
                
                # Create .gitkeep files
                gitkeep = dir_path / ".gitkeep"
                gitkeep.touch()
            
            console.print("[green]✅ Created project directory structure[/green]")
        else:
            console.print("[yellow]📁 Using existing project structure[/yellow]")

async def main():
    """Test the project initializer"""
    initializer = SPARCProjectInitializer()
    
    # Test with a sample project
    test_path = "/tmp/test-sparc-project"
    result = await initializer.setup_project(test_path, "Build a simple calculator app")
    
    if result["success"]:
        console.print("[green]✅ Test successful![/green]")
    else:
        console.print("[red]❌ Test failed![/red]")

if __name__ == "__main__":
    asyncio.run(main())