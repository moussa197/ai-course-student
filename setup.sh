#!/usr/bin/env bash
set -euo pipefail

# Toujours se placer à la racine du repo
cd "$(dirname "$0")"

PYTHON_BIN="${PYTHON_BIN:-python3}"
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
  echo "==> Creating venv in .venv/"
  "$PYTHON_BIN" -m venv .venv
  if [ -f ".venv/Scripts/activate" ]; then
    ACTIVATE_PATH=".venv/Scripts/activate"
    VENV_PYTHON=".venv/Scripts/python.exe"
  else
    ACTIVATE_PATH=".venv/bin/activate"
    VENV_PYTHON=".venv/bin/python"
  fi
else
  echo "==> venv already exists (.venv/)"
fi

echo "==> Using Python: $PYTHON_BIN"
"$PYTHON_BIN" --version

echo "==> Activating venv"
# shellcheck disable=SC1091
source "$ACTIVATE_PATH"

echo "==> Upgrading pip"
"$VENV_PYTHON" -m pip install --upgrade pip

echo "==> Installing requirements"
"$VENV_PYTHON" -m pip install -r requirements.txt

echo "✅ Setup complete."
echo "Next: run ./run.sh"
