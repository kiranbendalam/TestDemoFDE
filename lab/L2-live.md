# L2 · live · Async, a timeout, and a FastAPI service (about 12–15 minutes)

**The short version, for everyone.** You run four commands and read their output, then open one page in your
browser. You write no code.

**What you'll learn:**
- `async` only helps if you really `await` the slow call.
- Never wait forever on a model: a timeout gives the caller a safe answer.
- FastAPI turns your Pydantic contract into an API that checks every request, and documents itself.

**In the deck:** the **Async** topic ("What is async?", "I made it async", "Never wait forever: the
reliability ladder") and the **Service** topic ("What is FastAPI?", "One request through FastAPI").

**Where:** the terminal of your codespace. Move into the primer folder:

```bash
cd primer/l2-async-fastapi-mini
```

(If you see "No such file or directory", run `cd /workspaces/<your-repo-name>` first, then try again.)

**No real LLM is called.** `model.py` is a stand-in: it waits (1 second, or 3 for a "slow" call), then
returns fixed JSON. So everyone gets the same timings and results.

---

## Step 1 · Async: 10 requests, blocking vs awaited (3 min)

Before you run it, **guess**: ten complaints arrive at once, each model call takes 1 second. How long does
each version take?

```bash
bash run.sh async
```

**What runs:** `async_demo.py`. It fires ten requests at once with `asyncio.gather`, first through
`handle_blocking` (a `time.sleep` inside `async def`, like a sync SDK), then through `handle_async`
(`await classify(...)`, like an async client). Both call the stand-in in `model.py`.

**What you'll see:**

```
BLOCKING  (time.sleep inside async def)   : 10 requests in 10.0 s   <- one after another
AWAITED   (await asyncio.sleep)           : 10 requests in 1.0 s    <- the waits overlap
```

**Why it matters:** both handlers say `async def`; only the awaited one is really asynchronous. One blocking
call freezes the whole event loop. Open `async_demo.py` and compare the two `handle_…` functions: one word
makes the difference.

## Step 2 · Never wait forever: a timeout (2 min)

```bash
bash run.sh timeout
```

**What runs:** `timeout_demo.py`. The stand-in model takes 3 seconds. The code wraps the call in
`async with asyncio.timeout(1.5):` and catches `TimeoutError` **outside** that block.

**What you'll see:**

```
The model needs 3.0 s; our deadline is 1.5 s.
  result after 1.5 s : {'route': 'human_review', 'reason': 'model timed out after 1.5 s'}
```

**Why it matters:** after 1.5 seconds we stop waiting and send the complaint to a person, with the reason. The
contact-centre screen gets an answer instead of a spinner.

## Step 3 · A FastAPI service: good request, bad request (3 min)

```bash
bash run.sh api
```

**What runs:** `api_demo.py`. It calls the tiny service in **`app.py`** the way the case system would, using
FastAPI's `TestClient` (no server needed yet). Open `app.py` beside it:

| In `app.py` | What it does |
|---|---|
| `class Complaint(BaseModel)` | What comes **in**: FastAPI checks every request against it |
| `class TriageReply(BaseModel)` | What goes **out**: only these fields leave the service |
| `@app.get("/healthz")` | The platform asks "are you alive?" |
| `@app.post("/triage", response_model=TriageReply)` | Typed in, typed out |
| `async with asyncio.timeout(1.5)` + `await classify(...)` | Steps 1 and 2, inside the service |
| `TriageReply.model_validate_json(raw)` | The L1 contract, on the model's reply |

**What you'll see:**

```
GET  /healthz                                   -> 200  {"status": "ok"}
POST /triage  {"id": "C-002", "text": "Two card transactions I did not make"}
                                                -> 200  {"team": "fraud_ops", "priority": 1, "summary": "…"}
POST /triage  {"id": "", "text": ""}            -> 422  [… "loc": ["body", "id"] …, … "loc": ["body", "text"] …]
```

**Why it matters:** the bad request got **422** before our code even ran, and the reply lists exactly which
fields failed. Both checks come from the Pydantic classes in `app.py`.

## Step 4 · The same service in your browser: /docs (4 min)

```bash
bash run.sh serve
```

**What runs:** `uvicorn app:app --port 8000`, a small web server running `app.py`. It keeps running until you
press **Ctrl+C**.

1. Open the **Ports** tab (next to Terminal), find port **8000**, and click the **globe** icon.
2. A browser tab opens. Add **`/docs`** to the end of the address and press Enter.
3. You'll see **"Example Bank triage (primer)"**, with `GET /healthz` and `POST /triage`.
4. Click **POST /triage** → **Try it out**. Replace the example body with
   `{"id": "C-002", "text": "Two card transactions I did not make"}` → **Execute**. You'll get **200** with
   `fraud_ops`.
5. Try `{"id": "", "text": ""}` → **Execute**. You'll get **422**, listing `id` and `text`.

**Why it matters:** this page is generated from the same Pydantic classes. It's the contract, written down, and
it can't drift from the code. The port shows **Private**: keep it that way (making it public is the first thing
a CISO would flag).

Press **Ctrl+C** in the terminal to stop the server when you're done.

---

## ✅ Done with live L2

```bash
cd ../..
```

Post **✅ L2** in the chat.

## If something goes wrong

| You see | Do this |
|---|---|
| `No such file or directory` | `cd /workspaces/<your-repo-name>`, then `cd primer/l2-async-fastapi-mini` |
| `ModuleNotFoundError` | `pip install -r ../../requirements.txt` |
| `address already in use` (step 4) | Another server is running: press Ctrl+C in that terminal, or run `pkill -f uvicorn` |
| No port 8000 in the Ports tab | Wait 5 seconds after `serve` starts; or click **Forward a Port** and type 8000 |
| The browser page says "Not Found" | Add `/docs` at the end of the address |
