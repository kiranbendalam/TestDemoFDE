"""L1 Contract checks. Run: bash grade.sh l1"""

import json

import pytest
from pydantic import ValidationError

from app.llm import StubLLM
from app.models import Complaint, Team, TriageResult, parse_triage

GOOD = {"category": "fraud", "priority": 1, "team": "fraud_ops", "summary": "Unauthorised UPI debit"}


def test_complaint_accepts_valid_input():
    c = Complaint(id="C-001", text="Charged twice", channel="chat")
    assert c.channel == "chat"
    assert Complaint(id="C-002", text="x").channel == "email"  # default


@pytest.mark.parametrize("bad", [{"id": "", "text": "x"}, {"id": "C-1", "text": ""}, {"id": "C-1", "text": "x", "channel": "fax"}])
def test_complaint_rejects_bad_input(bad):
    with pytest.raises(ValidationError):
        Complaint(**bad)


def test_valid_model_output_parses():
    r = parse_triage(json.dumps(GOOD))
    assert isinstance(r, TriageResult)
    assert r.team == Team.FRAUD_OPS and r.priority == 1 and r.needs_human is False


@pytest.mark.parametrize(
    "raw",
    [
        json.dumps({**GOOD, "priority": "urgent", "team": "fraud ops"}),   # wrong types / values
        json.dumps({k: v for k, v in GOOD.items() if k != "team"}),        # missing field
        "Sure! Here is the JSON you asked for:\n" + json.dumps(GOOD),      # prose around the JSON
        json.dumps({**GOOD, "priority": 7}),                                # out of range
        json.dumps({**GOOD, "summary": "x" * 201}),                         # too long
        json.dumps({**GOOD, "refund_amount": 25000}),                       # unknown field
    ],
    ids=["wrong-types", "missing-field", "prose-wrapper", "priority-out-of-range", "summary-too-long", "unknown-field"],
)
def test_bad_model_output_goes_to_human_review(raw):
    r = parse_triage(raw)  # must not raise
    assert r.needs_human is True
    assert r.team == Team.HUMAN_REVIEW


def test_stub_bad_outputs_are_caught():
    stub = StubLLM()
    for cid in ("C-013", "C-014", "C-015"):
        raw = stub.complete_blocking(cid, "Unauthorised UPI debit of 25000 rupees")
        assert parse_triage(raw).needs_human, cid
