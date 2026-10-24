#!/usr/bin/env bash
# Session 3 lab runner. Every step is one command; nothing to type into the code.
#   bash lab.sh l1 fail | check | show | apply | pass | try          (L1 Contract)
#   bash lab.sh l2 fail | check | show | apply | pass | try | serve  (L2 Service)
#   bash lab.sh l3 fail | check | show | apply | pass | try | serve  (L3 Observability)
#   bash lab.sh l4 fail | check | show | apply | pass | try          (L4 Ship)
#   bash lab.sh reset l1 | l2 | l3 | l4                              (put the TODO version back, e.g. for the assignment)
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python}
RUNG="L1 Contract"
hdr() { printf '\n\033[1m━━━ %s · %s ━━━\033[0m\n%s\n\n' "$RUNG" "$1" "$2"; }

case "${1:-}:${2:-}" in
  l1:fail)  hdr "step 1 · SEE IT FAIL" "Objective: model output is untrusted input. In the deck: Contract topic, 'The model's reply is untrusted input'."
            "$PY" lab/l1/fail.py ;;
  l1:check) hdr "steps 2 and 5 · RUN THE CHECKS" "Objective: see what the contract tests check, and why they fail or pass. In the deck: Service topic, 'How you test an LLM service'."
            "$PY" lab/l1/check.py ;;
  l1:show)  hdr "step 3 · READ THE FIX" "Objective: see exactly what Pydantic adds. In the deck: Contract topic, 'What is Pydantic?' and 'The contract in code'."
            "$PY" lab/l1/show.py ;;
  l1:apply) hdr "step 4 · APPLY THE FIX" "Objective: put the contract in place, and see exactly what changed."
            "$PY" lab/l1/apply.py ;;
  l1:pass)  hdr "step 5 · SEE IT PASS" "Objective: the same bad replies, now caught. In the deck: Contract topic, 'The contract in code'."
            "$PY" lab/l1/pass.py ;;
  l1:try)   hdr "step 6 · TRY IT" "Objective: read Pydantic's error types. Predict first. In the deck: Contract topic, 'Predict the validation error'."
            "$PY" lab/l1/try.py ;;
  l2:fail)  RUNG="L2 Service"; hdr "step 1 · SEE IT FAIL" "Objective: a script can't be called; the service's endpoints are still TODOs. In the deck: Service topic, 'What is FastAPI?'."
            "$PY" lab/l2/fail.py ;;
  l2:check) RUNG="L2 Service"; hdr "steps 2 and 5 · RUN THE CHECKS" "Objective: see what the service tests check, and why they fail or pass. In the deck: Service topic, 'How you test an LLM service'."
            "$PY" lab/l2/check.py ;;
  l2:show)  RUNG="L2 Service"; hdr "step 3 · READ THE FIX" "Objective: see the two endpoints, the timeout and the await. In the deck: Service topic, 'One request through FastAPI'; Async topic, 'Never wait forever'."
            "$PY" lab/l2/show.py ;;
  l2:apply) RUNG="L2 Service"; hdr "step 4 · APPLY THE FIX" "Objective: put the endpoints in place, and see exactly what changed."
            "$PY" lab/l2/apply.py ;;
  l2:pass)  RUNG="L2 Service"; hdr "step 5 · SEE IT PASS" "Objective: real requests to the real service: 200, human_review, 422, timeout. In the deck: Service topic, 'One request through FastAPI'."
            "$PY" lab/l2/pass.py ;;
  l2:try)   RUNG="L2 Service"; hdr "step 6 · TRY IT" "Objective: prove the real service is async (about 1 s vs about 10 s). In the deck: Async topic, 'I made it async'."
            "$PY" lab/l2/try_.py ;;
  l2:serve) RUNG="L2 Service"; hdr "step 7 · OPEN /docs" "Objective: the contract, written down, in your browser. In the deck: Service topic, 'One request through FastAPI'."
            echo "HOW THIS STEP RUNS"
            echo "  bash lab.sh l2 serve"
            echo "    └─ python -m uvicorn app.main:app --port 8000   (a web server running app/main.py; Ctrl+C to stop)"
            echo "  Then: Ports tab -> 8000 -> globe icon -> add /docs to the address. Keep the port Private."
            echo
            "$PY" -m uvicorn app.main:app --port 8000 ;;
  l3:fail)  RUNG="L3 Observability"; hdr "step 1 · SEE IT FAIL" "Objective: a print line leaks account numbers; the service leaves no audit trail. In the deck: Ship topic, 'What is structured logging?'."
            "$PY" lab/l3/fail.py ;;
  l3:check) RUNG="L3 Observability"; hdr "steps 2 and 5 · RUN THE CHECKS" "Objective: see what the logging tests check, and why they fail or pass. In the deck: Ship topic, 'One JSON line per request'."
            "$PY" lab/l3/check.py ;;
  l3:show)  RUNG="L3 Observability"; hdr "step 3 · READ THE FIX" "Objective: mask, the JSON formatter, the middleware and the audit fields. In the deck: Ship topic, 'One JSON line per request'."
            "$PY" lab/l3/show.py ;;
  l3:apply) RUNG="L3 Observability"; hdr "step 4 · APPLY THE FIX" "Objective: put logging in place in both files, and see exactly what changed."
            "$PY" lab/l3/apply.py ;;
  l3:pass)  RUNG="L3 Observability"; hdr "step 5 · SEE IT PASS" "Objective: one request, one JSON line, the ID echoed, the account masked. In the deck: Ship topic, 'One JSON line per request'."
            "$PY" lab/l3/pass.py ;;
  l3:try)   RUNG="L3 Observability"; hdr "step 6 · TRY IT" "Objective: search, count and audit your log lines. In the deck: Ship topic, 'What is structured logging?' and 'Logs, metrics, traces'."
            "$PY" lab/l3/try_.py ;;
  l3:serve) RUNG="L3 Observability"; hdr "step 7 · WATCH THE LOG LINES LIVE" "Objective: see one JSON line appear per request while you use /docs."
            echo "HOW THIS STEP RUNS"
            echo "  bash lab.sh l3 serve"
            echo "    └─ python -m uvicorn app.main:app --port 8000   (app/main.py calls setup_logging(): JSON lines go to this terminal)"
            echo "  Then: Ports tab -> 8000 -> globe -> /docs -> POST /triage -> Try it out. Watch this terminal. Ctrl+C to stop."
            echo
            "$PY" -m uvicorn app.main:app --port 8000 ;;
  l4:fail)  RUNG="L4 Ship"; hdr "step 1 · SEE IT FAIL" "Objective: a careless commit leaks .env; an image that builds is still refused. In the deck: Ship topic, 'Git in the customer's repo' and '\"It builds, so we're done\"'."
            "$PY" lab/l4/fail.py ;;
  l4:check) RUNG="L4 Ship"; hdr "steps 2 and 5 · RUN THE CHECKS" "Objective: see what the L4 checks look for, and why they fail or pass. In the deck: Ship topic, 'Your Git workflow, step by step' and 'What is Docker?'."
            "$PY" lab/l4/check.py ;;
  l4:show)  RUNG="L4 Ship"; hdr "step 3 · READ THE FIX" "Objective: the deliberate commit, and the Dockerfile line by line. In the deck: Ship topic, 'Your Git workflow, step by step' and '\"It builds, so we're done\"'."
            "$PY" lab/l4/show.py ;;
  l4:apply) RUNG="L4 Ship"; hdr "step 4 · APPLY THE FIX" "Objective: fix the Dockerfile, add .dockerignore, and commit deliberately (in the twin)."
            "$PY" lab/l4/apply.py ;;
  l4:pass)  RUNG="L4 Ship"; hdr "step 5 · SEE IT PASS" "Objective: the same checks as step 1, now passing. In the deck: Ship topic, '\"It builds, so we're done\"'."
            "$PY" lab/l4/pass.py ;;
  l4:try)   RUNG="L4 Ship"; hdr "step 6 · TRY IT" "Objective: the whole service in the shipped image: secret at run time, one request, its log line. In the deck: Ship topic, 'Where a key leaks, and where it belongs'."
            "$PY" lab/l4/try_.py ;;
  reset:l4) echo "HOW THIS STEP RUNS: copies lab/l4/Dockerfile_start -> Dockerfile, deletes .dockerignore and the twin (fde-s03-l4-twin in the temp folder), removes the lab images if Docker is here"
            cp lab/l4/Dockerfile_start Dockerfile; rm -f .dockerignore
            rm -rf "$("$PY" -c 'import tempfile; print(tempfile.gettempdir())')/fde-s03-l4-twin"
            command -v docker >/dev/null 2>&1 && docker rmi -f s03-before s03-triage >/dev/null 2>&1 || true
            echo "  ↩️  Dockerfile is back to the starter (5 TODOs), .dockerignore and the twin are gone (for the write-it-yourself assignment)." ;;
  reset:l3) echo "HOW THIS STEP RUNS: copies lab/l3/logging_start.py -> app/logging_setup.py and lab/l3/main_start.py (L2 done, L3 TODOs) -> app/main.py"
            cp lab/l3/logging_start.py app/logging_setup.py; cp lab/l3/main_start.py app/main.py
            echo "  ↩️  app/logging_setup.py and app/main.py are back to the L3 TODO version (for the write-it-yourself assignment)." ;;
  reset:l2) echo "HOW THIS STEP RUNS: copies lab/l2/main_start.py (the L2 starter) -> app/main.py"
            cp lab/l2/main_start.py app/main.py
            echo "  ↩️  app/main.py is back to the TODO version (for the write-it-yourself assignment)." ;;
  reset:l1) echo "HOW THIS STEP RUNS: copies lab/l1/models_start.py (the empty starter) -> app/models.py"
            cp lab/l1/models_start.py app/models.py
            echo "  ↩️  app/models.py is back to the TODO version (for the write-it-yourself assignment)." ;;
  *) echo "Unknown command: bash lab.sh $*  (your copy may be out of date: run git pull)"; grep '^#  ' "$0"; exit 1 ;;
esac
