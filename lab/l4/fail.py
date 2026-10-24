"""L4 · step 1: see it fail. A careless commit in the twin, then the starter image through the platform team's checks."""
from _common import BEFORE, ROOT, TWIN, chain, code, docker_done, ensure_l1_l3, have_docker, make_twin, run

chain(f"""  bash lab.sh l4 fail
    └─ python lab/l4/fail.py
         ├─ makes the twin: git clone of this lab folder into {TWIN}
         │    plus your current app/ and Dockerfile, plus a demo .env holding a fake key
         │    (your real repo is never touched: no branch, no commit, no push)
         ├─ A. Git: runs git status, then `git add -A`, in the twin
         └─ B. Docker: builds this folder's Dockerfile (in the twin) and inspects the image
              the way the platform team would: docker history, docker run, docker inspect
  Every command is printed as `$ ...` before its output.""")
ensure_l1_l3()
make_twin()

print("━━ A. Git: the careless commit ━━\n")
run("git", "branch", "--show-current")
print()
run("git", "status", "--short")
print("""
  The M lines are your L1-L3 work. `?? .env` is the demo secrets file, untracked. Now the habit that leaks it:
""")
run("git", "add", "-A")
run("git", "status", "--short")
print("""
WHAT WENT WRONG (A)
  You're on main: this would go straight to the customer's main branch, with no review.
  `A  .env`: git add -A staged the secrets file. One commit and one push later, the key is in the
  repo's history for good; deleting the file later doesn't remove it from history.
  .gitignore has no .env line, so nothing stopped it:
""")
run("cat", ".gitignore")
run("git", "reset", "-q", show=False)
print()

print("━━ B. Docker: it builds, so we're done? ━━\n")
if docker_done():
    print("  The Dockerfile fix is already applied, so there's nothing to see fail. To see it again: bash lab.sh reset l4")
elif have_docker():
    code("Dockerfile", "FROM python", "CMD [", "The starter Dockerfile", {
        "FROM python": "TODO 1: Docker Hub, full size, not pinned",
        "ENV SERVICE_API_KEY": "TODO 2: a key baked into the image",
        "COPY . .": "TODO 3: copies .env and .git too",
        "CMD [": "TODO 4, 5: runs as root; no HEALTHCHECK"})
    print("  Building it (the first time takes a minute or two: python:3.12 is about 1 GB):")
    if run("docker", "build", "-q", "-t", BEFORE, ".").returncode:
        raise SystemExit("  ✗ docker build failed. See the error above.")
    print("\n  The platform team's checks:")
    run("sh", "-c", f"docker history --no-trunc {BEFORE} | grep -o 'SERVICE_API_KEY=[^ ]*' | head -1")
    run("docker", "run", "--rm", "--entrypoint", "cat", BEFORE, "/app/.env")
    run("docker", "run", "--rm", "--entrypoint", "sh", BEFORE, "-c", "ls -d /app/.git")
    run("docker", "run", "--rm", "--entrypoint", "id", BEFORE, "-u")
    run("docker", "inspect", "-f", "{{.Config.Healthcheck}}", BEFORE)
    run("sh", "-c", f"docker image inspect -f '{{{{.Size}}}}' {BEFORE} | awk '{{printf \"%.0f MB\\n\", $1/1000000}}'")
    print("""
WHAT WENT WRONG (B)
  The image builds and would start, and the platform team would still refuse it:
  docker history  anyone with the image can read SERVICE_API_KEY
  /app/.env       COPY . . copied the secrets file in; /app/.git came too, with the whole history
  id -u = 0       the service runs as root
  <nil>           no health check, so the platform can't tell when it's stuck
  size            the full python:3.12 image, from Docker Hub (anonymous pulls are rate-limited)
""")
print("  Next: bash lab.sh l4 check")
