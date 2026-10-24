"""L2 · step 6: try it. Is the real service really async? Ten requests at once, a 1-second model."""
import asyncio
import sys
import time

from _common import ROOT, chain, code, ensure_l1

chain("""  bash lab.sh l2 try
    └─ python lab/l2/try_.py
         ├─ sends 10 requests at once to app/main.py, in-process (httpx.AsyncClient + ASGITransport)
         ├─ round A: StubLLM(delay=1.0).complete  -> awaits asyncio.sleep  (an async client)
         └─ round B: the same, but the model call does time.sleep          (a blocking, sync client)""")
ensure_l1()
import app.main as main  # noqa: E402
if "NotImplementedError" in open(main.__file__).read():
    print("  app/main.py still has the L2 TODOs. Run: bash lab.sh l2 apply"); sys.exit(1)
import httpx  # noqa: E402
from app.llm import StubLLM  # noqa: E402

code("app/llm.py", "async def complete(", "return _stub_output(complaint_id, text)", "Round A: the async model call")


class BlockingLLM(StubLLM):
    async def complete(self, complaint_id, text):          # says async...
        return self.complete_blocking(complaint_id, text)  # ...but time.sleep blocks the loop


async def ten(llm):
    main.llm, main.TIMEOUT_S = llm, 30
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app), base_url="http://lab") as c:
        start = time.perf_counter()
        rs = await asyncio.gather(*(c.post("/triage", json={"id": f"C-{i:03}", "text": "charged twice"}) for i in range(10)))
        return time.perf_counter() - start, {r.status_code for r in rs}

t_a, s_a = asyncio.run(ten(StubLLM(delay=1.0)))
print(f"  A  async model call    : 10 requests in {t_a:.1f} s   (status {sorted(s_a)})")
t_b, s_b = asyncio.run(ten(BlockingLLM(delay=1.0)))
print(f"  B  blocking model call : 10 requests in {t_b:.1f} s   (status {sorted(s_b)})")
print("""
WHAT TO NOTICE
  Your triage() is `async def` and awaits the model, so ten waits overlap: about 1 s.
  Give it a blocking client (round B) and the same code takes about 10 s: the event loop is frozen.
  An FDE checks what's inside the async function, not the keyword on top.""")
