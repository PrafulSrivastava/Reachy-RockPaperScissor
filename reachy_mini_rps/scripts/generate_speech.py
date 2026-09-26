"""Render the game's WAV clips with Qwen3-TTS CustomVoice, speaker Aiden.

Aiden is the conversation app's default voice. The game still plays these
files; it does not call the model at runtime.
"""

import wave
from pathlib import Path

import numpy as np
from mlx_audio.tts.utils import load_model


MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16"
SPEAKER = "Aiden"
LANGUAGE = "English"
ASSETS = Path(__file__).resolve().parent.parent / "reachy_mini_rps" / "assets"

_WORDS = ("zero", "one", "two", "three")
CLIPS: list[tuple[str, str]] = [
    ("ready", "Ready."),
    ("three", "Three."),
    ("two", "Two."),
    ("one", "One."),
    ("shoot", "Shoot."),
    ("i_choose_rock", "I choose rock."),
    ("i_choose_paper", "I choose paper."),
    ("i_choose_scissors", "I choose scissors."),
    ("you_win", "You win."),
    ("i_win", "I win."),
    ("tie", "Tie."),
    ("no_hand", "I didn't see a hand. Let's try again."),
    ("you_win_match", "You win the match."),
    ("i_win_match", "I win the match."),
]
for player in range(4):
    for reachy in range(4):
        if (player, reachy) == (3, 3):
            continue
        CLIPS.append(
            (
                f"score_{player}_{reachy}",
                f"The score is you {_WORDS[player]}, me {_WORDS[reachy]}.",
            )
        )


def _as_mono(audio: np.ndarray) -> np.ndarray:
    samples = np.asarray(audio, dtype=np.float32)
    if samples.ndim == 2:
        samples = samples[:, 0] if samples.shape[1] <= samples.shape[0] else samples[0]
    return np.squeeze(samples)


def _trim(samples: np.ndarray, rate: int) -> np.ndarray:
    """Drop leading and trailing quiet, and keep a short pad."""
    loud = np.flatnonzero(np.abs(samples) > 0.02)
    if loud.size == 0:
        return samples
    pad = int(0.04 * rate)
    start = max(0, int(loud[0]) - pad)
    end = min(samples.shape[0], int(loud[-1]) + pad)
    return samples[start:end]


def _write_wav(path: Path, samples: np.ndarray, rate: int) -> None:
    pcm = np.clip(samples, -1.0, 1.0)
    frames = (pcm * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(frames.tobytes())


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    print(f"Loading {MODEL}")
    model = load_model(MODEL)
    for name, text in CLIPS:
        results = list(
            model.generate_custom_voice(
                text=text,
                speaker=SPEAKER,
                language=LANGUAGE,
            )
        )
        if not results:
            raise RuntimeError(f"No audio for {name}")
        result = results[0]
        rate = int(getattr(result, "sample_rate", 24000))
        samples = _trim(_as_mono(result.audio), rate)
        path = ASSETS / f"{name}.wav"
        _write_wav(path, samples, rate)
        seconds = samples.shape[0] / float(rate)
        print(f"{name}: {seconds:.2f}s")
        if seconds < 0.15 or seconds > 8.0:
            raise RuntimeError(f"{name} duration {seconds:.2f}s is outside 0.15-8.0s")
    print(f"Wrote {len(CLIPS)} clips to {ASSETS}")


if __name__ == "__main__":
    main()
