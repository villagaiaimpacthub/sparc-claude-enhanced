# SPARC CLI - Global Autonomous Software Development System

🚀 **36 AI Agents Working Together to Build Complete Software Solutions**

SPARC CLI is a global command-line tool that brings autonomous software development to your fingertips. Install once, use everywhere.

## Features

✨ **36 Specialized AI Agents** - Complete development pipeline from specification to deployment  
🌍 **Global Installation** - Install once, use in any project directory  
🐳 **Docker Integration** - Automated container management for Qdrant and PostgreSQL  
☁️ **Supabase Integration** - Cloud database and real-time features  
🔧 **Claude Code Integration** - Seamless slash commands in Claude Code CLI  
📊 **Real-time Monitoring** - Live dashboard and agent activity tracking  
🔄 **SPARC Methodology** - Specification → Pseudocode → Architecture → Refinement → Completion  

## Quick Start

### Installation

```bash
# Install globally
pip install sparc-cli

# Run interactive installer
sparc-install

# Initialize in your project
cd your-project
sparc init

# Use in Claude Code
/sparc "Build a REST API for user management"
```

### System Requirements

- Python 3.11+
- Docker Desktop (for containers)
- Supabase account (for cloud features)
- Claude Code CLI (for slash commands)

## Usage

### Basic Commands

```bash
# Initialize SPARC in current directory
sparc init

# Check system status
sparc status

# Run development task
sparc run "Create a web application with user authentication"

# Manage Docker containers
sparc docker start
sparc docker stop
sparc docker status

# Configuration management
sparc config show
sparc config set supabase.project_url "https://your-project.supabase.co"
```

### Claude Code Integration

After running `sparc init`, use these commands in Claude Code:

- `/sparc` - Enter SPARC development mode
- `/stopsparc` - Exit SPARC mode
- `/phase` - Check current development phase
- `/status` - View project status
- `/agents` - Show agent activity

## Architecture

### The 36 AI Agents

**Orchestrators (11 agents)**
- Uber Orchestrator - Master conductor
- Goal Clarification - Requirements gathering
- Specification Phase - Detailed specs
- Architecture Phase - System design
- Pseudocode Phase - High-level implementation
- Refinement Implementation - Code generation
- Refinement Testing - Test suite creation
- BMO Completion - Final validation
- Completion Documentation - Docs generation
- Completion Maintenance - Ongoing support
- State Scribe - Memory management

**Researchers (3 agents)**
- Strategic Research Planner
- Edge Case Synthesizer
- High-Level Test Researcher

**Writers (6 agents)**
- Comprehensive Spec Writer
- Example-Based Spec Writer
- Pseudocode Writer
- High-Level Architect
- Feature Documentation Writer
- Acceptance Test Plan Writer

**Coders (3 agents)**
- Framework Boilerplate Coder
- Test-Driven Coder
- Targeted Debugger

**Reviewers (4 agents)**
- Code Comprehension Assistant
- Devil's Advocate Evaluator
- Optimizer Module
- Security Reviewer

**Testers (2 agents)**
- TDD Test Master
- Chaos Engineer

**BMO Agents (6 agents)**
- Contract Verifier
- E2E Test Generator
- Intent Triangulator
- Holistic Intent Verifier
- System Model Synthesizer
- Test Suite Generator

**Utility Agent (1 agent)**
- Spec to Test Plan Converter

### SPARC Methodology

1. **Specification** - Gather requirements and define scope
2. **Pseudocode** - Create high-level implementation plan
3. **Architecture** - Design system structure and components
4. **Refinement** - Generate code and tests
5. **Completion** - Validate, document, and deploy

## Configuration

### Global Configuration

Located at `~/.sparc/config.json`:

```json
{
  "supabase": {
    "project_url": "https://your-project.supabase.co",
    "anon_key": "your-anon-key",
    "service_role_key": "your-service-role-key"
  },
  "agent_system": {
    "max_concurrent_agents": 5,
    "agent_timeout_minutes": 10,
    "auto_phase_progression": true,
    "approval_required_phases": ["goal-clarification", "specification", "architecture"]
  },
  "projects": {
    "sparc-abc123": {
      "path": "/path/to/project",
      "name": "My Project",
      "created_at": 1640995200
    }
  }
}
```

### Project Configuration

Located at `.sparc/project.json` in each project:

```json
{
  "project_id": "sparc-abc123",
  "name": "My Project",
  "created_at": 1640995200,
  "sparc_cli_version": "1.0.0",
  "settings": {
    "auto_phase_progression": true,
    "approval_required_phases": ["goal-clarification", "specification", "architecture"],
    "max_concurrent_agents": 5,
    "agent_timeout_minutes": 10
  }
}
```

## Docker Services

SPARC CLI automatically manages these Docker containers:

- **Qdrant** - Vector database (ports 6336:6333, 6337:6334)
- **PostgreSQL** - Relational database (port 5432)

## Development

### Building from Source

```bash
git clone https://github.com/your-org/sparc-cli
cd sparc-cli
pip install -e .
```

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
black sparc_cli/
ruff check sparc_cli/
mypy sparc_cli/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- 📖 Documentation: https://sparc-cli.readthedocs.io
- 🐛 Issues: https://github.com/your-org/sparc-cli/issues
- 💬 Discussions: https://github.com/your-org/sparc-cli/discussions

## Roadmap

- [ ] VS Code extension
- [ ] Web dashboard
- [ ] Multi-language support
- [ ] Cloud deployment integration
- [ ] Advanced monitoring and analytics

---

**Built with ❤️ by the SPARC Development Team**