"""L1 Contract: what goes into the service and what comes out. (Solution.)"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class Category(str, Enum):
    CARD_DISPUTE = "card_dispute"
    FRAUD = "fraud"
    ACCOUNT_ACCESS = "account_access"
    CHARGES = "charges"
    OTHER = "other"


class Team(str, Enum):
    DISPUTES = "disputes"
    FRAUD_OPS = "fraud_ops"
    DIGITAL_SUPPORT = "digital_support"
    BRANCH_SERVICES = "branch_services"
    HUMAN_REVIEW = "human_review"


class Complaint(BaseModel):
    """What the contact-centre system sends us."""

    id: str = Field(min_length=1, max_length=20)
    text: str = Field(min_length=1, max_length=4000)
    channel: Literal["email", "chat", "branch", "phone"] = "email"


class TriageResult(BaseModel):
    """What we send back. Code downstream routes on this, so it must be exact."""

    model_config = ConfigDict(extra="forbid")

    category: Category
    priority: int = Field(ge=1, le=4)
    team: Team
    summary: str = Field(max_length=200)
    needs_human: bool = False


def human_review(reason: str) -> TriageResult:
    """The safe answer when we can't trust the model's output."""
    return TriageResult(
        category=Category.OTHER, priority=2, team=Team.HUMAN_REVIEW, summary=reason[:200], needs_human=True
    )


def parse_triage(raw: str) -> TriageResult:
    """Validate the model's raw text. Never crash, never guess: bad output goes to a human."""
    try:
        return TriageResult.model_validate_json(raw)
    except ValidationError as e:
        return human_review(f"invalid model output ({e.error_count()} error(s))")
