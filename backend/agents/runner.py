from agent import ComputerAgent
from computer import Computer
import os
import json
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
try:
    from supabase import create_client
except ImportError:
    print("⚠️ supabase-py not installed. Install with: pip install supabase")
    create_client = None
from dotenv import load_dotenv

from .utils import slugify, utc_now_iso, short_id, build_system_instructions

def build_autonomous_test_instructions(tests: List[Dict], suite: Dict) -> str:
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
    
    instructions += f"""

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
"""
    
    return instructions

# Load environment variables
load_dotenv()

# TODO: Replace with DB storage in the future
ARTIFACTS_ROOT = Path(__file__).parent.parent / "artifacts"

# Database client setup
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if create_client and SUPABASE_URL and SUPABASE_KEY else None


async def run_single_agent(spec: Dict[str, Any], run_dir: Path, suite_id: Optional[int] = None) -> Dict[str, Any]:
    persona = spec.get("persona") or "agent"
    persona_slug = slugify(str(persona))
    # TODO: dynamically route to the appropriate model
    model = spec.get("model") or os.getenv("CUA_MODEL", "anthropic/claude-3-5-sonnet-20241022")
    budget = spec.get("budget", 5.0)
    max_duration_sec: Optional[float] = spec.get("max_duration_sec")
    os_type = "linux"
    provider_type = "cloud"
    container_name = spec.get("container_name") or os.getenv("CUA_CONTAINER_NAME")
    api_key = os.getenv("CUA_API_KEY")
    if not api_key:
        raise RuntimeError("CUA_API_KEY is required")
    if not container_name:
        raise RuntimeError("CUA_CONTAINER_NAME is required")

    instructions = spec.get("instructions")
    if not instructions:
        raise RuntimeError(f"Spec for persona '{persona}' must include 'instructions'")

    # TODO: Replace with DB storage in the future
    agent_dir = run_dir / persona_slug
    agent_dir.mkdir(parents=True, exist_ok=True)

    async def _execute() -> Dict[str, Any]:
        steps: List[Dict[str, Any]] = []
        texts: List[str] = []
        usage_snapshots: List[Dict[str, Any]] = []
        status = "success"
        error: Optional[str] = None

        async with Computer(
            os_type=os_type,
            provider_type=provider_type,
            name=container_name,
            api_key=api_key
        ) as computer:
            agent = ComputerAgent(
                model=model,
                tools=[computer],
                trajectory_dir=str(agent_dir),
                max_trajectory_budget=budget,
                instructions=build_system_instructions(persona),
            )

            # Open the browser before starting agent steps
            try:
                await computer.interface.left_click(536, 742)
                print(f"[{persona_slug}] opened browser successfully")
            except Exception:
                print(f"[{persona_slug}] opened browser failed")
                pass

            try:
                async for result in agent.run(instructions):
                    usage = result.get("usage")
                    if usage is not None:
                        try:
                            usage_snapshots.append(json.loads(json.dumps(usage, default=str)))
                        except Exception:
                            pass

                    for item in result.get("output", []):
                        item_type = item.get("type")
                        if item_type == "message":
                            try:
                                content = item.get("content") or []
                                for block in content:
                                    if isinstance(block, dict) and block.get("text"):
                                        print(f"[{persona_slug}] message: {block['text']}")
                                        texts.append(block["text"])
                            except Exception:
                                pass
                        elif item_type in ("computer_call", "computer_call_output", "function_call", "function_call_output"):
                            pruned = dict(item)
                            if pruned.get("type") == "computer_call_output":
                                output = pruned.get("output", {})
                                if isinstance(output, dict) and "image_url" in output:
                                    output = dict(output)
                                    # Note: actual screenshots are saved under the trajectory dir
                                    output["image_url"] = "[omitted]"
                                    pruned["output"] = output
                                print(f"[{persona_slug}] computer_call_output: screenshot captured (image omitted)")
                            elif pruned.get("type") == "computer_call":
                                action = pruned.get("action", {}) or {}
                                a_type = action.get("type", "unknown")
                                a_args = {k: v for k, v in action.items() if k != "type"}
                                print(f"[{persona_slug}] computer_call: {a_type}({a_args})")
                            elif pruned.get("type") == "function_call":
                                fname = pruned.get("name", "<anon>")
                                print(f"[{persona_slug}] function_call: {fname}")
                            elif pruned.get("type") == "function_call_output":
                                print(f"[{persona_slug}] function_call_output: received")
                            steps.append(pruned)
            except Exception as e:
                status = "error"
                error = repr(e)

        result = {
            "persona": persona,
            "persona_slug": persona_slug,
            "model": model,
            "container_name": container_name,
            "trajectory_dir": str(agent_dir),
            "status": status,
            "error": error,
            "texts": texts,
            "steps": steps,
            "usage": usage_snapshots,
            "suite_id": suite_id,
        }
        
        # Save results to database if available
        if supabase and suite_id:
            await save_agent_results_to_db(result, suite_id)
            
        return result

    if max_duration_sec and max_duration_sec > 0:
        return await asyncio.wait_for(_execute(), timeout=float(max_duration_sec))
    return await _execute()


