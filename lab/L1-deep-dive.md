# L1 deep dive (after the session) · Contract: never trust the model's reply

**After the session, at your own pace, about 13 minutes, after the live L1** (`lab/L1-live.md`, the short primer). You won't write any code
here: every step is one command. It goes deeper: the real service contract, the 12 contract tests, and
Pydantic's error types.

**What you'll learn:** a model's reply is untrusted input, and a Pydantic contract turns a silent misroute into a
safe hand-over to a human.

**In the deck:** the **Contract** topic: the FDE production toolkit, what a contract is and why it's yours, the model's reply is untrusted input, What is Pydantic?, the contract in code, when to use it, and predict the validation error.

**Where:** the terminal of your codespace (or the Colab notebook), in the lab folder. If you just opened the
codespace, you're already there. If not, run `cd /workspaces/<your-repo-name>`.

---

## Step 1 · See it fail (3 min)

```bash
bash lab.sh l1 fail
```

**How it runs:** `lab.sh` runs `lab/l1/fail.py`, which does two things.

- **A. It runs the real prototype**, `triage_prototype.py`, and first prints its `call_model()` function (lines
  17–26). That function is a **stand-in for the LLM**: it waits 1 second and returns fixed text, including a
  bad reply for C-013. **No real model is called**, so the lab runs offline, needs no API key, and gives
  everyone the same result.
- **B. It prints the prototype's own two routing lines** (`triage_prototype.py`, lines 34–35). Then it traces
  three bad replies from `lab/l1/replies.py` through them: reply → `json.loads` → team → `TEAM_QUEUES.get(...)`
  → queue (or crash).

**What you'll see (the key lines):**

```
C-013 -> Q-GENERAL priority urgent                         (part A: the real prototype)

C-013  TEAM_QUEUES.get('fraud ops', 'Q-GENERAL') -> Q-GENERAL   ⚠ silent misroute
C-014  TEAM_QUEUES.get(None, 'Q-GENERAL') -> Q-GENERAL          ⚠ silent misroute
C-015  json.loads  : ✗ JSONDecodeError ... -> CRASH
```

**Why it matters:** the model wrote `"fraud ops"` with a space, so the lookup missed and a fraud complaint
went to the **general queue**, with no error. The crash on C-015 is the *good* failure, because someone
notices. This is the Contract topic in the deck: "The model's reply is untrusted input". Also notice that every `processing` line prints the full account number: that's the
problem L3 fixes.

## Step 2 · Run the checks, and see what's missing (2 min)

```bash
bash lab.sh l1 check
```

**How it runs:** `lab.sh` runs `lab/l1/check.py`, which runs `pytest -v tests/test_l1.py`. These are the same
tests `bash grade.sh l1` runs. The tests import `Complaint`, `TriageResult` and `parse_triage` from
**`app/models.py`**, the file being checked, and the stub model's bad replies from `app/llm.py`. Open
`tests/test_l1.py` in the editor to read any test.

**What you'll see:** 12 checks, each as a plain sentence, all ❌ for now:

```
❌ Complaint rejects an empty id                                     needs L1.1
❌ Reply with prose around the JSON -> human review                  needs L1.3
…
0 of 12 checks pass.
WHERE THE GAP IS: app/models.py still has the empty starter.
    app/models.py:41  # TODO (L1.1): id, text, channel
    app/models.py:47  # TODO (L1.2): model_config that rejects unknown fields
    app/models.py:48  # TODO (L1.2): category, priority, team, summary, needs_human
    app/models.py:61  raise NotImplementedError(...)
```

Open `app/models.py` and look at those lines: the classes exist, but they have no fields yet, and
`parse_triage` doesn't validate anything.

**Why it matters:** these are **contract tests**: the bottom layer of the test pyramid ("How you test an LLM
service" in the deck's Service topic). A CI gate runs them on every pull request.

## Step 3 · Read the fix (3 min)

```bash
bash lab.sh l1 show
```

**How it runs:** `lab.sh` runs `lab/l1/show.py`, which prints the finished contract from
**`lab/l1/models_done.py`**, with its real line numbers and a note beside each important line. Step 4 copies
this exact file over `app/models.py`. Open `lab/l1/models_done.py` in the editor to follow along.

**What you'll see:** three blocks.
- **L1.1** `class Complaint`: what the case system sends us (id, text, channel, each with its limits).
- **L1.2** `class TriageResult`: what we send back, with notes 1–4.
- **L1.3** `def parse_triage`: checks the model's reply, with notes 5–6.

| # | Line | What it does |
|---|---|---|
| 1 | `class TriageResult(BaseModel)` | Makes the class a contract that Pydantic checks |
| 2 | `extra="forbid"` | Rejects fields we didn't ask for |
| 3 | `category: Category`, `team: Team` | Only our exact values: `"fraud ops"` ✗ |
| 4 | `Field(ge=1, le=4)`, `max_length` | Ranges and lengths: `"urgent"` ✗, `7` ✗ |
| 5 | `model_validate_json(raw)` | Parses and checks in one step: prose around the JSON ✗ |
| 6 | `except ValidationError: human_review(...)` | Your decision: never guess, send it to a human |

This is the same code as "The contract in code" in the deck's Contract topic. The allowed values (`Category`
and `Team`) are at the top of the same file.

