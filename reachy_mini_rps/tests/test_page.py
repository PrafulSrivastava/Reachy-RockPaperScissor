import io

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

from reachy_mini_rps.game import Game
from reachy_mini_rps.hand_tracker import jpeg_with_points
from reachy_mini_rps.main import RockPaperScissorsApp


def test_score_page_reports_state_and_starts_a_round() -> None:
    app = RockPaperScissorsApp()
    game = Game(choose=lambda: "rock")
    app._install_routes(game)
    assert app.settings_app is not None
    client = TestClient(app.settings_app)

    page = client.get("/")
    assert page.status_code == 200
    assert "Rock, paper, scissors" in page.text
    assert 'src="/frame.jpg"' in page.text
    assert 'width="640"' not in page.text
    assert 'height="360"' not in page.text

    state = client.get("/state")
    assert state.status_code == 200
    assert state.json()["phase"] == "idle"
    assert state.json()["player_score"] == 0

    frame = client.get("/frame.jpg")
    assert frame.status_code == 200
    assert frame.headers["content-type"] == "image/jpeg"
    assert frame.content[:2] == b"\xff\xd8"

    assert client.post("/play").status_code == 200
    assert game.play_requested is True

    assert client.post("/stop").status_code == 200
    assert game.stop_requested is True
    assert app.stop_event.is_set()


def test_preview_draws_green_landmark_dots() -> None:
    frame = np.zeros((48, 64, 3), dtype=np.uint8)
    jpeg = jpeg_with_points(frame, [(0.5, 0.5, 0.0)])
    image = Image.open(io.BytesIO(jpeg))
    pixel = image.getpixel((image.width // 2, image.height // 2))
    assert pixel[1] > 180 and pixel[1] > pixel[0]
