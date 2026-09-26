#!/usr/bin/env bash
# Start MuJoCo visual sim + conversation voice on macOS (two Terminal windows).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ "$(uname)" != "Darwin" ]]; then
  echo "This launcher is for macOS. Use two terminals:"
  echo "  1) mjpython -m reachy_mini.daemon.app.main --sim"
  echo "  2) reachy-mini-conversation-app --ui"
  exit 1
fi

if [[ ! -d .venv ]]; then
  echo "Missing .venv — run: ./scripts/setup_mac_venv.sh"
  exit 1
fi

# shellcheck source=/dev/null
source .venv/bin/activate

if lsof -nP -iTCP:8000 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port 8000 in use — stopping existing Reachy daemons/apps..."
  "$ROOT/scripts/stop_all.sh" || exit 1
fi

SIM_CMD="cd '$ROOT' && source .venv/bin/activate && echo '=== Visual sim (keep this window open) ===' && mjpython -m reachy_mini.daemon.app.main --sim"
VOICE_CMD="cd '$ROOT' && source .venv/bin/activate && ./scripts/wait_for_daemon.sh 90 && echo '=== Conversation app ===' && reachy-mini-conversation-app --ui"

osascript <<EOF
tell application "Terminal"
  activate
  do script "$SIM_CMD"
  delay 2
  do script "$VOICE_CMD"
end tell
EOF

echo ""
echo "Opened two Terminal windows:"
echo "  1) MuJoCo sim (3D robot)"
echo "  2) Conversation app (starts after daemon is up)"
echo ""
echo "Then open http://localhost:7860 → Talk (allow Microphone for Terminal)."
