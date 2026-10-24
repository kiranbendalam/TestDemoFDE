#!/usr/bin/env bash
# Instant feedback for each rung.  Usage: bash grade.sh l1 | l2 | l3 | l4 | handover | all
set -u
cd "$(dirname "$0")"
PY=$(command -v python3 || command -v python)
export FORCE_OFFLINE=1   # always grade against the offline stub
PASS=0; FAIL=0
ok()   { echo "  ✅ $1"; PASS=$((PASS + 1)); }
bad()  { echo "  ❌ $1"; FAIL=$((FAIL + 1)); }
info() { echo "  ℹ️  $1"; }

hints() {  # one plain-language hint per failing test
  local t
  for t in $(grep -oE "::test_[a-z0-9_]+" "$1" | sort -u | tr -d ':'); do
    case "$t" in
      test_complaint_accepts_valid_input|test_complaint_rejects_bad_input) echo "       hint: L1.1 add id, text, channel to Complaint with Field(...) limits and a Literal for channel" ;;
      test_valid_model_output_parses) echo "       hint: L1.2 TriageResult needs category, priority, team, summary, needs_human" ;;
      test_bad_model_output_goes_to_human_review|test_stub_bad_outputs_are_caught) echo "       hint: L1.3 wrap model_validate_json in try/except ValidationError and return human_review(...)" ;;
      test_healthz) echo "       hint: L2.1 return {\"status\": \"ok\"}" ;;
      test_triage_routes_a_dispute|test_bad_model_output_returns_human_review) echo "       hint: L2.2 await llm.complete(...), then return parse_triage(raw)" ;;
      test_slow_model_times_out_to_human_review) echo "       hint: L2.2 put the call inside async with asyncio.timeout(TIMEOUT_S) and catch TimeoutError" ;;
      test_invalid_request_is_rejected_by_the_contract|test_openapi_contract_is_published) echo "       hint: finish L1 first: the API contract comes from your Pydantic models" ;;
      test_mask) echo "       hint: L3.1 ACCOUNT_RE.sub(lambda m: \"EB-******\" + m.group(0)[-4:], text)" ;;
      test_one_json_line_per_request_with_the_audit_fields|test_request_id_is_echoed_and_logged) echo "       hint: L3.2-L3.4 JsonFormatter, the middleware, request.state.log and setup_logging()" ;;
      test_no_full_account_number_in_logs) echo "       hint: L3 mask the whole JSON line in JsonFormatter.format" ;;
    esac
  done
}

explain() {  # explain <label>: the call chain for each part (rule: no black-box steps)
  case "$1" in
    L1) printf '  HOW THIS RUNS: python -m pytest -q tests/test_l1.py\n    tests import Complaint, TriageResult, parse_triage from app/models.py (the file being checked)\n    and the stub model'"'"'s bad replies from app/llm.py. Plain-language list of all 12 checks: bash lab.sh l1 check\n' ;;
    L2) printf '  HOW THIS RUNS: python -m pytest -q tests/test_l2.py\n    tests call /healthz and /triage on app/main.py through FastAPI'"'"'s TestClient (no server needed)\n' ;;
    L3) printf '  HOW THIS RUNS: python -m pytest -q tests/test_l3.py\n    tests check mask() and JsonFormatter in app/logging_setup.py and the request middleware in app/main.py\n' ;;
  esac
}

open_todos() {  # open_todos <label>: TODO lines still open in the file this part checks
  local f
  case "$1" in L1) f=app/models.py ;; L2) f=app/main.py ;; L3) f="app/logging_setup.py app/main.py" ;; *) return ;; esac
  local hits; hits=$(grep -H -n -E "TODO \($1|NotImplementedError\(\"$1" $f 2>/dev/null | head -8)
  [ -n "$hits" ] && { echo "       Still TODO (file:line):"; echo "$hits" | sed 's/^/         /'; }
}

tests() {  # tests <label> <file>
  echo "== $1"
  explain "$1"
  local log="/tmp/grade_$1.log"
  if "$PY" -m pytest -q "$2" >"$log" 2>&1; then
    ok "$1 tests pass"
  else
    bad "$1 tests fail. First problems:"
    grep -E "^(FAILED|ERROR)|NotImplementedError|AssertionError|assert " "$log" | head -4 | sed 's/^/       /'
    hints "$log" | awk '!seen[$0]++'
    open_todos "$1"
    echo "       Full output: $log"
  fi
}

