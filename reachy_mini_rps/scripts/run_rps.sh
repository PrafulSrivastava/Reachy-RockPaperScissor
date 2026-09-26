#!/usr/bin/env bash
# Play rock-paper-scissors against Reachy Mini.
# Pass --laptop-camera to watch the Mac camera instead of the robot camera.
# Start the daemon first (real robot, or the webcam mockup).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
# shellcheck source=/dev/null
source "$REPO/reachy_mini_conversation_app/.venv/bin/activate"

if pgrep -f "reachy-mini-conversation-app" >/dev/null 2>&1; then
  echo "Stop the conversation app first. It uses the same camera and microphone."
  exit 1
fi

if ! lsof -nP -iTCP:8000 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Nothing is listening on port 8000."
  echo "Start the webcam daemon first: ./reachy_mini_conversation_app/scripts/run_mockup_sim_daemon.sh"
  exit 1
fi

exec python -m reachy_mini_rps.main "$@"
