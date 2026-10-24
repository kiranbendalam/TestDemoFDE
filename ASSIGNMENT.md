# Assignment: write it yourself (L1–L4 and the handover)

In the session you **watched** each rung work (the live lab), and the deep dives showed the finished code line by
line. Now you write it. Each rung starts from its TODO version and is checked by `grade.sh`.

**Start each rung from its TODOs:** `bash lab.sh reset l1` (or `l2`, `l3`, `l4`). This puts the starter files back
if you applied the fix during a deep dive. Do the rungs in order: each one builds on the one before.

**Check as you go:** `bash grade.sh l1` … `l4`, `bash grade.sh handover`, and finally `bash grade.sh all`. A ❌ line
tells you which TODO is still open, with its file and line.

Work in your codespace. Colab can do L1–L3; L4 needs a codespace.

## L1 Contract (about 15 min)

**Want to see it working first?** The L1 deep dive (`lab/L1-deep-dive.md`) runs the finished version step by step.

`bash lab.sh reset l1`, then fill in the TODOs in **`app/models.py`**:

1. **L1.1 `Complaint`**: `id` and `text` as `str` with `Field(min_length=1, max_length=...)` limits, and `channel` as a
   `Literal` of `"email"`, `"chat"`, `"branch"`, `"phone"` (default `"email"`).
2. **L1.2 `TriageResult`**: `model_config = ConfigDict(extra="forbid")`, then `category: Category`, `priority: int`
   between 1 and 4 (`Field(ge=1, le=4)`), `team: Team`, `summary: str` (max 200), `needs_human: bool = False`.
3. **L1.3 `parse_triage()`**: `return TriageResult.model_validate_json(raw)` inside `try`; on `ValidationError`,
   return `human_review(...)` with the reason. Never crash, never guess.

Check: `bash grade.sh l1`.

## L2 Service (about 15 min)

**Want to see it working first?** The L2 deep dive (`lab/L2-deep-dive.md`) runs the finished version step by step.

`bash lab.sh reset l2`, then fill in the TODOs in **`app/main.py`**:

1. **L2.1 `/healthz`**: return `{"status": "ok"}`.
2. **L2.2 `/triage`**: follow the pattern in the TODO comment: `async with asyncio.timeout(TIMEOUT_S):` around
   `raw = await llm.complete(...)`, then `parse_triage(raw)`; catch `TimeoutError` **outside** the `async with` and
   return `human_review("model timed out")`. Remove the `raise`.

Check: `bash grade.sh l2`. Then run it: `bash lab.sh l2 serve` and try `/docs` (Ports → 8000 → globe).

## L3 Observability (about 20 min)

**Want to see it working first?** The L3 deep dive (`lab/L3-deep-dive.md`) runs the finished version step by step.

**Why:** the CISO's rule is that every decision has an audit trail, and no account numbers reach the logs.
A `print()` line can't be searched, joined or trusted. One JSON line per request can.

**See it fail first (1 min):** run `python triage_prototype.py | head -2` from the lab folder. Look at the first
line: the full account number, no request ID, nothing a machine can search. At the end of L3, compare it with
your own JSON line.

1. **L3.1 `mask()`** in `app/logging_setup.py`: replace each `EB-` + 10 digits with `EB-******` + the last 4.
   Use `ACCOUNT_RE.sub(...)`.
2. **L3.2 `JsonFormatter.format()`**: build a dict with `ts` (UTC, ISO 8601), `level`, `msg`, plus every
   name in `FIELDS` that's present on the record (`hasattr(record, name)`). Return `mask(json.dumps(entry))`.
   Masking the whole line means no field can leak.
3. **L3.3 middleware** in `app/main.py`, under the TODO. Add `@app.middleware("http")` with an async function that:
   - takes the request ID from the `X-Request-ID` header, or makes one (`uuid.uuid4().hex[:12]`)
   - sets `request.state.log = {}`, notes the start time, and calls `response = await call_next(request)`
   - adds `X-Request-ID` to the response headers
   - logs one line: `logger.info("request", extra={"request_id": ..., "route": request.url.path,
     "status": response.status_code, "latency_ms": ..., **request.state.log})`
4. **L3.4** in `triage()`: before returning, set `request.state.log` to `model` (`llm.model`),
   `prompt_version` (`PROMPT_VERSION`), `outcome` (`"human_review"` or `"routed"`) and
   `complaint_excerpt` (the first 80 characters of the text).
5. Call `setup_logging()` once, near the top of `app/main.py` (after `llm = get_llm()`).

Check: `bash grade.sh l3`. Then run the service and watch the terminal while you call `/triage` from `/docs`.

## L4a Git (15 min)

**Want to see it working first?** The L4 deep dive (`lab/L4-deep-dive.md`) runs the finished version step by step. Do L4 in a codespace (Colab has no Docker).

**Why:** at a customer you work in *their* repo, under *their* review rules. Small branches and clear PRs
are how you earn merge rights.

```bash
git switch -c feat/triage-service
cp .env.example .env            # local settings; must never be committed
echo ".env" >> .gitignore       # now git ignores it
git status                      # .env must NOT be listed
git add app/ .gitignore         # stage deliberately: never `git add -A` with untracked files around
git commit -m "feat: triage service with contract, timeout and JSON logs"
git push -u origin feat/triage-service
```

Then open a pull request on GitHub (into your own copy's `main`). Fill in the template.
Check: `bash grade.sh l4` (the Git part).

## L4b Docker (15 min)

**Why:** the platform team runs containers, not scripts. They'll check the base image, the user, secrets and health.

**See it fail first (2 min):** build the starter Dockerfile as it is, and look at it the way the platform team will:

```bash
docker build -t s03-before .
docker history --no-trunc s03-before | grep SERVICE_API_KEY   # the key is readable in the image
docker run --rm s03-before id -u                              # 0 means it runs as root
```

Fix the five TODOs in `Dockerfile`:

1. `FROM public.ecr.aws/docker/library/python:3.12.15-slim-bookworm` (pinned to a patch version, slim, and mirrored on
   ECR Public, which avoids Docker Hub's anonymous limit of 100 pulls per 6 hours)
2. Delete the `ENV SERVICE_API_KEY=...` line. Secrets go in at run time: `docker run -e LLM_API_KEY=...`
3. Copy only what's needed: `COPY requirements.txt .`, `RUN pip install --no-cache-dir -r requirements.txt`,
   `COPY app ./app`. Create `.dockerignore` with at least `.env`, `.git`, `__pycache__/`
4. `RUN useradd --create-home --uid 10001 appuser` then `USER appuser`
5. `HEALTHCHECK --interval=5s --timeout=3s --start-period=5s CMD python -c "import urllib.request as u; u.urlopen('http://127.0.0.1:8000/healthz', timeout=2)"`
   (without `--interval`, Docker waits 30 s before the first check)

```bash
docker build -t s03-triage .
docker run --rm -p 8000:8000 s03-triage          # in another terminal: curl localhost:8000/healthz
docker history --no-trunc s03-triage | head      # no keys in here
docker image ls s03-triage                       # note the size: the full python:3.12 image is several times larger
```

Check: `bash grade.sh l4`.

## Handover (10 min)

Fill in `HANDOVER.md`: half a page for the Sr. Platform Engineer. Then:

```bash
bash grade.sh all
git add Dockerfile .dockerignore HANDOVER.md && git commit -m "docs: handover note" && git push
```

Clean up: `docker system prune -f`, stop your codespace, and delete it once you've finished.
