"""L3 · step 1: see it fail. The prototype prints account numbers; the service logs nothing at all."""
import subprocess
import sys

from _common import ROOT, chain, code, ensure_l1_l2, l3_done

chain("""  bash lab.sh l3 fail
    └─ python lab/l3/fail.py
         ├─ A. runs triage_prototype.py and shows its first two lines of output, plus the line that prints them
         └─ B. sends one request to the real app/main.py (TestClient) and looks for a log line
  No real LLM: StubLLM answers offline.""")
ensure_l1_l2()
print("━━ A. What the prototype logs ━━\n")
code("triage_prototype.py", 'print("processing", c)', 'print("processing", c)', "The line that logs")
out = subprocess.run([sys.executable, "triage_prototype.py"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()[:2]
for l in out:
    print("    " + l)
print("""
  Three problems: the full account number is now in the log system; there's no request ID to follow it;
  and nothing a machine can search (which model? which prompt? routed or human review?).
""")
print("━━ B. What the service logs today ━━\n")
if l3_done():
    print("  L3 is already applied, so there's nothing failing to show.\n  To see it fail again: bash lab.sh reset l3   then   bash lab.sh l3 fail\n")
    raise SystemExit(0)
from _common import logged_client, lines  # noqa: E402
c, buf = logged_client()
try:
    r = c.post("/triage", json={"id": "C-013", "text": "Unauthorised UPI debit. Account EB-9081726354."})
    status = r.status_code
except Exception as e:  # noqa: BLE001
    status = f"error: {type(e).__name__}"
got = lines(buf)
print(f"  POST /triage (C-013)  -> {status}\n  JSON log lines written: {len(got)}\n")
code("app/main.py", "# TODO (L3.3)", "# TODO (L3.3)", "No request-logging middleware yet")
code("app/logging_setup.py", "def mask(", 'raise NotImplementedError("L3.1")', "mask() isn't written")
code("app/logging_setup.py", "class JsonFormatter", 'raise NotImplementedError("L3.2")', "The JSON formatter isn't written")
print("""WHAT WENT WRONG
  The service answers, but leaves no audit trail: no line per request, no request ID, nothing masked.
  The CISO's question, "which model decided C-013, and was the account number kept out of the logs?",
  has no answer yet.
""")
