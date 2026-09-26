#!/usr/bin/env bash
# macOS `say` into 22.05 kHz 16-bit WAV clips for the game speaker.
set -euo pipefail
OUT="$(cd "$(dirname "$0")/.." && pwd)/reachy_mini_rps/assets"
mkdir -p "$OUT"

say_clip() {
  local name="$1"
  local text="$2"
  say -o "$OUT/${name}.wav" --data-format=LEI16@22050 "$text"
}

say_clip ready "Ready."
say_clip three "Three."
say_clip two "Two."
say_clip one "One."
say_clip shoot "Shoot."
say_clip i_choose_rock "I choose rock."
say_clip i_choose_paper "I choose paper."
say_clip i_choose_scissors "I choose scissors."
say_clip you_win "You win."
say_clip i_win "I win."
say_clip tie "Tie."
say_clip no_hand "I didn't see a hand. Let's try again."
say_clip you_win_match "You win the match."
say_clip i_win_match "I win the match."

words=(zero one two three)
for player in 0 1 2 3; do
  for reachy in 0 1 2 3; do
    if [[ "$player" == "3" && "$reachy" == "3" ]]; then
      continue
    fi
    say_clip "score_${player}_${reachy}" "The score is you ${words[$player]}, me ${words[$reachy]}."
  done
done

echo "Wrote speech clips to $OUT"
