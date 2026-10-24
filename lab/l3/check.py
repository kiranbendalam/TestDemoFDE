"""L3 · steps 2 and 5: run the logging tests and explain each one."""
import re
import subprocess
import sys

from _common import ROOT, chain, ensure_l1_l2

CHECKS = [
    ("test_mask", "mask() turns EB-4418203391 into EB-******3391 and leaves other text alone", "L3.1"),
    ("test_one_json_line_per_request_with_the_audit_fields", "One /triage request -> exactly one JSON line with ts, level, request_id, route, status, latency_ms, model, prompt_version, outcome", "L3.2-L3.4"),
    ("test_request_id_is_echoed_and_logged", "X-Request-ID req-abc123 comes back in the response and in the log; one is generated if the caller sends none", "L3.3"),
    ("test_no_full_account_number_in_logs", "C-013 with account EB-9081726354 -> no full account number anywhere in the logs", "L3.1-L3.2"),
]
chain("""  bash lab.sh l3 check
    └─ python -m pytest -v tests/test_l3.py        (the same tests `bash grade.sh l3` runs)
         ├─ calls mask() and setup_logging() from app/logging_setup.py, writing logs into a buffer
         └─ sends requests to app/main.py (TestClient) and reads back the JSON lines it logged
  Open tests/test_l3.py in the editor to read each test.""")
ensure_l1_l2()
sys.stdout.flush()
proc = subprocess.run([sys.executable, "-m", "pytest", "-v", "--tb=no", "-p", "no:cacheprovider", "tests/test_l3.py"], cwd=ROOT, capture_output=True, text=True)
status = dict(re.findall(r"tests/test_l3\.py::(\S+) (PASSED|FAILED|ERROR)", proc.stdout))
ok = 0
print(f"THE {len(CHECKS)} CHECKS (tests/test_l3.py)\n")
for tid, what, need in CHECKS:
    st = status.get(tid, "ERROR"); ok += st == "PASSED"
    print(f"  {'✅' if st == 'PASSED' else '❌'} {what}\n       needs {need}")
print(f"\n  {ok} of {len(CHECKS)} checks pass.\n")
if ok < len(CHECKS):
    print("WHERE THE GAP IS: the L3 TODOs still open:\n")
    for f in ("app/logging_setup.py", "app/main.py"):
        for n, l in enumerate((ROOT / f).read_text().splitlines(), 1):
            if "TODO (L3" in l or 'NotImplementedError("L3' in l:
                print(f"    {f}:{n:<3} {l.strip()}")
    print("""
  L3.1  mask() raises instead of hiding all but the last four digits.
  L3.2  JsonFormatter.format() raises instead of writing one JSON line.
  L3.3  no middleware, so no line per request and no request ID.
  L3.4  triage() doesn't record model, prompt_version and outcome for the log line.
  Next: bash lab.sh l3 show, then bash lab.sh l3 apply""")
else:
    print("WHAT MADE THEM PASS:\n")
    for f, keys in [("app/logging_setup.py", ["return ACCOUNT_RE.sub(", "for field in FIELDS", "return mask(json.dumps("]),
                    ("app/main.py", ['@app.middleware("http")', 'request.headers.get("X-Request-ID")', 'response.headers["X-Request-ID"]', 'logger.info(', '"prompt_version": PROMPT_VERSION', "setup_logging()"])]:
        src = (ROOT / f).read_text().splitlines()
        for k in keys:
            n = next((i for i, l in enumerate(src, 1) if k in l), None)
            if n:
                print(f"    {f}:{n:<3} {src[n - 1].strip()}")
    print("\n  Next: bash lab.sh l3 pass")
