"""Play short WAV clips on the Reachy speaker and keep the mic quiet afterward."""

import time
import wave
from pathlib import Path


ASSETS = Path(__file__).resolve().parent / "assets"
DURATIONS: dict[str, float] = {}
_MIC_TAIL_S = 0.8
_quiet_until = 0.0

COUNTDOWN_CLIPS = ("ready", "three", "two", "one", "shoot")


def clip_path(name: str) -> Path:
    return ASSETS / f"{name}.wav"


def duration(name: str) -> float:
    """Seconds of audio in the named clip. Cached in DURATIONS."""
    if name not in DURATIONS:
        path = clip_path(name)
        with wave.open(str(path), "rb") as handle:
            rate = handle.getframerate()
            frames = handle.getnframes()
        DURATIONS[name] = (frames / float(rate)) if rate else 0.0
    return DURATIONS[name]


def accepting_mic() -> bool:
    """False while a clip is playing and for a short echo tail after it."""
    return time.monotonic() >= _quiet_until


def say(media: object, clip_name: str) -> None:
    """Play a clip. play_sound returns immediately, so this sleeps for its duration."""
    global _quiet_until
    path = clip_path(clip_name)
    length = duration(clip_name)
    _quiet_until = time.monotonic() + length + _MIC_TAIL_S
    play_sound = getattr(media, "play_sound")
    play_sound(str(path))
    time.sleep(length)


def required_clips() -> list[str]:
    """Every clip the match can ask the speaker to play."""
    names = [
        *COUNTDOWN_CLIPS,
        "i_choose_rock",
        "i_choose_paper",
        "i_choose_scissors",
        "you_win",
        "i_win",
        "tie",
        "no_hand",
        "you_win_match",
        "i_win_match",
    ]
    for player in range(4):
        for reachy in range(4):
            if (player, reachy) == (3, 3):
                continue
            names.append(f"score_{player}_{reachy}")
    return names