async def save_agent_results_to_db(agent_result: Dict[str, Any], suite_id: int):
    """Save individual agent test results to database"""
    try:
        print(f"[{agent_result['persona_slug']}] Saving results to database for suite {suite_id}")
        
        # Update suite success status
        suite_success = agent_result["status"] == "success"
        
        # If we have S3 integration, save trajectory/screenshots there and get S3 link
        s3_link = None  # TODO: Implement S3 upload for trajectory files
        
        # Update the suite record with results
        suite_update = {
            'suites-success': suite_success,
            's3-link': s3_link
        }
        
        response = supabase.table('suites').update(suite_update).eq('id', suite_id).execute()
        
        if response.data:
            print(f"[{agent_result['persona_slug']}] ✅ Updated suite {suite_id} with success status: {suite_success}")
        else:
            print(f"[{agent_result['persona_slug']}] ❌ Failed to update suite {suite_id}")
            
        # Get all tests for this suite and update them with results
        tests_response = supabase.table('tests').select('*').eq('suite_id', suite_id).execute()
        
        if tests_response.data:
            print(f"[{agent_result['persona_slug']}] Found {len(tests_response.data)} tests to update")
            
            # For now, mark all tests in the suite with the same status as the agent
            # In future, could parse individual test results from agent steps
            test_updates = []
            for test in tests_response.data:
                test_update = {
                    'id': test['id'],
                    'test-success': suite_success,
                    'summary': f"Agent {agent_result['persona']} completed with status: {agent_result['status']}"
                }
                if agent_result.get('error'):
                    test_update['summary'] += f" Error: {agent_result['error']}"
                test_updates.append(test_update)
                
            # Update all tests in batch
            for test_update in test_updates:
                test_response = supabase.table('tests').update({
                    'test-success': test_update['test-success'],
                    'summary': test_update['summary']
                }).eq('id', test_update['id']).execute()
                
                print(f"[{agent_result['persona_slug']}] Updated test {test_update['id']} - success: {test_update['test-success']}")
                
    except Exception as e:
        print(f"[{agent_result['persona_slug']}] ❌ Database save error: {str(e)}")


async def load_suite_from_db(suite_id: int) -> Dict[str, Any]:
    """Load suite and associated tests from database"""
    try:
        print(f"Loading suite {suite_id} from database...")
        
        # Get suite details
        suite_response = supabase.table('suites').select('*').eq('id', suite_id).single().execute()
        
        if not suite_response.data:
            raise RuntimeError(f"Suite {suite_id} not found")
            
        suite = suite_response.data
        print(f"✅ Loaded suite: {suite['name']}")
        
        # Get associated tests
        tests_response = supabase.table('tests').select('*').eq('suite_id', suite_id).execute()
        
        tests = tests_response.data or []
        print(f"✅ Loaded {len(tests)} tests for suite {suite_id}")
        
        return {
            'suite': suite,
            'tests': tests
        }
        
    except Exception as e:
        print(f"❌ Failed to load suite {suite_id}: {str(e)}")
        raise


