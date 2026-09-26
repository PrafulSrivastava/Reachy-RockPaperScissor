import pytest

from reachy_mini_rps.rules import TURNS, Score, judge, match_clip, match_reached


PAIRS = [
    ("rock", "rock", "tie"),
    ("rock", "paper", "reachy"),
    ("rock", "scissors", "player"),
    ("paper", "rock", "player"),
    ("paper", "paper", "tie"),
    ("paper", "scissors", "reachy"),
    ("scissors", "rock", "reachy"),
    ("scissors", "paper", "player"),
    ("scissors", "scissors", "tie"),
]


@pytest.mark.parametrize("player,reachy,expected", PAIRS)
def test_judge_each_pair(player: str, reachy: str, expected: str) -> None:
    assert judge(player, reachy) == expected


def test_match_ends_after_three_turns() -> None:
    score = Score()
    assert match_reached(score) is False
    score.player = 2
    score.turns = TURNS - 1
    assert match_reached(score) is False
    score.turns = TURNS
    assert match_reached(score) is True
    assert match_clip(score) == "you_win_match"

    tied = Score(player=1, reachy=1, turns=TURNS)
    assert match_reached(tied) is True
    assert match_clip(tied) == "tie"
