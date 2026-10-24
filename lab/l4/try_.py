"""L4 · step 6: try it. The whole service (L1-L3) in the shipped image: a secret at run time, one request, its log line."""
import subprocess
import sys
import time

from _common import AFTER, BRANCH, TWIN, base, chain, docker_done, ensure_l1_l3, have_docker, run, twin

REQ = ("import json, urllib.request as u; "
       "r = u.Request('http://127.0.0.1:8000/triage', method='POST', "
       "data=json.dumps({'id': 'C-013', 'text': 'Unauthorised UPI debit. Account EB-9081726354.'}).encode(), "
       "headers={'Content-Type': 'application/json', 'X-Request-ID': 'req-docker-001'}); "
       "print(u.urlopen(r, timeout=5).read().decode())")

chain(f"""  bash lab.sh l4 try
    └─ python lab/l4/try_.py
         ├─ A. Git, in the twin ({TWIN}): git diff --stat, the view a reviewer opens first
         └─ B. Docker: docker run -d -e SERVICE_API_KEY=... {AFTER}   (the secret goes in at run time)
              ├─ docker exec ... printenv / docker history   (where the secret is, and isn't)
              ├─ docker exec ... python -c "POST /triage"   (from inside the container: no port is published)
              └─ docker logs   (the L3 JSON line, written by the service in the container)""")
ensure_l1_l3()
twin()
if not docker_done() or run("git", "branch", "--show-current", show=False).stdout.strip() != BRANCH:
    print("  L4 isn't applied yet. Run: bash lab.sh l4 apply"); sys.exit(1)

print("━━ A. Git: what the pull request shows ━━\n")
run("git", "diff", "--stat", f"{base()}...HEAD")
print("""
  This is what the reviewer sees first: which files changed and how much. No .env. The PR template
  (.github/pull_request_template.md) then asks: what this changes, how you tested it, risk and rollback.
  For real, in your own repo: git push -u origin """ + BRANCH + """, then open the PR on GitHub.
""")

print("━━ B. Docker: the shipped service, end to end ━━\n")
if have_docker():
    if subprocess.run(["docker", "image", "inspect", AFTER], capture_output=True).returncode:
        print("  Building the image first:")
        run("docker", "build", "-q", "-t", AFTER, ".", check=True)
    cid = run("docker", "run", "-d", "-e", "FORCE_OFFLINE=1", "-e", "SERVICE_API_KEY=demo-runtime-key", AFTER, check=True).stdout.strip()
    try:
        for _ in range(40):
            st = subprocess.run(["docker", "inspect", "-f", "{{.State.Health.Status}}", cid], capture_output=True, text=True).stdout.strip()
            if st == "healthy":
                break
            time.sleep(1)
        print("\n  1. Where the secret is: in the running container, not in the image")
        run("docker", "exec", cid, "printenv", "SERVICE_API_KEY")
        run("sh", "-c", f"docker history --no-trunc {AFTER} | grep -c SERVICE_API_KEY || true")
        print("\n  2. One request, sent from inside the container (FORCE_OFFLINE=1: the stub model, no real LLM)")
        print("    $ docker exec <container> python -c \"POST /triage  C-013, X-Request-ID: req-docker-001\"")
        r = subprocess.run(["docker", "exec", cid, "python", "-c", REQ], capture_output=True, text=True)
        print("      " + (r.stdout or r.stderr).strip())
        print("\n  3. The service's log line, as the platform's log collector would read it")
        print("    $ docker logs <container> | grep req-docker-001")
        logs = subprocess.run(["docker", "logs", cid], capture_output=True, text=True)
        hit = [l for l in (logs.stdout + logs.stderr).splitlines() if "req-docker-001" in l]
        print("      " + (hit[0] if hit else "(no line found: is L3 applied? bash lab.sh l3 check)"))
    finally:
        run("docker", "rm", "-f", cid, show=False)
    print("""
WHAT TO NOTICE
  The key is in the running container (docker run -e) and in 0 image history lines: rotate it without a rebuild.
  C-013 still goes to human_review (L1), within the timeout (L2), and the container wrote one JSON line with
  request_id req-docker-001 and EB-******6354, masked (L3). Same service, now in a box the platform team runs.""")
print("""
  Done. The assignment does all of L4 for real in your repo: bash lab.sh reset l4, then follow L4a and L4b in
  ASSIGNMENT.md, and check with bash grade.sh l4.""")
