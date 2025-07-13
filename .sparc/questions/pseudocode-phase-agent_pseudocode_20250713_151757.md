# 🤖 SPARC Interactive Question

**Agent**: pseudocode-phase-agent  
**Phase**: pseudocode  
**Question ID**: pseudocode-phase-agent_pseudocode_20250713_151757

## Question
What authentication method should the API use? building on your previous answer about API endpoints should implement: 1) Input validatio...

## Context
**Progress**: 2 questions answered
**Previous Answer**: API endpoints should implement: 1) Input validation using schema validation, 2) Authentication check...

## AI-Verifiable Success Criteria
✅ Answer is specific and measurable
   📋 Verification: Check that answer contains specific details, numbers, or measurable outcomes
   ✅ Success: 'API should respond in under 200ms' or 'Support 1000 concurrent users'
   ❌ Failure: 'API should be fast' or 'Should handle lots of users'
✅ Answer avoids vague or subjective terms
   📋 Verification: Scan answer for vague terms like 'good', 'fast', 'easy', 'nice'
   ✅ Success: 'REST API with JSON responses' or 'React frontend with TypeScript'
   ❌ Failure: 'Good API' or 'Nice interface' or 'Fast system'
✅ API functionality includes specific HTTP methods and endpoints
   📋 Verification: Check that answer specifies HTTP methods (GET, POST, PUT, DELETE) and endpoint paths
   ✅ Success: 'GET /api/users, POST /api/users, PUT /api/users/{id}'
   ❌ Failure: 'User management endpoints' or 'CRUD operations'

## Suggested Answers
1. **CRUD operations for user management (GET /users, POST /users, PUT /users/{id}, DELETE /users/{id})**
2. **Authentication endpoints (POST /auth/login, POST /auth/refresh, DELETE /auth/logout)**
3. **Data processing endpoints (POST /data/process, GET /data/results, DELETE /data/{id})**
4. **File management endpoints (POST /files/upload, GET /files/{id}, DELETE /files/{id})**

5. **[Custom Answer]** - Provide your own response

## Instructions
Please respond with your choice:

- **Option 1-4**: Select one of the suggested answers
- **Custom Answer**: Provide your own detailed response
- **Skip**: Type "skip" to skip this question
- **Done**: Type "done" or "next phase" to move to the next phase

### Response Format
When you provide your answer, please create a response file:

**File**: `.sparc/responses/pseudocode-phase-agent_pseudocode_20250713_151757_response.md`

**Content**:
```markdown
# Response to Question pseudocode-phase-agent_pseudocode_20250713_151757

## Selected Answer
[Your choice: Option 1, Option 2, Option 3, Option 4, Custom Answer, or Skip]

## Answer Details
[If custom answer, provide full details here]
[If selected option, you can add additional context here]

## Additional Context
[Any additional information or clarification]
```


## 🔄 Potential Follow-up Questions
- What authentication method should the API use?
- What's the expected response time for API calls?
- Should the API support versioning (e.g., /api/v1/)?


---

**Note**: Your response will be automatically validated against the AI-verifiable criteria listed above. This ensures the SPARC workflow can proceed with measurable, testable requirements.
