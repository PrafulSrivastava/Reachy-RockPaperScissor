#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=/dev/null
source .venv/bin/activate

if ! curl -sf --max-time 2 http://localhost:8000/docs >/dev/null; then
  echo "Daemon not reachable at http://localhost:8000 — start scripts/run_sim_daemon.sh first."
  exit 1
fi

# Camera uses the daemon video pipeline (Mac webcam in mockup-sim, MuJoCo robot view in --sim).
exec reachy-mini-conversation-app --ui "$@"
