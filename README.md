# 🤖 SPARC - Autonomous Software Development

**36 AI agents that code complete software projects for you.**

## Install

**macOS/Linux:** One-line install
```bash
curl -sSL https://raw.githubusercontent.com/villagaiaimpacthub/sparc-installer/main/install.sh | bash
```

## Setup

1. **Database:** Create free [Supabase](https://supabase.com) account
2. **One-click:** Copy [`setup.sql`](setup.sql) → Paste in Supabase SQL Editor → Run
3. **Connect:** Run `sparc-init` and enter your Supabase URL + API key

## Use

```bash
# In any project directory
cd my-project
sparc-init

# Start building with Claude Code
claude
/sparc "Build a REST API with user authentication"
```

**The 36 agents handle everything:** requirements → architecture → code → tests → docs

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