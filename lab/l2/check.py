"""L2 · steps 2 and 5: run the service tests and explain each one."""
import re
import subprocess
import sys

from _common import ROOT, chain, ensure_l1

CHECKS = [
    ("test_healthz", "GET /healthz answers 200 {\"status\": \"ok\"}", "L2.1"),
    ("test_triage_routes_a_dispute", "POST /triage with a 'charged twice' complaint -> 200, team disputes", "L2.2"),
    ("test_bad_model_output_returns_human_review", "POST /triage for C-013 (the bad model reply) -> 200, team human_review", "L2.2"),
    ("test_invalid_request_is_rejected_by_the_contract", "A bad request (empty text, channel 'fax') -> 422 before our code runs", "L1 contract"),
    ("test_slow_model_times_out_to_human_review", "A model slower than the deadline -> human_review, 'model timed out'", "L2.2"),
    ("test_openapi_contract_is_published", "/openapi.json lists /triage, /healthz and TriageResult's fields (what /docs shows)", "L1 + L2"),
]
chain("""  bash lab.sh l2 check
    └─ python -m pytest -v tests/test_l2.py        (the same tests `bash grade.sh l2` runs)
         ├─ sends requests to app/main.py (the file being checked) through FastAPI's TestClient
         └─ swaps in StubLLM from app/llm.py (and a slow one, for the timeout test)
  Open tests/test_l2.py in the editor to read each test.""")
ensure_l1()
sys.stdout.flush()
proc = subprocess.run([sys.executable, "-m", "pytest", "-v", "--tb=no", "-p", "no:cacheprovider", "tests/test_l2.py"],
                      cwd=ROOT, capture_output=True, text=True)
status = dict(re.findall(r"tests/test_l2\.py::(\S+) (PASSED|FAILED|ERROR)", proc.stdout))
ok = 0
print(f"THE {len(CHECKS)} CHECKS (tests/test_l2.py)\n")
for tid, what, need in CHECKS:
    st = status.get(tid, "ERROR"); ok += st == "PASSED"
    print(f"  {'✅' if st == 'PASSED' else '❌'} {what:<84} needs {need}")
print(f"\n  {ok} of {len(CHECKS)} checks pass.\n")
src = (ROOT / "app/main.py").read_text().splitlines()
if ok < len(CHECKS):
    print("WHERE THE GAP IS: app/main.py still has the L2 TODOs:\n")
    for n, l in enumerate(src, 1):
        if "TODO (L2" in l or 'NotImplementedError("L2' in l:
            print(f"    app/main.py:{n:<3} {l.strip()}")
    print("""
  L2.1  healthz() raises instead of returning {"status": "ok"}.
  L2.2  triage() raises instead of calling the model (with a timeout) and checking the reply.
  (The 422 and /openapi.json checks may already pass: they come from L1's contract, which FastAPI reads.)
  Next: bash lab.sh l2 show, then bash lab.sh l2 apply""")
else:
    print("WHAT MADE THEM PASS: these lines in app/main.py\n")
    for k in ['return {"status": "ok"}', "async with asyncio.timeout(TIMEOUT_S)", "raw = await llm.complete(", "result = parse_triage(raw)", "except TimeoutError", 'result = human_review("model timed out")', "    return result"]:
        n = next((i for i, l in enumerate(src, 1) if k in l), None)
        if n:
            print(f"    app/main.py:{n:<3} {src[n - 1].strip()}")
    print("\n  Next: bash lab.sh l2 pass")
