from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone

from events import MODEL, PROMPT_VERSION

ACCOUNT_RE = re.compile(r"\bEB-\d{10}\b")


def mask(text: str) -> str:
    return ACCOUNT_RE.sub(lambda m: f"EB-******{m.group(0)[-4:]}", text)


def build_audit_line(*, path: str, status: int, latency_ms: int, outcome: str, complaint_text: str, incoming_request_id: str | None) -> tuple[str, str]:
    request_id = incoming_request_id or uuid.uuid4().hex[:12]
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "level": "INFO",
        "msg": "request",
        "request_id": request_id,
        "route": path,
        "status": status,
        "latency_ms": latency_ms,
        "model": MODEL,
        "prompt_version": PROMPT_VERSION,
        "outcome": outcome,
        "complaint_excerpt": complaint_text[:80],
    }
    return request_id, mask(json.dumps(entry))
