# 🎯 SPARC Perfect Execution Context

## 🤖 AGENT ROLE: Goal Clarification Specialist - Convert vague goals into AI-verifiable requirements

**Primary Mission**: Create comprehensive mutual understanding document

**Execution Mode**: Perfect Prompt with Complete Context Awareness

## 🎯 PRIMARY OBJECTIVE

Create comprehensive mutual understanding document

### 🎯 AI-VERIFIABLE OUTCOMES REQUIRED
- Main page loads with 200 status in under 2 seconds
- All pages render correctly at 375px, 768px, 1024px widths

### 📊 SUCCESS MEASUREMENT
Every outcome listed above MUST be achievable and verifiable by automated testing.

## 🧠 COMPLETE PROJECT CONTEXT

### 💬 User Conversation History
**Q1**: Unknown question
**A1**: [Pending response]

**Q2**: Unknown question
**A2**: [Pending response]

**Q3**: Unknown question
**A3**: [Pending response]

## ✅ AI-VERIFIABLE SUCCESS CRITERIA

### 1. Website loads successfully in browser
- **Verification**: HTTP GET request returns 200 and valid HTML
- **Success**: curl -I website.com returns 200 OK with text/html
- **Failure**: Returns 404, 500, or non-HTML content
- **Measurable**: Main page loads with 200 status in under 2 seconds
### 2. Website is mobile responsive
- **Verification**: Test rendering at mobile viewport sizes
- **Success**: Content adapts properly at 375px width
- **Failure**: Content overflows or becomes unreadable on mobile
- **Measurable**: All pages render correctly at 375px, 768px, 1024px widths

### 🔍 Glass Box Verification Points
- **verify_website_loads_successfully_in_browser**: Main page loads with 200 status in under 2 seconds
- **verify_website_is_mobile_responsive**: All pages render correctly at 375px, 768px, 1024px widths

### ✅ Success Examples
- curl -I website.com returns 200 OK with text/html
- Content adapts properly at 375px width

### ❌ Failure Examples
- Returns 404, 500, or non-HTML content
- Content overflows or becomes unreadable on mobile

## 🎯 BMO INTENT ALIGNMENT

### 🎯 Primary Intent
Build software project with proper architecture and best practices

### ⚖️ Intent Validation Required
Your solution MUST align with the primary intent and avoid all anti-goals.

## 🔄 PERFECT EXECUTION INSTRUCTIONS

1. **Context Analysis**: Read and understand all project context provided above
2. **Requirement Validation**: Ensure all AI-verifiable outcomes are achievable
3. **Implementation Planning**: Plan approach to meet all success criteria
4. **Quality Focus**: Prioritize correctness and verifiability over speed
5. **Documentation**: Document all decisions and rationale
6. **Testing**: Ensure all outcomes can be verified automatically
7. **Completion**: Signal completion with required file
8. **Mutual Understanding**: Create comprehensive mutual understanding document
9. **Constraints**: Document all constraints and anti-goals clearly
10. **Verifiability**: Ensure all requirements are AI-verifiable

### 🎯 CRITICAL SUCCESS FACTORS
- Every requirement must have AI-verifiable outcome
- All edge cases must be explicitly handled  
- Error conditions must be predictable and testable
- Solution must pass glass box verification tests
- Documentation must be complete and accurate

## 🚨 QUALITY GATES & VALIDATION

### 📊 Quality Standards
- **AI-Verifiable Score**: Must achieve ≥0.9
- **Test Coverage**: All critical paths must be testable
- **Error Handling**: All failure modes must be documented
- **Performance**: All response time requirements must be met

### 🔍 Pre-Completion Checklist
Before marking task complete, verify:
- [ ] All AI-verifiable outcomes are achievable
- [ ] All success criteria can be tested automatically
- [ ] All files created follow project conventions
- [ ] All error conditions are handled gracefully
- [ ] Documentation is complete and accurate
- [ ] Glass box tests can verify the implementation

### ⚠️ Failure Conditions
Task is considered FAILED if:
- Any AI-verifiable outcome cannot be achieved
- Success criteria are vague or unmeasurable
- Critical errors are not handled
- Documentation is missing or incomplete

## 🏁 COMPLETION REQUIREMENTS

### 📁 Completion Signal
When you have successfully completed this task, create the following file:

**File**: `.sparc/completions/orchestrator-goal-clarification_20250712_232430_done.md`

**Content**:
```markdown
# Task Completion Report

## Agent: orchestrator-goal-clarification
## Completed: 2025-07-12T23:24:30.340687

## Summary
[Brief summary of what was accomplished]

## Files Created/Modified
[List all files that were created or modified]

## AI-Verifiable Outcomes Achieved
[List each outcome and how it can be verified]

## Quality Validation
[Confirm all quality gates were met]

## Next Steps
[Any recommendations for next phase]
```

### 🔄 Workflow Continuation
Creating this completion file will automatically trigger the SPARC hook system to:
1. Analyze your accomplishments
2. Validate against success criteria
3. Determine the next agent in the workflow
4. Continue autonomous development process

**IMPORTANT**: Do not create the completion file until ALL requirements are met.