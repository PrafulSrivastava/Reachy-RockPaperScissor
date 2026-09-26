"""Throw comparison and match score."""

from dataclasses import dataclass
from typing import Literal


Throw = Literal["rock", "paper", "scissors"]
Result = Literal["player", "reachy", "tie"]

THROWS: tuple[Throw, ...] = ("rock", "paper", "scissors")
TURNS = 3

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
    """Points and completed turns in a three-turn match."""

    player: int = 0
    reachy: int = 0
    turns: int = 0

    def reset(self) -> None:
        self.player = 0
        self.reachy = 0
        self.turns = 0


def match_reached(score: Score) -> bool:
    """True once three turns have been scored."""
    return score.turns >= TURNS


def match_winner(score: Score) -> Result:
    """Who leads after the scored turns. An even score is a tie."""
    if score.player > score.reachy:
        return "player"
    if score.reachy > score.player:
        return "reachy"
    return "tie"


def match_clip(score: Score) -> str:
    """Speech clip for the end of the match."""
    return {"player": "you_win_match", "reachy": "i_win_match", "tie": "tie"}[match_winner(score)]