## Step 4 · Apply the fix (1 min)

```bash
bash lab.sh l1 apply
```

**How it runs:** `lab.sh` runs `lab/l1/apply.py`, which copies `lab/l1/models_done.py` over **`app/models.py`**.
Then it prints what changed: each TODO line from step 2 (`-`) and the code that replaced it (`+`), with the line
number. Your empty starter is kept in `lab/l1/models_start.py`.

**What you'll see (part of it):**

```
app/models.py, from line 30:
  -    # TODO (L1.1): id, text, channel
  +    id: str = Field(min_length=1, max_length=20)
  +    text: str = Field(min_length=1, max_length=4000)
  +    channel: Literal["email", "chat", "branch", "phone"] = "email"
```

Open `app/models.py` in the editor: the TODO lines are now real fields.

## Step 5 · See it pass (3 min)

```bash
bash lab.sh l1 check
bash lab.sh l1 pass
```

**How it runs:** `check` is the same as in step 2. `pass` runs `lab/l1/pass.py`, which first prints
`parse_triage` from `app/models.py` (with line numbers), then sends each of the three replies from step 1
(`lab/l1/replies.py`) through it.

**What you'll see:** first, the same 12 checks, now all ✅, plus the exact lines in `app/models.py` that made
them pass (with line numbers). Then the same three bad replies from step 1, now going through `parse_triage`:

```
12 of 12 checks pass.
C-013 ... -> team=human_review  needs_human=True  (invalid model output (2 error(s)))
C-014 ... -> team=human_review  needs_human=True  (invalid model output (1 error(s)))
C-015 ... -> team=human_review  needs_human=True  (invalid model output (1 error(s)))
```

**Why it matters:** the same three replies now go to a person, with the reason. Nothing was misrouted, and
nothing crashed. C-013 has **2** errors: the team isn't one of our values, and the priority isn't a number.
(`bash grade.sh l1` is the short form of the same check; you'll use it for the assignment.)

## Step 6 · Try it: predict first (3 min)

Before you run it, guess what Pydantic will say about each reply: **A** has `priority: 7`, **B** has an extra
field `confidence`, and **C** is a good reply. This is "Predict the validation error" in the deck's Contract topic.

```bash
bash lab.sh l1 try
```

**How it runs:** `lab.sh` runs `lab/l1/try.py`, which first prints `class TriageResult` from `app/models.py` (with
line numbers). Then it calls `TriageResult.model_validate_json(reply)` on each reply A, B and C. A valid reply
becomes a typed object; an invalid one raises `ValidationError`, and the script prints each error's field and
type.

**What you'll see:**

```
A  ✗ priority: less_than_equal        (we said le=4)
B  ✗ confidence: extra_forbidden      (extra="forbid")
C  ✓ valid: a typed object, team=Team.FRAUD_OPS, priority=1 (int)
```

**Why it matters:** the error type names exactly *what* broke, so the service can log it and count failures
by kind.

---

## ✅ Done with L1

Post **✅ L1** in the chat. You now have:
- a contract (`app/models.py`) that the rest of the lab builds on;
- the habit: **validate at the edge, trust inside** (the Contract topic in the deck: "when to use it, when not").

**The limit to remember:** a contract catches *malformed* replies. A perfectly valid reply with the *wrong*
team still passes. Checking that is evaluation, later in the programme.

## If something goes wrong

| You see | Do this |
|---|---|
| `No such file or directory: lab.sh` | You're in the wrong folder. Run `cd /workspaces/<your-repo-name>`, then try again |
| `ModuleNotFoundError: pydantic` | `pip install -r requirements.txt` |
| `Your app/models.py still has the TODO version` | Run `bash lab.sh l1 apply` (step 4) first |
| You edited `app/models.py` and broke it | `bash lab.sh l1 apply` puts the finished version back |

## Later: the write-it-yourself assignment

`bash lab.sh reset l1` puts the empty starter back. Then write the contract yourself, following the TODOs in
`app/models.py`, and check it with `bash grade.sh l1`. The full assignment is in the lab handout.
