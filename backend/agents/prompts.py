from typing import List, Dict
import os

from dotenv import load_dotenv
load_dotenv()


def build_agent_instructions(tests: List[Dict], suite: Dict) -> str:
	"""Build optimized instructions for autonomous agent testing with concise STEP emissions."""
	base_url = os.getenv("DEPLOYMENT_URL", "https://www.larris.me/")

	# Create concise, UI-friendly testing instructions
	instructions = f"""
You are an autonomous QA testing agent for web applications. Your goal is to thoroughly test the deployment at {base_url}.

SUITE: {suite['name']}
TOTAL TESTS: {len(tests)}

COMMUNICATION RULES (MANDATORY):
- Only output concise major steps in the exact format: "STEP: <short gerund phrase>".
- Use action/gerund form ending with "-ing" (e.g., "Clicking Admissions", "Navigating to home").
- Major steps are human-meaningful actions: navigation, key clicks that change pages, form submissions, and verifications.
- Exclude micro steps (mouse moves, small scrolls, key-by-key typing) unless they are the core action.
- Exclude continuations from the last step (ex. "Continuing to scroll").
- Keep each step as simple as possible, under 7 words ideally.
- After completing each test scenario, output exactly one line: "RESULT: PASSED" or "RESULT: FAILED".

TESTING APPROACH:
1. Navigate to the base URL: {base_url}
2. Execute each scenario's intent
3. Verify the expected destination/state
4. Document ONLY major actions using STEP lines in gerund form

SPECIFIC TEST SCENARIOS:
"""

	for i, test in enumerate(tests, 1):
		instructions += f"""
{i}. {test['name']}
   Description: {test.get('summary', 'No description provided')}
   Priority: {'HIGH' if 'critical' in test.get('summary', '').lower() else 'MEDIUM'}
"""

	instructions += """

TESTING GUIDELINES:
- Be thorough, but keep communication to STEP lines only
- Take screenshots at key moments for your own reasoning, but do not describe them
- YOU ARE ON AN EXTREME TIME CRUNCH, test as EFFICIENTLY as possible, which could mean forming a conclusion PASS/FAIL faster instead of trying over and over again.
- Prioritize actions that meaningfully change app state or page

FINAL VERDICT FORMAT (MANDATORY):
- After each scenario, output exactly one line: RESULT: PASSED or RESULT: FAILED
"""

	return instructions