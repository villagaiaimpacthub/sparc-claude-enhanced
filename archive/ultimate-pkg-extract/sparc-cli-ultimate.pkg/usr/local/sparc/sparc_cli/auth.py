#!/usr/bin/env python3
"""
SPARC CLI Authentication Manager
Handles user authentication and namespace generation for project isolation
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm

console = Console()


class AuthManager:
    """Manages user authentication and project namespaces for SPARC CLI"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.sparc'
        self.config_dir.mkdir(exist_ok=True)
        
        self.auth_file = self.config_dir / 'auth.json'
        self.projects_file = self.config_dir / 'projects.json'
        
        self._load_auth_data()
        self._load_projects_data()
    
    def _load_auth_data(self):
        """Load authentication data from file"""
        try:
            if self.auth_file.exists():
                with open(self.auth_file, 'r') as f:
                    self.auth_data = json.load(f)
            else:
                self.auth_data = {}
        except Exception as e:
            console.print(f"⚠️  [yellow]Warning: Could not load auth data: {e}[/yellow]")
            self.auth_data = {}
    
    def _load_projects_data(self):
        """Load projects data from file"""
        try:
            if self.projects_file.exists():
                with open(self.projects_file, 'r') as f:
                    self.projects_data = json.load(f)
            else:
                self.projects_data = {}
        except Exception as e:
            console.print(f"⚠️  [yellow]Warning: Could not load projects data: {e}[/yellow]")
            self.projects_data = {}
    
    def _save_auth_data(self) -> bool:
        """Save authentication data to file"""
        try:
            with open(self.auth_file, 'w') as f:
                json.dump(self.auth_data, f, indent=2)
            return True
        except Exception as e:
            console.print(f"❌ [red]Error saving auth data: {e}[/red]")
            return False
    
    def _save_projects_data(self) -> bool:
        """Save projects data to file"""
        try:
            with open(self.projects_file, 'w') as f:
                json.dump(self.projects_data, f, indent=2)
            return True
        except Exception as e:
            console.print(f"❌ [red]Error saving projects data: {e}[/red]")
            return False
    
    def _generate_user_id(self, email: str) -> str:
        """Generate consistent user ID from email"""
        # Create a consistent hash from email
        return hashlib.sha256(email.lower().encode()).hexdigest()[:16]
    
    def _normalize_project_name(self, project_name: str) -> str:
        """Normalize project name for namespace use"""
        # Remove special characters and convert to lowercase
        import re
        normalized = re.sub(r'[^a-zA-Z0-9_]', '_', project_name.lower())
        return normalized.strip('_')
    
    def login(self, email: str, display_name: Optional[str] = None) -> bool:
        """Login user with email and optional display name"""
        try:
            if not email or '@' not in email:
                console.print("❌ [red]Invalid email address[/red]")
                return False
            
            user_id = self._generate_user_id(email)
            
            self.auth_data = {
                'user_id': user_id,
                'email': email,
                'display_name': display_name or email.split('@')[0],
                'authenticated': True,
                'login_time': time.time()
            }
            
            if self._save_auth_data():
                console.print("✅ [green]Successfully logged in![/green]")
                console.print(f"👤 [blue]User: {self.auth_data['display_name']}[/blue]")
                console.print(f"🆔 [dim]User ID: {user_id}[/dim]")
                return True
            else:
                return False
            
        except Exception as e:
            console.print(f"❌ [red]Login failed: {e}[/red]")
            return False
    
    def interactive_login(self) -> bool:
        """Interactive login flow"""
        try:
            console.print("🔐 [cyan]SPARC CLI Authentication[/cyan]")
            console.print("Please provide your email address for authentication.")
            
            email = Prompt.ask("Email address")
            if not email or '@' not in email:
                console.print("❌ [red]Invalid email address[/red]")
                return False
            
            display_name = Prompt.ask("Display name (optional)", default=email.split('@')[0])
            
            return self.login(email, display_name)
            
        except KeyboardInterrupt:
            console.print("\n❌ [red]Login cancelled[/red]")
            return False
        except Exception as e:
            console.print(f"❌ [red]Login failed: {e}[/red]")
            return False
    
    def logout(self) -> bool:
        """Logout current user"""
        try:
            if not self.is_authenticated():
                console.print("❌ [red]Not authenticated[/red]")
                return False
            
            user_name = self.auth_data.get('display_name', 'User')
            
            self.auth_data = {}
            
            if self._save_auth_data():
                console.print(f"✅ [green]Successfully logged out {user_name}[/green]")
                return True
            else:
                return False
            
        except Exception as e:
            console.print(f"❌ [red]Logout failed: {e}[/red]")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.auth_data.get('authenticated', False) and self.auth_data.get('user_id')
    
    def get_user_id(self) -> Optional[str]:
        """Get current user ID"""
        if self.is_authenticated():
            return self.auth_data.get('user_id')
        return None
    
    def get_namespace(self, project_name: str) -> Optional[str]:
        """Generate namespace for user and project"""
        user_id = self.get_user_id()
        if not user_id:
            return None
        
        normalized_project = self._normalize_project_name(project_name)
        return f"{user_id}_{normalized_project}"
    
    def register_project(self, project_name: str, project_path: str) -> bool:
        """Register a new project for the current user"""
        try:
            if not self.is_authenticated():
                console.print("❌ [red]Not authenticated[/red]")
                return False
            
            user_id = self.get_user_id()
            namespace = self.get_namespace(project_name)
            
            # Initialize user projects if not exists
            if user_id not in self.projects_data:
                self.projects_data[user_id] = {}
            
            # Register project
            self.projects_data[user_id][project_name] = {
                'name': project_name,
                'path': project_path,
                'namespace': namespace,
                'created_at': time.time()
            }
            
            return self._save_projects_data()
            
        except Exception as e:
            console.print(f"❌ [red]Error registering project: {e}[/red]")
            return False
    
    def list_projects(self) -> Dict[str, Any]:
        """List all projects for current user"""
        if not self.is_authenticated():
            return {}
        
        user_id = self.get_user_id()
        return self.projects_data.get(user_id, {})
    
    def remove_project(self, project_name: str) -> bool:
        """Remove a project from the registry"""
        try:
            if not self.is_authenticated():
                console.print("❌ [red]Not authenticated[/red]")
                return False
            
            user_id = self.get_user_id()
            user_projects = self.projects_data.get(user_id, {})
            
            if project_name not in user_projects:
                console.print(f"❌ [red]Project '{project_name}' not found[/red]")
                return False
            
            del user_projects[project_name]
            
            if self._save_projects_data():
                console.print(f"✅ [green]Project '{project_name}' removed from registry[/green]")
                return True
            else:
                return False
            
        except Exception as e:
            console.print(f"❌ [red]Error removing project: {e}[/red]")
            return False
    
    def get_auth_status(self) -> Dict[str, Any]:
        """Get comprehensive authentication status"""
        if not self.is_authenticated():
            return {
                'authenticated': False,
                'user': None,
                'projects': {},
                'projects_count': 0
            }
        
        user_projects = self.list_projects()
        
        return {
            'authenticated': True,
            'user': {
                'user_id': self.auth_data.get('user_id'),
                'email': self.auth_data.get('email'),
                'display_name': self.auth_data.get('display_name'),
                'login_time': self.auth_data.get('login_time')
            },
            'projects': user_projects,
            'projects_count': len(user_projects)
        }