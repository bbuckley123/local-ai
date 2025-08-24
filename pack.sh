#!/usr/bin/env bash
set -euo pipefail

NAME="Local AI (Chat)"
ENTRY="src/app.py"
ASSETS="src/assets"

# resolve venv bin dir of the python running this script
PYBIN="$(python -c 'import sys,os; print(os.path.dirname(sys.executable))')"
FLET="$PYBIN/flet"
PYI="$PYBIN/pyinstaller"

# ensure tools exist in the venv
python -m pip install -U flet pyinstaller >/dev/null

METHOD="${1:-flet}"

if [[ "$METHOD" == "flet" ]]; then
  echo "Packing with flet…"
  "$FLET" pack "$ENTRY" --name "$NAME"
elif [[ "$METHOD" == "pyi" ]]; then
  echo "Packing with PyInstaller…"
  if [[ "${OS:-}" == "Windows_NT" ]]; then
    ADDDATA="--add-data ${ASSETS};${ASSETS}"
  else
    ADDDATA="--add-data ${ASSETS}:${ASSETS}"
  fi
  "$PYI" --noconfirm --windowed --name "$NAME" \
    --collect-binaries llama_cpp --collect-data llama_cpp \
    $ADDDATA "$ENTRY"
else
  echo "Usage: $0 [flet|pyi]"
  exit 2
fi

echo "Done. See ./dist"
