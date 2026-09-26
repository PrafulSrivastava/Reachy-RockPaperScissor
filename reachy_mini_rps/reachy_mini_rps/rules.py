"""Throw comparison and match score."""

from dataclasses import dataclass
from typing import Literal


Throw = Literal["rock", "paper", "scissors"]
Result = Literal["player", "reachy", "tie"]

THROWS: tuple[Throw, ...] = ("rock", "paper", "scissors")
TARGET = 3

_BEATS: dict[Throw, Throw] = {
    "rock": "scissors",
    "scissors": "paper",
    "paper": "rock",
}


def judge(player: Throw, reachy: Throw) -> Result:
    """Return who wins this throw. The same throw is a tie."""
    if player == reachy:
        return "tie"
    if _BEATS[player] == reachy:
        return "player"
    return "reachy"


@dataclass
class Score:
    """First to TARGET wins the match."""

    player: int = 0
    reachy: int = 0

    def reset(self) -> None:
        self.player = 0
        self.reachy = 0


def match_reached(score: Score) -> bool:
    """True once either side has reached the match target."""
    return score.player >= TARGET or score.reachy >= TARGET
