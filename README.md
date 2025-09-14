# QAI

QAI is an autonomous QA system that analyzes pull requests, generates focused test suites, executes them with computer-use agents, records evidence, and updates a central results database. It integrates with CI to provide end-to-end verification for web applications.

## Highlights
- PR → Tests automatically: Uses LLMs to analyze changes and synthesize suites and tests with rich context summaries
- Multi-suite execution: Up to 4 suites run concurrently on pre-configured agent containers
- Evidence and traceability: Video recordings and condensed step logs; DB reflects per-test and overall results
- API-driven: FastAPI service to run single suites or full results; simple to integrate with any CI provider

## System Flow
1. CI calls the pipeline (`backend/cicd/qai-pipeline.js`) for the PR
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
  agents/            # FastAPI service, agent runner, Supabase integration
  cicd/              # PR analysis + CI pipeline scripts
  tests/             # Python tests
  artifacts/         # Local run artifacts (videos, logs) mirrored by pipeline
frontend/            # Next.js dashboard (optional viewer)
API.md               # Detailed API and DB schema
README.md            # This file
```

### Key Back-End Components
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
- Supabase project (or compatible PostgREST + storage)
- OpenAI API key
- Agent compute provider (CUA) credentials
- AWS S3 bucket (optional, for video uploads)

## Environment Variables
Create a `.env` in the repo root (consumed by both backend and cicd):

Backend (FastAPI/agents):
- `SUPABASE_URL` / `SUPABASE_KEY`
- `CUA_API_KEY` (agent provider API key)
- `CUA_MODEL` (e.g., `anthropic/claude-3-5-sonnet-20241022`)
- `CUA_CONTAINER_1`..`CUA_CONTAINER_4` (names/ids of up to 4 agent containers)
- `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET_NAME` (optional, recording uploads)
- `PORT` (FastAPI port, default 8000)

Pipeline (CI) and shared:
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

Artifacts are mirrored to `backend/artifacts/agent/<runId>` including generated scenarios, options, API responses, and verification summaries.

## Running Only Agents for Existing Suites
If suites/tests have already been created in Supabase (e.g., via the pipeline), you can run them by `result_id`:
```
curl -X POST "$QAI_ENDPOINT/run-result" \
  -H 'Content-Type: application/json' \
  -d '{"result_id": 123}'
```

## Frontend (Optional Dashboard)
```
cd frontend
npm ci
npm run dev
# open http://localhost:3000
```

## Testing
```
cd backend
pytest
```

## Conventions
- Suites are capped to 4 (mapped to `CUA_CONTAINER_1..4`)
- Prefer 2–3 high-value tests per suite; avoid trivial/duplicate cases
- Test `summary` is the primary instruction for the agent; database adapters convert it to agent-ready format

## Troubleshooting
- API 500 on /run-result
  - Ensure `SUPABASE_URL/KEY`, `CUA_API_KEY`, and at least one `CUA_CONTAINER_*` are set
  - Check FastAPI logs and Supabase table names/columns (see API.md)
- Pipeline cannot connect to API
  - Verify `QAI_ENDPOINT` and local port; allowlist in CORS
- No suites created
  - OpenAI generation may have produced 0 suites; check `backend/cicd/test-scenarios.json`
- Videos not uploaded
  - Validate AWS credentials and `S3_BUCKET_NAME`

## Security & Data
- Secrets are read from `.env` at runtime (do not commit)
- Test artifacts can include sensitive UI states; configure S3 access policies accordingly

## Roadmap
- Retry/auto-heal for flaky steps
- Adaptive test generation from historical failures
- Richer dashboard for real-time run monitoring

## License
MIT (or your preferred license)
