"""L2 Service checks. Run: bash grade.sh l2"""

import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.llm import StubLLM


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(main, "llm", StubLLM())
    return TestClient(main.app)


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200 and r.json() == {"status": "ok"}


def test_triage_routes_a_dispute(client):
    r = client.post("/triage", json={"id": "C-001", "text": "I was charged twice for the same bill", "channel": "email"})
    assert r.status_code == 200
    body = r.json()
    assert body["category"] == "card_dispute" and body["team"] == "disputes" and body["needs_human"] is False


def test_bad_model_output_returns_human_review(client):
    r = client.post("/triage", json={"id": "C-013", "text": "Unauthorised UPI debit of 25000 rupees"})
    assert r.status_code == 200 and r.json()["team"] == "human_review"


def test_invalid_request_is_rejected_by_the_contract(client):
    r = client.post("/triage", json={"id": "C-1", "text": "", "channel": "fax"})
    assert r.status_code == 422  # FastAPI + Pydantic reject it before our code runs


def test_slow_model_times_out_to_human_review(monkeypatch):
    monkeypatch.setattr(main, "llm", StubLLM(delay=1.0))
    monkeypatch.setattr(main, "TIMEOUT_S", 0.1)
    r = TestClient(main.app).post("/triage", json={"id": "C-001", "text": "charged twice"})
    assert r.status_code == 200
    assert r.json()["needs_human"] is True and "timed out" in r.json()["summary"]


def test_openapi_contract_is_published(client):
    spec = client.get("/openapi.json").json()
    assert "/triage" in spec["paths"] and "/healthz" in spec["paths"]
    fields = spec["components"]["schemas"]["TriageResult"].get("properties", {})
    assert {"category", "priority", "team", "summary"} <= fields.keys(), "the contract must publish TriageResult's fields"
