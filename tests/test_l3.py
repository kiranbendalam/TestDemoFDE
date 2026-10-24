"""L3 Observability checks. Run: bash grade.sh l3"""

import io
import json
import re

import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.llm import StubLLM
from app.logging_setup import mask, setup_logging

REQUIRED = {"ts", "level", "msg", "request_id", "route", "status", "latency_ms", "model", "prompt_version", "outcome"}
FULL_ACCOUNT = re.compile(r"EB-\d{10}")


def test_mask():
    assert mask("acct EB-4418203391 and EB-7720019384") == "acct EB-******3391 and EB-******9384"
    assert mask("no account here") == "no account here"


@pytest.fixture
def logs(monkeypatch):
    monkeypatch.setattr(main, "llm", StubLLM())
    buf = io.StringIO()
    setup_logging(stream=buf)
    client = TestClient(main.app)
    return client, buf


def _lines(buf):
    return [json.loads(line) for line in buf.getvalue().splitlines() if line.strip()]


def test_one_json_line_per_request_with_the_audit_fields(logs):
    client, buf = logs
    client.post("/triage", json={"id": "C-001", "text": "Charged twice. Account EB-4418203391."})
    lines = [x for x in _lines(buf) if x.get("route") == "/triage"]
    assert len(lines) == 1, "expected exactly one log line for the /triage request"
    missing = REQUIRED - lines[0].keys()
    assert not missing, f"log line is missing {sorted(missing)}"
    assert lines[0]["prompt_version"] and lines[0]["outcome"] in {"routed", "human_review"}


def test_request_id_is_echoed_and_logged(logs):
    client, buf = logs
    r = client.post("/triage", json={"id": "C-001", "text": "charged twice"}, headers={"X-Request-ID": "req-abc123"})
    assert r.headers.get("X-Request-ID") == "req-abc123"
    assert any(x.get("request_id") == "req-abc123" for x in _lines(buf))
    r2 = client.get("/healthz")
    assert r2.headers.get("X-Request-ID"), "a request ID must be generated when the caller sends none"


def test_no_full_account_number_in_logs(logs):
    client, buf = logs
    client.post("/triage", json={"id": "C-013", "text": "Unauthorised UPI debit. Account EB-9081726354."})
    assert buf.getvalue(), "nothing was logged"
    assert not FULL_ACCOUNT.search(buf.getvalue()), "an unmasked account number reached the logs"
