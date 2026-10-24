from __future__ import annotations

import json

from replies import QUEUE_BY_TEAM, REPLIES

print("WITHOUT A CONTRACT")
print("The program trusts the LLM reply too early.\n")
print("Queue lookup:")
for team, queue in QUEUE_BY_TEAM.items():
    print(f"  {team!r} -> {queue}")
print()

for label, raw in REPLIES:
    print(f"CASE: {label}")
    print(f"  raw reply   : {raw!r}")
    try:
        reply = json.loads(raw)
        team = reply.get("team")
        queue = QUEUE_BY_TEAM.get(team, "Q-GENERAL")
        print(f"  json.loads  : ok")
        print(f"  team value  : {team!r}")
        print(f"  queue       : {queue}")
        if queue == "Q-GENERAL" and team != "fraud_ops":
            print("  outcome     : silent misroute")
        else:
            print("  outcome     : routed")
    except Exception as exc:
        print(f"  json.loads  : {type(exc).__name__}: {exc}")
        print("  outcome     : crash")
    print()

print("WHY THIS IS RISKY")
print("- Wrong-but-JSON-shaped replies can look fine and still go to the wrong queue.")
print("- Prose around JSON can crash the program.")
print("- Nothing checks whether the reply matches what the system expects.")
