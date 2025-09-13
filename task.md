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

-

Can you help me flush out the specifics, I'm building out the CI/CD pipeline right now, so can you help me setup the github actiosn, etc.
So
1) Github actions
2) LLM combines a pregiven codebase summary (say a textfile) with the new changes from the PR into some sort of system prompt
3) Through this, a series of testing things in a JSON are returned, and then that's POST to a random endpoint, where our agent will work (this is done by my hackathon teammate)
4) And then it runs, and then the agent will return TRUE / FALSE, which will pass / fail the CI.
5) Then if the changes pass, the CI will update the codebase summary by appending the new changes

Does this make sense?
Can we start just brainstorming ideas, and how we'd set it up?

I want to build it in JS (unless u think it's better to use py or something)
in @backend/cicd
What APIs do I need?
Let's just get something started