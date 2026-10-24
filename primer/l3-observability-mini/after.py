from __future__ import annotations

import json

from audit import build_audit_line
from events import EVENTS

print("AFTER: one JSON audit line per request")
print("The same requests are now logged in a machine-friendly, masked shape.\n")

lines = []
for event in EVENTS:
    complaint = event["complaint"]
    request_id, line = build_audit_line(
        path=event["path"],
        status=event["status"],
        latency_ms=event["latency_ms"],
        outcome=event["outcome"],
        complaint_text=complaint["text"],
        incoming_request_id=event["incoming_request_id"],
    )
    lines.append(line)
    caller_sent = event["incoming_request_id"] or "(none)"
    print(f"CASE: {event['label']}")
    print(f"  caller X-Request-ID : {caller_sent}")
    print(f"  response header     : {request_id}")
    print(f"  one JSON line       : {line}")
    parsed = json.loads(line)
    print(f"  key fields          : route={parsed['route']} status={parsed['status']} outcome={parsed['outcome']}")
    print()

print("WHAT TO NOTICE")
print(f"- {len(lines)} requests produced {len(lines)} JSON log lines.")
print("- The caller's request ID is echoed when present; otherwise the service can generate one.")
print("- Full account numbers never reach the stored log line.")
print("- A machine can filter by request_id, route, status or outcome without guessing.")
