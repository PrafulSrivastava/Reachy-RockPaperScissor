#!/usr/bin/env bash
# Wait until the Reachy daemon responds on port 8000.
set -euo pipefail
TRIES="${1:-60}"
for ((i = 1; i <= TRIES; i++)); do
  if curl -sf --max-time 2 http://127.0.0.1:8000/docs >/dev/null; then
    echo "Daemon ready (http://localhost:8000)"
    exit 0
  fi
  sleep 2
done
echo "Timed out waiting for daemon on port 8000" >&2
exit 1
