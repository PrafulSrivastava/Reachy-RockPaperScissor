import pytest

from reachy_mini_rps.rules import TARGET, Score, judge, match_reached


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


def test_first_to_three_transition() -> None:
    score = Score()
    assert match_reached(score) is False
    score.player = TARGET - 1
    assert match_reached(score) is False
    score.player = TARGET
    assert match_reached(score) is True

    other = Score()
    other.reachy = TARGET
    assert match_reached(other) is True
