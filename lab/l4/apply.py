"""L4 · step 4: apply the fix. Dockerfile and .dockerignore in your lab folder; the deliberate commit in the twin."""
import difflib
import shutil

from _common import BRANCH, HERE, ROOT, TWIN, chain, ensure_l1_l3, run, twin

chain(f"""  bash lab.sh l4 apply
    └─ python lab/l4/apply.py
         ├─ makes sure L1-L3 are in place
         ├─ B. copies lab/l4/Dockerfile_done   -> Dockerfile      (in your lab folder) and prints the diff
         │     copies lab/l4/dockerignore_done -> .dockerignore
         └─ A. in the twin ({TWIN}): branch, ignore .env, stage by name, commit
               (your real repo gets no branch and no commit; that's the assignment)
  `bash lab.sh reset l4` puts the starter Dockerfile back and removes .dockerignore.""")
ensure_l1_l3()

print("━━ B. Docker ━━\n")
before = (ROOT / "Dockerfile").read_text().splitlines()
shutil.copyfile(HERE / "Dockerfile_done", ROOT / "Dockerfile")
after = (ROOT / "Dockerfile").read_text().splitlines()
diff = list(difflib.unified_diff(before, after, "Dockerfile (before)", "Dockerfile (after)", lineterm="", n=0))
print("WHAT CHANGED in Dockerfile\n")
if diff:
    print("\n".join("    " + l for l in diff[2:] if not l.startswith("@@")))
else:
    print("    (nothing: it was already the fixed version)")
had = (ROOT / ".dockerignore").exists()
shutil.copyfile(HERE / "dockerignore_done", ROOT / ".dockerignore")
print("\n.dockerignore " + ("(replaced)" if had else "(new file)") + "\n")
print("\n".join("    +" + l for l in (ROOT / ".dockerignore").read_text().splitlines()))
print("""
  The five TODO comments went, and so did: FROM python:3.12 (TODO 1), ENV SERVICE_API_KEY (TODO 2),
  COPY . . (TODO 3). Added: the pinned slim base, two narrow COPY lines, a user (TODO 4) and HEALTHCHECK (TODO 5).
""")

print("━━ A. Git (in the twin) ━━\n")
twin()
if run("git", "branch", "--show-current", show=False).stdout.strip() == BRANCH:
    print(f"  The twin is already on {BRANCH} with the commit. To start over: bash lab.sh l4 fail\n")
else:
    run("git", "switch", "-c", BRANCH, check=True)
    gi = TWIN / ".gitignore"
    if ".env" not in gi.read_text().split():
        print('    $ echo ".env" >> .gitignore')
        gi.write_text(gi.read_text().rstrip("\n") + "\n.env\n")
    run("git", "add", "app/", ".gitignore", "Dockerfile", ".dockerignore", check=True)
    run("git", "status", "--short", "--ignored")
    run("git", "commit", "-q", "-m", "feat: triage service with contract, timeout, JSON logs and a safe image", check=True)
    run("git", "show", "--stat", "--format=%h %s", "HEAD")
    print("""
  Staged by name: app/, .gitignore, Dockerfile, .dockerignore. .env shows as !! (ignored), so it can't be added
  by accident, and it isn't in the commit.
""")
print("  Next: bash lab.sh l4 check, then bash lab.sh l4 pass")
