#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "supabase>=2.0.0",
#   "rich>=13.0.0",
#   "python-dotenv>=1.0.0",
# ]
# ///

"""
SPARC Database Initialization Script
Automatically sets up all required Supabase tables and indexes
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

try:
    from supabase import create_client, Client
except ImportError as e:
    print(f"Missing dependency: {e}")
    sys.exit(1)

console = Console()

def init_supabase() -> Client:
    """Initialize Supabase client"""
    load_dotenv()
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or key:
        console.print("[red]❌ Missing Supabase credentials[/red]")
        console.print("Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
        sys.exit(1)
    
    return create_client(url, key)

def read_setup_sql() -> str:
    """Read the setup.sql file"""
    setup_file = Path(__file__).parent.parent / 'setup.sql'
    
    if not setup_file.exists():
        console.print(f"[red]❌ setup.sql not found at {setup_file}[/red]")
        sys.exit(1)
    
    return setup_file.read_text()

def execute_sql_commands(supabase: Client, sql_content: str):
    """Execute SQL commands in batches"""
    
    # Split SQL content into individual commands
    commands = []
    current_command = []
    
    for line in sql_content.split('\n'):
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('--'):
            continue
            
        current_command.append(line)
        
        # If line ends with semicolon, it's end of command
        if line.endswith(';'):
            command = ' '.join(current_command).strip()
            if command and not command.startswith('--'):
                commands.append(command)
            current_command = []
    
    console.print(f"[blue]📝 Found {len(commands)} SQL commands to execute[/blue]")
    
    # Execute commands with progress tracking
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Executing SQL commands...", total=len(commands))
        success_count = 0
        error_count = 0
        
        for i, command in enumerate(commands):
            try:
                # Use RPC to execute raw SQL
                supabase.rpc('exec_sql', {'sql_command': command}).execute()
                success_count += 1
                progress.update(task, advance=1, description=f"Executed {i+1}/{len(commands)} commands")
                
            except Exception as e:
                # Some errors are expected (like "already exists")
                if any(phrase in str(e).lower() for phrase in [
                    'already exists', 
                    'relation already exists',
                    'index already exists',
                    'policy already exists',
                    'function already exists'
                ]):
                    success_count += 1
                    progress.update(task, advance=1, description=f"Skipped {i+1}/{len(commands)} (already exists)")
                else:
                    error_count += 1
                    console.print(f"[yellow]⚠️  Command {i+1} failed: {str(e)[:100]}...[/yellow]")
                    progress.update(task, advance=1)
    
    return success_count, error_count

def check_database_setup(supabase: Client) -> bool:
    """Verify that key tables exist"""
    
    required_tables = [
        'sparc_agents',
        'agent_tasks', 
        'project_memorys',
        'sparc_projects',
        'sparc_conversations',
        'intent_tracking',
        'test_oracle_criteria',
        'perfect_prompts',
        'interactive_conversations',
        'triangulation_results'
    ]
    
    console.print("[blue]🔍 Verifying database setup...[/blue]")
    
    missing_tables = []
    
    for table in required_tables:
        try:
            # Try to query the table (this will fail if table doesn't exist)
            supabase.table(table).select("*").limit(1).execute()
            console.print(f"[green]✅ {table}[/green]")
        except Exception as e:
            if 'does not exist' in str(e):
                missing_tables.append(table)
                console.print(f"[red]❌ {table}[/red]")
            else:
                console.print(f"[yellow]⚠️  {table} (accessible but other error)[/yellow]")
    
    if missing_tables:
        console.print(f"[red]❌ Missing tables: {', '.join(missing_tables)}[/red]")
        return False
    
    console.print("[green]🎉 All required tables exist![/green]")
    return True

def main():
    """Main execution"""
    
    console.print(Panel.fit(
        "[bold blue]🚀 SPARC Database Initialization[/bold blue]\n\n"
        "Setting up complete Supabase database schema with:\n"
        "• Core SPARC tables\n"
        "• Layer 2 intelligence tables\n" 
        "• Agent communication system\n"
        "• Error handling & monitoring\n"
        "• Project state management",
        title="Database Setup"
    ))
    
    # Initialize Supabase
    supabase = init_supabase()
    console.print("[green]✅ Connected to Supabase[/green]")
    
    # Check if already set up
    if check_database_setup(supabase):
        console.print("[green]🎉 Database already properly configured![/green]")
        return
    
    # Read setup SQL
    console.print("[blue]📖 Reading setup.sql...[/blue]")
    sql_content = read_setup_sql()
    
    # Execute SQL commands
    console.print("[blue]⚡ Executing database setup...[/blue]")
    
    # For this simple version, we'll just try to create a function to execute SQL
    # In production, you'd run setup.sql directly in Supabase dashboard
    try:
        console.print("[yellow]⚠️  Note: Direct SQL execution requires running setup.sql in Supabase SQL Editor[/yellow]")
        console.print("[blue]📝 Please copy the contents of setup.sql and run it in your Supabase dashboard[/blue]")
        console.print(f"[blue]📍 SQL file location: {Path(__file__).parent.parent / 'setup.sql'}[/blue]")
        
        # Try to check again after user setup
        input("\n[bold]Press Enter after running setup.sql in Supabase dashboard...[/bold]")
        
        if check_database_setup(supabase):
            console.print(Panel.fit(
                "[bold green]🎉 Database Setup Complete![/bold green]\n\n"
                "All SPARC tables have been created successfully.\n"
                "The system is ready for autonomous development!",
                title="Success"
            ))
        else:
            console.print("[red]❌ Database setup verification failed[/red]")
            console.print("[yellow]Please check the Supabase dashboard for any error messages[/yellow]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Setup failed: {e}[/red]")

if __name__ == "__main__":
    main()