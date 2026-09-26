"""Camera hand labels via MediaPipe Hand Landmarker."""

import io
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageDraw

from reachy_mini_rps.gestures import classify_landmarks
from reachy_mini_rps.rules import Throw
from reachy_mini_rps.speech import ASSETS


MODEL_PATH = ASSETS / "hand_landmarker.task"


class HandTracker:
    """Classify the clearest hand in a BGR frame. Each call is an independent image."""

    def __init__(self, model_path: Path | None = None) -> None:
        self._model_path = model_path or MODEL_PATH
        self._detector: object | None = None
        self.last_points: list[tuple[float, float, float]] | None = None

    def read_throw(self, frame_bgr: NDArray[np.uint8] | None) -> Throw | None:
        """Return rock, paper, scissors, or None when no clear hand is in frame."""
        self.last_points = None
        if frame_bgr is None:
            return None

        import mediapipe as mp

        rgb = np.ascontiguousarray(frame_bgr[:, :, ::-1])
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self._landmarker().detect(image)
        landmarks = getattr(result, "hand_landmarks", None) or []
        if not landmarks:
            return None

        best = 0
        best_score = -1.0
        for index, categories in enumerate(getattr(result, "handedness", None) or []):
            score = float(categories[0].score) if categories else 0.0
            if score > best_score:
                best_score = score
                best = index

        chosen = landmarks[best]
        points = [(float(point.x), float(point.y), float(point.z)) for point in chosen]
        self.last_points = points
        return classify_landmarks(points)

    def close(self) -> None:
        detector = self._detector
        self._detector = None
        if detector is not None:
            close = getattr(detector, "close", None)
            if close is not None:
                close()

    def _landmarker(self) -> object:
        if self._detector is not None:
            return self._detector

        from mediapipe.tasks.python.core.base_options import BaseOptions
        from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=str(self._model_path),
                delegate=BaseOptions.Delegate.CPU,
            ),
            running_mode=RunningMode.IMAGE,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._detector = HandLandmarker.create_from_options(options)
        return self._detector


def jpeg_with_points(
    frame_bgr: NDArray[np.uint8],
    points: list[tuple[float, float, float]] | None,
    max_width: int = 640,
) -> bytes:
    """Encode a camera frame, drawing landmark dots when a hand was found.

    The preview is scaled down before JPEG encoding. Landmark coordinates stay
    normalized, so dots still land on the smaller image.
    """
    rgb = np.ascontiguousarray(frame_bgr[:, :, ::-1])
    image = Image.fromarray(rgb, mode="RGB")
    if image.width > max_width:
        height = max(1, int(image.height * max_width / image.width))
        image = image.resize((max_width, height), Image.Resampling.BILINEAR)
    if points:
        draw = ImageDraw.Draw(image)
        width, height = image.size
        for x, y, _z in points:
            px = x * width
            py = y * height
            radius = 5
            draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=(80, 220, 120))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=70)
    return buffer.getvalue()
