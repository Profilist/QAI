from agent import ComputerAgent
from computer import Computer
import os
import json
import asyncio
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from enum import Enum

from .database import save_agent_results_to_db
from .prompts import build_agent_instructions
from .utils import slugify, utc_now_iso, short_id, normalize_tests, make_remote_recording_dir, process_item
from .record import start_recording, stop_recording

class RunStatus(Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"

# Load environment variables
load_dotenv()

async def run_single_agent(spec: Dict[str, Any]) -> Dict[str, Any]:
    # Setup CUA agent
    model = spec.get("model") or os.getenv("CUA_MODEL", "anthropic/claude-3-5-sonnet-20241022")
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
            
            # Open the browser before starting agent steps
            try:
                await computer.interface.left_click(536, 742)
                print(f"[Agent {suite_id}] opened browser successfully")
            except Exception:
                print(f"[Agent{suite_id}] opened browser failed")
                pass

            for test in tests:
                test_name = test.get("name", "test")
                test_instructions = test.get("instructions") or []
                
                # Per-test accumulators
                test_agent_steps: List[Dict[str, Any]] = []
                test_run_status = RunStatus.RUNNING
                recording_stop = None
                
                # Start recording inside VM
                try:
                    remote_dir = make_remote_recording_dir(suite_id, test_name)
                    await computer.venv_exec("demo_venv", start_recording, output_dir=remote_dir, fps=5)
                    print(f"[Agent {suite_id}] recording started for {test_name}")
                except Exception as _e:
                    print(f"[Agent {suite_id}] recording start failed for {test_name}: {_e}")
                    
                try:
                    async for result in agent.run(test_instructions):
                        for item in result.get("output", []):
                            # Add agent's current step
                            test_agent_steps = process_item(item, suite_id, test_agent_steps)  
                except Exception as e:
                    test_run_status = RunStatus.FAILED
                    print(f"[Agent {suite_id}] test {test_name} failed: {e}")
                finally:
                    # Determine pass/fail
                    passed = test_run_status == RunStatus.PASSED
                    recording_url = None
                    
                    # Stop recording and get S3 URL
                    try:
                        if isinstance(recording_stop, dict):
                            upload = recording_stop.get("upload") or {}
                            resp = upload.get("response") or {}
                            recording_url = resp.get("fileUrl") or resp.get("url")
                            print(f"[Agent {suite_id}] recording stopped for {test_name}")
                    except Exception:
                        pass
                
                # Add test result to suite results
                suite_results.append({
                    "suite_id": suite_id,
                    "name": test_name,
                    "test_success": passed,
                    "steps": test_agent_steps,
                    "s3_link": recording_url,
                    "run_status": test_run_status,
                    })
        
        return suite_results
    
    return await _execute()

async def run_agents(test_specs: List[Dict[str, Any]], pr_name: str, pr_link: str) -> Dict[str, Any]:
    tasks = [run_single_agent(spec) for spec in test_specs]
    results: List[Dict[str, Any]] = await asyncio.gather(*tasks, return_exceptions=True)
    
    run_status = RunStatus.RUNNING
    passed = failed = 0
    
    for res in results:
        if isinstance(res, Exception):
            failed += 1
            run_status = RunStatus.FAILED
        else:
            passed += 1
    
    overall_result = {
        "passed_tests": passed,
        "failed_tests": failed,
        "total_tests": passed + failed,
        }
    
    results = {
        "pr_name": pr_name,
        "pr_link": pr_link,
        "overall_result": overall_result,
        "run_status": run_status,
        }
    
    print(json.dumps(results))
    return results


async def run_qai_tests(test_specs: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Main entry point for running QAI tests"""
    print(f"🗄️ Running tests from suite {test_specs[0]['suite_id']}")
    return await run_agents(test_specs)

