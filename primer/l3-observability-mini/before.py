from __future__ import annotations

from events import EVENTS, MODEL

print("BEFORE: plain print() logging")
print("One request becomes multiple loose lines, with full account numbers still present.\n")

for event in EVENTS:
    complaint = event["complaint"]
    print(f"CASE: {event['label']}")
    print("  processing", complaint)
    print(f"  model={MODEL} outcome={event['outcome']} latency_ms={event['latency_ms']}")
    print()

print("WHAT TO NOTICE")
print("- The full account number is visible in the logs.")
print("- One request is spread across multiple lines, so searching and joining is harder.")
print("- There is no request ID to connect the caller, the response and the logs.")
print("- Fields like route, status and outcome are not in a reliable machine-friendly shape.")
