# QAI CI/CD Deployment Checklist

## ✅ Ready to Test Once You Add Secrets

Yes! The system is fully testable with a GitHub repo + PR once you add the required secrets.

## Required GitHub Secrets

Add these in your repo settings → Secrets and variables → Actions:

1. **`OPENAI_API_KEY`** - Your OpenAI API key (starts with `sk-`)
2. **`QAI_ENDPOINT`** - URL where your agent testing endpoint will be hosted
3. **`GITHUB_TOKEN`** - ✅ Automatically provided by GitHub Actions

## Optional Secrets

- **`DEPLOYMENT_URL`** - Override the staging URL if needed
- **`AGENT_TIMEOUT`** - Custom timeout in milliseconds (default: 300000)

## Testing Locally

1. Copy secrets to `.env`:
```bash
cd backend/cicd
cp .env.example .env
# Edit .env with your actual values
```

2. Install dependencies:
```bash
npm install
```

3. Test individual scripts:
```bash
# Requires a PR context (set GITHUB_REPOSITORY, etc.)
node analyze-pr.js

# Requires test-scenarios.json to exist
node run-tests.js

# Requires PR context
node update-summary.js
```

## Integration Requirements

### Agent Endpoint Format
Your teammate's agent endpoint should:

**Accept POST requests with:**
```json
{
  "url": "https://staging-url.com",
  "scenarios": [
    {
      "description": "Test login form",
      "priority": "high",
      "type": "ui", 
      "persona": "new_user",
      "steps": ["Navigate to login", "Enter credentials", "Submit"]
    }
  ],
  "timeout": 300000
}
```

**Return response:**
```json
[
  {
    "scenario": { /* original scenario object */ },
    "success": true,
    "error": null,
    "video_url": "https://s3.../recording.mp4",
    "duration": 12500
  }
]
```

## How to Test

1. **Create a test repo** with this CI/CD setup
2. **Add the GitHub secrets** 
3. **Create a PR** with some code changes
4. **Watch the action run** in Actions tab
5. **Check outputs** in the action logs

The workflow will:
- ✅ Analyze your PR changes
- ✅ Generate relevant test scenarios using LLM
- ✅ Send scenarios to your agent endpoint
- ✅ Pass/fail the CI based on test results
- ✅ Update codebase summary if tests pass

## Structured Output Benefits

✅ **No JSON parsing failures** - Uses OpenAI's structured output with schema validation
✅ **Guaranteed format** - Schema enforces required fields and types  
✅ **Type safety** - Enum values for priority/type prevent invalid data