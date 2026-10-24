# L3 deep dive (after the session) · Observability: one JSON line per request, masked

**After the session, at your own pace, about 15 minutes, after the L3 primer** (`primer/l3-observability-mini/`). You write no code: every
step is one command, and every step prints how it runs and the exact code lines involved. It works on the real
service: **`app/logging_setup.py`** and **`app/main.py`**.

**What you'll learn:** why a `print()` line fails an audit; how one middleware writes one JSON line per request
with a request ID; how masking the whole line keeps account numbers out; and what a log platform can then do.

**In the deck:** the **Ship** topic ("What is structured logging?", "One JSON line per request", "Logs, metrics,
traces").

**Where:** the terminal of your codespace, in the lab folder (`cd /workspaces/<your-repo-name>`).

**L3 builds on L1 and L2.** If they aren't applied yet, the first L3 command applies them for you and says so.
**No real LLM is called:** `StubLLM` answers offline.

---

## Step 1 · See it fail (2 min)

```bash
bash lab.sh l3 fail
```

**How it runs:** `lab/l3/fail.py` (A) runs `triage_prototype.py` and shows its first two output lines, plus the
line that prints them (`triage_prototype.py`, line 33). (B) It sends one `POST /triage` to the real
`app/main.py` and counts the JSON log lines written, then shows the open L3 TODOs.

**What you'll see:** (A) `processing {… 'Account EB-4418203391.'}`: the full account number. (B)
`JSON log lines written: 0`, and the TODOs: `app/main.py` line 31 (no middleware), and `app/logging_setup.py`
lines 20–23 (`mask`) and 26–30 (`JsonFormatter`).

**Why it matters:** the CISO's question, "which model decided C-013, and was the account number kept out of the
logs?", has no answer yet.

## Step 2 · Run the checks (2 min)

```bash
bash lab.sh l3 check
```

**How it runs:** `lab/l3/check.py` runs `pytest -v tests/test_l3.py`, the same tests as `bash grade.sh l3`. They
call `mask()` and `setup_logging()` from `app/logging_setup.py` (logging into a buffer), send requests to
`app/main.py`, and read back the JSON lines. Open `tests/test_l3.py` to read them.

**What you'll see:** 4 checks in plain sentences, **0 of 4** pass, then the open TODO lines in both files.

## Step 3 · Read the fix (3 min)

```bash
bash lab.sh l3 show
```

**How it runs:** `lab/l3/show.py` prints the finished code from **`lab/l3/logging_done.py`** and
**`lab/l3/main_done.py`**, with real line numbers and notes.

| Where | Line | What it does |
|---|---|---|
| `logging_setup.py` | `ACCOUNT_RE`, `FIELDS` | What we mask (`EB-` + 10 digits), and the audit fields a line may carry |
| `logging_setup.py` | `return ACCOUNT_RE.sub(...)` | **L3.1** keep the last four digits: `EB-******3391` |
| `logging_setup.py` | `JsonFormatter.format` → `return mask(json.dumps(entry))` | **L3.2** one JSON line; mask the **whole** line, so no field can leak |
| `main.py` | `setup_logging()` | Turn it on, once: JSON lines go to stdout |
| `main.py` | `@app.middleware("http")` … `logger.info("request", extra={…})` | **L3.3** wraps every request: request ID (the caller's or a new one), echoed in the response; route, status, latency |
| `main.py` | `request.state.log = {"model", "prompt_version", "outcome", …}` | **L3.4** what only `triage()` knows |

## Step 4 · Apply the fix (1 min)

```bash
bash lab.sh l3 apply
```

**How it runs:** `lab/l3/apply.py` checks L1 and L2, copies `logging_done.py` over **`app/logging_setup.py`** and
`main_done.py` over **`app/main.py`**, then prints, for each file, every L3 TODO line (`-`) and the code that
replaced it (`+`), including the new `setup_logging()` call.

## Step 5 · See it pass (3 min)

```bash
bash lab.sh l3 check
bash lab.sh l3 pass
```

**How it runs:** `check` is now **4 of 4**, with the lines that made them pass. `pass` runs `lab/l3/pass.py`: it
sends `POST /triage` for C-013 (account `EB-9081726354`) with header `X-Request-ID: req-demo-001`, and
`GET /healthz` with no ID. Then it prints the JSON lines the logger wrote.

**What you'll see (the /triage line):**

```json
{"ts": "…", "level": "INFO", "msg": "request", "request_id": "req-demo-001", "route": "/triage",
 "status": 200, "latency_ms": 0.9, "model": "stub-triage-1", "prompt_version": "triage-v1",
 "outcome": "human_review", "complaint_excerpt": "Unauthorised UPI debit. Account EB-******6354."}
```

`/healthz` gets a **generated** request ID, and the line ends `Full account numbers in the logs: 0`.

## Step 6 · Try it: search, count, audit (2 min)

```bash
bash lab.sh l3 try
```

**How it runs:** `lab/l3/try_.py` sends every complaint in `data/complaints.jsonl` (20) to `app/main.py`, each
with its own `X-Request-ID` (`req-C-001` …). Then it queries the JSON lines the way a log platform would.

**What you'll see:**

```
SEARCH  outcome = human_review      req-C-013, req-C-014, req-C-015
COUNT   by outcome                  routed 17 · human_review 3
AUDIT   req-C-013                   model=stub-triage-1  prompt_version=triage-v1  outcome=human_review
LEAK CHECK                          full account numbers in all 20 lines: 0
```

**Why it matters:** a `print()` line can't answer any of these. Named fields can.

## Step 7 · Watch the lines live (2 min)

```bash
bash lab.sh l3 serve
```

**How it runs:** `uvicorn app.main:app --port 8000`. `app/main.py` calls `setup_logging()`, so each request writes
one JSON line to **this terminal**. Open **Ports** → **8000** → **globe** → `/docs`, send a few requests, and
watch the terminal. **Ctrl+C** to stop.

You'll also see uvicorn's own `INFO: … "POST /triage HTTP/1.1" 200` lines. Those come from uvicorn's
logger, which our mask doesn't cover: one of the known limits for your handover note.

---

## ✅ Done with the L3 deep dive

**Later, the write-it-yourself assignment:** `bash lab.sh reset l3` puts the L3 starters back in
`app/logging_setup.py` and `app/main.py`. Write `mask()`, `JsonFormatter`, the middleware and
`request.state.log` yourself, and check with `bash grade.sh l3`.

| You see | Do this |
|---|---|
| `L3 isn't applied yet` | `bash lab.sh l3 apply` |
| `address already in use` (step 7) | Ctrl+C the other server, or `pkill -f uvicorn` |
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
