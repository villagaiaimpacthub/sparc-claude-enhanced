# Context7 MCP Integration Guide for SPARC Agents

## Overview

Context7 MCP is integrated into SPARC agents to enhance documentation quality by analyzing actual implementation code rather than relying only on specifications.

## When Context7 Is Used

Context7 is specifically used in **documentation phases** (NOT during active file creation or agent triggering):

- ✅ **completion-documentation** phase (final documentation generation)
- ✅ **API documentation** generation from implemented code
- ✅ **User documentation** based on actual features
- ❌ **NOT during file creation** (Write/Edit operations)
- ❌ **NOT during agent triggering** (hooks remain unaffected)

## Hook Safety

Context7 MCP calls are made **AFTER** file creation is complete:

1. **Agents create files** (triggers hooks normally)
2. **State-scribe commits to git** (hooks work as designed)
3. **Documentation agents use Context7** (analyze completed code)
4. **No interference** with existing hook system

## Agent Integration Pattern

### For Documentation Agents

When an agent receives `"use_context7": true` in task context:

```python
# Check if Context7 is available and requested
if task_context.get("use_context7") and task_context.get("codebase_directory"):
    # Use Context7 to analyze codebase
    codebase_analysis = await analyze_with_context7(task_context["codebase_directory"])
    # Generate documentation based on actual implementation
else:
    # Fallback to specification-based documentation
```

### MCP Call Pattern

Context7 MCP calls should be made using `/mcp__context7__analyze` slash commands:

```
/mcp__context7__analyze codebase_path={namespace}/src/ output_format=api_documentation
```

## Integration Points

### 1. completion-documentation Orchestrator
- **user_docs_task_id**: Uses Context7 to analyze features from implementation
- **api_docs_task_id**: Uses Context7 to generate accurate API docs from code
- **developer_docs_task_id**: Can use Context7 for implementation guides

### 2. code-comprehension-assistant-v2 Agent
- Receives `"use_context7": true` flag
- Analyzes codebase before generating API documentation
- Creates accurate schemas and endpoint documentation

### 3. docs-writer-feature Agent  
- Receives `"analyze_codebase": "{namespace}/src/"` parameter
- Uses Context7 to understand implemented features
- Generates user documentation matching actual functionality

## Timing and Sequence

```
1. Implementation Phase Completes
   ├── Files created: src/main.py, src/api/, etc.
   ├── State-scribe commits: "feat: Implement core functionality"
   └── Hooks trigger normally ✅

2. Documentation Phase Begins
   ├── completion-documentation orchestrator starts
   ├── Delegates to documentation agents
   └── Context7 analysis requested

3. Context7 Analysis (Safe Point)
   ├── /mcp__context7__analyze {namespace}/src/
   ├── Analyzes completed implementation
   └── Returns feature analysis

4. Documentation Generation
   ├── Generate docs based on analysis
   ├── Create files: docs/api/, docs/user/
   └── State-scribe commits: "docs: Add final documentation"
```

## Error Handling

Context7 integration includes fallback mechanisms:

```python
try:
    # Attempt Context7 analysis
    if use_context7:
        codebase_analysis = analyze_with_context7(codebase_path)
        documentation = generate_from_analysis(codebase_analysis)
except Exception as e:
    # Fallback to specification-based generation
    console.print(f"[yellow]Context7 unavailable, using specifications: {e}[/yellow]")
    documentation = generate_from_specifications(task_context)
```

## Hook Compatibility

✅ **Hooks remain unaffected because**:
- Context7 calls happen in agent execution (not during Write/Edit)
- MCP calls don't trigger PostToolUse hooks (different tool type)
- Agent workflow triggering happens before Context7 analysis
- Git commits occur before documentation analysis

## Testing Context7 Integration

### Test Command
```bash
uv run agents/uber_orchestrator.py --goal "build a REST API" --namespace test_context7
```

### Expected Behavior
1. Normal SPARC workflow execution
2. Implementation phase creates source code
3. Documentation phase uses Context7 to analyze code
4. Generated documentation reflects actual implementation
5. Git commits occur normally throughout process

### Verification
- Check git log for proper phase commits
- Verify documentation matches implemented features
- Confirm no hook interference (agent tasks still queued properly)

## Best Practices

1. **Always provide fallback** if Context7 fails
2. **Use Context7 only in documentation phases** (not implementation)
3. **Pass explicit codebase paths** for analysis
4. **Include Context7 usage in AI-verifiable outcomes**
5. **Test hook compatibility** when adding new Context7 integrations

## Agent Modification Template

```python
async def _execute_task(self, task: TaskPayload, context: Dict[str, Any]) -> AgentResult:
    # Standard agent logic...
    
    # Context7 integration point (safe - after file creation)
    if context.get("use_context7") and context.get("codebase_directory"):
        try:
            # Analyze codebase with Context7
            analysis = await self._analyze_with_context7(context["codebase_directory"])
            # Use analysis for enhanced documentation
            documentation = self._generate_from_analysis(analysis, context)
        except Exception as e:
            # Fallback to specification-based approach
            documentation = self._generate_from_specifications(context)
    else:
        documentation = self._generate_from_specifications(context)
    
    # Create documentation files (triggers hooks normally)
    # ... rest of agent logic
```

This integration enhances documentation quality while maintaining full compatibility with the existing hook-based agent coordination system.