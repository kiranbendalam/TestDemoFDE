# L3 · live · Observability: one safe, searchable log line per request (about 8 minutes)

**The short version, for everyone.** You run three commands and read their output. You write no code.

**What you'll learn:**
- A `print()` line leaks account numbers, and nobody can search it or join it to a request.
- Mask before you store: keep the last four digits, and mask the **whole** line.
- One JSON line per request, with a request ID and the audit fields, answers the CISO's question: "which model
  decided C-013, and were the account numbers kept out of the logs?"

**In the deck:** the **Ship** topic ("What is structured logging?", "One JSON line per request", "Logs, metrics,
traces: three questions").

**Where:** the terminal of your codespace. Move into the primer folder:

```bash
cd primer/l3-observability-mini
```

(If you see "No such file or directory", run `cd /workspaces/<your-repo-name>` first, then try again.)

**No real LLM or server is used.** `events.py` holds two fixed sample requests (C-001 and C-013) and their
decisions, so everyone sees the same output.

---

## Step 1 · Before: plain print() logs (2 min)

```bash
bash run.sh before
```

**What runs:** `before.py`. It logs the two requests the way the prototype does: `print()` the complaint, then
`print()` the result.

**What you'll see:**

```
CASE: good route with caller request ID
  processing {'id': 'C-001', 'text': 'Charged twice. Account EB-4418203391.'}
  model=stub-triage-1 outcome=routed latency_ms=142
```

**Why it matters:** the full account number is in the log. One request is spread over two lines with no request
ID, so you can't follow it across systems, and a machine can't reliably pick out the route, status or outcome.

## Step 2 · Masking (2 min)

```bash
bash run.sh mask
```

**What runs:** `mask_demo.py`. It calls `mask()` from **`audit.py`**: a regular expression (`ACCOUNT_RE`, `EB-` and
10 digits) replaced by `EB-******` plus the last four digits. It masks a plain sentence, then a whole JSON line.

**What you'll see:**

```
plain text after  : Charged twice. Account EB-******3391.
JSON line after   : {"msg": "request", "complaint_excerpt": "Unauthorised UPI debit. Account EB-******6354."}
```

**Why it matters:** the last four digits are enough to match a case, and not enough to misuse. Masking the whole
line is safer than protecting one field at a time: a new field can't leak by accident.

## Step 3 · After: one JSON audit line per request (3 min)

```bash
bash run.sh after
```

**What runs:** `after.py`. For each request it calls `build_audit_line()` from **`audit.py`**: take the caller's
`X-Request-ID` or generate one, build one dict with the audit fields, `json.dumps` it, then mask the whole line.
Open `audit.py` beside the terminal:

| In `audit.py` | What it does |
|---|---|
| `ACCOUNT_RE` + `mask()` | Step 2: hide all but the last four digits |
| `incoming_request_id or uuid.uuid4().hex[:12]` | Echo the caller's ID, or make one |
| `entry = {"ts": ..., "request_id": ..., "route": ..., "status": ..., "model": ..., "prompt_version": ..., "outcome": ...}` | The audit fields, named |
| `mask(json.dumps(entry))` | One line, masked as a whole |

**What you'll see** (shortened):

```
CASE: good route with caller request ID
  caller X-Request-ID : req-abc123
  response header     : req-abc123
  one JSON line       : {"ts": "…", "level": "INFO", "msg": "request", "request_id": "req-abc123", "route": "/triage",
                         "status": 200, "latency_ms": 142, "model": "stub-triage-1", "prompt_version": "triage-v1",
                         "outcome": "routed", "complaint_excerpt": "Charged twice. Account EB-******3391."}

CASE: human review with generated request ID
  caller X-Request-ID : (none)
  response header     : 317fabd214ef          <- generated: yours will differ
  ...                   "outcome": "human_review", "complaint_excerpt": "… EB-******6354."
```

**Why it matters:** 2 requests, 2 lines. A log platform can now filter by `request_id`, `outcome` or `model`
without guessing, and the full account number never reaches the stored line. The `ts` and the generated ID
differ on every run; everything else is the same for everyone.

---

## ✅ Done with live L3

```bash
cd ../..
```

Post **✅ L3** in the chat. Later, at your own pace: `lab/L3-deep-dive.md` does the same on the real service.

## If something goes wrong

| You see | Do this |
|---|---|
| `No such file or directory` | `cd /workspaces/<your-repo-name>`, then `cd primer/l3-observability-mini` |
| `usage: bash run.sh before \| mask \| after \| all` | Check the spelling: `before`, `mask` or `after` |
| A different request ID or `ts` from the one shown here | Expected: they're generated on each run |
