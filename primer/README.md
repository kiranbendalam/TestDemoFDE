# Session 3 primers: short concept-first versions

These primers are **small, separate warm-ups** for Session 3. Learners run commands and read output; they write no code.

They are the **live lab**: the trainer runs them in the session, and you follow `lab/L1-live.md` … `lab/L4-live.md`.

## Suggested order

The primers are designed to match the Session 3 sequence:

1. **L1 Contract** → validate model output before trusting it
2. **L2 Service** → call the model safely in an async API
3. **L3 Observability** → log one safe, searchable audit line per request
4. **L4 Ship** → stage only what you mean and build an image the platform team will accept

If a learner is short on time, they can still jump straight to one topic.

## Pick the topic you need

### L1 · Contract and Pydantic

Why messy LLM output needs a contract before routing.

```bash
cd primer/l1-pydantic-mini
bash run.sh all
```

### L2 · Async, timeout and FastAPI

Why `await`, deadlines and request validation matter in a service.

```bash
cd primer/l2-async-fastapi-mini
bash run.sh async
bash run.sh timeout
bash run.sh api
```

Optional browser step:

```bash
bash run.sh serve
```

### L3 · Observability and safe audit logs

Why `print()` is not enough, why request IDs matter, and why masking must happen before logs are stored.

```bash
cd primer/l3-observability-mini
bash run.sh all
```

### L4 · Git and Docker for shipping

Why deliberate staging matters, and why “the image builds” is not enough.

```bash
cd primer/l4-ship-mini
bash run.sh all
```

## Best learner flow

- Sequence: **live lab (these primers) → deep dives (`lab/L*-deep-dive.md`) → assignment (`ASSIGNMENT.md`)**.
- If one topic already feels clear, skip straight to the next one.
- The primers teach the **why**; the deep dives and the assignment show the **how in a real service**.
