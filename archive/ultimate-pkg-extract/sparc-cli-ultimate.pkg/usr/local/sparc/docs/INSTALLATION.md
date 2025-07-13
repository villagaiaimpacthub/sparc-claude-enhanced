# SPARC CLI Installation Guide

This guide will walk you through installing SPARC CLI on your system.

## System Requirements

- **Python**: 3.11 or higher
- **Operating System**: macOS, Windows, or Linux
- **Docker**: Docker Desktop (will be installed if needed)
- **Claude Code CLI**: For slash command integration
- **Supabase Account**: For cloud features (optional but recommended)

## Quick Installation

### 1. Install SPARC CLI

```bash
# Using pip
pip install sparc-cli

# Using uv (recommended)
uv tool install sparc-cli
```

### 2. Run Interactive Installer

```bash
sparc-install
```

The installer will guide you through:
- System requirements check
- Docker setup
- Supabase configuration
- Agent system setup
- Installation verification

### 3. Initialize Your First Project

```bash
cd your-project-directory
sparc init
```

### 4. Start Using SPARC

In Claude Code CLI:
```
/sparc "Build a REST API for user management"
```

## Detailed Installation Steps

### Step 1: Python Environment

Ensure you have Python 3.11+ installed:

```bash
python --version  # Should show 3.11 or higher
```

If you need to install Python:
- **macOS**: Use Homebrew: `brew install python@3.11`
- **Windows**: Download from python.org
- **Linux**: Use your package manager: `sudo apt install python3.11`

### Step 2: Package Installation

#### Option A: Using uv (Recommended)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install SPARC CLI globally
uv tool install sparc-cli

# Verify installation
sparc --version
```

#### Option B: Using pip

```bash
# Install globally
pip install sparc-cli

# Or in a virtual environment
python -m venv sparc-env
source sparc-env/bin/activate  # On Windows: sparc-env\\Scripts\\activate
pip install sparc-cli
```

### Step 3: Interactive Setup

Run the interactive installer:

```bash
sparc-install
```

This will:

1. **Check System Requirements**
   - Verify Python version
   - Check platform compatibility
   - Verify architecture support

2. **Docker Setup**
   - Check if Docker is installed
   - Provide installation instructions if needed
   - Start required containers (Qdrant, PostgreSQL)

3. **Supabase Configuration**
   - Guide you through account creation
   - Configure project connection
   - Set up database schema

4. **Agent System Setup**
   - Configure 36 AI agents
   - Set performance parameters
   - Enable monitoring

5. **Verification**
   - Test all components
   - Verify connections
   - Confirm installation

### Step 4: Project Initialization

Navigate to your project directory and initialize SPARC:

```bash
cd /path/to/your/project
sparc init
```

This creates:
- `.sparc/project.json` - Project configuration
- `.sparc/session_state.json` - Session management
- `.claude/commands/` - Claude Code slash commands

### Step 5: Claude Code Integration

Install Claude Code CLI if you haven't already:
```bash
# Installation instructions for Claude Code CLI
curl -fsSL https://claude.ai/cli/install.sh | bash
```

The SPARC slash commands will automatically be available:
- `/sparc` - Enter development mode
- `/stopsparc` - Exit development mode
- `/status` - Check project status
- `/phase` - View current phase
- `/agents` - Show agent status

## Docker Setup Details

### Automatic Docker Setup

The installer can automatically set up Docker containers for:

- **Qdrant** (Vector Database)
  - Port: 6336 (HTTP), 6337 (gRPC)
  - Used for: Memory storage, semantic search
  
- **PostgreSQL** (Relational Database)
  - Port: 5432
  - Used for: Structured data, project state

### Manual Docker Setup

If you prefer manual setup:

```bash
# Start containers
sparc docker start

# Check status
sparc docker status

# Stop containers
sparc docker stop
```

### Docker Installation

If Docker is not installed:

**macOS:**
1. Download Docker Desktop from docker.com
2. Install the .dmg file
3. Start Docker Desktop

**Windows:**
1. Download Docker Desktop from docker.com
2. Run the installer
3. Restart if prompted
4. Start Docker Desktop

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and log back in
sudo systemctl start docker
```

## Supabase Setup

### Creating a Supabase Account

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up with GitHub, Google, or email
4. Create a new project:
   - Choose a project name
   - Set a strong database password
   - Select a region close to you
5. Wait for project creation (1-2 minutes)

### Getting Your Keys

1. Go to Settings > API in your Supabase dashboard
2. Copy the following:
   - **Project URL**: `https://your-project.supabase.co`
   - **Anon Key**: Public key for client access
   - **Service Role Key**: Admin key (optional)

### Database Schema

The installer will provide SQL schema to run in your Supabase project:

1. Go to SQL Editor in Supabase
2. Copy the schema from `~/.sparc/supabase_schema.sql`
3. Execute the SQL to create SPARC tables

## Configuration

### Global Configuration

Located at `~/.sparc/config.json`:

```json
{
  "supabase": {
    "project_url": "https://your-project.supabase.co",
    "anon_key": "your-anon-key"
  },
  "agent_system": {
    "max_concurrent_agents": 5,
    "agent_timeout_minutes": 10
  }
}
```

### Project Configuration

Each project has `.sparc/project.json`:

```json
{
  "project_id": "sparc-abc123",
  "name": "My Project",
  "settings": {
    "auto_phase_progression": true,
    "approval_required_phases": ["goal-clarification", "specification"]
  }
}
```

## Verification

After installation, verify everything works:

```bash
# Check installation
sparc-install check

# Check system status
sparc status

# Test Docker containers
sparc docker status

# Test a simple project
mkdir test-project
cd test-project
sparc init
```

## Troubleshooting

### Common Issues

**Python Version Error:**
```bash
# Check Python version
python --version

# Install correct version if needed
# See Step 1 above
```

**Docker Not Found:**
```bash
# Install Docker Desktop
# See Docker Setup section above

# Start Docker
sparc docker start
```

**Permission Errors (Linux):**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in
```

**Supabase Connection Error:**
```bash
# Test configuration
sparc config show

# Reconfigure if needed
sparc config set supabase.project_url "https://your-project.supabase.co"
```

### Getting Help

- **Documentation**: Check the docs/ directory
- **GitHub Issues**: Report bugs or ask questions
- **Community**: Join our discussions
- **CLI Help**: Run `sparc --help`

## Uninstallation

To remove SPARC CLI:

```bash
# Stop services
sparc docker stop

# Uninstall package
pip uninstall sparc-cli

# Remove configuration (optional)
rm -rf ~/.sparc
```

## Next Steps

After successful installation:

1. **Read the User Guide**: `docs/USER_GUIDE.md`
2. **Try Examples**: `docs/EXAMPLES.md`
3. **Learn About Agents**: `docs/AGENTS.md`
4. **Configure Advanced Features**: `docs/CONFIGURATION.md`

---

**Need help?** Check our [troubleshooting guide](TROUBLESHOOTING.md) or [open an issue](https://github.com/your-org/sparc-cli/issues).