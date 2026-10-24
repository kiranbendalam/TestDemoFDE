"""L4 · steps 2 and 5: run the L4 checks (the same as `bash grade.sh l4`) in the twin, and explain each one."""
from _common import ROOT, TWIN, chain, ensure_l1_l3, grade_l4

WHY = [  # (words in grade.sh's line, what it means, which fix)
    ("feature branch", "work on a branch, never straight on main", "L4a.1"),
    ("on '", "work on a branch, never straight on main", "L4a.1"),
    ("in .gitignore", ".env is listed in .gitignore, so git won't offer it", "L4a.2"),
    ("not ignored", ".env is listed in .gitignore, so git won't offer it", "L4a.2"),
    ("tracked", ".env is not in any commit", "L4a.2"),
    ("ahead of", "at least one commit on the branch, ready for a pull request", "L4a.3"),
    ("pinned", "base image pinned to a patch version, slim", "L4b.1"),
    ("pin a slim", "base image pinned to a patch version, slim", "L4b.1"),
    ("base image", "base image from ECR Public, not Docker Hub", "L4b.1"),
    (".dockerignore", ".dockerignore keeps .env out of the build", "L4b.3"),
    ("builds", "the image builds", "—"),
    ("build failed", "the image builds", "—"),
    ("root", "the container runs as a non-root user", "L4b.4"),
    ("history", "no key readable in docker history", "L4b.2"),
    (".env is inside", "no .env file inside the image", "L4b.3"),
    ("no .env file", "no .env file inside the image", "L4b.3"),
    ("health", "the health check reports healthy", "L4b.5"),
]

chain(f"""  bash lab.sh l4 check
    └─ python lab/l4/check.py
         └─ bash grade.sh l4, run inside the twin ({TWIN})   (the same checks as the assignment)
              ├─ Git: git rev-parse (branch), git check-ignore / git ls-files (.env), git rev-list (commits ahead)
              └─ Docker: reads Dockerfile and .dockerignore, then docker build, docker history, docker run, docker inspect
  Open grade.sh (functions l4_git and l4_docker) to read each check.""")
ensure_l1_l3()
res = grade_l4()
ok = sum(m == "✅" for m, _ in res)
total = sum(m in "✅❌" for m, _ in res)
print(f"THE {total} CHECKS (grade.sh l4)\n")
for m, text in res:
    if m == "ℹ️":
        print(f"  ℹ️  {text}")
        continue
    what, need = next(((w, n) for k, w, n in WHY if k in text), (text, "—"))
    print(f"  {m} {what}\n       grade.sh says: {text}" + (f"   (needs {need})" if m == "❌" else ""))
print(f"\n  {ok} of {total} checks pass.\n")
if ok < total:
    print("WHERE THE GAP IS\n")
    print("  Git (in the twin): still on main, .env not ignored, nothing committed on a branch.")
    print("  Docker: the TODOs still open in Dockerfile:")
    for n, l in enumerate((ROOT / "Dockerfile").read_text().splitlines(), 1):
        if l.startswith("# TODO"):
            print(f"    Dockerfile:{n:<3} {l[2:]}")
    if not (ROOT / ".dockerignore").exists():
        print("    .dockerignore   (missing)")
    print("\n  Next: bash lab.sh l4 show, then bash lab.sh l4 apply")
else:
    print("  Next: bash lab.sh l4 pass")
