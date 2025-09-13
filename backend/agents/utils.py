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

