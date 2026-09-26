"""Laptop webcam frames, leaving the Reachy camera free."""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray


logger = logging.getLogger(__name__)

_DEVICE_LINE = re.compile(r"\[(\d+)\] (.+)$")
_SKIP = ("reachy", "desk view", "capture screen", "iphone")
_PREFER = ("macbook", "facetime", "built-in", "built in", "laptop", "isight")


def parse_avfoundation_video_devices(text: str) -> list[str]:
    """Names in ``avfvideosrc`` device-index order, from ffmpeg's device list."""
    devices: list[str | None] = []
    in_video = False
    for line in text.splitlines():
        if "AVFoundation video devices:" in line:
            in_video = True
            continue
        if "AVFoundation audio devices:" in line:
            break
        if not in_video:
            continue
        match = _DEVICE_LINE.search(line)
        if match is None:
            continue
        index = int(match.group(1))
        while len(devices) <= index:
            devices.append(None)
        devices[index] = match.group(2).strip()
    return [name or "" for name in devices]


def select_laptop_camera(names: Sequence[str]) -> tuple[int, str]:
    """Pick the built-in camera, skipping the robot, phone, and desk-view devices."""
    usable = [
        (index, name)
        for index, name in enumerate(names)
        if name and not any(skip in name.lower() for skip in _SKIP)
    ]
    if not usable:
        raise RuntimeError(
            "No laptop camera found. The only cameras listed were the robot, a phone, or a screen."
        )
    for index, name in usable:
        lowered = name.lower()
        if any(token in lowered for token in _PREFER):
            return index, name
    return usable[0]


def list_avfoundation_video_devices() -> list[str]:
    """Ask ffmpeg for the cameras ``avfvideosrc device-index`` understands."""
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError(
            "ffmpeg is required to find the laptop camera. "
            "Install it, or run without --laptop-camera."
        )
    completed = subprocess.run(
        [ffmpeg, "-hide_banner", "-f", "avfoundation", "-list_devices", "true", "-i", ""],
        capture_output=True,
        text=True,
        check=False,
    )
    listing = f"{completed.stderr}\n{completed.stdout}"
    devices = parse_avfoundation_video_devices(listing)
    if not any(devices):
        raise RuntimeError("ffmpeg did not list any cameras.")
    return devices


class LaptopCamera:
    """BGR frames from the Mac camera, via the GStreamer already used by the SDK."""

    def __init__(self) -> None:
        self.device_name: str | None = None
        self._pipeline: object | None = None
        self._sink: object | None = None

    def open(self) -> None:
        import gi

        gi.require_version("Gst", "1.0")
        from gi.repository import Gst

        Gst.init(None)
        index, name = select_laptop_camera(list_avfoundation_video_devices())
        self.device_name = name
        # Keep the camera's own size. The MacBook camera is portrait (1080x1920);
        # forcing 1280x720 stretches that picture into a landscape frame.
        pipeline = Gst.parse_launch(
            f"avfvideosrc name=cam device-index={index} ! "
            "videoconvert ! video/x-raw,format=BGR ! "
            "appsink name=sink max-buffers=1 drop=true sync=false"
        )
        self._pipeline = pipeline
        self._sink = pipeline.get_by_name("sink")
        change = pipeline.set_state(Gst.State.PLAYING)
        if change == Gst.StateChangeReturn.FAILURE:
            pipeline.set_state(Gst.State.NULL)
            raise RuntimeError(f"Could not open laptop camera {name!r}.")
        logger.info("Laptop camera: %s (device-index %s)", name, index)

    def read(self) -> NDArray[np.uint8] | None:
        """Return the newest frame, or None if the camera has not delivered one yet."""
        sink = self._sink
        pipeline = self._pipeline
        if sink is None or pipeline is None:
            return None

        from gi.repository import Gst

        sample = sink.emit("try-pull-sample", 50 * Gst.MSECOND)
        if sample is None:
            return None
        structure = sample.get_caps().get_structure(0)
        width = int(structure.get_value("width"))
        height = int(structure.get_value("height"))
        buffer = sample.get_buffer()
        ok, mapping = buffer.map(Gst.MapFlags.READ)
        if not ok:
            return None
        try:
            frame = np.frombuffer(mapping.data, dtype=np.uint8)
            expected = height * width * 3
            if frame.size < expected:
                return None
            return np.array(frame[:expected], copy=True).reshape(height, width, 3)
        finally:
            buffer.unmap(mapping)

    def close(self) -> None:
        pipeline = self._pipeline
        self._pipeline = None
        self._sink = None
        if pipeline is None:
            return
        from gi.repository import Gst

        pipeline.set_state(Gst.State.NULL)
