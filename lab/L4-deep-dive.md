# L4 deep dive (after the session) · Ship: a reviewable commit and an image the platform team accepts

**After the session, at your own pace, about 15 minutes, after the L4 primer** (`primer/l4-ship-mini/`). You write no code: every step is
one command, and every step prints how it runs and every `git` and `docker` command, as `$ ...`, before its
output.

**What you'll learn:** how `git add -A` leaks a secrets file, and the deliberate commit that doesn't; why an image
that builds can still be refused; the five Dockerfile fixes; and where a secret belongs (at run time, not in the
image).

**In the deck:** the **Ship** topic ("Where a key leaks, and where it belongs", "What are Git, branches and pull
requests?", "Git in the customer's repo", "Your Git workflow, step by step", "What is Docker?", "\"It builds, so
we're done\"").

**Where:** the terminal of your **codespace** (Docker is needed for the Docker half), in the lab folder
(`cd /workspaces/<your-repo-name>`).

**Two halves, two places:**
- **Git runs in a twin.** Step 1 clones your lab folder into a throwaway folder in `/tmp` (`fde-s03-l4-twin`), adds
  your current files and a demo `.env` with a fake key. Every branch and commit happens there. Your real repo gets
  no branch, no commit and no push. Doing it for real is the assignment.
- **Docker fixes your real `Dockerfile`** (and adds `.dockerignore`), like L1–L3 fix your real files. The images
  are built from the twin, so the demo `.env` is there to prove it stays out.

**L4 ships the whole service.** If L1–L3 aren't applied yet, the first L4 command applies them for you and says
so. **No real LLM is called**, and **no port is published**: step 6 talks to the container from the inside.

---

## Step 1 · See it fail (4 min; the first build takes a minute or two)

```bash
bash lab.sh l4 fail
```

**How it runs:** `lab/l4/fail.py` makes the twin. (A) In the twin: `git status`, then `git add -A`, then
`git status` again. (B) It prints your `Dockerfile` with the five TODOs marked, builds it as `s03-before`, and
inspects the image the way the platform team would.

**What you'll see:**

```
A.  $ git branch --show-current     main
    $ git add -A
    $ git status --short            A  .env        <- the secrets file is staged
                                    M  app/...
B.  $ docker history ... | grep     SERVICE_API_KEY=demo-key-123
    $ docker run ... cat /app/.env  LLM_API_KEY=sk-demo-not-a-real-key
    $ docker run ... ls -d /app/.git   /app/.git
    $ docker run ... id -u          0
    $ docker inspect ... Healthcheck   <nil>
```

**Why it matters:** each of these is a real reason a platform team or a CISO says no: a key in the image, a
secrets file in the repo, root, and no way to tell the service is stuck.

## Step 2 · Run the checks (2 min)

```bash
bash lab.sh l4 check
```

**How it runs:** `lab/l4/check.py` runs **`bash grade.sh l4` inside the twin**, the same checks as the
assignment, and explains each line. Open `grade.sh` (functions `l4_git` and `l4_docker`) to read them.

**What you'll see:** 12 checks (4 Git, 8 Docker). Before the fix, only ".env is not in any commit" and "the image
builds" pass. Then the TODO lines still open in `Dockerfile`, and `.dockerignore (missing)`.

## Step 3 · Read the fix (3 min)

```bash
bash lab.sh l4 show
```

**How it runs:** `lab/l4/show.py` prints the Git commands that step 4 runs, and the finished **`lab/l4/Dockerfile_done`**
and **`lab/l4/dockerignore_done`**, with real line numbers and notes.

| Fix | What changes | Why |
|---|---|---|
| **L4a.1** | `git switch -c feat/triage-service` | `main` only changes through a reviewed pull request |
| **L4a.2** | `.env` added to `.gitignore` | git can't offer the secrets file any more |
| **L4a.3** | `git add app/ .gitignore Dockerfile .dockerignore`, then commit | stage by name; never `git add -A` |
| **L4b.1** | `FROM public.ecr.aws/docker/library/python:3.12.15-slim-bookworm` | slim, pinned to a patch version, not Docker Hub (anonymous pulls are rate-limited) |
| **L4b.2** | the `ENV SERVICE_API_KEY=...` line is gone | a key in the image is readable by anyone with the image |
| **L4b.3** | `COPY requirements.txt .` + `COPY app ./app`, and `.dockerignore` | only what the app needs: no `.env`, no `.git` |
| **L4b.4** | `useradd ... appuser` + `USER appuser` | not root |
| **L4b.5** | `HEALTHCHECK --interval=5s ... /healthz` | the platform can tell when it's stuck (slim has no curl, so it uses python) |

## Step 4 · Apply the fix (1 min)

```bash
bash lab.sh l4 apply
```

**How it runs:** `lab/l4/apply.py` copies `Dockerfile_done` over your **`Dockerfile`** and prints the diff, writes
**`.dockerignore`**, then, **in the twin**: `git switch -c feat/triage-service`, adds `.env` to `.gitignore`, stages
the four paths by name, shows `git status --short --ignored` and commits.

**What you'll see:** the Dockerfile diff (the five TODOs out, the fixes in), and in the twin `!! .env` (ignored),
then `git show --stat`: six files in the commit, and `.env` isn't one of them.

## Step 5 · See it pass (3 min)

```bash
bash lab.sh l4 check
bash lab.sh l4 pass
```

**How it runs:** `check` is now **12 of 12**. `pass` runs `lab/l4/pass.py`: in the twin, `git log`,
`git check-ignore -v .env` and `git ls-files .env`; then it builds the fixed image as `s03-triage` (from the twin,
which still has the demo `.env`) and repeats step 1's checks.

**What you'll see:**

```
A.  feat/triage-service · 1 commit ahead · .gitignore:5:.env  .env · .env in no commit
B.  SERVICE_API_KEY lines in the history: 0
    ls -a /app        app  requirements.txt           <- no .env, no .git
    id                uid=10001(appuser)
    health            healthy
    size              s03-before: about 1 GB  ·  s03-triage: a fraction of that
```

## Step 6 · Try it: the whole service, in the box (3 min)

```bash
bash lab.sh l4 try
```

**How it runs:** `lab/l4/try_.py` shows `git diff --stat` in the twin (what a reviewer opens first). Then
`docker run -d -e SERVICE_API_KEY=demo-runtime-key s03-triage`: the secret goes in **at run time**. It checks where
the secret is (`docker exec ... printenv`) and isn't (`docker history`), sends `POST /triage` for C-013 from inside
the container (`docker exec ... python`), and reads the service's log line with `docker logs`.

**What you'll see:**

```
printenv SERVICE_API_KEY      demo-runtime-key       <- in the running container
docker history | grep -c      0                      <- not in the image
POST /triage C-013            {"team": "human_review", ...}
docker logs | grep req-docker-001
  {"request_id": "req-docker-001", ..., "outcome": "human_review", "complaint_excerpt": "... EB-******6354."}
```

**Why it matters:** this is L1 (contract), L2 (timeout) and L3 (masked JSON logs), running in an image the
platform team accepts. That's the handover.

---

## ✅ Done with the L4 deep dive

**Later, the write-it-yourself assignment:** `bash lab.sh reset l4` puts the starter `Dockerfile` back, removes
`.dockerignore` and the twin. Then do L4a and L4b **for real in your own repo**, following `ASSIGNMENT.md`: a
branch, `.env` in `.gitignore`, a deliberate commit, a push and a pull request; then the five Dockerfile fixes.
Check with `bash grade.sh l4`, then write `HANDOVER.md`.

| You see | Do this |
|---|---|
| `Docker isn't available here` | Use your codespace. If you're in one: Ctrl/Cmd+Shift+P → **Codespaces: Full Rebuild Container** |
| `L4 isn't applied yet` | `bash lab.sh l4 apply` |
| `this lab folder isn't a git repo` | Open your own copy of the lab repo in a codespace |
| `toomanyrequests` during step 1's build | Docker Hub's anonymous pull limit: the lesson of L4b.1. Skip to step 3; the fixed image uses ECR Public |
| `docker build failed` | Read the error above it; run `bash check_setup.sh` |
