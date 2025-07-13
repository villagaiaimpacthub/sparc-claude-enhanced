#!/usr/bin/env python3
"""
Security utilities for SPARC CLI
Production-grade security for API keys and sensitive data
"""

import os
import hashlib
import secrets
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from rich.console import Console
from dotenv import load_dotenv

console = Console()

class SecurityManager:
    """Production-grade security manager for SPARC CLI"""
    
    def __init__(self):
        self.load_environment()
        self._encryption_key = None
        
    def load_environment(self):
        """Load environment variables with security validation"""
        # Try loading from .env file first
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv(env_file)
        
        # Also load from global user .env if exists
        global_env = Path.home() / ".sparc" / ".env"
        if global_env.exists():
            load_dotenv(global_env)
            
    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate all API keys are properly configured"""
        required_keys = {
            "PERPLEXITY_API_KEY": "sk-or-v1-",
            "SUPABASE_URL": "https://",
            "SUPABASE_ANON_KEY": "eyJ",
        }
        
        validation_results = {}
        
        for key, expected_prefix in required_keys.items():
            value = os.getenv(key)
            if value and value.startswith(expected_prefix):
                validation_results[key] = True
                # Mask key in logs
                masked_key = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
                console.print(f"✅ [green]{key}: {masked_key}[/green]")
            else:
                validation_results[key] = False
                console.print(f"❌ [red]{key}: Not configured or invalid format[/red]")
                
        return validation_results
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Securely retrieve API key for a service"""
        key_mapping = {
            "perplexity": "PERPLEXITY_API_KEY",
            "supabase": "SUPABASE_ANON_KEY", 
            "supabase_service": "SUPABASE_SERVICE_ROLE_KEY",
            "mistral": "MISTRAL_API_KEY",
            "openai": "OPENAI_API_KEY",
            "qdrant": "QDRANT_API_KEY"
        }
        
        env_key = key_mapping.get(service.lower())
        if not env_key:
            console.print(f"⚠️  [yellow]Unknown service: {service}[/yellow]")
            return None
            
        api_key = os.getenv(env_key)
        if not api_key:
            console.print(f"⚠️  [yellow]{env_key} not configured[/yellow]")
            return None
            
        # Validate key format
        if not self._validate_key_format(service, api_key):
            console.print(f"❌ [red]Invalid {service} API key format[/red]")
            return None
            
        return api_key
    
    def _validate_key_format(self, service: str, key: str) -> bool:
        """Validate API key format for specific services"""
        format_validators = {
            "perplexity": lambda k: k.startswith("sk-or-v1-") and len(k) > 20,
            "supabase": lambda k: k.startswith("eyJ") and len(k) > 100,
            "mistral": lambda k: len(k) > 20,
            "openai": lambda k: k.startswith("sk-") and len(k) > 20,
            "qdrant": lambda k: len(k) > 10 or k == ""  # Optional
        }
        
        validator = format_validators.get(service.lower())
        if validator:
            return validator(key)
        return True
    
    def generate_secure_secret(self, length: int = 32) -> str:
        """Generate cryptographically secure random secret"""
        return secrets.token_hex(length)
    
    def hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data for storage"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not self._encryption_key:
            self._encryption_key = self._get_or_create_encryption_key()
        
        f = Fernet(self._encryption_key)
        encrypted_data = f.encrypt(data.encode())
        return encrypted_data.decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not self._encryption_key:
            self._encryption_key = self._get_or_create_encryption_key()
        
        f = Fernet(self._encryption_key)
        decrypted_data = f.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = Path.home() / ".sparc" / ".encryption_key"
        
        if key_file.exists():
            return key_file.read_bytes()
        else:
            # Create new encryption key
            key = Fernet.generate_key()
            key_file.parent.mkdir(exist_ok=True)
            key_file.write_bytes(key)
            key_file.chmod(0o600)  # Restrict permissions
            return key
    
    def secure_environment_check(self) -> Dict[str, Any]:
        """Comprehensive security environment check"""
        checks = {
            "env_file_exists": Path(".env").exists(),
            "env_file_permissions": self._check_file_permissions(Path(".env")),
            "gitignore_protects_env": self._check_gitignore_protection(),
            "api_keys_valid": self.validate_api_keys(),
            "encryption_key_exists": (Path.home() / ".sparc" / ".encryption_key").exists(),
        }
        
        return checks
    
    def _check_file_permissions(self, file_path: Path) -> bool:
        """Check if file has secure permissions"""
        if not file_path.exists():
            return False
        
        # Check that file is not world-readable
        stat = file_path.stat()
        return (stat.st_mode & 0o077) == 0
    
    def _check_gitignore_protection(self) -> bool:
        """Check if .gitignore protects .env files"""
        gitignore = Path(".gitignore")
        if not gitignore.exists():
            return False
        
        content = gitignore.read_text()
        return ".env" in content
    
    def setup_secure_environment(self):
        """Set up secure environment for production"""
        console.print("🔒 [cyan]Setting up secure environment...[/cyan]")
        
        # Create .sparc directory with secure permissions
        sparc_dir = Path.home() / ".sparc"
        sparc_dir.mkdir(exist_ok=True)
        sparc_dir.chmod(0o700)  # Owner only
        
        # Generate encryption key if needed
        self._get_or_create_encryption_key()
        
        # Check .env file permissions
        env_file = Path(".env")
        if env_file.exists():
            env_file.chmod(0o600)  # Owner read/write only
        
        console.print("✅ [green]Secure environment configured[/green]")
    
    def audit_security(self):
        """Perform security audit"""
        console.print("🔍 [cyan]Performing security audit...[/cyan]")
        
        checks = self.secure_environment_check()
        
        for check, result in checks.items():
            if check == "api_keys_valid":
                valid_keys = sum(1 for v in result.values() if v)
                total_keys = len(result)
                status = "✅" if valid_keys > 0 else "⚠️"
                console.print(f"{status} API Keys: {valid_keys}/{total_keys} valid")
            else:
                status = "✅" if result else "❌"
                console.print(f"{status} {check.replace('_', ' ').title()}: {result}")

# Global security manager instance
_security_manager = None

def get_security_manager() -> SecurityManager:
    """Get singleton security manager instance"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager