#!/usr/bin/env bash
# Same machine, one script: visual sim in background is unreliable on macOS (needs GUI).
# Prefer launch_visual_sim_and_voice_mac.sh on Mac, or run two terminals manually.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Visual sim must run in a foreground terminal (MuJoCo window)."
echo ""
echo "Terminal 1:"
echo "  cd '$ROOT' && ./scripts/run_sim_daemon.sh"
echo ""
echo "Terminal 2 (after http://localhost:8000/docs works):"
echo "  cd '$ROOT' && ./scripts/run_conversation.sh"
echo ""
if [[ "$(uname)" == "Darwin" ]]; then
  read -r -p "Open both in Terminal.app now? [y/N] " ans
  if [[ "${ans,,}" == "y" ]]; then
    exec "$ROOT/scripts/launch_visual_sim_and_voice_mac.sh"
  fi
fi
