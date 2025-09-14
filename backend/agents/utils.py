from datetime import datetime, timezone


def slugify(value: str) -> str:
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789-_"
    value = value.strip().lower().replace(" ", "-")
    return "".join([c for c in value if c in allowed]) or "agent"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_tests(spec: dict) -> list[dict]:
    tests = spec.get("tests")
    
    # Multiple tests
    if isinstance(tests, list) and tests:
        normalized = []
        for idx, t in enumerate(tests):
            name = t.get("name") or f"test-{idx+1}"
            instructions = t.get("instructions") or []
            normalized.append({"name": name, "instructions": instructions})
        return normalized
    
    # Single test
    instructions = spec.get("instructions") or []
    suite_name = spec.get("suite_name") or "Standard"
    return [{"name": str(suite_name), "instructions": instructions}]


def make_remote_recording_dir(suite_id: str, test_name: str) -> str:
    test_slug = slugify(str(test_name))
    # Use a user-writable base path by default
    return f"/tmp/replays/{suite_id}/{test_slug}"


def process_item(item: dict, suite_id: str, test_agent_steps: list[dict]) -> dict:
    item_type = item.get("type")
    
    if item_type == "message":
        try:
            content = item.get("content") or []
            for block in content:
                if isinstance(block, dict) and block.get("text"):
                    text = block["text"]
                    for line in str(text).splitlines():
                        candidate = line.strip()
                        if candidate.upper().startswith("STEP:"):
                            step_text = candidate.split(":", 1)[1].strip()
                            step_text = step_text
                            if step_text:
                                print(f"[Agent {suite_id}] STEP: {step_text}")
                                test_agent_steps.append(step_text)
        except Exception:
            pass
    
    elif item_type in ("computer_call", "computer_call_output", "function_call", "function_call_output"):
        # Keep debug output, but do not append raw tool calls to steps
        pruned = dict(item)
        if pruned.get("type") == "computer_call_output":
            output = pruned.get("output", {})
            if isinstance(output, dict) and "image_url" in output:
                print(f"[Agent {suite_id}] computer_call_output: screenshot captured")
        elif pruned.get("type") == "computer_call":
            action = pruned.get("action", {}) or {}
            a_type = action.get("type", "unknown")
            a_args = {k: v for k, v in action.items() if k != "type"}
            print(f"[Agent {suite_id}] computer_call: {a_type}({a_args})")
        elif pruned.get("type") == "function_call":
            fname = pruned.get("name", "<anon>")
            print(f"[Agent {suite_id}] function_call: {fname}")
        elif pruned.get("type") == "function_call_output":
            print(f"[Agent {suite_id}] function_call_output: received")
            
    return test_agent_steps


def extract_major_steps(item: dict) -> list[str]:
    """Extract condensed STEP lines from a single agent output item."""
    steps: list[str] = []
    try:
        if item.get("type") != "message":
            return steps
        content = item.get("content") or []
        for block in content:
            if isinstance(block, dict) and block.get("text"):
                text = block["text"]
                for line in str(text).splitlines():
                    candidate = line.strip()
                    if candidate.upper().startswith("STEP:"):
                        step_text = candidate.split(":", 1)[1].strip()
                        step_text = step_text
                        if step_text:
                            steps.append(step_text)
    except Exception:
        return steps
    return steps

