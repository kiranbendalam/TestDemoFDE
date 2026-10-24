"""L1 · step 1: see it fail. Runs the real prototype, then traces three bad model replies through its own code.

Call chain:  bash lab.sh l1 fail  ->  python lab/l1/fail.py
               -> runs triage_prototype.py (the real file)
               -> reads lab/l1/replies.py (three recorded model replies)
No real LLM is called: the lab runs offline and is identical for everyone.
"""
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

from replies import REPLIES  # noqa: E402
from triage_prototype import TEAM_QUEUES  # noqa: E402  (the prototype's own routing table)

PROTO = ROOT / "triage_prototype.py"
LINES = PROTO.read_text().splitlines()


def line_no(snippet):
    return next(i for i, l in enumerate(LINES, 1) if snippet in l)


def show(label, snippet_start, snippet_end=None):
    a = line_no(snippet_start)
    b = line_no(snippet_end) if snippet_end else a
    print(f"  {label}  ({PROTO.name}, lines {a}-{b}):")
    for n in range(a, b + 1):
        print(f"    {n:>3} | {LINES[n - 1]}")
    print()


print("""HOW THIS STEP RUNS
  bash lab.sh l1 fail
    └─ python lab/l1/fail.py
         ├─ A. runs the real triage_prototype.py
         └─ B. reads lab/l1/replies.py (three recorded model replies) and traces them
              through the prototype's own two routing lines
  No real LLM is called. In the prototype, call_model() is a stand-in that returns fixed text,
  so the lab runs offline, needs no key, and gives everyone the same result.
""")

print("━━ A. The real prototype ━━  python triage_prototype.py   (takes ~6 s: call_model sleeps 1 s per complaint)\n")
show("The stand-in for the LLM", "def call_model", "return '{\"category\": \"other\"")
sys.stdout.flush()
subprocess.run([sys.executable, str(PROTO)], cwd=ROOT, check=False)
print("""
  Look at the last line: C-013, a fraud complaint, went to Q-GENERAL, and nothing failed.
  (C-003 to C-005 land in Q-BRANCH only because this stand-in knows just two patterns; ignore them.
   Also notice every 'processing' line prints the full account number: that's the L3 problem.)
""")

print("━━ B. Three bad replies, through the prototype's own routing code ━━\n")
show("The two lines that trust the reply", "out = json.loads(call_model(c))", "queue = TEAM_QUEUES.get(")
for complaint, raw in REPLIES.items():
    print(f"  {complaint}")
    print(f"    model reply : {raw!r}")
    try:
        out = json.loads(raw)
        team = out.get("team")
        queue = TEAM_QUEUES.get(team, "Q-GENERAL")
        print(f"    json.loads  : ok -> team={team!r}, priority={out['priority']!r}")
        print(f"    TEAM_QUEUES.get({team!r}, 'Q-GENERAL') -> {queue}" + ("   ⚠ silent misroute" if queue == "Q-GENERAL" else ""))
    except Exception as e:
        print(f"    json.loads  : ✗ {type(e).__name__}: {e}")
        print("    -> CRASH: the prototype stops here")
    print()

print("""WHAT WENT WRONG
  C-013  "fraud ops" (with a space) isn't a key in TEAM_QUEUES, so .get() quietly returned Q-GENERAL.
         Priority is the word "urgent", not a number. Nothing failed loudly: this is the dangerous one.
  C-014  no "team" at all, so it also went to Q-GENERAL.
  C-015  prose before the JSON, so json.loads crashed. A crash is the *good* failure: someone notices.
""")
