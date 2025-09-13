import uuid
from datetime import datetime, timezone


def slugify(value: str) -> str:
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789-_"
    value = value.strip().lower().replace(" ", "-")
    return "".join([c for c in value if c in allowed]) or "agent"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def short_id() -> str:
    return uuid.uuid4().hex[:8]


def build_system_instructions(persona: str | None) -> str:
    persona_text = f"You are {persona}." if persona else "You are a meticulous QA tester."
    return (
        f"{persona_text} "
        "The browser is already open. "
        "Act like a real end user for this persona. "
        "Follow the user's instructions step-by-step, using the computer tools when needed. "
        "If you want to click at the current cursor position, use the 'left_click' action and leave out the coordinates (doing 0,0 will click at the top left corner, not the current cursor position)."
        "DO NOT DO action: {'button': 'left', 'type': 'click', 'x': 0, 'y': 0}, leave out the coordinates."
        "Be concise, avoid hallucinations, and surface any errors encountered."
    )


def normalize_tests(spec: dict) -> list[dict]:
    tests = spec.get("tests")
    if isinstance(tests, list) and tests:
        normalized = []
        for idx, t in enumerate(tests):
            name = t.get("name") or f"test-{idx+1}"
            messages = t.get("instructions") or t.get("messages") or []
            normalized.append({"name": name, "messages": messages})
        return normalized
    # Fallback: single test using top-level instructions/messages
    messages = spec.get("instructions") or spec.get("messages") or []
    suite_name = spec.get("suite") or spec.get("suite_name") or "default"
    return [{"name": str(suite_name), "messages": messages}]


def make_remote_recording_dir(persona_slug: str, test_name: str) -> str:
    test_slug = slugify(str(test_name))
    # Use a user-writable base path by default
    return f"/tmp/replays/{persona_slug}/{test_slug}"

