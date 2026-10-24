from __future__ import annotations

import json

from audit import mask

plain = "Charged twice. Account EB-4418203391."
line = json.dumps(
    {
        "msg": "request",
        "complaint_excerpt": "Unauthorised UPI debit. Account EB-9081726354.",
    }
)

print("MASKING")
print("Before storing a log, hide the sensitive parts.\n")
print(f"plain text before : {plain}")
print(f"plain text after  : {mask(plain)}\n")
print(f"JSON line before  : {line}")
print(f"JSON line after   : {mask(line)}\n")
print("WHAT TO NOTICE")
print("- The last 4 digits remain for debugging and matching with a case.")
print("- Masking the whole JSON line is safer than trying to protect one field at a time.")
