#!/usr/bin/env bash
# Run once before the session to confirm your lab environment is ready.
cd "$(dirname "$0")"
echo "Checking your lab environment..."
echo "  HOW THIS RUNS: checks the Python version, imports the lab packages, then runs git --version and docker info"
ok=1
pass() { echo "  ✅ $1"; }
fail() { echo "  ❌ $1"; ok=0; }

PY=$(command -v python3 || command -v python)
if "$PY" -c 'import sys; sys.exit(sys.version_info < (3, 11))'; then pass "Python $("$PY" -V 2>&1 | cut -d' ' -f2)"
else fail "Python 3.11+ needed (found $("$PY" -V 2>&1))"; fi

if "$PY" -c 'import fastapi, pydantic, uvicorn, httpx, pytest' 2>/dev/null; then pass "lab packages installed"
else fail "lab packages missing: run  pip install -r requirements.txt"; fi

if git --version >/dev/null 2>&1; then pass "$(git --version)"; else fail "git not found"; fi
if [ -n "$(git config user.email)" ]; then pass "git identity set ($(git config user.name))"
else fail "set your git identity: git config --global user.name \"Your Name\"; git config --global user.email you@example.com"; fi

if "$PY" -m uvicorn --version >/dev/null 2>&1; then
  "$PY" - <<'PY' && pass "a FastAPI app starts and answers on port 8000" || fail "could not start a test API on port 8000 (is something already using it?)"
import threading, time, urllib.request
import uvicorn
from fastapi import FastAPI
app = FastAPI()
@app.get("/healthz")
def h(): return {"status": "ok"}
server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="error"))
threading.Thread(target=server.run, daemon=True).start()
for _ in range(50):
    try:
        assert urllib.request.urlopen("http://127.0.0.1:8000/healthz", timeout=1).status == 200
        break
    except Exception:
        time.sleep(0.1)
else:
    raise SystemExit(1)
server.should_exit = True
PY
fi

if command -v docker >/dev/null 2>&1; then
  tmp=$(mktemp -d)
  printf 'FROM public.ecr.aws/docker/library/python:3.12.15-slim-bookworm\nCMD ["python", "-c", "print(42)"]\n' > "$tmp/Dockerfile"
  if docker build -q -t s03-check "$tmp" >/dev/null 2>&1 && [ "$(docker run --rm s03-check)" = "42" ]; then pass "Docker builds and runs an image"
  else fail "Docker could not build or run an image (Ctrl/Cmd+Shift+P → Codespaces: Full Rebuild Container)"; fi
  docker rmi -f s03-check >/dev/null 2>&1; rm -rf "$tmp"
elif [ "${CODESPACES:-}" = "true" ]; then
  fail "Docker not found: Ctrl/Cmd+Shift+P → Codespaces: Full Rebuild Container"
else
  echo "  ⚠️  Docker not found. Fine for Colab or a laptop without Docker: do L4b in a codespace."
fi

if [ "$ok" -eq 1 ]; then echo "All good. You are ready for the session."
else echo "Something failed. Fix the ❌ lines above, or tell the trainer before the session."; exit 1; fi