async def run_agents_from_db(suite_id: int) -> Dict[str, Any]:
    """Run agents using suite and tests loaded from database"""
    if not supabase:
        raise RuntimeError("Database connection not available. Check SUPABASE_URL and SUPABASE_KEY environment variables.")
    
    # Load suite and tests from database
    suite_data = await load_suite_from_db(suite_id)
    suite = suite_data['suite']
    tests = suite_data['tests']
    
    print(f"🚀 Running agents for suite: {suite['name']}")
    
    # Convert database tests to agent specs format
    # Create optimized instructions for autonomous testing
    persona = suite['name'].replace(' Agent Suite', '').lower()
    
    # Build comprehensive test instructions
    test_instructions = build_autonomous_test_instructions(tests, suite)
    
    test_spec = {
        "persona": persona,
        "instructions": test_instructions,
        "model": os.getenv("CUA_MODEL", "anthropic/claude-3-5-sonnet-20241022"),
        "budget": 10.0,  # Increased budget for comprehensive testing
        "max_duration_sec": float(os.getenv("AGENT_TIMEOUT", "600")) if os.getenv("AGENT_TIMEOUT") else None,  # Increased timeout
        "container_name": os.getenv("CUA_CONTAINER_NAME")
    }
    
    run_id = short_id()
    started_at = utc_now_iso()
    artifacts_dir = ARTIFACTS_ROOT
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📋 Test spec created for persona: {test_spec['persona']}")
    print(f"📋 Instructions: {test_spec['instructions']}")
    
    # Run the single agent with the suite
    agent_result = await run_single_agent(test_spec, artifacts_dir, suite_id)
    
    summary = {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": utc_now_iso(),
        "artifacts_root": str(artifacts_dir),
        "suite_id": suite_id,
        "suite_name": suite['name'],
        "num_tests": len(tests),
        "agent_result": agent_result,
    }
    
    # Save summary locally (keep existing behavior)
    output_path = os.getenv("CUA_OUTPUT_PATH") or str(artifacts_dir / f"summary_suite_{suite_id}.json")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"💾 Summary saved to {output_path}")
    except Exception as e:
        print(f"❌ Failed to save summary: {str(e)}")
        pass
    
    print(json.dumps(summary, indent=2))
    return summary


async def run_agents(test_specs: List[Dict[str, Any]]) -> Dict[str, Any]:
    run_id = short_id()
    started_at = utc_now_iso()
    artifacts_dir = ARTIFACTS_ROOT
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    tasks = [run_single_agent(spec, artifacts_dir) for spec in test_specs]
    results: List[Dict[str, Any]] = await asyncio.gather(*tasks, return_exceptions=True)

    agents: List[Dict[str, Any]] = []
    for spec, res in zip(test_specs, results):
        if isinstance(res, Exception):
            agents.append({
                "persona": spec.get("persona") or "agent",
                "status": "error",
                "error": repr(res),
            })
        else:
            agents.append(res)

    summary = {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": utc_now_iso(),
        "artifacts_root": str(artifacts_dir),
        "num_agents": len(test_specs),
        "agents": agents,
    }

    output_path = os.getenv("CUA_OUTPUT_PATH") or str(artifacts_dir / "summary.json")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
    except Exception:
        pass

    print(json.dumps(summary))
    return summary


# Main entry point that can handle both old format (test_specs) and new format (suite_id)
async def run_qai_tests(suite_id: Optional[int] = None, test_specs: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Main entry point for running QAI tests - supports both database and legacy modes"""
    if suite_id is not None:
        print(f"🗄️ Running tests from database suite {suite_id}")
        return await run_agents_from_db(suite_id)
    elif test_specs is not None:
        print(f"📝 Running tests from provided specs (legacy mode)")
        return await run_agents(test_specs)
    else:
        raise ValueError("Either suite_id or test_specs must be provided")

