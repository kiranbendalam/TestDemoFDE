"""L2 · step 5: see it pass. Real requests to the real service, through FastAPI's TestClient."""
import sys

from _common import chain, client, code, ensure_l1

chain("""  bash lab.sh l2 pass
    └─ python lab/l2/pass.py
         └─ five requests to app/main.py through FastAPI's TestClient (no server needed):
              StubLLM from app/llm.py answers; for the last one, a slow StubLLM and a short deadline""")
ensure_l1()
import app.main as main  # noqa: E402
if "NotImplementedError" in open(main.__file__).read():
    print("  app/main.py still has the L2 TODOs. Run: bash lab.sh l2 apply"); sys.exit(1)
code("app/main.py", '@app.post("/triage"', "return result", "The endpoint every /triage request goes through")
from app.llm import StubLLM  # noqa: E402

c = client()
cases = [
    ("1. Is it alive?", "GET", "/healthz", None),
    ("2. A good complaint", "POST", "/triage", {"id": "C-002", "text": "Two card transactions I did not make"}),
    ("3. C-013: the model's bad reply ('fraud ops', 'urgent')", "POST", "/triage", {"id": "C-013", "text": "Unauthorised UPI debit of 25000 rupees"}),
    ("4. A bad request (empty text, channel 'fax')", "POST", "/triage", {"id": "C-1", "text": "", "channel": "fax"}),
]
for label, m, p, body in cases:
    r = c.request(m, p, json=body)
    print(f"{label}\n  {m} {p}" + (f"  body={body}" if body else "") + f"\n  -> {r.status_code}  {r.text[:170]}\n")
r = client(llm=StubLLM(delay=1.0), timeout=0.3).post("/triage", json={"id": "C-001", "text": "charged twice"})
print(f"5. A slow model (1 s) and a 0.3 s deadline\n  POST /triage\n  -> {r.status_code}  {r.text[:170]}\n")
print("""WHAT TO NOTICE
  1 the platform's probe works · 2 a valid reply routes (fraud_ops) · 3 a malformed reply goes to human_review
  4 a bad request gets 422 before triage() runs · 5 a slow model gives a safe answer, not a hang""")
