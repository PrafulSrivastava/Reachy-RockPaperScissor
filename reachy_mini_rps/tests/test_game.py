from reachy_mini_rps.game import Game
from reachy_mini_rps.voice import voice_active


def test_begin_round_stores_throw_before_any_frame() -> None:
    game = Game(choose=lambda: "rock")
    assert game.reachy_throw is None
    assert game.begin_round() is True
    assert game.reachy_throw == "rock"
    assert game.player_throw is None
    assert game.phase == "countdown"


def test_begin_round_refuses_unless_idle() -> None:
    game = Game(choose=lambda: "rock")
    game.begin_round()
    assert game.begin_round() is False
    assert game.reachy_throw == "rock"


def test_none_snap_leaves_the_score_unchanged() -> None:
    game = Game(choose=lambda: "paper")
    game.begin_round()
    game.finish_snap(None)
    assert game.score.player == 0
    assert game.score.reachy == 0
    assert game.last_result == "no_hand"
    assert game.match_over is False
    assert game.reveal_clips() == ["no_hand", "score_0_0"]


def test_player_win_increments_player_score() -> None:
    game = Game(choose=lambda: "scissors")
    game.begin_round()
    game.finish_snap("rock")
    assert game.score.player == 1
    assert game.score.reachy == 0
    assert game.last_result == "player"
    assert game.reveal_clips() == ["i_choose_scissors", "you_win", "score_1_0"]
    assert game.reaction_pose() == "lose"


def test_reachy_win_increments_reachy_score() -> None:
    game = Game(choose=lambda: "paper")
    game.begin_round()
    game.finish_snap("rock")
    assert game.score.reachy == 1
    assert game.score.player == 0
    assert game.last_result == "reachy"
    assert game.reaction_pose() == "win"


def test_tie_changes_no_score() -> None:
    game = Game(choose=lambda: "rock")
    game.begin_round()
    game.finish_snap("rock")
    assert game.score.player == 0
    assert game.score.reachy == 0
    assert game.last_result == "tie"
    assert game.reaction_pose() == "watch"


def test_reaching_three_sets_match_over() -> None:
    game = Game(choose=lambda: "scissors")
    for expected in (1, 2):
        assert game.begin_round() is True
        game.finish_snap("rock")
        assert game.match_over is False
        assert game.score.player == expected
        game.back_to_idle()
        assert game.phase == "idle"
        assert game.score.player == expected

    game.begin_round()
    game.finish_snap("rock")
    assert game.score.player == 3
    assert game.match_over is True
    assert game.reveal_clips()[-1] == "you_win_match"
    game.back_to_idle()
    assert game.phase == "idle"
    assert game.score.player == 0
    assert game.score.reachy == 0
    assert game.match_over is False
    assert game.announcement == "you_win_match"


def test_reachy_match_announcement() -> None:
    game = Game(choose=lambda: "paper")
    for _ in range(3):
        game.begin_round()
        game.finish_snap("rock")
        if not game.match_over:
            game.back_to_idle()
    assert game.match_over is True
    assert game.reveal_clips()[-1] == "i_win_match"


def test_play_request_is_consumed_on_begin() -> None:
    game = Game(choose=lambda: "rock")
    game.request_play()
    assert game.play_requested is True
    game.begin_round()
    assert game.play_requested is False


def test_snapshot_reports_the_round() -> None:
    game = Game(choose=lambda: "rock")
    game.begin_round()
    game.finish_snap("scissors")
    snap = game.snapshot()
    assert snap["phase"] == "reveal"
    assert snap["player_score"] == 0
    assert snap["reachy_score"] == 1
    assert snap["reachy_throw"] == "rock"
    assert snap["player_throw"] == "scissors"
    assert snap["last_result"] == "reachy"
    assert snap["match_over"] is False


def test_voice_active_uses_rms() -> None:
    assert voice_active(None) is False
    assert voice_active([]) is False
    assert voice_active([0.0, 0.0, 0.0]) is False
    assert voice_active([0.1, -0.1, 0.1]) is True
