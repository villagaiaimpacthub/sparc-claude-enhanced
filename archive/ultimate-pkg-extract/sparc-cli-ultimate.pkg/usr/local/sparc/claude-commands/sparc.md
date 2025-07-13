---
description: "Start SPARC autonomous development in current project"
allowed-tools: ["read", "write", "bash", "ls", "glob", "grep"]
---

**Arguments**: $ARGUMENTS

```
┌─────────────────────────────────────────────────────────────────┐
│ 🤖 SPARC Autonomous Development Starting...                    │
│                                                                 │
│ Activating 36 AI agents for your project                       │
│                                                                 │
│ cwd: $PWD                                                       │
└─────────────────────────────────────────────────────────────────┘
```

## **SPARC Project Analysis & Session Resumption**

Let me analyze this project and check for previous session state:

### Step 1: Project Detection & State Loading

```bash
# Check for SPARC project files and state
if [ -f "CLAUDE.md" ] && grep -q "project_id:" CLAUDE.md; then
    echo "✅ SPARC project detected"
    
    # Load project state if available
    if [ -f ".sparc/project_state.json" ]; then
        echo "📊 Loading previous session state..."
        python3 -c "
import json
from datetime import datetime

try:
    with open('.sparc/project_state.json', 'r') as f:
        state = json.load(f)
    
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
    last_goal = state.get('last_goal', 'Not defined')
    session_count = state.get('session_count', 1)
    
    print(f'📋 Previous Session Found:')
    print(f'   Phase: {current_phase} ({completion:.0f}% complete)')
    print(f'   Goal: {last_goal}')
    print(f'   Session: #{session_count}')
    
    # Check database health
    db_health = state.get('database_health', {})
    supabase_ok = db_health.get('supabase', False)
    qdrant_ok = db_health.get('qdrant', False)
    
    if supabase_ok and qdrant_ok:
        print(f'   🟢 Databases: Healthy')
    else:
        print(f'   🟡 Databases: Need attention')
        
    # Show next actions
    next_actions = state.get('progress', {}).get('next_actions', [])
    if next_actions:
        print(f'   ⏭️ Next: {next_actions[0]}')
        
    print('')
    print('🔄 Resuming development session...')
    
except Exception as e:
    print('📊 No previous state found - starting fresh session')
"
    else
        echo "📊 No previous state found - starting fresh session"
    fi
else
    echo "❌ This is not a SPARC project"
    echo "💡 Run 'sparc-init' first to initialize SPARC in this directory"
    echo "💡 Or use '/sparc-switch' to switch to an existing project"
    exit 1
fi
```

### Step 2: Database Connectivity Check

```bash
# Verify database connections
echo "🔍 Checking database connectivity..."

if [ -f ".env" ]; then
    # Check Qdrant
    QDRANT_URL=$(grep "QDRANT_URL=" .env | cut -d'=' -f2)
    if [ -z "$QDRANT_URL" ]; then
        QDRANT_URL="http://localhost:6336"
    fi
    
    if curl -s "$QDRANT_URL/" > /dev/null 2>&1; then
        echo "✅ Qdrant: Connected ($QDRANT_URL)"
    else
        echo "🟡 Qdrant: Not responding ($QDRANT_URL)"
        echo "💡 Start Qdrant: docker run -d --name sparc-qdrant -p 6336:6333 qdrant/qdrant"
    fi
    
    # Check Supabase configuration
    SUPABASE_URL=$(grep "SUPABASE_URL=" .env | cut -d'=' -f2)
    SUPABASE_KEY=$(grep "SUPABASE_KEY=" .env | cut -d'=' -f2)
    
    if [[ "$SUPABASE_URL" == *"supabase.co"* ]] && [[ ${#SUPABASE_KEY} -gt 20 ]] && [[ "$SUPABASE_URL" != *"your-project"* ]]; then
        echo "✅ Supabase: Configured"
    else
        echo "🟡 Supabase: Needs configuration"
        echo "💡 Edit .env file with your Supabase URL and key"
    fi
else
    echo "🟡 No .env file found"
    echo "💡 Run 'sparc-init' to set up the project properly"
fi
echo ""
```

### Step 3: Project Configuration Reading

Now let me read the project configuration to understand the current state:

**Based on the project analysis, I'll:**

1. **Read the project's CLAUDE.md** to understand the current goal and namespace
2. **Check the project type** (new, existing, or SPARC-managed)
3. **Analyze existing codebase** if present
4. **Activate appropriate SPARC agents** based on the project phase
5. **Begin autonomous development** with the 36-agent system

Let me start by reading the project configuration:

```read
./CLAUDE.md
```

## **SPARC Agent Activation**

Based on the project configuration, I'll now activate the appropriate SPARC agents:

### **Phase Detection**
I'll determine which SPARC phase this project is in:
- **Specification**: Define requirements and scope
- **Pseudocode**: High-level algorithm design  
- **Architecture**: System design and structure
- **Refinement**: Detailed implementation
- **Completion**: Testing and deployment

### **Agent Orchestration**
The **Uber Orchestrator** will coordinate:
- **Goal Clarification Agent**: Refine project objectives
- **State Scribe**: Track development progress
- **Research Agents**: Gather relevant information
- **Writer Agents**: Create documentation and specs
- **Coder Agents**: Implement functionality
- **Tester Agents**: Ensure quality
- **BMO Agents**: Validate decisions

### **Next Steps**

I'll begin autonomous development by:

1. **Clarifying the project goal** if needed
2. **Analyzing the current codebase** (if any)
3. **Creating a development plan** with the orchestrator agents
4. **Implementing features** with specialized agents
5. **Testing and validation** throughout the process

**The SPARC system is now active!** I'll work autonomously using the 36-agent methodology while keeping you informed of progress and asking for approval on major decisions.

Would you like me to begin autonomous development, or do you have specific guidance for the SPARC agents?