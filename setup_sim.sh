#!/usr/bin/env bash
# MuJoCo mjpython on macOS + uv venv needs libpython next to the venv (see HF sim docs).
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  echo "Create .venv first: uv venv .venv --python 3.12"
  exit 1
fi

source .venv/bin/activate
uv pip install "reachy-mini[mujoco]==1.8.0"

if [[ "$(uname)" != "Darwin" ]]; then
  echo "On Linux/Windows, start sim with: reachy-mini-daemon --sim"
  exit 0
fi

PY_LIB="$(python -c "import sysconfig; print(sysconfig.get_config_var('LIBDIR'))")/libpython$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')").dylib"
mkdir -p .venv/lib
ln -sf "$PY_LIB" .venv/lib/libpython3.12.dylib
echo "Linked $PY_LIB -> .venv/lib/libpython3.12.dylib"
echo "Start simulation: mjpython -m reachy_mini.daemon.app.main --sim"
