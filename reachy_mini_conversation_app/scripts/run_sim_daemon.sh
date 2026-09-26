#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=/dev/null
source .venv/bin/activate

if lsof -nP -iTCP:8000 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port 8000 is already in use. Quit Reachy Mini Control or run: pkill -f reachy_mini.daemon"
  exit 1
fi

echo "Starting sim daemon (SDK $(python -c 'import reachy_mini; print(reachy_mini.__version__)'))..."
echo "For headless sim (no 3D window): reachy-mini-daemon --sim --headless"
exec mjpython -m reachy_mini.daemon.app.main --sim
