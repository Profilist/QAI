from agent import ComputerAgent
from computer import Computer
import os
import json
import asyncio
from typing import Any, Dict, List
from dotenv import load_dotenv
from enum import Enum

from database import (
    get_or_create_test,
    append_test_step,
    update_test_fields,
    create_result,
    set_suite_result_id,
    get_suites_with_tests_for_result,
    update_result_fields,
)
from prompts import build_agent_instructions
from utils import normalize_tests, make_remote_recording_dir, process_item, extract_major_steps
from record import start_recording, stop_recording

class RunStatus(Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING" 
    PASSED = "PASSED"
    FAILED = "FAILED"

# Load environment variables
load_dotenv()

async def run_single_agent(spec: Dict[str, Any]) -> Dict[str, Any]:
    print(f"SPEC: {spec}")
    # Setup CUA agent
    model = spec.get("model") or os.getenv("CUA_MODEL", "claude-sonnet-4-20250514")
    budget = spec.get("budget", 5.0)
    suite_id = spec.get("suite_id")
    
    # Setup CUA computer
    os_type = "linux"
    provider_type = "cloud"
    container_name = spec.get("container_name") or os.getenv("CUA_CONTAINER_NAME")
    api_key = os.getenv("CUA_API_KEY")
    if not api_key:
        raise RuntimeError("CUA_API_KEY is required")
    if not container_name:
        raise RuntimeError("CUA_CONTAINER_NAME is required")
    
    # Setup tests
    tests = normalize_tests(spec)
    print(f"TESTS: {tests}")
    
    async def _execute() -> Dict[str, Any]:
        # Results from all tests from the suite
        suite_results: List[Dict[str, Any]] = []
        
        async with Computer(
            os_type=os_type,
            provider_type=provider_type,
            name=container_name,
            api_key=api_key
            ) as computer:
            
            agent = ComputerAgent(
                model=model,
                tools=[computer],
                max_trajectory_budget=budget,
                instructions=build_agent_instructions(tests, spec),
                )
            
            await computer.venv_install("recording_venv", [])
            
            # Open the browser before starting agent steps
            try:
                await computer.interface.left_click(536, 742)
                print(f"[Agent {suite_id}] opened browser successfully")
            except Exception:
                print(f"[Agent{suite_id}] opened browser failed")
                pass

            for test in tests:
                print(f"TEST: {test}")
                test_name = test.get("name", "test")
                test_instructions = test.get("instructions") or []
                
                # Per-test accumulators
                test_agent_steps: List[Dict[str, Any]] = []
                test_run_status = RunStatus.RUNNING
                
                # Ensure DB row exists for this test
                test_id = await get_or_create_test(suite_id, test_name) if suite_id is not None else None
                
                # Start recording inside VM
                try:
                    remote_dir = make_remote_recording_dir(suite_id, test_name)
                    await computer.venv_exec("recording_venv", start_recording, output_dir=remote_dir, fps=5)
                    print(f"[Agent {suite_id}] recording started for {test_name}")
                except Exception as _e:
                    print(f"[Agent {suite_id}] recording start failed for {test_name}: {_e}")
                    
                try:
                    print(f"TEST INSTRUCTIONS: {test_instructions}")
                    async for result in agent.run(test_instructions):
                        print(f"RESULT: {result}")
                        for item in result.get("output", []):
                            # Add agent's current condensed steps
                            test_agent_steps = process_item(item, suite_id, test_agent_steps)
                            # Persist condensed steps immediately to DB
                            if test_id is not None:
                                for step in extract_major_steps(item):
                                    await append_test_step(test_id, step)
                            # Parse explicit verdict from agent message content
                            try:
                                if isinstance(item, dict) and item.get("type") == "message":
                                    content = item.get("content") or []
                                    for block in content:
                                        text = block.get("text") if isinstance(block, dict) else None
                                        if isinstance(text, str):
                                            cleaned = text.strip().upper()
                                            if cleaned.endswith("RESULT: PASSED") or cleaned == "RESULT: PASSED":
                                                test_run_status = RunStatus.PASSED
                                            elif cleaned.endswith("RESULT: FAILED") or cleaned == "RESULT: FAILED":
                                                test_run_status = RunStatus.FAILED
                            except Exception:
                                pass
                except Exception as e:
                    test_run_status = RunStatus.FAILED
                    print(f"[Agent {suite_id}] test {test_name} failed: {e}")
                finally:
                    # Determine pass/fail
                    passed = test_run_status == RunStatus.PASSED
                    s3_link = None
                    
                    # Stop recording and get S3 URL
                    try:
                        recording_stop = await computer.venv_exec("recording_venv", stop_recording)
                        if isinstance(recording_stop, dict):
                            upload = recording_stop.get("upload") or {}
                            resp = upload.get("response") or {}
                            s3_link = resp.get("fileUrl") or resp.get("url")
                            print(f"[Agent {suite_id}] recording stopped for {test_name}")
                    except Exception as e:
                        print(f"[Agent {suite_id}] stop_recording error for {test_name}: {e}")
                        pass
                    
                    # Persist final test fields
                    if test_id is not None:
                        await update_test_fields(test_id, {
                            "test_success": passed,
                            "s3_link": s3_link,
                            "run_status": test_run_status.value,
                        })
                
                # Add test result to suite results
                suite_results.append({
                    "suite_id": suite_id,
                    "name": test_name,
                    "test_success": passed,
                    "steps": test_agent_steps,
                    "s3_link": s3_link,
                    "run_status": test_run_status,
                    })
        
        return suite_results
    
    return await _execute()

async def run_qai_tests(suite_id: int) -> Dict[str, Any]:
    """
    Run tests for a specific suite ID from the database
    This function is called by run_suite.py and qai-pipeline.js
    """
    from database import get_suite_with_tests
    
    try:
        # Fetch suite and test data from database
        print(f"[run_qai_tests] Fetching suite data for suite_id: {suite_id}")
        suite_data = await get_suite_with_tests(suite_id)
        if not suite_data:
            print(f"[run_qai_tests] Suite {suite_id} not found in database")
            return {
                'agent_result': {
                    'status': 'failed',
                    'error': f'Suite {suite_id} not found'
                }
            }
        print(f"[run_qai_tests] Suite data: {suite_data}")
        
        print(f"[run_qai_tests] Retrieved suite data: {suite_data.get('name', 'Unknown')} with {len(suite_data.get('tests', []))} tests")
        
        # Convert database format to agent spec format
        spec = {
            'suite_id': suite_id,
            'name': suite_data.get('name'),  # Add suite name for build_agent_instructions
            'model': os.getenv("CUA_MODEL", "anthropic/claude-3-5-sonnet-20241022"),
            'budget': 5.0,
            'container_name': os.getenv("CUA_CONTAINER_NAME"),
            'tests': suite_data.get('tests')
        }
        
        # Run the agent
        result = await run_single_agent(spec)
        
        return {
            'agent_result': {
                'status': 'success',
                'suite_id': suite_id,
                'tests_run': len(result),
                'results': result
            }
        }
    except Exception as e:
        print(f"Error running QAI tests for suite {suite_id}: {e}")
        return {
            'agent_result': {
                'status': 'failed',
                'error': str(e),
                'suite_id': suite_id
            }
        }

async def run_agents(test_specs: List[Dict[str, Any]], pr_name: str, pr_link: str) -> Dict[str, Any]:
    tasks = [run_single_agent(spec) for spec in test_specs]
    results: List[Dict[str, Any]] = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    for res in results:
        if isinstance(res, Exception):
            continue
        for t in res:
            total_tests += 1
            if t.get("test_success"):
                passed_tests += 1
            else:
                failed_tests += 1
    run_status = RunStatus.PASSED if failed_tests == 0 else RunStatus.FAILED
    overall_result = {
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "total_tests": total_tests,
    }
    # Create result row and link suites
    try:
        result_id = await create_result(pr_name, pr_link, overall_result, run_status.value)
        if result_id is not None:
            suite_ids = {spec.get("suite_id") for spec in test_specs if spec.get("suite_id") is not None}
            for sid in suite_ids:
                await set_suite_result_id(int(sid), int(result_id))
    except Exception as _e:
        print(f"[db] result update error: {_e}")
    summary = {
        "pr_name": pr_name,
        "pr_link": pr_link,
        "overall_result": overall_result,
        "run_status": run_status.value,
    }
    print(json.dumps(summary))
    return summary


async def run_suites_for_result(result_id: int) -> Dict[str, Any]:
    """
    Fetch all suites/tests for a given result_id and run them together.
    Updates the existing result row with overall summary and run_status.
    """
    try:
        # Load suite specs for this result
        specs: List[Dict[str, Any]] = await get_suites_with_tests_for_result(result_id)
        if not specs:
            await update_result_fields(result_id, {"run_status": RunStatus.FAILED.value})
            return {
                "result_id": result_id,
                "overall_result": {"passed_tests": 0, "failed_tests": 0, "total_tests": 0},
                "run_status": RunStatus.FAILED.value,
                "error": "No suites found for result"
            }

        # Run each suite's tests concurrently
        tasks = [run_single_agent(spec) for spec in specs]
        results: List[Any] = await asyncio.gather(*tasks, return_exceptions=True)

        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        for res in results:
            if isinstance(res, Exception):
                continue
            for t in res:
                total_tests += 1
                if t.get("test_success"):
                    passed_tests += 1
                else:
                    failed_tests += 1

        run_status = RunStatus.PASSED if failed_tests == 0 and total_tests > 0 else RunStatus.FAILED
        overall_result = {
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "total_tests": total_tests,
        }

        await update_result_fields(result_id, {
            "overall_result": overall_result,
            "run_status": run_status.value,
        })

        summary = {
            "result_id": result_id,
            "overall_result": overall_result,
            "run_status": run_status.value,
        }
        print(json.dumps(summary))
        return summary
    except Exception as e:
        await update_result_fields(result_id, {"run_status": RunStatus.FAILED.value})
        return {
            "result_id": result_id,
            "overall_result": {"passed_tests": 0, "failed_tests": 0, "total_tests": 0},
            "run_status": RunStatus.FAILED.value,
            "error": str(e),
        }
