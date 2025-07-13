---
description: "Switch to a different SPARC project with state tracking"
allowed-tools: ["bash", "read"]
---

# 🔄 Switch SPARC Project

**Project Switching with State Tracking**

Let me help you switch to a different SPARC project and show you the last state of each project...

## Current Project Status

First, let me check if we're currently in a SPARC project:

```bash
# Check current directory for SPARC project
current_dir=$(pwd)
if [ -f "CLAUDE.md" ] && grep -q "project_id:" CLAUDE.md; then
    echo "✅ Currently in SPARC project: $(basename "$current_dir")"
    
    # Show current project state if available
    if [ -f ".sparc/project_state.json" ]; then
        echo ""
        echo "📊 Current Project State:"
        python3 -c "
import json
import sys
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
    
    print(f'Phase: {current_phase} ({completion:.0f}% complete)')
    print(f'Goal: {state.get('last_goal', 'Not defined')}')
    print(f'Files: {len(state.get('progress', {}).get('files_created', []))} created')
    print(f'Sessions: {state.get('session_count', 1)}')
    
    # Show database health
    db_health = state.get('database_health', {})
    supabase_ok = db_health.get('supabase', False)
    qdrant_ok = db_health.get('qdrant', False)
    status = '🟢 Healthy' if supabase_ok and qdrant_ok else '🟡 Needs attention'
    print(f'Databases: {status}')
    
    # Show next actions
    next_actions = state.get('progress', {}).get('next_actions', [])
    if next_actions:
        print(f'Next: {', '.join(next_actions[:2])}')
        
except Exception as e:
    print('No state information available')
"
    else
        echo "No state tracking available for current project"
    fi
    echo ""
else
    echo "❌ Not currently in a SPARC project"
    echo ""
fi
```

## Available SPARC Projects

Let me scan for all your SPARC projects with their last states:

```bash
echo "🔍 Scanning for SPARC projects..."
echo ""

# Check recent projects with state
if [ -f "$HOME/.sparc/recent_projects.json" ]; then
    echo "📁 Recent SPARC Projects (with last activity):"
    python3 -c "
import json
import sys
import os
from pathlib import Path
from datetime import datetime

try:
    with open('$HOME/.sparc/recent_projects.json', 'r') as f:
        projects = json.load(f)
    
    for i, proj in enumerate(projects[:5], 1):
        if os.path.exists(proj):
            # Check if it's a SPARC project
            claude_md = Path(proj) / 'CLAUDE.md'
            state_file = Path(proj) / '.sparc' / 'project_state.json'
            
            if claude_md.exists():
                try:
                    content = claude_md.read_text()
                    if 'project_id:' in content:
                        project_name = Path(proj).name
                        print(f'{i}. {project_name} ({proj})')
                        
                        # Show last state if available
                        if state_file.exists():
                            try:
                                with open(state_file, 'r') as sf:
                                    state = json.load(sf)
                                
                                phase_names = {
                                    'goal_clarification': '🎯 Goal',
                                    'specification': '📋 Spec', 
                                    'architecture': '🏗️ Arch',
                                    'pseudocode': '📝 Code',
                                    'refinement': '⚒️ Refine',
                                    'completion': '✅ Done'
                                }
                                
                                current_phase = phase_names.get(state.get('current_phase', 'unknown'), '❓')
                                completion = state.get('progress', {}).get('phase_completion', 0) * 100
                                last_updated = state.get('last_updated', '')
                                
                                if last_updated:
                                    try:
                                        dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                                        time_str = dt.strftime('%m/%d %H:%M')
                                    except:
                                        time_str = 'Unknown'
                                else:
                                    time_str = 'Unknown'
                                
                                print(f'   {current_phase} ({completion:.0f}%) - Last: {time_str}')
                                
                                # Show database status
                                db_health = state.get('database_health', {})
                                supabase_ok = db_health.get('supabase', False)
                                qdrant_ok = db_health.get('qdrant', False)
                                if supabase_ok and qdrant_ok:
                                    print(f'   🟢 Databases ready')
                                else:
                                    print(f'   🟡 Databases need attention')
                            except:
                                print(f'   📊 State tracking available')
                        else:
                            print(f'   📊 No state tracking')
                        print('')
                except:
                    pass
except:
    print('No recent projects found')
"
else
    echo "No recent projects found"
fi
```

## Switch Project Options

### Option 1: Quick Switch (Recommended)
```bash
# Run sparc-init to get the interactive project picker
echo "💡 Quick switch: Run 'sparc-init' in your terminal"
echo "   This will show all projects with arrow-key navigation"
```

### Option 2: Direct Navigation
```bash
echo "💡 Direct navigation:"
echo "   cd /path/to/your-sparc-project"
echo "   claude"
echo "   Then use /sparc to continue development"
```

### Option 3: Recent Project by Number
Based on the list above, you can navigate directly:
```bash
echo "💡 Navigate to a recent project:"
echo "   Example: cd [project-path-from-above]"
echo "   Then: claude"
echo "   Then: /sparc"
```

## Next Steps

After switching to your project:

1. **If databases need attention**: The /sparc command will help you fix them
2. **If project is ready**: Use `/sparc` to continue from where you left off
3. **To see detailed status**: Use `/status` for comprehensive project information

## Commands

- `/sparc` - Continue autonomous development
- `/status` - Detailed project and database status
- `/agents` - View all 36 agents
- `/phase` - Check current development phase

---

*💡 Tip: Use sparc-init for the best project switching experience with full state visibility*