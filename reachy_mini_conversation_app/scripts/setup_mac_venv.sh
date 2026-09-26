#!/usr/bin/env bash
# macOS fixes for uv venv + MuJoCo mjpython + GStreamer (Reachy Mini sim + conversation app).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  echo "Run: uv venv --python 3.12 .venv && uv sync"
  exit 1
fi

# shellcheck source=/dev/null
source .venv/bin/activate

uv pip install 'reachy-mini[mujoco]==1.10.0rc5'

PY_LIB="$(python -c "import sysconfig,sys; print(sysconfig.get_config_var('LIBDIR')+'/libpython'+f'{sys.version_info.major}.{sys.version_info.minor}.dylib')")"
mkdir -p .venv/lib
ln -sf "$PY_LIB" .venv/lib/libpython3.12.dylib

GST_PKG=".venv/lib/python3.12/site-packages/gstreamer_python/lib"
mkdir -p "$GST_PKG/lib"
ln -sf "$PY_LIB" "$GST_PKG/lib/libpython3.12.dylib"

DYLIB="$GST_PKG/gstreamer-1.0/libgstpython.dylib"
if [[ -f "$DYLIB" ]]; then
  mv "$DYLIB" "${DYLIB%.dylib}_.dylib"
  echo "Renamed libgstpython.dylib (macOS GStreamer workaround)"
fi

echo "Venv ready. Daemon SDK: $(python -c 'import reachy_mini; print(reachy_mini.__version__)')"
