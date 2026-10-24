from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
path = HERE / "contract.py"

print("THE TINY PYDANTIC CONTRACT")
print("This is the only new idea in the mini-lab:\n")

for line_no, line in enumerate(path.read_text().splitlines(), 1):
    print(f"{line_no:>3} | {line}")

print("\nWHAT TO NOTICE")
print("- `team` must be exactly `fraud_ops` or `disputes`.")
print("- `priority` must be an integer from 1 to 4.")
print("- `model_validate_json(raw)` parses and validates in one step.")
print("- Bad replies do not route; they go to `human_review(...)`.")
