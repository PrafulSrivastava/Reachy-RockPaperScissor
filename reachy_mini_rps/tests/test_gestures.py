from reachy_mini_rps.gestures import classify_landmarks, majority


def _hand(extended: set[str]) -> list[tuple[float, float, float]]:
    """21 landmarks. Wrist at the origin. Extended tips sit beyond the PIP joint."""
    points = [(0.0, 0.0, 0.0)] * 21
    fingers = {
        "thumb": (3, 4, (1.0, 0.0, 1.0)),
        "index": (6, 8, (1.0, 0.0, 0.0)),
        "middle": (10, 12, (0.0, 1.0, 0.0)),
        "ring": (14, 16, (0.0, 0.0, 1.0)),
        "pinky": (18, 20, (1.0, 1.0, 0.0)),
    }
    for name, (pip_i, tip_i, axis) in fingers.items():
        length = (axis[0] ** 2 + axis[1] ** 2 + axis[2] ** 2) ** 0.5
        unit = (axis[0] / length, axis[1] / length, axis[2] / length)
        points[pip_i] = unit
        tip_scale = 2.0 if name in extended else 0.8
        points[tip_i] = (unit[0] * tip_scale, unit[1] * tip_scale, unit[2] * tip_scale)
    return points


def test_fist_is_rock() -> None:
    assert classify_landmarks(_hand(set())) == "rock"


def test_one_finger_is_rock() -> None:
    assert classify_landmarks(_hand({"index"})) == "rock"


def test_open_hand_is_paper() -> None:
    assert classify_landmarks(_hand({"index", "middle", "ring", "pinky"})) == "paper"


def test_two_fingers_are_scissors() -> None:
    assert classify_landmarks(_hand({"index", "middle"})) == "scissors"


def test_three_fingers_are_unlabeled() -> None:
    assert classify_landmarks(_hand({"index", "middle", "ring"})) is None


def test_index_and_ring_are_unlabeled() -> None:
    assert classify_landmarks(_hand({"index", "ring"})) is None


def test_short_landmark_list_is_unlabeled() -> None:
    assert classify_landmarks([(0.0, 0.0, 0.0)]) is None


def test_majority_picks_the_repeated_label() -> None:
    assert majority(["rock", None, "rock", "paper"]) == "rock"


def test_majority_tie_is_unlabeled() -> None:
    assert majority(["rock", "paper"]) is None


def test_majority_all_none_is_unlabeled() -> None:
    assert majority([None, None, None]) is None
