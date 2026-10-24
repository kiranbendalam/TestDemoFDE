"""L4 · step 5: see it pass. The commit a reviewer gets, and the image through the same platform checks as step 1."""
import subprocess
import sys
import time

from _common import AFTER, BEFORE, BRANCH, base, TWIN, chain, docker_done, ensure_l1_l3, have_docker, run, twin

chain(f"""  bash lab.sh l4 pass
    └─ python lab/l4/pass.py
         ├─ A. Git, in the twin ({TWIN}): git log, git check-ignore, git ls-files
         └─ B. Docker: builds the fixed Dockerfile (in the twin, which still has the demo .env)
              and repeats step 1's checks: docker history, docker run, docker inspect
  Every command is printed as `$ ...` before its output.""")
ensure_l1_l3()
twin()
if not docker_done() or run("git", "branch", "--show-current", show=False).stdout.strip() != BRANCH:
    print("  L4 isn't applied yet. Run: bash lab.sh l4 apply"); sys.exit(1)

print("━━ A. Git: what the reviewer gets ━━\n")
run("git", "branch", "--show-current")
run("git", "log", "--oneline", f"{base()}..HEAD")
run("git", "check-ignore", "-v", ".env")
if not run("git", "ls-files", ".env").stdout.strip():
    print("      (no output: .env is in no commit)")
print("""
  On a branch, one commit ahead, .env ignored (by .gitignore line shown) and in 0 commits.
""")

print("━━ B. Docker: the same checks as step 1 ━━\n")
if have_docker():
    print("  Building the fixed image (the slim base is much smaller, so this is quicker):")
    if run("docker", "build", "-q", "-t", AFTER, ".").returncode:
        sys.exit("  ✗ docker build failed. See the error above.")
    print("\n  The platform team's checks:")
    run("sh", "-c", f"docker history --no-trunc {AFTER} | grep -c 'SERVICE_API_KEY' || true")
    run("docker", "run", "--rm", "--entrypoint", "sh", AFTER, "-c", "ls -a /app")
    run("docker", "run", "--rm", "--entrypoint", "id", AFTER)
    cid = run("docker", "run", "-d", AFTER).stdout.strip()
    status = "starting"
    print("    (waiting for the health check: every 5 s, after a 5 s start period)")
    for _ in range(40):
        status = subprocess.run(["docker", "inspect", "-f", "{{.State.Health.Status}}", cid],
                                capture_output=True, text=True).stdout.strip()
        if status == "healthy":
            break
        time.sleep(1)
    run("docker", "inspect", "-f", "{{.State.Health.Status}}", cid)
    run("docker", "rm", "-f", cid, show=False)
    for tag in (BEFORE, AFTER):
        if subprocess.run(["docker", "image", "inspect", tag], capture_output=True).returncode == 0:
            run("sh", "-c", f"docker image inspect -f '{tag}: {{{{.Size}}}}' {tag} | awk '{{printf \"%s %.0f MB\\n\", $1, $2/1000000}}'")
    print("""
WHAT TO NOTICE
  0 lines with SERVICE_API_KEY in the history. /app holds only app/ and requirements.txt: no .env, no .git,
  even though the twin has both (.dockerignore and the narrow COPY lines). uid=10001(appuser), not 0.
  The health check says healthy: it called /healthz from inside the container. And the image is far smaller.""")
print("\n  Next: bash lab.sh l4 try")