l4_git() {
  echo "== L4a Git"
  echo "  HOW THIS RUNS: git rev-parse (your branch), git check-ignore and git ls-files (.env), git rev-list (commits ahead of main)"
  local branch; branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
  if [ "$branch" != "main" ] && [ "$branch" != "master" ] && [ "$branch" != "?" ]; then ok "on a feature branch ($branch)"
  else bad "you're on '$branch': create a branch, e.g. git switch -c feat/triage-service"; fi
  if git check-ignore -q .env 2>/dev/null; then ok ".env is in .gitignore"; else bad ".env is not ignored: add it to .gitignore"; fi
  if git ls-files --error-unmatch .env >/dev/null 2>&1; then bad ".env is tracked by git: git rm --cached .env"; else ok ".env is not tracked"; fi
  local base ahead
  base=$(git rev-parse --verify -q origin/main >/dev/null && echo origin/main || echo main)
  ahead=$(git rev-list --count "$base"..HEAD 2>/dev/null || echo 0)
  if [ "$ahead" -ge 1 ]; then ok "$ahead commit(s) ahead of $base"; else bad "no commits ahead of $base yet"; fi
  info "Open the PR on GitHub yourself; the template asks what reviewers need."
}

l4_docker() {
  echo "== L4b Docker"
  echo "  HOW THIS RUNS: reads Dockerfile and .dockerignore, then docker build, docker history (secrets), docker run (user, .env, health)"
  if ! command -v docker >/dev/null 2>&1; then
    info "Docker isn't available here (Colab?). Skipping L4b: do it in your codespace."; return
  fi
  local from; from=$(grep -m1 -E '^FROM ' Dockerfile || true)
  if echo "$from" | grep -Eq 'public\.ecr\.aws|mcr\.microsoft\.com'; then ok "base image from ECR Public (avoids Docker Hub anonymous pull limits)"
  else bad "base image '$from': use public.ecr.aws/docker/library/python:3.12.15-slim-bookworm"; fi
  if echo "$from" | grep -Eq ':[0-9]+\.[0-9]+\.[0-9]+-slim' ; then ok "base image is pinned to a patch version and slim"
  else bad "pin a slim patch tag (e.g. 3.12.15-slim-bookworm), never latest"; fi
  if [ -f .dockerignore ] && grep -qE '^\.env$' .dockerignore; then ok ".dockerignore keeps .env out"; else bad "add a .dockerignore with .env in it"; fi
  if ! docker build -q -t s03-triage . >/tmp/grade_build.log 2>&1; then
    bad "docker build failed: see /tmp/grade_build.log"; return
  fi
  ok "image builds"
  local uid; uid=$(docker run --rm --entrypoint id s03-triage -u 2>/dev/null || echo "?")
  if [ "$uid" != "0" ] && [ "$uid" != "?" ]; then ok "runs as a non-root user (uid $uid)"; else bad "container runs as root: add a USER"; fi
  if docker history --no-trunc s03-triage 2>/dev/null | grep -Eiq 'API_KEY|demo-key|GEMINI'; then bad "a secret is visible in docker history: remove ENV/ARG keys"
  else ok "no secret in the image history"; fi
  if docker run --rm --entrypoint sh s03-triage -c 'test ! -e .env && test ! -e /app/.env' 2>/dev/null; then ok "no .env file inside the image"
  else bad ".env is inside the image"; fi
  if grep -qE '^HEALTHCHECK' Dockerfile; then
    local cid status="starting" i
    cid=$(docker run -d s03-triage)
    for i in $(seq 1 60); do
      status=$(docker inspect -f '{{.State.Health.Status}}' "$cid" 2>/dev/null || echo "?")
      [ "$status" = "healthy" ] && break; sleep 1
    done
    docker rm -f "$cid" >/dev/null 2>&1
    if [ "$status" = "healthy" ]; then ok "health check reports healthy"; else bad "health check status after 60 s: $status (did you set --interval=5s?)"; fi
  else
    bad "add a HEALTHCHECK that calls /healthz"
  fi
  info "image size: $(docker image inspect -f '{{.Size}}' s03-triage | awk '{printf "%.0f MB", $1/1000000}')"
}

handover() {
  echo "== Handover note"
  echo "  HOW THIS RUNS: reads HANDOVER.md; each of the four ## sections needs at least one line of your own (TODO lines don't count)"
  local h missing=0
  for h in "What it does" "How to run it" "What is logged" "Known limits"; do
    if awk -v h="## $h" '$0==h{f=1;next} /^## /{f=0} f && NF && $0 !~ /TODO/{c++} END{exit !(c>0)}' HANDOVER.md 2>/dev/null; then :
    else bad "HANDOVER.md: fill in '## $h'"; missing=1; fi
  done
  [ "$missing" = 0 ] && ok "HANDOVER.md has all four sections"
}

case "${1:-all}" in
  l1) tests L1 tests/test_l1.py ;;
  l2) tests L2 tests/test_l2.py ;;
  l3) tests L3 tests/test_l3.py ;;
  l4) l4_git; l4_docker ;;
  handover) handover ;;
  all) tests L1 tests/test_l1.py; tests L2 tests/test_l2.py; tests L3 tests/test_l3.py; l4_git; l4_docker; handover ;;
  *) echo "usage: bash grade.sh l1|l2|l3|l4|handover|all"; exit 2 ;;
esac
echo
echo "Result: $PASS passed, $FAIL to fix."
[ "$FAIL" -eq 0 ]
