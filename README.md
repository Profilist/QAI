# QAI (Hack the North 2025 Submission)
> Autonomous agentic QA system that integrates with CI to analyze PRs, generate test suites, and execute them with computer-use agents.

<img width="1440" height="900" alt="qai-zeta vercel app_(MacBook Air)" src="https://github.com/user-attachments/assets/07db2968-f7ab-487d-935c-be5835bce1cf" />
<img width="1440" height="900" alt="qai-zeta vercel app_(MacBook Air) (1)" src="https://github.com/user-attachments/assets/6bcfb3d1-9f8d-44da-beb6-3c3f150da52c" />
<img width="1440" height="900" alt="qai-zeta vercel app_1000_test-suites_68(MacBook Air)" src="https://github.com/user-attachments/assets/82dcbc8e-a322-4e1f-b494-609dc9c4052c" />


## How It Works
- PR → Tests automatically: Submitting a PR triggers a pipeline that uses LLMs to analyze changes and synthesize suites (ex. personas like seniors, or categories like authentication) and tests that are often missed by humans (ex. edge cases, race conditions)
- Multi-suite execution: Up to 4 suites run concurrently on pre-configured VMs that computer-use agents can navigate via Cua
- Evidence and traceability: Video recordings and condensed step logs for each test to facilitate bug reproduction and fixes
- API-driven: FastAPI service to run single suites or full results; simple to integrate with any CI provider

## System Flow
1. CI calls the pipeline for the PR
2. Pipeline analyzes PR diff + codebase summary to generate scenarios
3. Scenarios are saved to Supabase as:
   - `results` (one per PR)
   - `suites` (categories, up to 4)
   - `tests` (2–3 high-value tests per suite where meaningful)
4. Pipeline triggers the Agent Runner API (`/run-result`) to execute all suites
5. Agents interact with a browser VM, record videos, and stream steps back
6. The API updates `tests`, then aggregates to `results.overall_result` and `run_status`

## Repository Structure
```
backend/
  agents/            # FastAPI service, agent runner, DB integration
  cicd/              # CI pipeline scripts
  tests/             # Python tests
frontend/            # Next.js dashboard
API.md               # Detailed API and DB schema
README.md            # This file
```

### Backend References
- `backend/agents/main.py`: FastAPI with endpoints
  - `GET /health`
  - `POST /run-suite` (single suite by `suite_id`)
  - `POST /run-result` (run all suites for a `result_id`)
  - `POST /run-agents` (submit explicit `test_specs`)
- `backend/agents/runner.py`: Orchestrates agent runs, recording, DB updates
  - `run_suites_for_result(result_id)`: assigns containers and runs suites concurrently
  - `run_single_agent(spec)`: executes all tests for a suite
- `backend/agents/database.py`: Supabase helpers for `results`, `suites`, `tests`
- `backend/cicd/qai-pipeline.js`: CI entrypoint
  - Generates scenarios with OpenAI (rich `summary` for each test)
  - Writes to Supabase (`results/suites/tests`)
  - Calls `POST /run-result` and verifies final state
  - Mirrors files to `backend/artifacts/agent/<runId>`

## Requirements
- Python 3.11+
- Node.js 18+
- Supabase project 
- OpenAI API key
- Agent compute provider (CUA) credentials
- AWS S3 bucket

## Environment Variables
Create a `.env` in the repo root (consumed by both backend and cicd):

Backend:
- `SUPABASE_URL` / `SUPABASE_KEY`
- `CUA_API_KEY` (agent provider API key)
- `CUA_MODEL` (e.g., `anthropic/claude-3-5-sonnet-20241022`)
- `CUA_CONTAINER_1`..`CUA_CONTAINER_4` (names/ids of up to 4 agent containers)
- `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET_NAME` (optional, recording uploads)

Pipeline (CI):
- `OPENAI_API_KEY`
- `GITHUB_TOKEN`
- `GITHUB_REPOSITORY`, `GITHUB_EVENT_PATH` (GitHub Actions)
- `QAI_ENDPOINT` (e.g., `http://localhost:8000` for API)
- `DEPLOYMENT_URL` (target app base URL; used in summaries)
- `AGENT_TIMEOUT` (ms; default 600000)

## Database Schema
See `API.md` for canonical DDL. Current tables include:
- `results`: `id`, `pr_link`, `pr_name`, `overall_result` (jsonb), `run_status`
- `suites`: `id`, `result_id`, `name`
- `tests`: `id`, `suite_id`, `name`, `summary`, `test_success`, `run_status`, `steps` (jsonb), `s3_link`

## Setup & Run (Local)
1) Install dependencies
```
# Python backend
cd backend/agents
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Node cicd
cd ../cicd
npm ci
```

2) Start the API
```
# From repo root
python -m uvicorn backend.agents.main:app --host 0.0.0.0 --port 8000
```

3) Run the pipeline end-to-end
```
# From backend/cicd
node qai-pipeline.js full
# or
node qai-pipeline.js analyze
node qai-pipeline.js test
```

## Running Only Agents for Existing Suites
If suites/tests have already been created in Supabase (e.g., via the pipeline), you can run them by `result_id`:
```
curl -X POST "$QAI_ENDPOINT/run-result" \
  -H 'Content-Type: application/json' \
  -d '{"result_id": 123}'
```

## Frontend Dashboard
```
cd frontend
npm ci
npm run dev
# open http://localhost:3000
```
