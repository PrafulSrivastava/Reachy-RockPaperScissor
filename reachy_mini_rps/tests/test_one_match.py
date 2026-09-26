import threading

import numpy as np

from reachy_mini_rps.game import Game
from reachy_mini_rps.main import RockPaperScissorsApp


class _Media:
    def __init__(self) -> None:
        self.started = 0
        self.stopped = 0

    def start_recording(self) -> None:
        self.started += 1

    def stop_recording(self) -> None:
        self.stopped += 1

    def get_frame(self) -> np.ndarray:
        return np.zeros((8, 8, 3), dtype=np.uint8)

    def get_audio_sample(self) -> list[float]:
        return [0.2, -0.2, 0.2]

    def play_sound(self, path: str) -> None:
        return None


class _Reachy:
    def __init__(self) -> None:
        self.media = _Media()

    def goto_target(self, **kwargs: object) -> None:
        return None


class _Tracker:
    last_points = None

    def read_throw(self, frame: object) -> str:
        return "paper"

    def close(self) -> None:
        return None


def test_one_match_returns_to_the_caller_when_someone_wins(monkeypatch) -> None:
    monkeypatch.setattr("reachy_mini_rps.main.HandTracker", lambda: _Tracker())
    monkeypatch.setattr("reachy_mini_rps.main.Game", lambda: Game(choose=lambda: "rock"))
    monkeypatch.setattr("reachy_mini_rps.main.speech.say", lambda media, name: None)
    monkeypatch.setattr("reachy_mini_rps.main.matrix.notify", lambda game: None)
    reachy = _Reachy()

    result = RockPaperScissorsApp().play_one_match(reachy, threading.Event())

    assert result == {
        "status": "match_over",
        "winner": "player",
        "player_score": 3,
        "reachy_score": 0,
    }
    assert reachy.media.started == 0
    assert reachy.media.stopped == 0
