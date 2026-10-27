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
else
  echo "❌ .venv absent. Lancez d'abord: ./setup.sh"
  exit 1
fi

# shellcheck disable=SC1091
source "$ACTIVATE_PATH"

echo "==> Starting Jupyter Lab..."
"$VENV_PYTHON" -m jupyterlab
