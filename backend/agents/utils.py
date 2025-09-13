import uuid
from datetime import datetime, timezone
from typing import Any


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
        "Be concise, avoid hallucinations, and surface any errors encountered."
    )

