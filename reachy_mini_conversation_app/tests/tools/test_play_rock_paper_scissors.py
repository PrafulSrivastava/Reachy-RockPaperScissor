from unittest.mock import MagicMock

import pytest

from reachy_mini_conversation_app.tools.core_tools import ToolDependencies
from reachy_mini_conversation_app.tools.play_rock_paper_scissors import PlayRockPaperScissors


def test_play_rock_paper_scissors_has_no_required_arguments() -> None:
    """The model should be able to start a match without extra arguments."""
    assert PlayRockPaperScissors.parameters_schema["required"] == []


@pytest.mark.asyncio
async def test_play_rock_paper_scissors_needs_the_activity_handoff() -> None:
    """The tool should refuse to run when the conversation cannot be paused."""
    deps = ToolDependencies(reachy_mini=MagicMock(), movement_manager=MagicMock())

    result = await PlayRockPaperScissors()(deps)

    assert result == {"error": "rock-paper-scissors is unavailable in this runtime"}


@pytest.mark.asyncio
async def test_play_rock_paper_scissors_pauses_conversation_for_one_match(monkeypatch: pytest.MonkeyPatch) -> None:
    """A match runs between pausing the conversation and handing it back."""
    order: list[str] = []

    class _App:
        def play_one_match(self, reachy: object, stop: object) -> dict[str, object]:
            order.append("play")
            return {
                "status": "match_over",
                "winner": "reachy",
                "player_score": 1,
                "reachy_score": 3,
            }

    monkeypatch.setattr("reachy_mini_rps.main.RockPaperScissorsApp", _App)
    deps = ToolDependencies(
        reachy_mini=MagicMock(),
        movement_manager=MagicMock(),
        enter_activity=lambda: order.append("enter"),
        exit_activity=lambda: order.append("exit"),
    )

    result = await PlayRockPaperScissors()(deps)

    assert order == ["enter", "play", "exit"]
    assert result["winner"] == "reachy"
