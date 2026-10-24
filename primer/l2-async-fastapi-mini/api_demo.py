"""Call the tiny service the way the case system would, without starting a server (FastAPI's TestClient)."""
from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def show(label: str, method: str, path: str, body: dict | None = None) -> None:
    r = client.request(method, path, json=body)
    print(f"{label}\n  {method} {path}" + (f"  body={json.dumps(body)}" if body is not None else ""))
    print(f"  -> {r.status_code}  {json.dumps(r.json())[:300]}\n")


show("1. Is it alive? (what the platform probes)", "GET", "/healthz")
show("2. A good complaint", "POST", "/triage", {"id": "C-002", "text": "Two card transactions I did not make"})
show("3. A bad request: empty id and text", "POST", "/triage", {"id": "", "text": ""})
print("""WHAT TO NOTICE
- 200: the reply matches the contract (team, priority, summary), nothing extra.
- 422: FastAPI rejected the bad request BEFORE our code ran, and listed each field that failed.
- Both checks come from the Pydantic classes in app.py: Complaint (in) and TriageReply (out).""")
