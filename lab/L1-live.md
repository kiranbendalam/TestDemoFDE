# L1 · live · Why Pydantic helps with LLM output (about 8 minutes)

**The short version, for everyone.** You run three commands and read their output. You write no code. When
you're done, the deeper version, for after the session, is `lab/L1-deep-dive.md`.

**What you'll learn:** a model's reply is untrusted input. Code that trusts it can send a fraud complaint to the
wrong queue without any error. A small Pydantic contract catches the same bad replies and sends them to a person.

**In the deck:** the **Contract** topic: "The model's reply is untrusted input", "What is Pydantic?" and
"The contract in code". (The lab uses a simplified contract with three fields, so it's easy to read.)

**Where:** the terminal of your codespace. First move into the primer folder:

```bash
cd primer/l1-pydantic-mini
```

(If you see "No such file or directory", run `cd /workspaces/<your-repo-name>` first, then try again.)

---

## Step 1 · Without a contract (2 min)

```bash
bash run.sh before
```

**What runs:** `before.py`. It reads four model replies from `replies.py` and does what a prototype does:
`json.loads(reply)`, then looks up the team in a queue table.

**What you'll see:**

```
CASE: good reply                   queue : Q-FRAUD      outcome : routed
CASE: wrong team + wrong priority  queue : Q-GENERAL    outcome : silent misroute
CASE: missing team                 queue : Q-GENERAL    outcome : silent misroute
CASE: prose around JSON            json.loads : JSONDecodeError …   outcome : crash
```

**Why it matters:** the model wrote `"fraud ops"` with a space instead of `fraud_ops`, so the lookup missed
and the complaint went to the **general queue**, with no error. Prose around the JSON made the program crash.

## Step 2 · Read the contract (3 min)

```bash
bash run.sh contract
```

**What runs:** `show_contract.py`. It prints `contract.py` with line numbers. Open `contract.py` in the editor
to follow along.

**What to look at:**

| In `contract.py` | What it does |
|---|---|
| `class ModelReply(BaseModel)` | The shape we expect back from the model: Pydantic checks every reply against it |
| `extra="forbid"` | Rejects fields we didn't ask for |
| `team: Literal["fraud_ops", "disputes"]` | Only these exact values: `"fraud ops"` ✗ |
| `priority: int = Field(ge=1, le=4)` | A whole number from 1 to 4: `"urgent"` ✗ |
| `summary: str = Field(min_length=1, max_length=80)` | Not empty, at most 80 characters |
| `ModelReply.model_validate_json(raw)` | Parses and checks in one step: prose around the JSON ✗ |
| `except ValidationError` → `human_review(...)` | Never guess: a bad reply goes to a person, with the reason |

## Step 3 · With the contract (2 min)

```bash
bash run.sh after
```

**What runs:** `after.py`. It sends the **same four replies** through `safe_route()` in `contract.py`, which
validates each one before any routing happens.

**What you'll see:**

```
CASE: good reply                   queue : Q-FRAUD   needs_human : False   reason : validated
CASE: wrong team + wrong priority  queue : Q-HUMAN   needs_human : True    reason : invalid model output (2 error(s))
CASE: missing team                 queue : Q-HUMAN   needs_human : True    reason : invalid model output (1 error(s))
CASE: prose around JSON            queue : Q-HUMAN   needs_human : True    reason : invalid model output (1 error(s))
```

**Why it matters:** good replies still flow through. Every bad one goes to a person, with the reason, so
nothing is misrouted and nothing crashes. The model didn't get smarter; **the system got safer**.

---

## ✅ Done with live L1

Go back to the lab folder, ready for L2:

```bash
cd ../..
```

Post **✅ L1** in the chat.

**The limit to remember:** a contract catches *malformed* replies. A valid reply with the wrong team still
passes. Checking that is evaluation, later in the programme.

**Want more? (after the session):** `lab/L1-deep-dive.md` runs the same idea on the real service contract
(`app/models.py`), shows the 12 contract tests, and lets you try Pydantic's error types.
