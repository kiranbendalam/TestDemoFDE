"""L3 · step 4: apply the fix to both files, and show exactly what changed."""
import difflib
import shutil

from _common import HERE, ROOT, chain, ensure_l1_l2

chain("""  bash lab.sh l3 apply
    └─ python lab/l3/apply.py
         ├─ makes sure L1 and L2 are in place
         ├─ copies lab/l3/logging_done.py -> app/logging_setup.py
         ├─ copies lab/l3/main_done.py    -> app/main.py
         └─ prints what changed in each: every L3 TODO line (-) and the code that replaced it (+)
  `bash lab.sh reset l3` puts both L3 starters back.""")
ensure_l1_l2()
for src, dst in [("logging_done.py", "app/logging_setup.py"), ("main_done.py", "app/main.py")]:
    before = (ROOT / dst).read_text().splitlines()
    shutil.copyfile(HERE / src, ROOT / dst)
    after = (ROOT / dst).read_text().splitlines()
    diff = list(difflib.unified_diff(before, after, lineterm="", n=0))[2:]
    hunks, cur = [], []
    for l in diff:
        if l.startswith("@@"):
            if cur: hunks.append(cur)
            cur = [l]
        else:
            cur.append(l)
    if cur: hunks.append(cur)
    todo = [h for h in hunks if any((l.startswith("-") and ("TODO (L3" in l or 'NotImplementedError("L3' in l))
                                    or (l.startswith("+") and l.strip() == "+setup_logging()") for l in h)]
    print(f"WHAT CHANGED in {dst}\n")
    if not hunks:
        print("    already had L3: nothing changed.\n")
    for h in todo:
        start = int(h[0].split("+")[1].split(",")[0].split(" ")[0])
        print(f"    {dst}, from line {start}:")
        for l in h[1:]:
            print("      " + l)
        print()
    if len(hunks) > len(todo):
        print(f"    (plus {len(hunks) - len(todo)} small edit(s) to imports and docstrings)\n")
print("  ✅ L3 applied. Open app/logging_setup.py and app/main.py, then: bash lab.sh l3 check")
