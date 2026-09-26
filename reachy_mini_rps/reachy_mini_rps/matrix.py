"""Publish round results to the UNO Q LED matrix over MQTT."""

import json
import logging
import threading
import time
from collections.abc import Callable
from typing import TYPE_CHECKING

import paho.mqtt.client as mqtt

if TYPE_CHECKING:
    from reachy_mini_rps.game import Game

logger = logging.getLogger(__name__)

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "digitalpet/rps/result"

_OUTCOMES = {"reachy": "win", "player": "lose", "tie": "tie"}


def matrix_payload(reachy_throw: str | None, result: str | None) -> dict[str, str] | None:
    """Map a scored round to the LED payload. Skips unseen hands."""
    if reachy_throw is None or result not in _OUTCOMES:
        return None
    return {"move": reachy_throw, "outcome": _OUTCOMES[result]}


def send_rps_result(move: str, outcome: str) -> None:
    connected = False

    def on_connect(
        client: mqtt.Client,
        userdata: object,
        flags: object,
        rc: object,
        properties: object = None,
    ) -> None:
        nonlocal connected
        if rc == 0:
            connected = True

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    try:
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_start()

        timeout = 5
        start = time.time()
        while not connected:
            if time.time() - start > timeout:
                logger.warning("Timed out waiting for LED matrix broker")
                client.loop_stop()
                return
            time.sleep(0.1)

        payload = json.dumps({"move": move, "outcome": outcome})
        result = client.publish(TOPIC, payload, qos=1)
        result.wait_for_publish()
        time.sleep(0.5)
        logger.info("Sent LED matrix move=%s outcome=%s", move, outcome)
    except Exception:
        logger.exception("Failed to publish LED matrix result")
    finally:
        client.loop_stop()
        try:
            client.disconnect()
        except Exception:
            logger.exception("Failed to disconnect from LED matrix broker")


def notify(
    game: "Game",
    *,
    send: Callable[[str, str], None] | None = None,
    background: bool = True,
) -> None:
    """Publish the current round to the UNO Q. No-ops when there is nothing to show."""
    payload = matrix_payload(
        game.reachy_throw if isinstance(game.reachy_throw, str) else None,
        str(game.last_result) if game.last_result is not None else None,
    )
    if payload is None:
        return
    publish = send if send is not None else send_rps_result
    if not background:
        publish(payload["move"], payload["outcome"])
        return
    threading.Thread(
        target=publish,
        args=(payload["move"], payload["outcome"]),
        name="rps-matrix",
        daemon=True,
    ).start()
