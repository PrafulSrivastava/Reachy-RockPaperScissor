"""Round state for a first-to-three match."""

import threading
from typing import Callable

from reachy_mini_rps.rules import TARGET, Result, Score, Throw, judge, match_reached


Phase = str


class Game:
    """Owns the score and the current round. The robot loop drives the phases."""

    def __init__(self, choose: Callable[[], Throw] | None = None) -> None:
        self._choose = choose if choose is not None else _default_choose
        self.phase: Phase = "idle"
        self.score = Score()
        self.reachy_throw: Throw | None = None
        self.player_throw: Throw | None = None
        self.last_result: Result | str | None = None
        self.match_over = False
        self.play_requested = False
        self.stop_requested = False
        self.announcement: str | None = None
        self._lock = threading.Lock()

    def request_play(self) -> None:
        with self._lock:
            self.play_requested = True

    def request_stop(self) -> None:
        with self._lock:
            self.stop_requested = True

    def begin_round(self) -> bool:
        """Commit Reachy's throw. Refuses unless the game is idle."""
        with self._lock:
            return self._begin_round()

    def _begin_round(self) -> bool:
        if self.phase != "idle":
            return False
        self.reachy_throw = self._choose()
        self.player_throw = None
        self.last_result = None
        self.match_over = False
        self.announcement = None
        self.play_requested = False
        self.phase = "countdown"
        return True

    def start_snap(self) -> None:
        with self._lock:
            self.phase = "snap"

    def finish_snap(self, label: Throw | None) -> None:
        """Score the voted hand. An unseen hand discards the round."""
        with self._lock:
            self._finish_snap(label)

    def _finish_snap(self, label: Throw | None) -> None:
        self.player_throw = label
        if label is None or self.reachy_throw is None:
            self.last_result = "no_hand"
            self.phase = "reveal"
            return
        result = judge(label, self.reachy_throw)
        self.last_result = result
        if result == "player":
            self.score.player += 1
        elif result == "reachy":
            self.score.reachy += 1
        self.match_over = match_reached(self.score)
        self.phase = "reveal"

    def reveal_clips(self) -> list[str]:
        """Speech clip names for the reveal, in play order."""
        with self._lock:
            return self._reveal_clips()

    def _reveal_clips(self) -> list[str]:
        clips: list[str] = []
        if self.last_result == "no_hand":
            clips.append("no_hand")
        else:
            clips.append(f"i_choose_{self.reachy_throw}")
            clips.append({"player": "you_win", "reachy": "i_win", "tie": "tie"}[self.last_result])
        clips.append(f"score_{self.score.player}_{self.score.reachy}")
        if self.match_over:
            if self.score.player >= TARGET:
                clips.append("you_win_match")
            else:
                clips.append("i_win_match")
        return clips

    def reaction_pose(self) -> str:
        """Pose name after the result is known."""
        with self._lock:
            poses = {
                "player": "lose",
                "reachy": "win",
                "tie": "watch",
                "no_hand": "watch",
            }
            return poses[str(self.last_result)]

    def back_to_idle(self) -> None:
        """Return to idle. A finished match resets the score after it is announced."""
        with self._lock:
            self._back_to_idle()

    def _back_to_idle(self) -> None:
        if self.match_over:
            if self.score.player >= TARGET:
                self.announcement = "you_win_match"
            else:
                self.announcement = "i_win_match"
            self.score.reset()
            self.match_over = False
        self.reachy_throw = None
        self.player_throw = None
        self.phase = "idle"

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            return {
                "phase": self.phase,
                "player_score": self.score.player,
                "reachy_score": self.score.reachy,
                "reachy_throw": self.reachy_throw,
                "player_throw": self.player_throw,
                "last_result": self.last_result,
                "match_over": self.match_over,
                "announcement": self.announcement,
                "play_requested": self.play_requested,
            }


def _default_choose() -> Throw:
    import secrets

    return secrets.choice(("rock", "paper", "scissors"))
