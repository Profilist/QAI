from agent import ComputerAgent
from computer import Computer
import os
import json
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils import slugify, utc_now_iso, short_id, build_system_instructions

# TODO: Replace with DB storage in the future
ARTIFACTS_ROOT = Path(__file__).parent.parent / "artifacts"


async def run_single_agent(spec: Dict[str, Any], run_dir: Path) -> Dict[str, Any]:
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
                await computer.interface.double_click(536, 742)
                
            except Exception:
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

        return {
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
        }

    if max_duration_sec and max_duration_sec > 0:
        return await asyncio.wait_for(_execute(), timeout=float(max_duration_sec))
    return await _execute()


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

