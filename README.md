# 🤖 SPARC - Autonomous Software Development

**36 AI agents that code complete software projects for you.**

## Install

**macOS/Linux:** One-line install
```bash
curl -sSL https://raw.githubusercontent.com/villagaiaimpacthub/sparc-claude/main/install.sh | bash
```

## Setup

1. **Database:** Create free [Supabase](https://supabase.com) account
2. **One-click:** Copy [`setup.sql`](setup.sql) → Paste in Supabase SQL Editor → Run
3. **Initialize:** Run `sparc-init` and enter your Supabase URL + API key
4. **Hooks:** SPARC automatically installs Claude Code hooks for seamless integration

## Use

```bash
# Initialize project
cd my-project
sparc-init

# Start autonomous development  
sparc "Build a REST API with user authentication"

# Monitor progress
sparc status

# Start agents manually
sparc start

# Continue with Claude Code
claude
# File changes automatically trigger agent workflows via hooks
```

**The 36 agents handle everything:** requirements → architecture → code → tests → docs

## How It Works

SPARC uses **UV single file scripts** + **Claude Code hooks** for autonomous development:

1. **Start:** `sparc "your goal"` activates the 36-agent system via UV orchestrator
2. **Agent Execution:** Each agent runs as independent UV script with embedded dependencies
3. **Orchestration:** Agents communicate via Supabase task queue  
4. **Claude Code Integration:** Agents generate prompts, Claude Code executes file operations
5. **Hook-Driven Memory:** File changes trigger UV hooks that update agent memory
6. **Workflow Continuation:** Hooks trigger next agents in autonomous workflow
7. **Isolation:** Each project has unique namespace for complete separation

### Autonomous Workflow

```
User: sparc "Build a todo app"
  ↓
UV Orchestrator: Creates tasks → Delegates to agents
  ↓
UV Agents: Analyze requirements → Generate detailed prompts
  ↓
Claude Code: Processes prompts → Creates/edits files
  ↓
UV Hooks: Capture changes → Update memory → Trigger next agents
  ↓
Result: Complete application with tests, docs, and deployment config
```

### Key Benefits of UV Architecture

- **Self-contained agents:** Each agent is a complete sandbox with dependencies
- **Fast execution:** UV provides instant script startup and dependency resolution  
- **Easy iteration:** Modify agents without complex setup or virtual environments
- **Portable deployment:** Agents run anywhere UV is installed
- **Hook-driven automation:** File changes automatically continue workflows

## What It Does

- **Specification:** Gathers requirements and defines scope
- **Architecture:** Designs system structure and components  
- **Pseudocode:** Creates implementation plans
- **Refinement:** Generates production code and tests
- **Completion:** Validates, documents, and deploys

## Example

```
You: "Build a blog platform"

SPARC: 
✅ Analyzed requirements (User auth, posts, comments)
✅ Designed database schema (Users, Posts, Comments tables)
✅ Generated REST API (Express.js + PostgreSQL)
✅ Built React frontend (Authentication, post editor)
✅ Created test suite (95% coverage)
✅ Added deployment config (Docker + CI/CD)

Ready to deploy!
```

---

## Credits

Built on the **[Pheromind Framework](https://pheromind.ai)** - the foundational multi-agent system that makes autonomous development possible.

**Autonomous development is here.** Try it now.