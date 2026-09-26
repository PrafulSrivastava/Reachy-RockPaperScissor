#!/usr/bin/env bash
# Stop conversation app, sim daemon, and Reachy Mini Control helpers on ports 8000/7860.
set -euo pipefail

pkill -f reachy-mini-conversation-app 2>/dev/null || true
pkill -f reachy-mini-daemon 2>/dev/null || true
pkill -f "reachy_mini.daemon.app.main" 2>/dev/null || true
pkill -f mjpython 2>/dev/null || true

sleep 1

if lsof -nP -iTCP:8000 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port 8000 still in use — quit Reachy Mini Control from the menu bar, then run this again."
  lsof -nP -iTCP:8000 -sTCP:LISTEN
  exit 1
fi

echo "Stopped Reachy processes (ports 8000 and 7860 should be free)."
