# SPARC CLI User Guide

Welcome to SPARC CLI - your autonomous software development companion. This guide will help you get the most out of the 36-agent system.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core Concepts](#core-concepts)
3. [Development Workflow](#development-workflow)
4. [Commands Reference](#commands-reference)
5. [Claude Code Integration](#claude-code-integration)
6. [Project Management](#project-management)
7. [Advanced Features](#advanced-features)
8. [Best Practices](#best-practices)

## Getting Started

### Your First Project

After installation, initialize SPARC in your project:

```bash
cd your-project
sparc init
```

This creates the minimal SPARC configuration needed to get started.

### Basic Usage

1. **Start Claude Code** in your project directory
2. **Use `/sparc`** to enter development mode
3. **Describe your goal** naturally
4. **Watch the agents work** through the SPARC methodology

Example:
```
/sparc "Create a REST API for a todo list application with user authentication"
```

## Core Concepts

### The SPARC Methodology

SPARC follows a structured 5-phase development approach:

1. **Specification** - Understanding and documenting requirements
2. **Pseudocode** - High-level implementation planning
3. **Architecture** - System design and component structure
4. **Refinement** - Code generation and testing
5. **Completion** - Final validation and documentation

### The 36 Agents

SPARC employs 36 specialized AI agents organized into categories:

- **11 Orchestrators** - Manage phases and coordination
- **6 Writers** - Create specifications and documentation
- **4 Reviewers** - Quality assurance and security
- **3 Researchers** - Strategic planning and analysis
- **3 Coders** - Implementation and debugging
- **2 Testers** - Test generation and validation
- **6 BMO Agents** - Final verification and completion
- **1 Utility Agent** - Supporting functionality

### Project Structure

Each SPARC project contains:

```
your-project/
├── .sparc/
│   ├── project.json          # Project configuration
│   └── session_state.json    # Current session state
├── .claude/
│   └── commands/             # Claude Code slash commands
│       ├── sparc.md
│       ├── stopsparc.md
│       ├── status.md
│       ├── phase.md
│       └── agents.md
└── your-application-files/
```

## Development Workflow

### 1. Goal Clarification

Start by describing what you want to build:

```
/sparc "I need a web application for managing customer orders with inventory tracking"
```

The Goal Clarification orchestrator will:
- Analyze your requirements
- Ask clarifying questions
- Define project scope
- Set success criteria

### 2. Specification Phase

The system automatically progresses to creating detailed specifications:
- Technical requirements
- User stories and use cases
- API specifications
- Database schemas
- UI/UX requirements

### 3. Architecture Phase

Architects design the system:
- System architecture diagrams
- Component relationships
- Technology stack decisions
- Deployment strategies
- Security considerations

### 4. Refinement Phase

Implementation begins:
- Code generation
- Test creation
- Database setup
- API implementation
- Frontend development

### 5. Completion Phase

Final validation and delivery:
- End-to-end testing
- Documentation generation
- Deployment preparation
- Performance optimization
- Security verification

### Monitoring Progress

Track progress with:

```bash
# Check current phase
/phase

# View project status
/status

# See agent activity
/agents

# Monitor system health
sparc status
```

## Commands Reference

### Claude Code Slash Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/sparc` | Enter SPARC development mode | `/sparc "your development goal"` |
| `/stopsparc` | Exit SPARC mode | `/stopsparc` |
| `/status` | View project status | `/status` |
| `/phase` | Check current development phase | `/phase` |
| `/agents` | Show agent activity | `/agents` |

### CLI Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `sparc init` | Initialize project | `sparc init [--project-id ID]` |
| `sparc status` | System status | `sparc status` |
| `sparc run` | Run development task | `sparc run "goal description"` |
| `sparc docker` | Manage containers | `sparc docker start\|stop\|status` |
| `sparc config` | Configuration management | `sparc config show\|set\|get` |

### Configuration Commands

```bash
# View all configuration
sparc config show

# Set configuration values
sparc config set supabase.project_url "https://your-project.supabase.co"
sparc config set agent_system.max_concurrent_agents 3

# Get specific values
sparc config get supabase.project_url
```

## Claude Code Integration

### Setting Up

SPARC integrates seamlessly with Claude Code CLI:

1. Install Claude Code CLI
2. Run `sparc init` in your project
3. Use slash commands in Claude Code

### Slash Command Details

#### `/sparc` Command

Enters SPARC development mode and processes your goal:

```
/sparc "Build a user authentication system with JWT tokens"
```

Features:
- Natural language goal processing
- Automatic phase progression
- Real-time agent coordination
- Progress monitoring

#### `/status` Command

Shows comprehensive project status:

```
/status
```

Displays:
- Current development phase
- Active agents
- System health
- Project information
- Recent activity

#### `/phase` Command

Shows detailed phase information:

```
/phase
```

Includes:
- Current phase description
- Progress indicators
- Next steps
- Agent assignments

### Session Management

SPARC maintains session state across Claude Code interactions:

- **Persistent Context** - Agents remember previous conversations
- **Phase Continuity** - Work continues from where you left off
- **Goal Tracking** - Original objectives remain in focus

## Project Management

### Multi-Project Support

SPARC supports multiple projects simultaneously:

```bash
# Initialize different projects
cd project-a && sparc init
cd project-b && sparc init

# Each project maintains separate state
```

### Project Configuration

Customize project behavior in `.sparc/project.json`:

```json
{
  "project_id": "my-project-123",
  "name": "My Awesome Project",
  "settings": {
    "auto_phase_progression": true,
    "approval_required_phases": ["specification", "architecture"],
    "max_concurrent_agents": 5,
    "agent_timeout_minutes": 10
  }
}
```

### Global vs Project Settings

- **Global settings** (`~/.sparc/config.json`) apply to all projects
- **Project settings** (`.sparc/project.json`) override global settings
- **Session settings** are temporary and reset between sessions

## Advanced Features

### Custom Agent Configuration

Adjust agent behavior:

```bash
# Set maximum concurrent agents
sparc config set agent_system.max_concurrent_agents 3

# Set agent timeout
sparc config set agent_system.agent_timeout_minutes 15

# Require approval for phases
sparc config set agent_system.approval_required_phases '["goal-clarification", "specification"]'
```

### Memory Management

SPARC uses sophisticated memory systems:

- **Vector Memory** (Qdrant) - Semantic code understanding
- **Relational Memory** (PostgreSQL) - Structured project data
- **Cloud Memory** (Supabase) - Persistent cross-session state

### Real-time Monitoring

Monitor system activity:

```bash
# View system status
sparc status

# Check Docker containers
sparc docker status

# Monitor agent activity
sparc agents --project-id your-project
```

### Supabase Integration

Advanced cloud features:

- **Real-time collaboration** - Multiple developers on same project
- **Cross-device synchronization** - Work from anywhere
- **Audit trails** - Complete development history
- **Analytics** - Development metrics and insights

## Best Practices

### Goal Specification

**Good Goals:**
```
/sparc "Create a REST API for a book library with user authentication, book search, and borrowing system"
```

**Better Goals:**
```
/sparc "Build a library management REST API with:
- User registration and JWT authentication
- Book catalog with search by title, author, genre
- Borrowing system with due dates and renewals
- Admin panel for book management
- PostgreSQL database
- Express.js backend"
```

### Phase Management

1. **Let phases complete** - Don't skip ahead
2. **Provide feedback** - Agents learn from your input
3. **Review outputs** - Check specifications and architecture
4. **Ask questions** - Clarify anything unclear

### Agent Collaboration

1. **Trust the process** - Agents are designed to work together
2. **Monitor progress** - Use `/status` and `/agents` regularly
3. **Intervene when needed** - Guide agents if they're off-track
4. **Provide context** - Share relevant information

### Project Organization

1. **Clear project structure** - Organize code logically
2. **Consistent naming** - Use meaningful file and variable names
3. **Document decisions** - Agents will reference your docs
4. **Version control** - Use git alongside SPARC

### Performance Optimization

1. **Adjust agent limits** - Reduce concurrent agents if system is slow
2. **Use specific goals** - Detailed goals get better results
3. **Regular cleanup** - Remove unused projects
4. **Monitor resources** - Check Docker container health

## Troubleshooting

### Common Issues

**Agents Not Responding:**
```bash
# Check system status
sparc status

# Restart Docker containers
sparc docker restart

# Check Supabase connection
sparc config show
```

**Phase Stuck:**
```bash
# Check current phase
/phase

# Review agent activity
/agents

# Restart SPARC session
/stopsparc
/sparc "continue with current project"
```

**Configuration Issues:**
```bash
# Reset to defaults
sparc config set agent_system.max_concurrent_agents 5

# Reconfigure Supabase
sparc-install
```

### Getting Help

1. **Check status first** - `sparc status`
2. **Review logs** - Check Docker container logs
3. **Consult documentation** - Read relevant guide sections
4. **Community support** - Ask in GitHub discussions
5. **Report bugs** - Create GitHub issues

## Next Steps

Now that you understand SPARC CLI basics:

1. **Try the examples** - See `docs/EXAMPLES.md`
2. **Learn about agents** - Read `docs/AGENTS.md`
3. **Advanced configuration** - Check `docs/CONFIGURATION.md`
4. **Integration guides** - Explore `docs/INTEGRATIONS.md`

---

**Happy developing with SPARC!** 🚀

The 36 agents are ready to help you build amazing software.