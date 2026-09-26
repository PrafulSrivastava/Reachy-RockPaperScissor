from reachy_mini_rps.laptop_camera import (
    parse_avfoundation_video_devices,
    select_laptop_camera,
)
from reachy_mini_rps.main import parse_args


FFMPEG_LIST = """
[AVFoundation indev @ 0x1] AVFoundation video devices:
[AVFoundation indev @ 0x1] [0] Reachy Mini Camera
[AVFoundation indev @ 0x1] [1] MacBook Pro Camera
[AVFoundation indev @ 0x1] [2] Praful's iPhone (2) Desk View Camera
[AVFoundation indev @ 0x1] [3] MacBook Pro Desk View Camera
[AVFoundation indev @ 0x1] [4] Praful's iPhone (2) Camera
[AVFoundation indev @ 0x1] [5] Capture screen 0
[AVFoundation indev @ 0x1] AVFoundation audio devices:
[AVFoundation indev @ 0x1] [0] Reachy Mini Audio
[AVFoundation indev @ 0x1] [1] MacBook Pro Microphone
"""


def test_parser_keeps_video_indexes_and_drops_audio() -> None:
    names = parse_avfoundation_video_devices(FFMPEG_LIST)
    assert names[0] == "Reachy Mini Camera"
    assert names[1] == "MacBook Pro Camera"
    assert "Reachy Mini Audio" not in names
    assert len(names) == 6


def test_selects_macbook_camera_not_the_robot_or_desk_view() -> None:
    index, name = select_laptop_camera(parse_avfoundation_video_devices(FFMPEG_LIST))
    assert (index, name) == (1, "MacBook Pro Camera")


def test_selects_facetime_when_it_is_the_only_built_in_camera() -> None:
    index, name = select_laptop_camera(["Reachy Mini Camera", "FaceTime HD Camera"])
    assert (index, name) == (1, "FaceTime HD Camera")


def test_laptop_camera_flag_defaults_off() -> None:
    assert parse_args([]).laptop_camera is False
    assert parse_args(["--laptop-camera"]).laptop_camera is True
