"""
Docker Management for SPARC CLI
Handles Docker container lifecycle and configuration
"""

import docker
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml

from rich.console import Console
from rich.prompt import Confirm

console = Console()


class DockerManager:
    """Manages Docker containers for SPARC system"""
    
    def __init__(self):
        self.client = None
        self.global_config_dir = Path.home() / ".sparc"
        self.docker_config_dir = self.global_config_dir / "docker"
        self.docker_config_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to connect to Docker
        try:
            self.client = docker.from_env()
            self.client.ping()
        except Exception as e:
            console.print(f"⚠️  [yellow]Warning: Docker not available: {e}[/yellow]")
            self.client = None
    
    def is_docker_available(self) -> bool:
        """Check if Docker is available and running"""
        return self.client is not None
    
    def setup_docker_config(self) -> bool:
        """Set up Docker configuration files"""
        try:
            # Create docker-compose.yml
            compose_config = {
                "version": "3.8",
                "services": {
                    "qdrant": {
                        "image": "qdrant/qdrant:latest",
                        "container_name": "sparc-qdrant",
                        "ports": ["6336:6333", "6337:6334"],
                        "volumes": [
                            "./qdrant_data:/qdrant/storage",
                            "./qdrant_snapshots:/qdrant/snapshots"
                        ],
                        "environment": [
                            "QDRANT__SERVICE__HTTP_PORT=6333",
                            "QDRANT__SERVICE__GRPC_PORT=6334",
                            "QDRANT__LOG_LEVEL=INFO",
                            "QDRANT__TELEMETRY_DISABLED=true"
                        ],
                        "restart": "unless-stopped",
                        "deploy": {
                            "resources": {
                                "limits": {"memory": "2G"},
                                "reservations": {"memory": "1G"}
                            }
                        }
                    },
                    "postgres": {
                        "image": "postgres:15-alpine",
                        "container_name": "sparc-postgres",
                        "ports": ["5432:5432"],
                        "environment": [
                            "POSTGRES_USER=postgres",
                            "POSTGRES_PASSWORD=postgres",
                            "POSTGRES_DB=sparc",
                            "POSTGRES_INITDB_ARGS=-E UTF8"
                        ],
                        "volumes": [
                            "./postgres_data:/var/lib/postgresql/data"
                        ],
                        "restart": "unless-stopped",
                        "healthcheck": {
                            "test": ["CMD-SHELL", "pg_isready -U postgres"],
                            "interval": "10s",
                            "timeout": "5s",
                            "retries": 5
                        }
                    }
                }
            }
            
            compose_file = self.docker_config_dir / "docker-compose.yml"
            with open(compose_file, 'w') as f:
                yaml.dump(compose_config, f, default_flow_style=False)
            
            # Create data directories
            (self.docker_config_dir / "qdrant_data").mkdir(exist_ok=True)
            (self.docker_config_dir / "qdrant_snapshots").mkdir(exist_ok=True)
            (self.docker_config_dir / "postgres_data").mkdir(exist_ok=True)
            
            return True
            
        except Exception as e:
            console.print(f"❌ [red]Error setting up Docker config: {e}[/red]")
            return False
    
    def start_containers(self) -> bool:
        """Start SPARC Docker containers"""
        if not self.is_docker_available():
            console.print("❌ [red]Docker is not available[/red]")
            return False
        
        try:
            # Ensure Docker config is set up
            if not self.setup_docker_config():
                return False
            
            # Start containers using docker-compose
            cmd = [
                "docker-compose", "-f", str(self.docker_config_dir / "docker-compose.yml"),
                "up", "-d"
            ]
            
            console.print("🚀 [blue]Starting SPARC containers...[/blue]")
            result = subprocess.run(cmd, cwd=self.docker_config_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print("✅ [green]Containers started successfully![/green]")
                
                # Wait for containers to be healthy
                self._wait_for_containers()
                return True
            else:
                console.print(f"❌ [red]Failed to start containers: {result.stderr}[/red]")
                return False
                
        except Exception as e:
            console.print(f"❌ [red]Error starting containers: {e}[/red]")
            return False
    
    def stop_containers(self) -> bool:
        """Stop SPARC Docker containers"""
        if not self.is_docker_available():
            console.print("❌ [red]Docker is not available[/red]")
            return False
        
        try:
            cmd = [
                "docker-compose", "-f", str(self.docker_config_dir / "docker-compose.yml"),
                "down"
            ]
            
            console.print("🛑 [blue]Stopping SPARC containers...[/blue]")
            result = subprocess.run(cmd, cwd=self.docker_config_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print("✅ [green]Containers stopped successfully![/green]")
                return True
            else:
                console.print(f"❌ [red]Failed to stop containers: {result.stderr}[/red]")
                return False
                
        except Exception as e:
            console.print(f"❌ [red]Error stopping containers: {e}[/red]")
            return False
    
    def restart_containers(self) -> bool:
        """Restart SPARC Docker containers"""
        if not self.is_docker_available():
            console.print("❌ [red]Docker is not available[/red]")
            return False
        
        try:
            cmd = [
                "docker-compose", "-f", str(self.docker_config_dir / "docker-compose.yml"),
                "restart"
            ]
            
            console.print("🔄 [blue]Restarting SPARC containers...[/blue]")
            result = subprocess.run(cmd, cwd=self.docker_config_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print("✅ [green]Containers restarted successfully![/green]")
                self._wait_for_containers()
                return True
            else:
                console.print(f"❌ [red]Failed to restart containers: {result.stderr}[/red]")
                return False
                
        except Exception as e:
            console.print(f"❌ [red]Error restarting containers: {e}[/red]")
            return False
    
    def get_container_status(self) -> Dict[str, Any]:
        """Get status of all SPARC containers"""
        status = {}
        
        if not self.is_docker_available():
            return status
        
        try:
            # Get container information
            containers = self.client.containers.list(all=True, 
                                                    filters={"name": "sparc-"})
            
            for container in containers:
                name = container.name
                status[name] = {
                    "status": container.status,
                    "ports": [f"{p['HostPort']}:{p['PrivatePort']}" 
                             for p in container.ports.values() 
                             if p for p in p],
                    "image": container.image.tags[0] if container.image.tags else "unknown",
                    "created": container.attrs["Created"]
                }
                
        except Exception as e:
            console.print(f"⚠️  [yellow]Warning: Could not get container status: {e}[/yellow]")
        
        return status
    
    def _wait_for_containers(self, timeout: int = 30):
        """Wait for containers to be healthy"""
        console.print("⏳ [blue]Waiting for containers to be ready...[/blue]")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check if Qdrant is responding
                import requests
                response = requests.get("http://localhost:6336/health", timeout=2)
                if response.status_code == 200:
                    console.print("✅ [green]Qdrant is ready![/green]")
                    break
            except:
                pass
            
            time.sleep(2)
        
        # Check PostgreSQL
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                import psycopg2
                conn = psycopg2.connect(
                    host="localhost",
                    port="5432",
                    database="sparc",
                    user="postgres",
                    password="postgres"
                )
                conn.close()
                console.print("✅ [green]PostgreSQL is ready![/green]")
                break
            except:
                pass
            
            time.sleep(2)
    
    def install_docker(self) -> bool:
        """Help user install Docker"""
        console.print("🐳 [blue]Docker Installation Required[/blue]")
        console.print()
        
        import platform
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            console.print("📥 [cyan]For macOS:[/cyan]")
            console.print("1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop")
            console.print("2. Install the .dmg file")
            console.print("3. Start Docker Desktop")
            console.print("4. Wait for Docker to be ready (whale icon in menu bar)")
            
        elif system == "windows":  # Windows
            console.print("📥 [cyan]For Windows:[/cyan]")
            console.print("1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop")
            console.print("2. Run the installer")
            console.print("3. Restart your computer if prompted")
            console.print("4. Start Docker Desktop")
            console.print("5. Wait for Docker to be ready")
            
        elif system == "linux":  # Linux
            console.print("📥 [cyan]For Linux:[/cyan]")
            console.print("1. Run: curl -fsSL https://get.docker.com -o get-docker.sh")
            console.print("2. Run: sh get-docker.sh")
            console.print("3. Add user to docker group: sudo usermod -aG docker $USER")
            console.print("4. Log out and log back in")
            console.print("5. Start Docker: sudo systemctl start docker")
            
        else:
            console.print(f"❌ [red]Unsupported platform: {system}[/red]")
            return False
        
        console.print()
        console.print("After installing Docker, run `sparc docker start` to start the containers.")
        
        return True
    
    def check_docker_installation(self) -> Dict[str, Any]:
        """Check Docker installation status"""
        status = {
            "docker_available": False,
            "docker_version": None,
            "docker_compose_available": False,
            "docker_compose_version": None,
            "containers_running": False
        }
        
        # Check Docker
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                status["docker_available"] = True
                status["docker_version"] = result.stdout.strip()
        except:
            pass
        
        # Check Docker Compose
        try:
            result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                status["docker_compose_available"] = True
                status["docker_compose_version"] = result.stdout.strip()
        except:
            pass
        
        # Check if containers are running
        if self.is_docker_available():
            container_status = self.get_container_status()
            running_containers = sum(1 for info in container_status.values() 
                                   if info.get("status") == "running")
            status["containers_running"] = running_containers > 0
        
        return status