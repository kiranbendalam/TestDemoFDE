#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY=$(command -v python3 || command -v python)

case "${1:-all}" in
  before) "$PY" before.py ;;
  mask)   "$PY" mask_demo.py ;;
  after)  "$PY" after.py ;;
  all)
    "$PY" before.py
    echo
    "$PY" mask_demo.py
    echo
    "$PY" after.py
    ;;
  *)
    echo "usage: bash run.sh before | mask | after | all"
    exit 2
    ;;
esac
