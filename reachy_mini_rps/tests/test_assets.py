import numpy as np
import pytest

from reachy_mini_rps.poses import pose_for
from reachy_mini_rps.speech import duration, required_clips


def test_every_clip_has_audio() -> None:
    names = required_clips()
    assert "score_3_3" not in names
    assert len(names) == 29
    for name in names:
        assert duration(name) > 0.05, name


@pytest.mark.parametrize(
    "name",
    ["watch", "nod", "rock", "paper", "scissors", "win", "lose"],
)
def test_pose_shapes(name: str) -> None:
    head, antennas = pose_for(name)
    assert head.shape == (4, 4)
    assert antennas.shape == (2,)
    assert float(np.max(np.abs(antennas))) < 3.0


def test_unknown_pose_is_rejected() -> None:
    with pytest.raises(ValueError):
        pose_for("shrug")
