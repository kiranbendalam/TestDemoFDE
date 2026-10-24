"""L2 · step 3: read the fix, straight from the file step 4 will copy in."""
from _common import chain, code

chain("""  bash lab.sh l2 show
    └─ python lab/l2/show.py
         └─ prints the two finished endpoints from lab/l2/main_done.py, with real line numbers.
            Step 4 copies this exact file over app/main.py. (Its L3 logging TODOs stay open for L3.)""")
code("lab/l2/main_done.py", "app = FastAPI(", "app = FastAPI(", "The app object",
     {"app = FastAPI(": "one FastAPI app: its routes become the API and the /docs page"})
code("lab/l2/main_done.py", '@app.get("/healthz")', 'return {"status": "ok"}', "L2.1  The health check",
     {'@app.get("/healthz")': "a GET route; the platform probes it every few seconds", 'return {"status": "ok"}': "alive: no model call, no database"})
code("lab/l2/main_done.py", '@app.post("/triage"', "return result", "L2.2  The triage endpoint",
     {'@app.post("/triage"': "response_model: only TriageResult's fields leave",
      "async def triage(complaint: Complaint": "typed in: FastAPI checks the body against Complaint (422 if wrong)",
      "async with asyncio.timeout(TIMEOUT_S)": "never wait forever (TIMEOUT_S, default 5 s)",
      "raw = await llm.complete(": "await: other requests run while the model thinks",
      "result = parse_triage(raw)": "L1's contract on the model's reply",
      "except TimeoutError": "caught outside the `async with`",
      'human_review("model timed out")': "too slow: a person gets it, with the reason",
      "return result": "typed out: a TriageResult"})
print("Next: bash lab.sh l2 apply")
