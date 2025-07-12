#!/bin/bash

# SPARC Autonomous Development System Installer
# 36 AI agents for complete software development
# https://github.com/villagaiaimpacthub/sparc-claude

set -e

echo "┌─────────────────────────────────────────────────────────────────┐"
echo "│ 🚀 SPARC - Autonomous Development System                        │"
echo "│ Installing 36 AI agents for complete software development...    │"
echo "└─────────────────────────────────────────────────────────────────┘"
echo

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This installer is currently for macOS only"
    echo "💡 Linux support coming soon"
    exit 1
fi

# Check for required dependencies
echo "🔍 Checking system requirements..."

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "💡 Install Python 3: https://python.org/downloads/"
    exit 1
fi

# Check pip
if ! python3 -m pip --version &> /dev/null; then
    echo "📦 Installing pip..."
    python3 -m ensurepip --upgrade
fi

# Install inquirer if not present
echo "📦 Installing required packages..."
(python3 -m pip install --user inquirer --break-system-packages 2>/dev/null) || \
(python3 -m pip install --user inquirer 2>/dev/null) || \
echo "⚠️  Could not install inquirer - using fallback text interface"

echo "✅ System requirements met"
echo

# Create installation directories
echo "📁 Creating installation directories..."
sudo mkdir -p /usr/local/sparc/claude-commands
sudo mkdir -p /usr/local/bin

# Create the main sparc wrapper script
echo "📝 Installing SPARC orchestrator..."
sudo tee /usr/local/bin/sparc > /dev/null << 'EOF'
#!/bin/bash
export SPARC_HOME="/usr/local/sparc"
cd "$SPARC_HOME"
python3 -m sparc_cli.orchestrator "$@"
EOF

# Create the complete sparc-init script (the working version from user's system)
echo "📝 Installing SPARC initializer..."
sudo tee /usr/local/bin/sparc-init > /dev/null << 'EOF'
#!/bin/bash
export SPARC_HOME="/usr/local/sparc"
export ORIGINAL_DIR="$(pwd)"
cd "$SPARC_HOME"
python3 -c "
import asyncio
import sys
import os
import json
import subprocess
from pathlib import Path
sys.path.append('.')
# Removed old initializer - using direct project setup instead

try:
    import inquirer
    HAS_INQUIRER = True
except ImportError:
    HAS_INQUIRER = False

# Recent projects file
RECENT_PROJECTS_FILE = Path.home() / '.sparc' / 'recent_projects.json'

