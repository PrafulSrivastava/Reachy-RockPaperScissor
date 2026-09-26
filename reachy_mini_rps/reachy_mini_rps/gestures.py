"""Map hand landmarks to rock, paper, or scissors."""

from collections import Counter
from typing import Sequence

from reachy_mini_rps.rules import Throw


Point = tuple[float, float, float]

# MediaPipe hand landmark indices.
_WRIST = 0
_FINGERS = (
    ("index", 6, 8),
    ("middle", 10, 12),
    ("ring", 14, 16),
    ("pinky", 18, 20),
)


def _dist(a: Point, b: Point) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def _extended(points: Sequence[Point], tip: int, pip: int) -> bool:
    wrist = points[_WRIST]
    return _dist(points[tip], wrist) > _dist(points[pip], wrist)


def classify_landmarks(points: Sequence[Point]) -> Throw | None:
    """Label one hand. Ambiguous shapes return None.

    A finger counts as extended when its tip is farther from the wrist than
    its PIP joint, so the hand does not need to point up in the image.
    """
    if len(points) < 21:
        return None

    extended = {name for name, pip, tip in _FINGERS if _extended(points, tip, pip)}
    count = len(extended)
    if count >= 4:
        return "paper"
    if extended == {"index", "middle"}:
        return "scissors"
    if count <= 1:
        return "rock"
    return None


def majority(labels: Sequence[Throw | None]) -> Throw | None:
    """Pick the most common label. Ties and empty votes return None."""
    counts = Counter(label for label in labels if label is not None)
    if not counts:
        return None
    ranked = counts.most_common()
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return None
    return ranked[0][0]
