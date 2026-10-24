"""L2 · step 4: apply the fix, and show exactly what changed in app/main.py."""
import difflib
import shutil

from _common import HERE, ROOT, chain, ensure_l1

chain("""  bash lab.sh l2 apply
    └─ python lab/l2/apply.py
         ├─ makes sure L1's contract is in app/models.py
         ├─ copies lab/l2/main_done.py  ->  app/main.py
         └─ prints what changed: each L2 TODO line (-) and the code that replaced it (+)
  Your starter is kept in lab/l2/main_start.py; `bash lab.sh reset l2` puts it back.""")
ensure_l1()
before = (ROOT / "app/main.py").read_text().splitlines()
shutil.copyfile(HERE / "main_done.py", ROOT / "app/main.py")
after = (ROOT / "app/main.py").read_text().splitlines()
diff = list(difflib.unified_diff(before, after, lineterm="", n=0))[2:]
hunks, cur = [], []
for l in diff:
    if l.startswith("@@"):
        if cur: hunks.append(cur)
        cur = [l]
    else:
        cur.append(l)
if cur: hunks.append(cur)
todo = [h for h in hunks if any(l.startswith("-") and ("TODO (L2" in l or "NotImplementedError" in l) for l in h)]
if not hunks:
    print("  app/main.py already had L2: nothing changed.")
else:
    print("WHAT CHANGED: each L2 TODO line (-) and the code that replaced it (+)\n")
    for h in todo:
        start = int(h[0].split("+")[1].split(",")[0].split(" ")[0])
        print(f"    app/main.py, from line {start}:")
        for l in h[1:]:
            print("      " + l)
        print()
    if len(hunks) > len(todo):
        print(f"    (plus {len(hunks) - len(todo)} small edit(s) to imports)")
print("\n  ✅ app/main.py now has /healthz and /triage. Open it in the editor, then: bash lab.sh l2 check")
