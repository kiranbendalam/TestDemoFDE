"""The model has a bad day and takes 3 seconds. We give it 1.5 seconds."""
from __future__ import annotations

import asyncio
import time

from model import classify

DEADLINE = 1.5


async def triage(text: str) -> dict:
    try:
        async with asyncio.timeout(DEADLINE):            # never wait forever
            raw = await classify(text, delay=3.0)        # the slow model
        return {"route": "team queue", "reply": raw}
    except TimeoutError:                                 # caught OUTSIDE the `async with` block
        return {"route": "human_review", "reason": f"model timed out after {DEADLINE} s"}


start = time.perf_counter()
result = asyncio.run(triage("Two card transactions I did not make"))
print(f"The model needs 3.0 s; our deadline is {DEADLINE} s.\n")
print(f"  result after {time.perf_counter() - start:.1f} s : {result}")
print("""
WHAT TO NOTICE
- After 1.5 s we stop waiting and send the complaint to human review, with the reason.
- The caller (the contact-centre screen) gets an answer instead of a spinner.
- `except TimeoutError` sits outside the `async with` block: that's where asyncio raises it.""")
