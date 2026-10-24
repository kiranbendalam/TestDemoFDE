# Session 3 mini-lab: why Pydantic helps with LLM output

This is a **separate, simplified primer** for Session 3.

It does **not** change the main lab in `labs/s03-python-prod/`.
Use it when learners need the basic story first:

1. **Without a contract** the program trusts the LLM reply too early.
2. A bad reply can **silently misroute** work or **crash** the program.
3. **With a small Pydantic contract**, the same bad replies are caught and sent to **human review**.

## What makes this version simpler

- no FastAPI
- no `grade.sh`
- no `StubLLM`
- no learner edits required
- only **three reply fields**: `team`, `priority`, `summary`

## 8-minute flow

From this folder, run:

```bash
bash run.sh before
bash run.sh contract
bash run.sh after
```

Or run the whole flow at once:

```bash
bash run.sh all
```

## What learners should notice

- In `before`, `"fraud ops"` quietly falls through to the wrong queue.
- In `before`, prose around JSON crashes the program.
- In `after`, the same bad replies no longer route or crash.
- Pydantic does not make the model smarter; it makes the system **safer**.

## Files

- `before.py` — naive handling with `json.loads(...)` and `dict.get(...)`
- `contract.py` — the tiny Pydantic model and safe fallback
- `after.py` — same replies, now validated first
- `show_contract.py` — prints the contract with line numbers
- `replies.py` — the fixed sample replies used in both demos

## Relation to the main Session 3 lab

This mini-lab is a **primer**, not a replacement. The main lab in `labs/s03-python-prod/`
adds the real Session 3 pieces after the concept lands:

- request model (`Complaint`)
- service endpoint
- timeout handling
- structured logging
- Git and Docker
