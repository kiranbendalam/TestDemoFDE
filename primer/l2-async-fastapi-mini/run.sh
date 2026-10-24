#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY=$(command -v python3 || command -v python)

case "${1:-}" in
  async)   "$PY" async_demo.py ;;
  timeout) "$PY" timeout_demo.py ;;
  api)     "$PY" api_demo.py ;;
  serve)   echo "Starting the service on port 8000. Open the Ports tab -> 8000 -> globe icon, add /docs to the URL. Ctrl+C to stop."
           "$PY" -m uvicorn app:app --port 8000 ;;
  *)       echo "usage: bash run.sh async | timeout | api | serve"; exit 2 ;;
esac
