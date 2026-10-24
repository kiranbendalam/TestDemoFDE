"""A stand-in for the LLM. No real model is called: each call just waits, then returns fixed JSON text."""
from __future__ import annotations

import asyncio
import json
import time

DELAY = 1.0  # seconds: how long the "model" takes to answer


def _reply(text: str) -> str:
    fraud = any(w in text.lower() for w in ("unauthorised", "did not make", "fraud"))
    return json.dumps({"team": "fraud_ops" if fraud else "disputes", "priority": 1 if fraud else 2, "summary": text[:80]})


def classify_blocking(text: str, delay: float = DELAY) -> str:
    """Like a sync SDK call: time.sleep blocks everything while it waits."""
    time.sleep(delay)
    return _reply(text)


async def classify(text: str, delay: float = DELAY) -> str:
    """Like an async client call: await asyncio.sleep lets other requests run while it waits."""
    await asyncio.sleep(delay)
    return _reply(text)
