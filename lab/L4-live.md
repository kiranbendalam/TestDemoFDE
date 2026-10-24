# L4 · live · Ship: commit only what you mean, and an image the platform team accepts (about 8–10 minutes)

**The short version, for everyone.** You run two commands and read their output. You write no code.

**What you'll learn:**
- `git add -A` stages everything, including a secrets file. Work on a branch, ignore `.env`, stage by name.
- An image that builds can still be refused: a key in its history, `.env` inside, running as root, no health check.
- The fixed image: a slim pinned base, only the app copied, a normal user, a health check.

**In the deck:** the **Ship** topic ("Where a key leaks, and where it belongs", "What are Git, branches and pull
requests?", "Your Git workflow, step by step", "What is Docker?", "\"It builds, so we're done\"").

**Where:** the terminal of your **codespace** (step 2 needs Docker, which your codespace has). Move into the
primer folder:

```bash
cd primer/l4-ship-mini
```

(If you see "No such file or directory", run `cd /workspaces/<your-repo-name>` first, then try again.)

**Nothing here touches your own repo.** Step 1 uses a throwaway repo in a temporary folder; step 2 builds two
small images from `docker_context/` and deletes them at the end. The keys are fake.

---

## Step 1 · Git: careless staging vs deliberate staging (3 min)

```bash
bash run.sh git
```

**What runs:** `git_demo.py`. It makes a throwaway repo, switches to the branch `feat/triage-service`, then makes
one real code change (`app/models.py`), one secrets file (`.env`) and one scratch note (`notes.txt`). It runs
`git add -A` and shows `git status`; then it undoes that, adds `.env` to `.gitignore`, stages only `app/` and
`.gitignore`, and commits.

**What you'll see:**

```
2. After `git add -A`
A  .env                <- the secrets file is staged
M  app/models.py
A  notes.txt           <- and the scratch note

3. After adding `.env` to `.gitignore` and staging only `app/` + `.gitignore`
M  .gitignore
M  app/models.py
?? notes.txt           <- left out on purpose
!! .env                <- ignored: git won't offer it again

- The branch is now 1 commit(s) ahead of main, ready for a PR.
```

**Why it matters:** once a key is committed and pushed, it's in the history for good; deleting the file later
doesn't remove it. At a customer, you work on a branch and they merge through a reviewed pull request.

## Step 2 · Docker: it builds, so we're done? (5 min; the first build takes a minute or two)

```bash
bash run.sh docker
```

**What runs:** `docker_demo.py`. It builds `docker_context/Dockerfile.before`, then
`docker_context/Dockerfile.after` (with `.dockerignore.after` as the `.dockerignore`), and inspects each image the
way a platform team would: `docker history` (secrets), `docker run ... cat /app/.env`, `docker run ... id -u`, the
health status, the size. Open both Dockerfiles side by side:

| `Dockerfile.before` | `Dockerfile.after` | Why |
|---|---|---|
| `FROM python:3.12` | `FROM public.ecr.aws/docker/library/python:3.12.15-slim-bookworm` | slim and pinned to a patch version; ECR Public avoids Docker Hub's anonymous pull limits |
| `ENV LLM_API_KEY=demo-key-123` | (gone) | a key in the image is readable by anyone with the image; pass it at run time (`docker run -e`) |
| `COPY . .` | `COPY requirements.txt .` + `COPY app ./app`, and `.dockerignore` | only what the app needs: no `.env` |
| (runs as root) | `RUN useradd ... appuser` + `USER appuser` | not root |
| (no health check) | `HEALTHCHECK ... /healthz` | the platform can tell when the service is stuck |

**What you'll see:**

```
1. BEFORE image
  base image               python:3.12
  secret in history        yes
  .env inside image        LLM_API_KEY=demo-secret-123
  runs as uid              0
  healthcheck              none
  size                     about 1 GB or more

2. AFTER image
  base image               public.ecr.aws/docker/library/python:3.12.15-slim-bookworm
  secret in history        no
  .env inside image        (none)
  runs as uid              10001
  healthcheck              healthy
  size                     much smaller
```

**Why it matters:** both images build and start. Only the second one would pass a platform team's review. Your
exact sizes will differ a little.

---

## ✅ Done with live L4

```bash
cd ../..
```

Post **✅ L4** in the chat. Later, at your own pace: `lab/L4-deep-dive.md` does the same on the real service and
its real `Dockerfile`.

## If something goes wrong

| You see | Do this |
|---|---|
| `No such file or directory` | `cd /workspaces/<your-repo-name>`, then `cd primer/l4-ship-mini` |
| `DOCKER: not available here` | You're not in a codespace (or Docker isn't running): Ctrl/Cmd+Shift+P → **Codespaces: Full Rebuild Container** |
| `toomanyrequests` while building the BEFORE image | Docker Hub's anonymous pull limit, which is exactly why the AFTER image uses ECR Public. Watch the trainer's screen |
| `CalledProcessError` from `docker build` | Run `bash check_setup.sh` from the lab folder and post the ❌ line in the chat |
