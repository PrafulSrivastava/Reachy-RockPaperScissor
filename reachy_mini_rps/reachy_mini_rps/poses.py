"""Head and antenna poses for each throw and reaction."""

import numpy as np
from numpy.typing import NDArray

from reachy_mini.utils import create_head_pose


_WATCH_ANTENNAS = np.array([0.17, -0.17], dtype=np.float64)


def pose_for(name: str) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Return a head pose and antenna angles in radians, [right, left]."""
    if name == "rock":
        head = create_head_pose(pitch=12, degrees=True)
        antennas = np.array([0.9, -0.9], dtype=np.float64)
    elif name == "paper":
        head = create_head_pose(pitch=-8, degrees=True)
        antennas = np.array([-1.0, 1.0], dtype=np.float64)
    elif name == "scissors":
        head = create_head_pose(roll=15, degrees=True)
        antennas = np.array([-1.1, -0.4], dtype=np.float64)
    elif name == "win":
        head = create_head_pose(pitch=-12, degrees=True)
        antennas = np.array([-0.5, 0.5], dtype=np.float64)
    elif name == "lose":
        head = create_head_pose(pitch=18, degrees=True)
        antennas = np.array([0.3, -0.3], dtype=np.float64)
    elif name == "nod":
        head = create_head_pose(pitch=10, degrees=True)
        antennas = _WATCH_ANTENNAS.copy()
    elif name == "watch":
        head = create_head_pose(pitch=-5, degrees=True)
        antennas = _WATCH_ANTENNAS.copy()
    else:
        raise ValueError(f"Unknown pose: {name}")
    return head, antennas
