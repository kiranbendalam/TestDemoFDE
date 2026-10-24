"""Ten complaints arrive at once. Each model call takes 1 second. Blocking vs awaited."""
from __future__ import annotations

import asyncio
import time

from model import classify, classify_blocking

N = 10


async def handle_blocking(i: int) -> str:
    return classify_blocking(f"complaint {i}")          # a sync call inside async def: blocks the loop


async def handle_async(i: int) -> str:
    return await classify(f"complaint {i}")              # awaited: the loop serves others while it waits


async def run(handler) -> float:
    start = time.perf_counter()
    await asyncio.gather(*(handler(i) for i in range(N)))  # fire all ten at once
    return time.perf_counter() - start


print(f"{N} complaints arrive at once; each model call takes 1 s.\n")
t1 = asyncio.run(run(handle_blocking))
print(f"  BLOCKING  (time.sleep inside async def)   : {N} requests in {t1:.1f} s   <- one after another")
t2 = asyncio.run(run(handle_async))
print(f"  AWAITED   (await asyncio.sleep)           : {N} requests in {t2:.1f} s   <- the waits overlap")
print("""
WHAT TO NOTICE
- Both handlers say `async def`. Only the awaited one is really asynchronous.
- One blocking call freezes the whole event loop, so requests queue behind each other.
- The fix is one word in the right place: `await` an async client.""")
