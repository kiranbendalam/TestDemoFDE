# L2 deep dive (after the session) · Service: the real FastAPI endpoint, async and with a timeout

**After the session, at your own pace, about 15 minutes, after the live L2** (`lab/L2-live.md`, the short primer). You write no code:
every step is one command, and every step prints how it runs and the exact code lines involved. It works on
the real service in **`app/main.py`**.

**What you'll learn:** how a script becomes a service other systems can call and probe; how the endpoint uses
L1's contract on the way in and out; and how to prove the service is really async.

**In the deck:** the **Service** topic ("What is FastAPI?", "One request through FastAPI", "How you test an
LLM service") and the **Async** topic ("I made it async", "Never wait forever: the reliability ladder").

**Where:** the terminal of your codespace, in the lab folder (`cd /workspaces/<your-repo-name>`).

**L2 builds on L1.** If you haven't applied L1's contract yet, the first L2 command does it for you and says so.
**No real LLM is called:** `app/llm.py`'s `StubLLM` answers offline.

---

## Step 1 · See it fail (2 min)

```bash
bash lab.sh l2 fail
```

**How it runs:** `lab/l2/fail.py` (A) shows the last two lines of `triage_prototype.py`: it only runs from a
terminal, with no web endpoint. (B) It sends `GET /healthz` and `POST /triage` to the real `app/main.py`
through FastAPI's `TestClient` (requests go straight into the app; no server needed), then prints the lines that
answered.

**What you'll see:** both requests get **500 Internal Server Error**, and the lines behind them:
`app/main.py` lines 36–37 (`raise NotImplementedError("L2.1")`) and 42–51 (the L2.2 TODO).

**Why it matters:** the endpoints exist, but answer nothing. A platform health check would mark this service as
down. (The Sr. Platform Engineer's "we don't run scripts".)

## Step 2 · Run the checks (2 min)

```bash
bash lab.sh l2 check
```

**How it runs:** `lab/l2/check.py` runs `pytest -v tests/test_l2.py`, the same tests as `bash grade.sh l2`. They
send requests to `app/main.py` and swap in `StubLLM` (and a slow one for the timeout test). Open
`tests/test_l2.py` to read them.

**What you'll see:** 6 checks as plain sentences; **2 of 6 pass** already (the 422 and `/openapi.json` come from
L1's contract, which FastAPI reads). Then the open TODO lines: `app/main.py:36, 37, 42, 51`.

## Step 3 · Read the fix (3 min)

```bash
bash lab.sh l2 show
```

**How it runs:** `lab/l2/show.py` prints the finished endpoints from **`lab/l2/main_done.py`**, with real line
numbers and a note on each important line. Step 4 copies this file over `app/main.py`.

| Line | What it does |
|---|---|
| `@app.get("/healthz")` → `return {"status": "ok"}` | The platform's probe: alive, no model call |
| `@app.post("/triage", response_model=TriageResult)` | Only `TriageResult`'s fields leave the service |
| `async def triage(complaint: Complaint, …)` | FastAPI checks the body against `Complaint` (422 if wrong) |
| `async with asyncio.timeout(TIMEOUT_S):` | Never wait forever (`TIMEOUT_S`, 5 s by default) |
| `raw = await llm.complete(...)` | `await`: other requests run while the model thinks |
| `result = parse_triage(raw)` | L1's contract, on the model's reply |
| `except TimeoutError: result = human_review("model timed out")` | Too slow: a person gets it, with the reason |

The L3 logging TODOs stay open in this file: that's the next rung.

## Step 4 · Apply the fix (1 min)

```bash
bash lab.sh l2 apply
```

**How it runs:** `lab/l2/apply.py` checks L1 is in place, copies `lab/l2/main_done.py` over **`app/main.py`**,
then prints each L2 TODO line (`-`) and the code that replaced it (`+`), with line numbers.

## Step 5 · See it pass (3 min)

```bash
bash lab.sh l2 check
bash lab.sh l2 pass
```

**How it runs:** `check` as in step 2, now **6 of 6**, plus the exact lines that made them pass. `pass` runs
`lab/l2/pass.py`: it prints `triage()` from `app/main.py`, then sends five requests through `TestClient`.

**What you'll see:**

```
1. GET  /healthz                     -> 200  {"status":"ok"}
2. POST /triage  C-002               -> 200  … "team":"fraud_ops" …
3. POST /triage  C-013 (bad reply)   -> 200  … "team":"human_review","summary":"invalid model output (2 error(s))" …
4. POST /triage  empty text, 'fax'   -> 422  … "loc":["body","text"] …
5. a 1 s model, a 0.3 s deadline     -> 200  … "summary":"model timed out" …
```

## Step 6 · Try it: is the real service really async? (2 min)

Guess first: 10 requests at once, a 1-second model. How long?

```bash
bash lab.sh l2 try
```

**How it runs:** `lab/l2/try_.py` sends 10 requests at once to `app/main.py`, in-process (`httpx.AsyncClient`
with `ASGITransport`). Round A uses `StubLLM.complete`, which awaits (its lines in `app/llm.py` are printed).
Round B swaps in a model client that calls `time.sleep`, like a sync SDK.

**What you'll see:**

```
A  async model call    : 10 requests in 1.0 s
B  blocking model call : 10 requests in 10.1 s
```

**Why it matters:** the same `async def triage()` is fast only when what's inside really awaits.

## Step 7 · Open /docs in your browser (2 min)

```bash
bash lab.sh l2 serve
```

**How it runs:** `uvicorn app.main:app --port 8000`, a web server running `app/main.py`, until you press Ctrl+C.
Then **Ports** tab → **8000** → **globe** → add **`/docs`**. Try **POST /triage** → **Try it out** with
`{"id": "C-002", "text": "Two card transactions I did not make"}` (200), then `{"id": "", "text": ""}` (422).
Keep the port **Private**. Press **Ctrl+C** when done.

---

## ✅ Done with the L2 deep dive

**Later, the write-it-yourself assignment:** `bash lab.sh reset l2` puts the L2 starter back in `app/main.py`.
Write `/healthz` and `/triage` yourself from the TODOs, and check with `bash grade.sh l2`.

| You see | Do this |
|---|---|
| `app/main.py still has the L2 TODOs` | `bash lab.sh l2 apply` |
| `address already in use` (step 7) | Ctrl+C the other server, or `pkill -f uvicorn` |
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
