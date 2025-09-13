## Product

Autonomous agentic user tester

- CALL VIA GITHUB ACTION
- Integrated in a CI/CD pipeline
  1. LLM gathers context about PR and codebase and determines what needs to be tested
  2. We spin up a series of agents in parallel to test the website (maybe extend to mobile)
     1. Agents have different personas representing potential users
     2. Can have cross-agent interactions (maybe) for things like chat interfaces
     3. Screen recording (maybe live streaming) agent actions that can be replayed
- On our frontend Vercel-like dashboard (with all GitHub projects)
  - we display the results of each agent, report of the bugs w/ replays of the interactions, suggested fixes (maybe)
  - save AI-generated tests (to reuse in the future) or manually input tests (in natural language)

## Pitch/Purpose

Currently, Agentic QA testers like [Spur](https://www.spurtest.com/) still require descriptions of tests even if in natural language. However, the most impactful bugs are most often unexpected and unplanned for (ex. race conditions, edge cases). That’s why our agentic framework is fully autonomous.

## User Flow

User triggers the github action either manually or automatically. It runs the tests thing etc and then the message would be “go to <url>” for more details. This shows the automatically generated tests on a sidebar and a video of the test etc on the main screen. The user can add more tests or save ones, which requires logging in first.

## Tech

### Backend/AI

- Cua (Docker for Computer-Use)
  - Cloud or local (via Docker) computer-simulating containers
    - Access to Sandbox python environment
    - Access to computer actions like clicking, scrolling, keyboard, screenshot, clipboard
  - Agent has access to computer
- OmniParser?
- GitHub Actions

### Database

- MongoDB
- S3 for video replays

### Frontend


# TASK
Look at the way @backend/cic/qai-pipeline.js connects with the database. 
Essentially, we want to pass a suite + a series of tests to each agent in @backend/agents/runner.py
@backend/agents/artifacts is what the agent returns right now, but integrate the current database flow into the agent's input and output bodies.
Keep the print statements and console.logs.
Rather than saving locally, please save everything to the database instead.
For now, assume the agent is hosted (it's not, so the link won't work, but like assume everything passes e2e you know)

#### SCHEMA
CREATE TABLE public.results (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  pr-link text,
  res-success boolean DEFAULT false,
  pr-name text,
  CONSTRAINT results_pkey PRIMARY KEY (id)
);
CREATE TABLE public.suites (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  suites-success boolean,
  name text,
  s3-link text,
  result_id bigint,
  CONSTRAINT suites_pkey PRIMARY KEY (id),
  CONSTRAINT suites_result_id_fkey FOREIGN KEY (result_id) REFERENCES public.results(id)
);
CREATE TABLE public.tests (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  summary text,
  test-success boolean,
  name text,
  suite_id bigint,
  CONSTRAINT tests_pkey PRIMARY KEY (id),
  CONSTRAINT tests_suite_id_fkey FOREIGN KEY (suite_id) REFERENCES public.suites(id)
);

#### Flow
Here's a general flow diagram, the CICD is done
@flow.png