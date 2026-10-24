from __future__ import annotations

PROMPT_VERSION = "triage-v1"
MODEL = "stub-triage-1"

EVENTS = [
    {
        "label": "good route with caller request ID",
        "incoming_request_id": "req-abc123",
        "path": "/triage",
        "status": 200,
        "latency_ms": 142,
        "outcome": "routed",
        "complaint": {
            "id": "C-001",
            "text": "Charged twice. Account EB-4418203391.",
        },
    },
    {
        "label": "human review with generated request ID",
        "incoming_request_id": None,
        "path": "/triage",
        "status": 200,
        "latency_ms": 151,
        "outcome": "human_review",
        "complaint": {
            "id": "C-013",
            "text": "Unauthorised UPI debit. Account EB-9081726354.",
        },
    },
]
