# Session 3 primer: observability and safe audit logs (live L3)

A **separate, simplified primer** for Session 3, like `../l1-pydantic-mini/` and `../l2-async-fastapi-mini/`.
Learners run commands and read output; they write no code.

1. **Before:** plain `print()` logs leak full account numbers and split one request across multiple lines.
2. **Masking:** account numbers are redacted before logs are stored.
3. **After:** one JSON log line per request, with a request ID and the key audit fields.
4. **Request IDs:** if the caller sends `X-Request-ID`, echo it; otherwise generate one.

```bash
bash run.sh before
bash run.sh mask
bash run.sh after
```

Or run the full flow:

```bash
bash run.sh all
```

No real LLM or server is needed here. The primer uses fixed sample requests and decisions so everyone sees the same thing.

## Files

- `events.py`: the sample requests and final decisions used in the demos
- `audit.py`: tiny helpers for masking and building one JSON audit log line
- `before.py`: what naive `print()` logging looks like
- `mask_demo.py`: shows how masking changes plain text and JSON logs
- `after.py`: the same requests as structured, masked audit log lines
