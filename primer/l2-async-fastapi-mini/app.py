"""A tiny FastAPI service: the same contract idea, now as an API other systems can call."""
from __future__ import annotations

import asyncio
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from model import classify

app = FastAPI(title="Example Bank triage (primer)", version="0.1.0")


class Complaint(BaseModel):                          # what comes IN: FastAPI checks every request
    id: str = Field(min_length=1, max_length=20)
    text: str = Field(min_length=1, max_length=4000)


class TriageReply(BaseModel):                        # what goes OUT: only these fields leave
    model_config = ConfigDict(extra="forbid")
    team: Literal["fraud_ops", "disputes", "human_review"]
    priority: int = Field(ge=1, le=4)
    summary: str = Field(max_length=80)


@app.get("/healthz")                                 # the platform asks: are you alive?
def healthz() -> dict:
    return {"status": "ok"}


@app.post("/triage", response_model=TriageReply)     # typed in, typed out
async def triage(complaint: Complaint) -> TriageReply:
    try:
        async with asyncio.timeout(1.5):             # never wait forever on the model
            raw = await classify(complaint.text)     # awaited: other requests keep running
        return TriageReply.model_validate_json(raw)  # the L1 contract on the model's reply
    except (TimeoutError, ValidationError):
        return TriageReply(team="human_review", priority=2, summary="needs a person")
