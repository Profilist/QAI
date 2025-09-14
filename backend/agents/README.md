# QAI Agent Runner API

FastAPI server for hosting QAI autonomous testing agents, deployable on Vercel.

## Features

- Full REST API matching the QAI API specification
- Database integration with Supabase
- Autonomous agent execution capabilities
- CICD pipeline integration
- Vercel-ready deployment configuration

## API Endpoints

### Database Management
- `POST /results` - Create new test result
- `PATCH /results/{id}` - Update result status
- `GET /results` - Get all results
- `POST /suites` - Create new test suite
- `PATCH /suites/{id}` - Update suite status
- `GET /results/{id}/suites` - Get suites for result
- `POST /tests` - Create new test
- `PATCH /tests/{id}` - Update test status
- `GET /suites/{id}/tests` - Get tests for suite

### Agent Execution
- `POST /run-suite` - Run test suite by ID (main CICD endpoint)
- `POST /run-agent` - Run single agent (legacy)
- `POST /run-agents` - Run multiple agents (legacy)

### Utility
- `GET /health` - Health check and database status
- `GET /` - API documentation

## Environment Variables

Required environment variables:

```bash
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Agent Configuration
CUA_MODEL=anthropic/claude-3-5-sonnet-20241022
CUA_API_KEY=your_cua_api_key
CUA_CONTAINER_NAME=your_container_name

# Optional
PORT=8000
```

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env` file

3. Run the server:
```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Vercel Deployment

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel --prod
```

3. Set environment variables in Vercel dashboard

The API will be available at your Vercel deployment URL.

## CICD Integration

The server integrates with the QAI pipeline via the `/run-suite` endpoint:

1. Pipeline creates database records (results, suites, tests)
2. Pipeline calls `POST /run-suite` with suite ID
3. Agent runs tests and updates database with results
4. Pipeline verifies completion via database queries

## Database Schema

See `API.md` for complete database schema documentation.

## Files Structure

- `main.py` - Local FastAPI server
- `api/index.py` - Vercel deployment handler
- `runner.py` - Agent execution logic
- `database.py` - Database operations
- `run_suite.py` - Command-line suite runner
- `vercel.json` - Vercel deployment configuration
- `requirements.txt` - Python dependencies