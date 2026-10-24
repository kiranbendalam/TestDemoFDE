"""L1 · steps 2 and 5: run the contract tests and explain each one.

Call chain:  bash lab.sh l1 check  ->  python lab/l1/check.py
               -> python -m pytest -v tests/test_l1.py   (the same tests `bash grade.sh l1` runs)
                    -> imports Complaint, TriageResult, parse_triage from app/models.py
                    -> imports StubLLM from app/llm.py (for the bad replies C-013, C-014, C-015)
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

# test id -> (plain-language check, which TODO in app/models.py makes it pass)
CHECKS = [
    ("test_complaint_accepts_valid_input", "Complaint accepts a valid request; channel defaults to email", "L1.1"),
    ("test_complaint_rejects_bad_input[bad0]", "Complaint rejects an empty id", "L1.1"),
    ("test_complaint_rejects_bad_input[bad1]", "Complaint rejects empty text", "L1.1"),
    ("test_complaint_rejects_bad_input[bad2]", "Complaint rejects channel 'fax' (not email/chat/branch/phone)", "L1.1"),
    ("test_valid_model_output_parses", "A good model reply becomes a TriageResult (team=fraud_ops, priority=1)", "L1.2 + L1.3"),
    ("test_bad_model_output_goes_to_human_review[wrong-types]", "Reply with priority 'urgent' and team 'fraud ops' -> human review", "L1.2 + L1.3"),
    ("test_bad_model_output_goes_to_human_review[missing-field]", "Reply with no team -> human review", "L1.2 + L1.3"),
    ("test_bad_model_output_goes_to_human_review[prose-wrapper]", "Reply with prose around the JSON -> human review", "L1.3"),
    ("test_bad_model_output_goes_to_human_review[priority-out-of-range]", "Reply with priority 7 -> human review", "L1.2 + L1.3"),
    ("test_bad_model_output_goes_to_human_review[summary-too-long]", "Reply with a 201-character summary -> human review", "L1.2 + L1.3"),
    ("test_bad_model_output_goes_to_human_review[unknown-field]", "Reply with an extra field (refund_amount) -> human review", "L1.2 + L1.3"),
    ("test_stub_bad_outputs_are_caught", "The stub model's bad replies for C-013, C-014, C-015 -> human review", "L1.3"),
]

print("""HOW THIS STEP RUNS
  bash lab.sh l1 check
    └─ python -m pytest -v tests/test_l1.py        (the same tests `bash grade.sh l1` runs)
         ├─ imports Complaint, TriageResult, parse_triage  from app/models.py   <- the file being checked
         └─ imports StubLLM                                  from app/llm.py      (bad replies C-013..C-015)
  Open tests/test_l1.py in the editor to read each test.
""")
sys.stdout.flush()
proc = subprocess.run([sys.executable, "-m", "pytest", "-v", "--tb=no", "-p", "no:cacheprovider", "tests/test_l1.py"],
                      cwd=ROOT, capture_output=True, text=True)
status = dict(re.findall(r"tests/test_l1\.py::(\S+) (PASSED|FAILED|ERROR)", proc.stdout))

ok = 0
print("THE 12 CHECKS (tests/test_l1.py)\n")
for tid, what, todo in CHECKS:
    st = status.get(tid, "ERROR")
    ok += st == "PASSED"
    mark = "✅" if st == "PASSED" else "❌"
    print(f"  {mark} {what:<72} needs {todo}")
print(f"\n  {ok} of {len(CHECKS)} checks pass.\n")

if ok < len(CHECKS):
    todo_lines = [(n, l.strip()) for n, l in enumerate((ROOT / "app/models.py").read_text().splitlines(), 1)
                  if "TODO" in l or "NotImplementedError" in l]
    print("WHERE THE GAP IS: app/models.py still has the empty starter. These lines are what's missing:\n")
    for n, l in todo_lines:
        print(f"    app/models.py:{n:<3} {l}")
    print("""
  L1.1  Complaint has no fields yet, so it can't check id, text or channel.
  L1.2  TriageResult has no fields yet, so a reply can't be checked against them.
  L1.3  parse_triage raises NotImplementedError instead of validating the reply.
  Next: bash lab.sh l1 show   (read the fix), then bash lab.sh l1 apply.""")
else:
    src = (ROOT / "app/models.py").read_text().splitlines()
    keys = [("L1.1", "id: str = Field("), ("L1.1", "text: str = Field("), ("L1.1", "channel: Literal["),
            ("L1.2", 'extra="forbid"'), ("L1.2", "category: Category"), ("L1.2", "priority: int = Field("),
            ("L1.2", "team: Team"), ("L1.2", "summary: str = Field("),
            ("L1.3", "model_validate_json(raw)"), ("L1.3", "except ValidationError")]
    print("WHAT MADE THEM PASS: these lines in app/models.py\n")
    for todo, k in keys:
        n = next((i for i, l in enumerate(src, 1) if k in l), None)
        if n:
            print(f"    {todo}  app/models.py:{n:<3} {src[n - 1].strip()}")
    print("""
  This is a contract test: the bottom layer of the test pyramid. A CI gate runs it on every pull request.
  Next: bash lab.sh l1 pass""")
