"""L4 · step 3: read the fix. The Git commands, the finished Dockerfile and the .dockerignore, with notes."""
from _common import BRANCH, chain, code

chain("""  bash lab.sh l4 show
    └─ python lab/l4/show.py
         ├─ prints the Git commands that `bash lab.sh l4 apply` will run in the twin, with notes
         └─ prints lab/l4/Dockerfile_done and lab/l4/dockerignore_done (the fix), with real line numbers""")

print(f"""━━ A. Git: the deliberate commit (run in the twin by step 4) ━━

  L4a.1  git switch -c {BRANCH}                     ← a branch: main only changes through a reviewed PR
  L4a.2  echo ".env" >> .gitignore                          ← git now ignores the secrets file
         git status --short --ignored                       ← check: .env shows as !! (ignored), not ??
  L4a.3  git add app/ .gitignore Dockerfile .dockerignore   ← name what you stage; never `git add -A`
         git commit -m "feat: ..."                          ← one commit, one clear message
  Then, for real (not in the twin): git push -u origin {BRANCH}, and open a pull request.
""")

print("━━ B. Docker: an image the platform team accepts ━━\n")
code("lab/l4/Dockerfile_done", "FROM ", 'CMD ["uvicorn"', "The finished Dockerfile", {
    "FROM ": "L4b.1 ECR Public mirror, slim, pinned to 3.12.15",
    "ENV PYTHON": "not a secret: Python settings only",
    "COPY requirements.txt": "L4b.3 copy the dependency list first ...",
    "pip install": "... so this layer is cached when only code changes",
    "COPY app": "L4b.3 only the app; no .env, no .git",
    "useradd": "L4b.4 a normal user ...",
    "USER appuser": "... and switch to it: not root",
    "HEALTHCHECK": "L4b.5 check every 5 s ...",
    "CMD python -c": "... by calling /healthz (slim has no curl)",
    'CMD ["uvicorn"': "0.0.0.0 inside the container; you choose the published port"})
print("  L4b.2: the ENV SERVICE_API_KEY line is gone. A secret goes in at run time: docker run -e LLM_API_KEY=...\n")
code("lab/l4/dockerignore_done", ".env", ".venv/", "The .dockerignore (what the build never sees)", {
    ".env": "the secrets file",
    ".git": "the repo history",
})
print("  Next: bash lab.sh l4 apply")
