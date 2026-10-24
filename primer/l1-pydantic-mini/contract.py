from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

QUEUE_BY_TEAM = {
    "fraud_ops": "Q-FRAUD",
    "disputes": "Q-DISPUTES",
}


class ModelReply(BaseModel):
    model_config = ConfigDict(extra="forbid")

    team: Literal["fraud_ops", "disputes"]
    priority: int = Field(ge=1, le=4)
    summary: str = Field(min_length=1, max_length=80)


def human_review(reason: str) -> dict[str, object]:
    return {
        "queue": "Q-HUMAN",
        "needs_human": True,
        "reason": reason,
    }


def safe_route(raw: str) -> dict[str, object]:
    try:
        reply = ModelReply.model_validate_json(raw)
    except ValidationError as exc:
        return human_review(f"invalid model output ({len(exc.errors())} error(s))")

    return {
        "queue": QUEUE_BY_TEAM[reply.team],
        "needs_human": False,
        "reason": "validated",
        "team": reply.team,
        "priority": reply.priority,
        "summary": reply.summary,
    }
