"""L1 · step 6: try it. Three ready-made replies; predict the result before you read it (Contract topic in the deck: "Predict the validation error")."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _view import chain, code  # noqa: E402
try:
    from pydantic import ValidationError

    from app.models import TriageResult
    TriageResult.model_validate_json('{"category": "other", "priority": 2, "team": "human_review", "summary": "x"}')
except Exception:
    print("Your app/models.py still has the TODO version. Run:  bash lab.sh l1 apply")
    sys.exit(1)

chain("""  bash lab.sh l1 try
    └─ python lab/l1/try.py
         └─ for each reply A, B, C: TriageResult.model_validate_json(reply)   (the class in app/models.py)
              ├─ valid   -> a typed TriageResult object
              └─ invalid -> pydantic.ValidationError; we print each error's field and type""")
code("app/models.py", "class TriageResult", "needs_human: bool", "The contract each reply is checked against")
CASES = [
    ("A  priority 7", '{"category": "fraud", "priority": 7, "team": "fraud_ops", "summary": "UPI debit"}'),
    ("B  an extra field", '{"category": "fraud", "priority": 1, "team": "fraud_ops", "summary": "UPI debit", "confidence": 0.9}'),
    ("C  a good reply", '{"category": "fraud", "priority": 1, "team": "fraud_ops", "summary": "UPI debit"}'),
]
for name, raw in CASES:
    print(f"{name}\n   reply: {raw}")
    try:
        r = TriageResult.model_validate_json(raw)
        print(f"   ✓ valid: a typed object. team={r.team!r}, priority={r.priority!r} ({type(r.priority).__name__})\n")
    except ValidationError as e:
        for err in e.errors():
            print(f"   ✗ {'.'.join(map(str, err['loc']))}: {err['type']}  ({err['msg']})")
        print()
print("A fails on priority (less_than_equal, because le=4). B fails on extra_forbidden (extra=\"forbid\").")
print("C becomes a real Python object your code can trust.")
