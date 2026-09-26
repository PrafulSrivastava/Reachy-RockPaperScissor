"""Hand the robot to one rock-paper-scissors match, then return to the conversation."""

import asyncio
import logging
import threading
from typing import Any

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies


logger = logging.getLogger(__name__)


class PlayRockPaperScissors(Tool):
    """Play one three-turn match, then hand the microphone back."""

    name = "play_rock_paper_scissors"
    description = (
        "Switch out of conversation and play one three-turn rock-paper-scissors match. "
        "Call this when the user asks to play rock-paper-scissors. "
        "The game uses the microphone, speaker, camera, and head until the match ends. "
        "Do not keep talking after calling it. When it returns, resume the conversation "
        "and comment on the winner in one sentence."
    )
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        """Suspend conversation audio, play one match, then restore it."""
        enter_activity = deps.enter_activity
        exit_activity = deps.exit_activity
        if enter_activity is None or exit_activity is None:
            return {"error": "rock-paper-scissors is unavailable in this runtime"}

        logger.info("Tool call: play_rock_paper_scissors")

        def _run() -> dict[str, Any]:
            enter_activity()
            try:
                from reachy_mini_rps.main import RockPaperScissorsApp

                raw = RockPaperScissorsApp().play_one_match(deps.reachy_mini, threading.Event())
                if not isinstance(raw, dict):
                    return {"error": "rock-paper-scissors returned an unexpected result"}
                return {
                    "status": raw.get("status", "stopped"),
                    "winner": raw.get("winner"),
                    "player_score": raw.get("player_score"),
                    "reachy_score": raw.get("reachy_score"),
                }
            finally:
                exit_activity()

        try:
            return await asyncio.to_thread(_run)
        except Exception as exc:
            logger.error("play_rock_paper_scissors failed: %s", exc)
            return {"error": f"play_rock_paper_scissors failed: {type(exc).__name__}: {exc}"}
