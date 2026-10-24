"""L3 · step 6: try it. Search, count and audit: what the log platform can now do with your lines."""
import collections
import json
import pathlib
import re
import sys

from _common import ROOT, chain, ensure_l1_l2, l3_done, lines, logged_client

chain("""  bash lab.sh l3 try
    └─ python lab/l3/try_.py
         ├─ sends every complaint in data/complaints.jsonl to app/main.py, each with its own X-Request-ID
         └─ then queries the JSON lines like a log platform would: search, count, audit, and a leak check""")
ensure_l1_l2()
if not l3_done():
    print("  L3 isn't applied yet. Run: bash lab.sh l3 apply"); sys.exit(1)
c, buf = logged_client()
complaints = [json.loads(l) for l in (ROOT / "data/complaints.jsonl").read_text().splitlines() if l.strip()]
for x in complaints:
    c.post("/triage", json={"id": x["id"], "text": x["text"], "channel": x.get("channel", "email")}, headers={"X-Request-ID": f"req-{x['id']}"})
logs = [x for x in lines(buf) if x.get("route") == "/triage"]
print(f"  {len(complaints)} requests sent, {len(logs)} JSON lines logged.\n")
print("  SEARCH  outcome = human_review")
for x in logs:
    if x.get("outcome") == "human_review":
        print(f"     {x['request_id']:<12} {x.get('complaint_excerpt', '')[:60]}")
print("\n  COUNT   by outcome")
for k, v in collections.Counter(x.get("outcome") for x in logs).most_common():
    print(f"     {k:<14} {v}")
a = next(x for x in logs if x["request_id"] == "req-C-013")
print(f"\n  AUDIT   which model and prompt decided req-C-013?\n     model={a['model']}  prompt_version={a['prompt_version']}  outcome={a['outcome']}  status={a['status']}  latency_ms={a['latency_ms']}")
leaks = re.findall(r"EB-\d{10}", buf.getvalue())
print(f"\n  LEAK CHECK  full account numbers in all {len(logs)} lines: {len(leaks)}")
print("""
WHAT TO NOTICE
  A print line can't answer any of these. Named fields can: search, count, and the CISO's audit question.""")
