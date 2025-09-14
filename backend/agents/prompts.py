from typing import List, Dict
import os

from dotenv import load_dotenv
load_dotenv()

def build_agent_instructions(tests: List[Dict], suite: Dict) -> str:
	"""Build optimized instructions for autonomous agent testing"""
	
	base_url = os.getenv('DEPLOYMENT_URL', 'https://staging.example.com')
	
	# Create comprehensive testing instructions
	instructions = f"""
You are an autonomous QA testing agent for web applications. Your goal is to thoroughly test the deployment at {base_url}.

SUITE: {suite['name']}
TOTAL TESTS: {len(tests)}

TESTING APPROACH:
1. Start by taking a screenshot to see the current state
2. Navigate to the base URL: {base_url}
3. Perform comprehensive exploratory testing
4. Look for bugs, broken functionality, and edge cases
5. Test user flows and interactions
6. Pay special attention to recent changes that might have introduced issues

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
- Be thorough and methodical in your approach
- Take screenshots at key moments to document your findings
- Test both happy paths and edge cases
- Look for unexpected behaviors, errors, or broken functionality
- Pay attention to UI/UX issues and usability problems
- Test form submissions, navigation, and interactive elements
- Check for responsive design and mobile compatibility if applicable
- Document any bugs or issues you discover with clear descriptions

SUCCESS CRITERIA:
- Complete testing of all specified scenarios
- Identify and document any bugs or issues found
- Verify that core functionality works as expected
- Provide clear feedback on the overall quality of the deployment

Remember: You are looking for unexpected bugs and issues that developers might miss. Be creative in your testing approach and explore edge cases.

FINAL VERDICT FORMAT (MANDATORY):
- After completing each test scenario, output exactly one line with no extra commentary:
- RESULT: PASSED   (if the scenario executed successfully and no critical issues were found)
- RESULT: FAILED   (if execution could not complete or a critical/blocking issue was found)
"""
	
	return instructions