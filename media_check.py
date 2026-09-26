#!/usr/bin/env python3
"""Grab one camera frame, listen for a second, and play a short beep.

The Reachy Mini daemon must already be running on http://localhost:8000.
For the laptop webcam:

    reachy-mini-daemon --mockup-sim

Run with the project venv, not Homebrew Python:

    source .venv/bin/activate
    python media_check.py

See CAMERA_MIC_SPEAKER.md.
"""

from __future__ import annotations

import sys
import time

import numpy as np
from reachy_mini import ReachyMini


def wait_for_frame(mini: ReachyMini, attempts: int = 50) -> np.ndarray:
    for _ in range(attempts):
        frame = mini.media.get_frame()
        if frame is not None:
            return frame
        time.sleep(0.1)
    raise RuntimeError("No camera frame after 5s. Is the daemon running without --no-media?")


def record_seconds(mini: ReachyMini, seconds: float = 1.0) -> np.ndarray:
    mini.media.start_recording()
    time.sleep(0.3)
    chunks: list[np.ndarray] = []
    deadline = time.time() + seconds
    while time.time() < deadline:
        sample = mini.media.get_audio_sample()
        if sample is None:
            time.sleep(0.01)
            continue
        chunks.append(sample)
    mini.media.stop_recording()
    if not chunks:
        raise RuntimeError("Microphone returned no samples.")
    return np.concatenate(chunks, axis=0)


def play_beep(mini: ReachyMini) -> None:
    sample_rate = mini.media.get_output_audio_samplerate()
    count = int(sample_rate * 0.4)
    t = np.arange(count) / sample_rate
    tone = (0.2 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    mini.media.start_playing()
    mini.media.push_audio_sample(tone)
    time.sleep(0.5)
    mini.media.stop_playing()


def main() -> None:
    print("Connecting (first import can take 10–30s)...")
    with ReachyMini(media_backend="local") as mini:
        frame = wait_for_frame(mini)
        print(f"Camera: BGR uint8 {frame.shape}")

        audio = record_seconds(mini)
        peak = float(np.max(np.abs(audio)))
        rate = mini.media.get_input_audio_samplerate()
        print(f"Mic: {audio.shape} float32 @ {rate} Hz, peak {peak:.3f}")

        print("Playing a 440 Hz beep...")
        play_beep(mini)
        print("OK")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
