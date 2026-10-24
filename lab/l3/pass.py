"""L3 · step 5: see it pass. One request, one JSON line, the request ID echoed, the account masked."""
import json
import re
import sys

from _common import chain, code, ensure_l1_l2, l3_done, lines, logged_client

chain("""  bash lab.sh l3 pass
    └─ python lab/l3/pass.py
         ├─ sends POST /triage (C-013, with account EB-9081726354) with header X-Request-ID: req-demo-001
         ├─ and GET /healthz with no ID
         └─ reads back the JSON lines the 'triage' logger wrote (app/logging_setup.py), as tests/test_l3.py does""")
ensure_l1_l2()
if not l3_done():
    print("  L3 isn't applied yet. Run: bash lab.sh l3 apply"); sys.exit(1)
code("app/main.py", "logger.info(", "**request.state.log,", "The line that writes each log entry")
c, buf = logged_client()
r = c.post("/triage", json={"id": "C-013", "text": "Unauthorised UPI debit. Account EB-9081726354."}, headers={"X-Request-ID": "req-demo-001"})
h = c.get("/healthz")
print(f"  POST /triage -> {r.status_code}, response header X-Request-ID: {r.headers.get('X-Request-ID')}")
print(f"  GET  /healthz -> {h.status_code}, response header X-Request-ID: {h.headers.get('X-Request-ID')}   (generated)\n")
for x in lines(buf):
    print("  " + json.dumps(x, indent=2).replace("\n", "\n  ") + "\n")
full = re.findall(r"EB-\d{10}", buf.getvalue())
print(f"  Full account numbers in the logs: {len(full)}   (EB-9081726354 became EB-******6354)\n")
print("""WHAT TO NOTICE
  One line per request, written by the middleware. request_id follows the complaint across systems;
  model + prompt_version say which configuration decided; outcome is human_review because C-013's reply
  was malformed (L1). The account number was masked on the whole line before it was written.""")
