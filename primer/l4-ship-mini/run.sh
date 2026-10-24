#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY=$(command -v python3 || command -v python)

case "${1:-all}" in
  git)    "$PY" git_demo.py ;;
  docker) "$PY" docker_demo.py ;;
  all)
    "$PY" git_demo.py
    echo
    "$PY" docker_demo.py
    ;;
  *)
    echo "usage: bash run.sh git | docker | all"
    exit 2
    ;;
esac
