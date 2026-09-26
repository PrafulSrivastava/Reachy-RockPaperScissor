#!/usr/bin/env bash
# Render game clips with Qwen3-TTS CustomVoice, speaker Aiden.
# Needs an Apple Silicon Mac. The model download is several gigabytes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
exec uv run --no-project --with mlx-audio python scripts/generate_speech.py
