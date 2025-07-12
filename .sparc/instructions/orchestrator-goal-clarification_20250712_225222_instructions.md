# 🎯 SPARC Perfect Execution Context

## 🤖 AGENT ROLE: Goal Clarification Specialist - Convert vague goals into AI-verifiable requirements

**Primary Mission**: Create comprehensive mutual understanding document

**Execution Mode**: Perfect Prompt with Complete Context Awareness

## 🎯 PRIMARY OBJECTIVE

Create comprehensive mutual understanding document

### 🎯 AI-VERIFIABLE OUTCOMES REQUIRED
- All defined endpoints return expected status codes within 500ms
- 100% of responses validate against OpenAPI schema
- All protected endpoints require valid authentication
- Every API function mapped to specific HTTP method + path

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

### 1. API endpoints respond with correct HTTP status codes
- **Verification**: Send HTTP requests and verify response codes
- **Success**: GET /users returns 200, POST /users returns 201
- **Failure**: GET /users returns 500 or timeout
- **Measurable**: All defined endpoints return expected status codes within 500ms
### 2. API returns valid JSON in specified format
- **Verification**: Parse response JSON and validate against schema
- **Success**: {"users": [{"id": 1, "name": "John"}]} matches UserList schema
- **Failure**: Invalid JSON or missing required fields
- **Measurable**: 100% of responses validate against OpenAPI schema
### 3. Authentication prevents unauthorized access
- **Verification**: Send requests without valid tokens and verify rejection
- **Success**: Protected endpoints return 401 without valid JWT
- **Failure**: Protected endpoints accessible without authentication
- **Measurable**: All protected endpoints require valid authentication
### 4. API functionality clearly defined with specific endpoints
- **Verification**: Check documentation lists exact HTTP methods and paths
- **Success**: GET /api/v1/users, POST /api/v1/users, PUT /api/v1/users/{id}
- **Failure**: Vague description like 'user management endpoints'
- **Measurable**: Every API function mapped to specific HTTP method + path

### 🔍 Glass Box Verification Points
- **verify_api_endpoints_respond_with_correct_http_status_codes**: All defined endpoints return expected status codes within 500ms
- **verify_api_returns_valid_json_in_specified_format**: 100% of responses validate against OpenAPI schema
- **verify_authentication_prevents_unauthorized_access**: All protected endpoints require valid authentication
- **verify_api_functionality_clearly_defined_with_specific_endpoints**: Every API function mapped to specific HTTP method + path

### ✅ Success Examples
- GET /users returns 200, POST /users returns 201
- {"users": [{"id": 1, "name": "John"}]} matches UserList schema
- Protected endpoints return 401 without valid JWT
- GET /api/v1/users, POST /api/v1/users, PUT /api/v1/users/{id}

### ❌ Failure Examples
- GET /users returns 500 or timeout
- Invalid JSON or missing required fields
- Protected endpoints accessible without authentication
- Vague description like 'user management endpoints'

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
- **AI-Verifiable Score**: Must achieve ≥0.8
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

**File**: `.sparc/completions/orchestrator-goal-clarification_20250712_225223_done.md`

**Content**:
```markdown
# Task Completion Report

## Agent: orchestrator-goal-clarification
## Completed: 2025-07-12T22:52:23.067863

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