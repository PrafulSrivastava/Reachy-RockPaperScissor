#!/usr/bin/env python3
"""Smoke test: daemon reachable + SDK connects and accepts motion commands.

From the project folder, activate the venv then run (see README steps below):

  source .venv/bin/activate
  python verify_setup.py

First-time setup:

  uv venv .venv --python 3.12
  source .venv/bin/activate
  uv pip install "reachy-mini"

Requires the Reachy Mini daemon (desktop app) running on http://localhost:8000.
"""

from __future__ import annotations

import sys
import urllib.error
import urllib.request

DAEMON_DOCS_URL = "http://localhost:8000/docs"


def check_daemon() -> None:
    try:
        with urllib.request.urlopen(DAEMON_DOCS_URL, timeout=5) as resp:
            if resp.status != 200:
                raise RuntimeError(f"unexpected status {resp.status}")
    except urllib.error.URLError as exc:
        raise SystemExit(
            "Daemon not reachable at http://localhost:8000 — "
            "start the Reachy Mini app (or reachy-mini-daemon) and try again.\n"
            f"  ({exc})"
        ) from exc
    print("✓ Daemon responding at http://localhost:8000")


def check_sdk() -> None:
    try:
        from reachy_mini import ReachyMini
    except ImportError:
        raise SystemExit(
            "reachy_mini is not installed in this Python.\n"
            "  source .venv/bin/activate && uv pip install -r requirements.txt"
        ) from None

    print("✓ reachy_mini import OK")
    print("  Connecting to robot (first run can take ~30s; GStreamer warnings are OK)...")
    with ReachyMini() as mini:
        print(f"✓ Connected ({type(mini).__name__})")
        mini.goto_target(antennas=[0.2, -0.2], duration=0.25)
        mini.goto_target(antennas=[0, 0], duration=0.25)
    print("✓ Motion command accepted")


def main() -> int:
    print("Reachy Mini setup verification\n")
    check_daemon()
    check_sdk()
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
