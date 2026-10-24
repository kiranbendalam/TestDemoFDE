"""L1 · step 3: read the fix, straight from the file step 4 will copy in."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _view import chain, code

chain("""  bash lab.sh l1 show
    └─ python lab/l1/show.py
         └─ prints the finished contract from lab/l1/models_done.py, with its real line numbers.
            Step 4 copies this exact file over app/models.py.""")

code("lab/l1/models_done.py", "class Complaint", "channel: Literal", "L1.1  What the case system sends us",
     {"id: str": "id must be 1-20 characters", "text: str": "text must be 1-4000 characters", "channel": "only these 4 values; default email"})
code("lab/l1/models_done.py", "class TriageResult", "needs_human: bool", "L1.2  What we send back",
     {"class TriageResult": "1 BaseModel: a contract Pydantic checks", 'extra="forbid"': "2 reject fields we didn't ask for",
      "category: Category": "3 enum: exact values only", "team: Team": "3 'fraud ops' ✗, 'fraud_ops' ✓",
      "priority: int": "4 a whole number 1-4: 'urgent' ✗, 7 ✗", "summary: str": "4 at most 200 characters"})
code("lab/l1/models_done.py", "def parse_triage", "return human_review(f", "L1.3  Check the model's reply",
     {"model_validate_json": "5 parse + check in one step; prose ✗", "except ValidationError": "6 your decision:",
      "return human_review(f": "6 never guess, send it to a human"})
print("1-5 are what Pydantic adds. 6 is plain Python: what your service does when the check fails.")
print("Category and Team (the allowed values) are defined at the top of the same file. Next: bash lab.sh l1 apply")
