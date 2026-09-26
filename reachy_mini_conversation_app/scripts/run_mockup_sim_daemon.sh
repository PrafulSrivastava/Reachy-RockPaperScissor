#!/usr/bin/env bash
# Lightweight sim: no MuJoCo window, but uses the Mac/laptop webcam (autovideosrc).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=/dev/null
source .venv/bin/activate

if lsof -nP -iTCP:8000 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port 8000 is in use. Quit Reachy Mini Control or stop other daemons."
  exit 1
fi

echo "Starting mockup sim (webcam as Reachy camera, SDK $(python -c 'import reachy_mini; print(reachy_mini.__version__)'))..."
# Do NOT pass --sim here: --sim + --mockup-sim forces MuJoCo video (UDP) and breaks the Mac webcam.
exec reachy-mini-daemon --mockup-sim
