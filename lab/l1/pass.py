"""L1 · step 5: see it pass. The same three replies, through your contract (app/models.py: parse_triage)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from replies import REPLIES  # noqa: E402
from _view import chain, code  # noqa: E402

try:
    from app.models import parse_triage
    results = {c: parse_triage(raw) for c, raw in REPLIES.items()}
except (NotImplementedError, TypeError, ImportError, AttributeError) as e:
    print(f"Your app/models.py still has the TODO version ({type(e).__name__}).")
    print("Run:  bash lab.sh l1 apply   then try this step again.")
    sys.exit(1)

chain("""  bash lab.sh l1 pass
    └─ python lab/l1/pass.py
         ├─ reads the same three replies as step 1  (lab/l1/replies.py)
         └─ calls parse_triage(reply) from app/models.py for each one, then prints the result""")
code("app/models.py", "def parse_triage", "return human_review(f", "The function each reply goes through")
print("Same replies, now validated by parse_triage before anything is routed:\n")
for complaint, r in results.items():
    print(f"  {complaint:<45} -> team={r.team.value:<13} needs_human={r.needs_human}  ({r.summary})")
print("""
What changed: every malformed reply goes to human_review, with the reason. Nothing misrouted, nothing crashed.
C-013 shows 2 errors: the team isn't one of our exact values, and the priority isn't a number from 1 to 4.
""")
