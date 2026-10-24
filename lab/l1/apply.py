"""L1 · step 4: apply the fix, and show exactly what changed in app/models.py."""
import difflib, pathlib, shutil, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _view import ROOT, chain

chain("""  bash lab.sh l1 apply
    └─ python lab/l1/apply.py
         ├─ copies lab/l1/models_done.py  ->  app/models.py
         └─ prints the difference (what the TODO lines became)
  Your empty starter is kept in lab/l1/models_start.py; `bash lab.sh reset l1` puts it back.""")
before = (ROOT / "app/models.py").read_text().splitlines()
shutil.copyfile(ROOT / "lab/l1/models_done.py", ROOT / "app/models.py")
after = (ROOT / "app/models.py").read_text().splitlines()
diff = list(difflib.unified_diff(before, after, lineterm="", n=0))[2:]
hunks, cur = [], []
for l in diff:
    if l.startswith("@@"):
        if cur:
            hunks.append(cur)
        cur = [l]
    else:
        cur.append(l)
if cur:
    hunks.append(cur)
todo = [h for h in hunks if any(l.startswith("-") and ("TODO" in l or "NotImplementedError" in l) for l in h)]
if not hunks:
    print("  app/models.py already had the contract: nothing changed.")
else:
    print("WHAT CHANGED: each TODO line (-) and the code that replaced it (+)\n")
    for h in todo:
        start = int(h[0].split("+")[1].split(",")[0].split(" ")[0])
        print(f"    app/models.py, from line {start}:")
        for l in h[1:]:
            print("      " + l)
        print()
    if len(hunks) > len(todo):
        print(f"    (plus {len(hunks) - len(todo)} small edits to docstrings and imports)")
print("\n  ✅ app/models.py now has the contract. Open it in the editor, then: bash lab.sh l1 check")
