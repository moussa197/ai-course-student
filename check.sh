#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

ACTIVATE_PATH=""
VENV_PYTHON=""

if [ -f ".venv/Scripts/activate" ]; then
  ACTIVATE_PATH=".venv/Scripts/activate"
  VENV_PYTHON=".venv/Scripts/python.exe"
elif [ -f ".venv/bin/activate" ]; then
  ACTIVATE_PATH=".venv/bin/activate"
  VENV_PYTHON=".venv/bin/python"
fi

if [ -z "$ACTIVATE_PATH" ] || [ -z "$VENV_PYTHON" ]; then
  echo "❌ .venv absent. Lancez d'abord: ./setup.sh"
  exit 1
fi
# shellcheck disable=SC1091
source "$ACTIVATE_PATH"

"$VENV_PYTHON" scripts/check_environment.py
