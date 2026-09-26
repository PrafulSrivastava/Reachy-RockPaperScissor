#!/usr/bin/env python3
"""Play a sad emotion from the official Reachy Mini emotions library."""

import argparse

from reachy_mini import ReachyMini
from reachy_mini.motion.recorded_move import RecordedMoves

EMOTIONS_DATASET = "pollen-robotics/reachy-mini-emotions-library"
# Other sad moves in the dataset: sad2, no_sad1, yes_sad1
SAD_MOVE = "sad1"


def main() -> None:
    parser = argparse.ArgumentParser(description="Play a sad Reachy Mini emote.")
    parser.add_argument(
        "--with-sound",
        action="store_true",
        help="Enable emote audio (needs Reachy USB audio + working daemon media).",
    )
    args = parser.parse_args()

    library = RecordedMoves(EMOTIONS_DATASET)
    if SAD_MOVE not in library.list_moves():
        sad_moves = sorted(m for m in library.list_moves() if "sad" in m.lower())
        raise SystemExit(
            f"Move '{SAD_MOVE}' not found. Sad moves available: {sad_moves or 'none'}"
        )

    move = library.get(SAD_MOVE)
    media_backend = "default" if args.with_sound else "no_media"
    with ReachyMini(
        connection_mode="localhost_only",
        media_backend=media_backend,
        log_level="WARNING",
    ) as mini:
        print(f"Playing {SAD_MOVE} ({move.description})...")
        mini.play_move(move, initial_goto_duration=0.5, sound=args.with_sound)
    print("Done.")


if __name__ == "__main__":
    main()
