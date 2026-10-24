# Session 3 primer: async and FastAPI (live L2)

A **separate, simplified primer** for Session 3, like `../l1-pydantic-mini/`. Learners run commands and read
output; they write no code.

1. **Async:** ten slow model calls, blocking vs awaited: about 10 s vs about 1 s.
2. **Timeout:** a 3-second model, a 1.5-second deadline, and a safe answer from human review.
3. **FastAPI:** a good request gets 200 with the contract; a bad one gets 422 listing the fields.
4. **/docs:** the same service in the browser.

```bash
bash run.sh async
bash run.sh timeout
bash run.sh api
bash run.sh serve      # then Ports tab -> 8000 -> globe -> add /docs; Ctrl+C to stop
```

No real LLM is called: `model.py` is a stand-in that waits, then returns fixed JSON.

## Files

- `model.py`: the stand-in model (a blocking and an async version)
- `async_demo.py`: 10 requests, blocking vs awaited
- `timeout_demo.py`: `asyncio.timeout` around a slow call
- `app.py`: the tiny FastAPI service (`/healthz`, `/triage`)
- `api_demo.py`: calls the service with FastAPI's TestClient (no server needed)
