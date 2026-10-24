from __future__ import annotations

from contract import safe_route
from replies import REPLIES

print("WITH A PYDANTIC CONTRACT")
print("The same replies are validated before routing.\n")

for label, raw in REPLIES:
    decision = safe_route(raw)
    print(f"CASE: {label}")
    print(f"  raw reply   : {raw!r}")
    print(f"  queue       : {decision['queue']}")
    print(f"  needs_human : {decision['needs_human']}")
    print(f"  reason      : {decision['reason']}")
    if not decision["needs_human"]:
        print(f"  team        : {decision['team']!r}")
        print(f"  priority    : {decision['priority']}")
    print()

print("WHY THIS IS BETTER")
print("- Good replies still flow through.")
print("- Bad replies are caught before queue lookup happens.")
print("- The system becomes safer even though the model did not change.")