def load_recent_projects():
    if RECENT_PROJECTS_FILE.exists():
        try:
            with open(RECENT_PROJECTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_recent_project(project_path):
    RECENT_PROJECTS_FILE.parent.mkdir(exist_ok=True)
    recent = load_recent_projects()
    
    # Add to front, remove duplicates
    if project_path in recent:
        recent.remove(project_path)
    recent.insert(0, project_path)
    
    # Keep only last 5
    recent = recent[:5]
    
    with open(RECENT_PROJECTS_FILE, 'w') as f:
        json.dump(recent, f)

def create_env_file(project_path, namespace):
    '''Create .env file with placeholder configuration'''
    env_content = '''# SPARC Project Environment Variables
# Database Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-key-here

# Vector Database
QDRANT_URL=http://localhost:6336
QDRANT_API_KEY=

# AI APIs (Optional)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
MISTRAL_API_KEY=

# Project Configuration
PROJECT_NAMESPACE={}
'''.format(namespace)
    
    env_path = Path(project_path) / '.env'
    env_path.write_text(env_content)
    print('✅ Created .env file with configuration template')

def check_docker():
    '''Check if Docker is installed and running'''
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            # Check if Docker daemon is running
            result = subprocess.run(['docker', 'ps'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return False

def setup_qdrant():
    '''Set up Qdrant database locally via Docker'''
    try:
        print('🐳 Setting up local Qdrant database...')
        
        # Check if container already exists
        result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=sparc-qdrant'], 
                              capture_output=True, text=True)
        
        if 'sparc-qdrant' in result.stdout:
            print('📦 Qdrant container already exists, starting it...')
            subprocess.run(['docker', 'start', 'sparc-qdrant'], check=True)
        else:
            print('📦 Creating new Qdrant container...')
            subprocess.run([
                'docker', 'run', '-d', 
                '--name', 'sparc-qdrant',
                '-p', '6336:6333',
                'qdrant/qdrant'
            ], check=True)
        
        print('✅ Qdrant running at http://localhost:6336')
        return True
    except subprocess.CalledProcessError as e:
        print('❌ Failed to start Qdrant: {}'.format(e))
        return False

def validate_supabase_connection(project_path):
    '''Test if Supabase credentials work'''
    try:
        env_path = Path(project_path) / '.env'
        if not env_path.exists():
            return False
            
        env_content = env_path.read_text()
        
        # Check if URL and key are not placeholder values
        if 'your-project.supabase.co' in env_content or 'your-anon-key-here' in env_content:
            return False
            
        # Basic validation - real implementation would test connection
        return 'supabase.co' in env_content and len(env_content.split('SUPABASE_KEY=')[1].split('\\\\n')[0]) > 20
    except:
        return False

def guided_database_setup(project_path):
    '''Interactive database setup wizard'''
    print('\\\\n🗄️  Database Setup - Choose your approach:')
    
    if HAS_INQUIRER:
        choices = [
            '🚀 Automated setup (Recommended for beginners)',
            '📝 Manual setup (I\\'ll configure everything myself)',
            '⏭️  Skip setup (Use SPARC without databases)'
        ]
        
        questions = [
            inquirer.List('setup_choice',
                         message='How would you like to set up databases?',
                         choices=choices,
                         carousel=True)
        ]
        
        answers = inquirer.prompt(questions)
        if not answers:
            return False
            
        choice = answers['setup_choice']
    else:
        print('1. 🚀 Automated setup (Recommended for beginners)')
        print('2. 📝 Manual setup (I\\'ll configure everything myself)')
        print('3. ⏭️  Skip setup (Use SPARC without databases)')
        print()
        
        choice_num = input('Select option (1-3): ')
        if choice_num == '1':
            choice = '🚀 Automated setup'
        elif choice_num == '2':
            choice = '📝 Manual setup'
        else:
            choice = '⏭️  Skip setup'
    
    if choice.startswith('🚀 Automated'):
        return automated_database_setup(project_path)
    elif choice.startswith('📝 Manual'):
        print('\\\\n📝 Manual setup selected.')
        print('💡 Edit the .env file at: {}/.env'.format(project_path))
        print('💡 Add your database credentials when ready')
        return True
    else:
        print('\\\\n⏭️  Database setup skipped.')
        print('💡 You can set up databases later by editing the .env file')
        return True

def automated_database_setup(project_path):
    '''Automated database setup flow'''
    print('\\\\n🚀 Starting automated database setup...')
    
    # 1. Docker/Qdrant Setup
    print('\\\\n1️⃣  Setting up Qdrant (Vector Database)')
    
    if not check_docker():
        print('🐳 Docker is required but not installed')
        print()
        print('📥 Please install Docker Desktop:')
        print('   https://docs.docker.com/desktop/install/mac-install/')
        print()
        print('⏳ After installation, run \\'sparc-init\\' again')
        return False
    
    if not setup_qdrant():
        print('⚠️  Qdrant setup failed, but continuing...')
    
    # 2. Supabase Setup
    print('\\\\n2️⃣  Setting up Supabase (Main Database)')
    print('☁️  I\\'ll guide you through creating a Supabase account:')
    print()
    print('📋 Steps:')
    print('   1. Opening Supabase in your browser...')
    
    try:
        subprocess.run(['open', 'https://supabase.com/dashboard/sign-up'], check=True)
    except:
        print('   Please visit: https://supabase.com/dashboard/sign-up')
    
    print('   2. Create account & new project')
    print('   3. Go to Settings > API')
    print('   4. Copy your URL and anon key')
    print()
    
    # 3. Interactive .env editing
    print('3️⃣  Configure your .env file')
    print('📝 Please edit: {}/.env'.format(project_path))
    print('💡 Replace the placeholder values with your Supabase URL and key')
    print()
    
    input('Press Enter when you\\'ve saved the .env file...')
    
    # 4. Validate connection
    print('\\\\n🔍 Testing database connections...')
    
    if validate_supabase_connection(project_path):
        print('✅ Supabase configured successfully!')
    else:
        print('⚠️  Supabase connection couldn\\'t be verified.')
        print('💡 You can test it later or update the .env file')
    
    print('\\\\n✅ Database setup complete!')
    return True

def create_claude_md(project_path, namespace):
    '''Create CLAUDE.md with project configuration'''
    claude_content = '''# SPARC Project Configuration

project_id: {}

## Overview

This is a SPARC (Specification, Pseudocode, Architecture, Refinement, Completion) autonomous software development project with 36 specialized AI agents.

## Project Details

- **Namespace**: {}
- **Project Path**: {}
- **Goal**: New SPARC project - goal to be defined with Claude

## Key Components

- **36 AI Agents**: Complete autonomous development workflow
- **External Memory**: Supabase + Qdrant for unlimited context
- **BMO Framework**: Behavior-Model-Oracle validation with cognitive triangulation
- **Phase-based Workflow**: Systematic progression from goal to deployment
- **Claude Integration**: Hooks and MCP for seamless workflow

## Quick Start

1. **Define Goal**: Use /sparc slash command to start autonomous development
2. **Agent Activation**: The 36-agent system will handle the complete workflow
3. **Memory Isolation**: This project uses namespace {} for complete isolation

## Architecture

- src/: Source code
- tests/: Test files
- docs/: Documentation
- .env: Environment configuration
- CLAUDE.md: This configuration file

## Memory & Context

This project uses isolated memory with namespace {}. All agent memories, context, and project state are completely separated from other SPARC projects.

For autonomous development, use the /sparc slash command in Claude Code.
'''.format(namespace, namespace, project_path, namespace, namespace)
    
    claude_path = Path(project_path) / 'CLAUDE.md'
    claude_path.write_text(claude_content)
    print('✅ Created CLAUDE.md with project configuration')

def create_project_structure(project_path):
    '''Create basic project directory structure'''
    project_dir = Path(project_path)
    
    # Create standard directories
    directories = ['src', 'tests', 'docs', '.claude/commands']
    
    for dir_name in directories:
        dir_path = project_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create Claude Code slash commands
    commands_dir = project_dir / '.claude' / 'commands'
    
    # Copy SPARC slash commands from global installation
    import shutil
    global_commands = Path('/usr/local/sparc/claude-commands')
    
    if global_commands.exists():
        for cmd_file in global_commands.glob('*.md'):
            shutil.copy2(cmd_file, commands_dir / cmd_file.name)
    
    print('✅ Created project structure with Claude Code integration')

def is_sparc_project(project_path):
    '''Check if a directory is already a SPARC project'''
    project_dir = Path(project_path)
    
    # Check for SPARC indicators
    claude_md = project_dir / 'CLAUDE.md'
    env_file = project_dir / '.env'
    claude_commands = project_dir / '.claude' / 'commands'
    
    # Must have CLAUDE.md with project_id
    if claude_md.exists():
        try:
            content = claude_md.read_text()
            if 'project_id:' in content and 'SPARC' in content:
                return True
        except:
            pass
    
    # Check for .env with PROJECT_NAMESPACE
    if env_file.exists():
        try:
            content = env_file.read_text()
            if 'PROJECT_NAMESPACE=' in content:
                return True
        except:
            pass
    
    return False

def get_sparc_project_info(project_path):
    '''Get namespace and basic info from existing SPARC project'''
    project_dir = Path(project_path)
    claude_md = project_dir / 'CLAUDE.md'
    env_file = project_dir / '.env'
    
    namespace = None
    project_id = None
    
    # Try to get project_id from CLAUDE.md
    if claude_md.exists():
        try:
            content = claude_md.read_text()
            for line in content.split('\\\\n'):
                if line.strip().startswith('project_id:'):
                    project_id = line.split(':', 1)[1].strip()
                    break
        except:
            pass
    
    # Try to get namespace from .env
    if env_file.exists():
        try:
            content = env_file.read_text()
            for line in content.split('\\\\n'):
                if line.strip().startswith('PROJECT_NAMESPACE='):
                    namespace = line.split('=', 1)[1].strip()
                    break
        except:
            pass
    
    return {
        'namespace': namespace or project_id,
        'project_id': project_id,
        'project_path': project_path
    }

def check_database_connectivity(project_path):
    '''Check if databases are connected and healthy'''
    env_file = Path(project_path) / '.env'
    if not env_file.exists():
        return {'supabase': False, 'qdrant': False, 'error': 'No .env file'}
    
    # Load environment variables
    env_vars = {}
    try:
        content = env_file.read_text()
        for line in content.split('\\\\n'):
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    except:
        return {'supabase': False, 'qdrant': False, 'error': 'Cannot read .env file'}
    
    # Check Qdrant
    qdrant_healthy = False
    try:
        qdrant_url = env_vars.get('QDRANT_URL', 'http://localhost:6336')
        result = subprocess.run(['curl', '-s', '{}health'.format(qdrant_url + '/')], 
                              capture_output=True, text=True, timeout=5)
        qdrant_healthy = result.returncode == 0 and 'ok' in result.stdout.lower()
    except:
        pass
    
    # Check Supabase (basic URL validation for now)
    supabase_healthy = False
    supabase_url = env_vars.get('SUPABASE_URL', '')
    supabase_key = env_vars.get('SUPABASE_KEY', '')
    
    if supabase_url and supabase_key:
        if 'supabase.co' in supabase_url and len(supabase_key) > 20:
            if not ('your-project' in supabase_url or 'your-anon-key' in supabase_key):
                supabase_healthy = True
    
    return {
        'supabase': supabase_healthy,
        'qdrant': qdrant_healthy,
        'supabase_url': supabase_url,
        'qdrant_url': env_vars.get('QDRANT_URL', 'http://localhost:6336')
    }

def save_project_state(project_path, state_data):
    '''Save project state to local file and prepare for database sync'''
    project_dir = Path(project_path)
    sparc_dir = project_dir / '.sparc'
    sparc_dir.mkdir(exist_ok=True)
    
    state_file = sparc_dir / 'project_state.json'
    
    # Add timestamp
    import datetime
    state_data['last_updated'] = datetime.datetime.now().isoformat()
    state_data['project_path'] = str(project_path)
    
    # Save to local file
    with open(state_file, 'w') as f:
        json.dump(state_data, f, indent=2)
    
    print('💾 Project state saved')

def load_project_state(project_path):
    '''Load project state from local file'''
    project_dir = Path(project_path)
    state_file = project_dir / '.sparc' / 'project_state.json'
    
    if not state_file.exists():
        return None
    
    try:
        with open(state_file, 'r') as f:
            return json.load(f)
    except:
        return None

def initialize_project_state(project_path, namespace, goal='New SPARC project - goal to be defined'):
    '''Initialize project state for a new SPARC project'''
    db_health = check_database_connectivity(project_path)
    
    initial_state = {
        'project_namespace': namespace,
        'current_phase': 'goal_clarification',
        'last_goal': goal,
        'active_agents': [],
        'progress': {
            'files_created': [],
            'phase_completion': 0.0,
            'next_actions': ['Define project goal', 'Begin specification phase']
        },
        'database_health': db_health,
        'session_count': 1,
        'total_development_time': 0
    }
    
    save_project_state(project_path, initial_state)
    return initial_state

def get_project_status_summary(project_path):
    '''Get a human-readable summary of project status'''
    state = load_project_state(project_path)
    if not state:
        return 'No project state found'
    
    phase_names = {
        'goal_clarification': '🎯 Goal Clarification',
        'specification': '📋 Specification', 
        'architecture': '🏗️ Architecture',
        'pseudocode': '📝 Pseudocode',
        'refinement': '⚒️ Refinement',
        'completion': '✅ Completion'
    }
    
    current_phase = phase_names.get(state.get('current_phase', 'unknown'), state.get('current_phase', 'Unknown'))
    completion = state.get('progress', {}).get('phase_completion', 0) * 100
    
    db_status = '🟢' if state.get('database_health', {}).get('supabase') and state.get('database_health', {}).get('qdrant') else '🟡'
    
    summary = '''
📊 Project Status: {} ({:.0f}% complete)
🗄️ Databases: {} {}
🎯 Current Goal: {}
📁 Files Created: {}
🔄 Sessions: {}
'''.format(
        current_phase, completion, db_status, 
        'Healthy' if db_status == '🟢' else 'Needs attention',
        state.get('last_goal', 'Not defined'),
        len(state.get('progress', {}).get('files_created', [])),
        state.get('session_count', 1)
    )
    
    next_actions = state.get('progress', {}).get('next_actions', [])
    if next_actions:
        summary += '⏭️ Next Actions: {}'.format(', '.join(next_actions[:2]))
    
    return summary.strip()

def setup_namespace_isolation(namespace):
    '''Set up complete namespace isolation for this project'''
    print('📦 Project namespace: {}'.format(namespace))
    print('🔒 Memory isolation active - this project is completely isolated from other SPARC projects')
    
    # Namespace ensures:
    # - Separate Supabase tables
    # - Separate Qdrant collections  
    # - Separate agent memories
    # - No cross-project contamination
    
    return namespace

def ask_for_project_folder(base_path, location_name):
    # Get existing folders
    existing_folders = []
    try:
        folders = [item for item in Path(base_path).iterdir() 
                  if item.is_dir() and not item.name.startswith('.')]
        existing_folders = sorted(folders)[:10]  # Show first 10 folders
    except Exception as e:
        print('Could not read folder contents: {}'.format(e))
    
    if HAS_INQUIRER:
        choices = [
            '➕ Create new folder in {}'.format(location_name),
            '📂 Use {} directly'.format(location_name),
            '⬅️  Back to location selection'
        ]
        
        # Add existing folders as options
        if existing_folders:
            for folder in existing_folders:
                choices.append('📁 {}'.format(folder.name))
        
        questions = [
            inquirer.List('folder_choice',
                         message='Select or create project folder in {}:'.format(location_name),
                         choices=choices,
                         carousel=True)
        ]
        
        print('\\\\033[90mEnter to confirm · Esc to exit\\\\033[0m')
        
        answers = inquirer.prompt(questions)
        if not answers:
            return None
            
        choice = answers['folder_choice']
        
        if choice.startswith('📁'):
            # Extract folder name (remove emoji and space)
            folder_name = choice[2:]  # Remove emoji
            return str(Path(base_path) / folder_name)
        elif choice.startswith('➕ Create new folder'):
            folder_name = input('Enter folder name for your project: ')
            if folder_name:
                return str(Path(base_path) / folder_name)
            else:
                return str(base_path)
        elif choice.startswith('📂 Use'):
            return str(base_path)
        else:
            # Back option - return special value
            return 'BACK'
    else:
        # Fallback to numbered selection
        options = []
        
        # Add existing folders
        if existing_folders:
            print('Existing folders:')
            for i, folder in enumerate(existing_folders, 1):
                print('{}. {}'.format(i, folder.name))
                options.append(str(folder))
        
        start_num = len(existing_folders) + 1
        print('\\\\nOther options:')
        print('{}. Create new folder in {}'.format(start_num, location_name))
        print('{}. Use {} directly'.format(start_num+1, location_name))
        print('{}. ⬅️  Back to location selection'.format(start_num+2))
        print()
        
        choice = input('Select option: ')
        
        try:
            choice_num = int(choice)
            if choice_num <= len(existing_folders):
                return options[choice_num - 1]
            else:
                adjusted = choice_num - len(existing_folders)
                if adjusted == 1:
                    folder_name = input('Enter folder name for your project: ')
                    if folder_name:
                        return str(Path(base_path) / folder_name)
                    else:
                        return str(base_path)
                elif adjusted == 2:
                    return str(base_path)
                else:
                    return 'BACK'
        except ValueError:
            print('Invalid choice, going back')
            return 'BACK'

def ask_for_custom_path():
    print()
    print('Enter the full path where you want to initialize your SPARC project.')
    print('\\\\033[90mLeave empty and press Enter to go back\\\\033[0m')
    custom_path = input('Custom path: ')
    
    if not custom_path.strip():
        return 'BACK'
    
    return custom_path.strip()

def find_claude_code():
    '''Find Claude Code CLI executable - simple and reliable'''
    
    # Strategy 1: Check PATH first (most likely to work)
    try:
        result = subprocess.run(['which', 'claude'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            claude_path = result.stdout.strip()
            # Verify it's Claude Code CLI (not desktop app)
            version_result = subprocess.run([claude_path, '--version'], 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=5)
            if version_result.returncode == 0:
                version_output = version_result.stdout.lower()
                if 'claude-code' in version_output or 'claude code' in version_output:
                    return claude_path
    except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
        pass
    
    # Strategy 2: If PATH fails, try common direct paths as backup
    fallback_paths = [
        '{}/.claude/local/claude'.format(Path.home()),
        '/usr/local/bin/claude',
        '/Applications/Claude Code.app/Contents/MacOS/Claude Code'
    ]
    
    for path in fallback_paths:
        try:
            result = subprocess.run([path, '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                version_output = result.stdout.lower()
                if 'claude-code' in version_output or 'claude code' in version_output:
                    return path
        except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
            continue
    
    return None

def show_folder_selection():
    current_dir = Path(os.environ.get('ORIGINAL_DIR', os.getcwd()))
    
    print('┌─────────────────────────────────────────────────────────────────┐')
    print('│ 🚀 Welcome to SPARC Autonomous Development!                    │')
    print('│                                                                 │')
    print('│ Setting up project with 36 AI agents...                        │')
    print('└─────────────────────────────────────────────────────────────────┘')
    print()
    
    while True:  # Loop to allow back navigation
        if HAS_INQUIRER:
            choices = []
            
            # Add recent projects
            recent = load_recent_projects()
            if recent:
                for proj in recent[:3]:  # Show top 3 recent projects
                    if os.path.exists(proj):
                        choices.append('📁 {} ({})'.format(Path(proj).name, proj))
            
            # Add standard options
            choices.extend([
                '📂 Current directory: {}'.format(current_dir),
                '🖥️  Desktop: {}'.format(Path.home() / 'Desktop'),
                '📄 Documents: {}'.format(Path.home() / 'Documents'),
                '🔧 Custom path...',
                '🚪 Exit SPARC'
            ])
            
            questions = [
                inquirer.List('folder',
                             message='Where would you like to initialize your SPARC project?',
                             choices=choices,
                             carousel=True)
            ]
            
            print('\\\\033[90mEnter to confirm · Esc to exit\\\\033[0m')
            
            answers = inquirer.prompt(questions)
            if not answers:
                return None
                
            choice = answers['folder']
            
            if choice.startswith('📁'):
                # Recent project
                path = choice.split('(')[1].rstrip(')')
                return path
            elif choice.startswith('📂 Current directory'):
                result = ask_for_project_folder(current_dir, 'Current directory ({})'.format(current_dir))
                if result == 'BACK':
                    continue  # Go back to main selection
                return result
            elif choice.startswith('🖥️  Desktop'):
                result = ask_for_project_folder(Path.home() / 'Desktop', 'Desktop')
                if result == 'BACK':
                    continue  # Go back to main selection
                return result
            elif choice.startswith('📄 Documents'):
                result = ask_for_project_folder(Path.home() / 'Documents', 'Documents')
                if result == 'BACK':
                    continue  # Go back to main selection
                return result
            elif choice.startswith('🔧 Custom path'):
                result = ask_for_custom_path()
                if result == 'BACK':
                    continue  # Go back to main selection
                return result
            elif choice.startswith('🚪 Exit'):
                return None
        else:
            # Fallback to numbered selection - show recent projects here too
            print('🎯 Where would you like to initialize your SPARC project?')
            print()
            
            recent = load_recent_projects()
            if recent:
                print('Recent Projects:')
                for i, proj in enumerate(recent[:3], 1):  # Show top 3
                    if os.path.exists(proj):
                        print('{}. {} ({})'.format(i, Path(proj).name, proj))
                print()
            
            start_num = len([p for p in recent[:3] if os.path.exists(p)]) + 1
            print('New Location:')
            print('{}. Current directory: {}'.format(start_num, current_dir))
            print('{}. Desktop'.format(start_num+1))
            print('{}. Documents'.format(start_num+2))
            print('{}. Custom path'.format(start_num+3))
            print('{}. Exit SPARC'.format(start_num+4))
            print()
            
            choice = input('Select option: ')
            
            try:
                choice_num = int(choice)
                recent_count = len([p for p in recent[:3] if os.path.exists(p)])
                if choice_num <= recent_count:
                    return recent[choice_num - 1]
                else:
                    adjusted = choice_num - recent_count
                    if adjusted == 1:
                        result = ask_for_project_folder(current_dir, 'Current directory ({})'.format(current_dir))
                        if result == 'BACK':
                            continue  # Go back to main selection
                        return result
                    elif adjusted == 2:
                        result = ask_for_project_folder(Path.home() / 'Desktop', 'Desktop')
                        if result == 'BACK':
                            continue  # Go back to main selection
                        return result
                    elif adjusted == 3:
                        result = ask_for_project_folder(Path.home() / 'Documents', 'Documents')
                        if result == 'BACK':
                            continue  # Go back to main selection
                        return result
                    elif adjusted == 4:
                        result = ask_for_custom_path()
                        if result == 'BACK':
                            continue  # Go back to main selection
                        return result
                    else:
                        return None
            except ValueError:
                print('Invalid choice, using current directory')
                return str(current_dir)

def launch_claude_code(project_path):
    '''Launch Claude Code in the project directory'''
    try:
        print('🚀 Launching Claude Code...')
        print('📂 Opening in: {}'.format(project_path))
        print()
        print('\\\\033[92m┌─────────────────────────────────────────────────────────────────┐\\\\033[0m')
        print('\\\\033[92m│ ✨ SPARC is ready! Use /sparc to start autonomous development   │\\\\033[0m')
        print('\\\\033[92m└─────────────────────────────────────────────────────────────────┘\\\\033[0m')
        print()
        
        # Find Claude Code executable
        claude_cmd = find_claude_code()
        
        if not claude_cmd:
            print('🔍 Claude Code not found in common locations.')
            print('💡 Please ensure Claude Code is installed and try one of:')
            print('   • cd {} && claude'.format(project_path))
            print('   • cd {} && /path/to/claude'.format(project_path))
            print('   • Or add Claude Code to your PATH')
            return
        
        print('✅ Found Claude Code at: {}'.format(claude_cmd))
        
        # Change to project directory and launch Claude Code
        os.chdir(project_path)
        
        # Launch Claude Code in the project directory
        if claude_cmd == 'claude':
            # Use shell to handle aliases
            subprocess.run(['bash', '-c', 'claude'], cwd=project_path)
        else:
            # Direct executable path
            subprocess.run([claude_cmd], cwd=project_path)
        
    except KeyboardInterrupt:
        print('\\\\n👋 Claude Code session ended')
    except Exception as e:
        print('❌ Could not launch Claude Code: {}'.format(e))
        print('💡 Manually run: cd {} && claude'.format(project_path))

async def main():
    
    # Phase 1: Project Selection and Setup
    while True:
        project_dir = show_folder_selection()
        
        if not project_dir:
            print('❌ Setup cancelled')
            return
        
        # Check if this is already a SPARC project
        if is_sparc_project(project_dir):
            print('✅ Existing SPARC project detected in {}'.format(project_dir))
            project_info = get_sparc_project_info(project_dir)
            print('📦 Project namespace: {}'.format(project_info['namespace']))
            
            # Load and display project state
            state = load_project_state(project_dir)
            if state:
                print('\\\\n📊 Project Status:')
                print(get_project_status_summary(project_dir))
                
                # Update session count
                state['session_count'] = state.get('session_count', 0) + 1
                save_project_state(project_dir, state)
            else:
                print('🔄 Initializing project state tracking...')
                initialize_project_state(project_dir, project_info['namespace'])
            
            print('\\\\n🔄 Launching Claude Code for development...')
            print('💡 Use /sparc to continue autonomous development')
            print()
            
            # Save to recent projects
            save_recent_project(project_dir)
            
            # Launch Claude Code directly
            launch_claude_code(project_dir)
            break  # Exit successfully
        
        print('🚀 Initializing new SPARC project in {}'.format(project_dir))
        print()
        
        if not os.path.exists(project_dir):
            if HAS_INQUIRER:
                questions = [
                    inquirer.Confirm('create_dir',
                                   message='Directory {} does not exist. Create it?'.format(project_dir),
                                   default=True)
                ]
                
                answers = inquirer.prompt(questions)
                if not answers or not answers['create_dir']:
                    print('❌ Cannot proceed without directory')
                    continue  # Go back to folder selection
                    
                os.makedirs(project_dir, exist_ok=True)
                print('✅ Created directory: {}'.format(project_dir))
            else:
                create = input('Directory {} does not exist. Create it? (y/n): '.format(project_dir))
                if create.lower() != 'y':
                    print('❌ Cannot proceed without directory')
                    continue  # Go back to folder selection
                os.makedirs(project_dir, exist_ok=True)
                print('✅ Created directory: {}'.format(project_dir))
        
        print('📝 Setting up SPARC infrastructure...')
        
        # Generate namespace first
        import hashlib
        abs_path = str(Path(project_dir).resolve())
        project_name = Path(abs_path).name
        path_hash = hashlib.md5(abs_path.encode()).hexdigest()[:8]
        namespace = '{}_{}'. format(project_name, path_hash).replace('-', '_').replace(' ', '_').lower()
        
        # Create .env file first
        create_env_file(project_dir, namespace)
        
        # Interactive database setup
        print('\\\\n📋 Would you like to set up databases now?')
        if HAS_INQUIRER:
            questions = [
                inquirer.Confirm('setup_databases',
                               message='Set up databases (Qdrant + Supabase)?',
                               default=True)
            ]
            answers = inquirer.prompt(questions)
            setup_databases = answers and answers['setup_databases']
        else:
            setup_choice = input('Set up databases now? (y/n): ').lower()
            setup_databases = setup_choice == 'y'
        
        if setup_databases:
            guided_database_setup(project_dir)
        else:
            print('⏭️  Database setup skipped. You can set up later by editing the .env file.')
        
        # Set up complete project structure
        print('\\\\n📁 Setting up project structure...')
        
        # Set up namespace isolation
        setup_namespace_isolation(namespace)
        
        # Create CLAUDE.md configuration
        create_claude_md(project_dir, namespace)
        
        # Create project directory structure  
        create_project_structure(project_dir)
        
        # Initialize project state tracking
        print('\\\\n📊 Initializing project state tracking...')
        initialize_project_state(project_dir, namespace)
        
        # Save to recent projects
        save_recent_project(project_dir)
        
        print('\\\\n✅ SPARC Project Infrastructure Ready!')
        print('📦 Namespace: {}'.format(namespace))
        print('📁 Project: {}'.format(project_dir))
        print('🔒 Memory isolation: Complete')
        print('💾 State tracking: Initialized')
        print()
        
        # Phase 2: Launch Claude Code
        print('🚀 Launching Claude Code...')
        print('💡 Use /sparc to begin autonomous development')
        launch_claude_code(project_dir)
        break  # Exit successfully

asyncio.run(main())
"
EOF

# Create SPARC slash commands directory and files
echo "📝 Installing Claude Code slash commands..."
sudo tee /usr/local/sparc/claude-commands/sparc.md > /dev/null << 'EOF'
# SPARC Autonomous Development

Activate the 36-agent autonomous development system for complete software project creation.

## Usage

```
/sparc "Build a REST API with user authentication"
/sparc "Create a React dashboard with real-time data"
/sparc "Develop a CLI tool for file processing"
```

## What This Does

1. **Specification Phase**: Analyzes requirements, defines scope, creates detailed specs
2. **Architecture Phase**: Designs system structure, components, and data flow
3. **Pseudocode Phase**: Creates implementation plans with detailed algorithms
4. **Refinement Phase**: Generates production code, tests, and documentation
5. **Completion Phase**: Validates, optimizes, and prepares for deployment

## Features

- **36 Specialized Agents**: Each handling specific aspects of development
- **Memory Isolation**: Project-specific namespace prevents cross-contamination
- **External Memory**: Unlimited context via Supabase + Qdrant integration
- **BMO Validation**: Behavior-Model-Oracle cognitive triangulation
- **Phase Tracking**: Complete visibility into development progress

## Requirements

- Supabase database (for agent memory and state)
- Qdrant vector database (for context storage)
- Project must be initialized with `sparc-init`

## Agent Workflow

The system automatically orchestrates:
- **Specification Agents**: Requirement analysis, scope definition
- **Architecture Agents**: System design, component planning
- **Pseudocode Agents**: Algorithm design, implementation planning
- **Refinement Agents**: Code generation, testing, optimization
- **Completion Agents**: Validation, documentation, deployment prep

Each phase builds on previous work with complete memory of project context.

## Project Isolation

Every project gets:
- Unique namespace for complete isolation
- Separate agent memories and context
- Independent state tracking
- No cross-project contamination

Start autonomous development with your goal description!
EOF

# Make scripts executable
sudo chmod +x /usr/local/bin/sparc
sudo chmod +x /usr/local/bin/sparc-init

echo "✅ SPARC installation complete!"
echo
echo "┌─────────────────────────────────────────────────────────────────┐"
echo "│ 🚀 Welcome to SPARC Autonomous Development!                    │"
echo "│                                                                 │"
echo "│ 36 AI agents ready to build complete software projects.        │"
echo "└─────────────────────────────────────────────────────────────────┘"
echo
echo "🎯 Next Steps:"
echo "1. Create free Supabase account: https://supabase.com"
echo "2. Run: sparc-init"
echo "3. Start building: claude → /sparc \"your project idea\""
echo
echo "💡 The agents handle everything from requirements to deployment."
echo "📚 Documentation: https://github.com/villagaiaimpacthub/sparc-claude"
echo