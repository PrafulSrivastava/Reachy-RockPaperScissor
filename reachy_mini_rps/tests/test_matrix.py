import json

from reachy_mini_rps.game import Game
from reachy_mini_rps.matrix import TOPIC, matrix_payload, notify, send_rps_result


def test_reachy_win_sends_reachy_throw_and_win() -> None:
    assert matrix_payload("paper", "reachy") == {"move": "paper", "outcome": "win"}


def test_player_win_sends_reachy_throw_and_lose() -> None:
    assert matrix_payload("scissors", "player") == {"move": "scissors", "outcome": "lose"}


def test_tie_sends_reachy_throw_and_tie() -> None:
    assert matrix_payload("rock", "tie") == {"move": "rock", "outcome": "tie"}


def test_no_hand_does_not_send() -> None:
    assert matrix_payload("rock", "no_hand") is None
    assert matrix_payload(None, "reachy") is None


def test_notify_publishes_after_a_scored_round() -> None:
    game = Game(choose=lambda: "paper")
    game.begin_round()
    game.finish_snap("rock")
    sent: list[tuple[str, str]] = []
    notify(game, send=lambda move, outcome: sent.append((move, outcome)), background=False)
    assert sent == [("paper", "win")]


def test_notify_skips_no_hand() -> None:
    game = Game(choose=lambda: "rock")
    game.begin_round()
    game.finish_snap(None)
    sent: list[tuple[str, str]] = []
    notify(game, send=lambda move, outcome: sent.append((move, outcome)), background=False)
    assert sent == []


def test_send_rps_result_publishes_json_to_the_matrix_topic(monkeypatch) -> None:
    published: list[tuple[str, str, int]] = []

    class FakeMessageInfo:
        def wait_for_publish(self) -> None:
            return None

    class FakeClient:
        on_connect = None

        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def connect(self, broker: str, port: int, keepalive: int = 60) -> None:
            assert self.on_connect is not None
            self.on_connect(self, None, None, 0)

        def loop_start(self) -> None:
            return None

        def loop_stop(self) -> None:
            return None

        def disconnect(self) -> None:
            return None

        def publish(self, topic: str, payload: str, qos: int = 0) -> FakeMessageInfo:
            published.append((topic, payload, qos))
            return FakeMessageInfo()

    monkeypatch.setattr("reachy_mini_rps.matrix.mqtt.Client", FakeClient)
    monkeypatch.setattr("reachy_mini_rps.matrix.time.sleep", lambda _seconds: None)
    send_rps_result("rock", "win")
    assert published == [(TOPIC, json.dumps({"move": "rock", "outcome": "win"}), 1)]
