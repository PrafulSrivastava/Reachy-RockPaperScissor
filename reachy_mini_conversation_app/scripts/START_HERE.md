# macOS: sim + voice (conversation app)

## Visual sim + voice together

One **daemon** powers both the **MuJoCo 3D window** and **mic/speaker** for the conversation app.

**Easiest (macOS):** opens two Terminal windows automatically:

```bash
./scripts/launch_visual_sim_and_voice_mac.sh
```

Or manually: Terminal 1 = `./scripts/run_sim_daemon.sh` (MuJoCo), Terminal 2 = `./scripts/run_conversation.sh` after port 8000 is up.

Quit **Reachy Mini Control** first so nothing else uses port 8000.

## One-time setup

```bash
cd ~/Documents/GitHub/reachy/reachy_mini_conversation_app
./scripts/setup_mac_venv.sh
```

## Every session (two terminals)

**Terminal 1 — simulation daemon** (pick one)

| Mode | Command | 3D window | Voice |
|------|---------|-----------|-------|
| **Visual + voice** | `./scripts/run_sim_daemon.sh` | Yes | Yes |
| Voice only | `reachy-mini-daemon --sim --headless` | No | Yes |

Wait until [http://localhost:8000/docs](http://localhost:8000/docs) loads. Quit **Reachy Mini Control** if port 8000 is busy.

**Terminal 2 — talk to Reachy**

```bash
./scripts/run_conversation.sh
```

Open [http://localhost:7860](http://localhost:7860) → choose a personality → **Talk** → tap the orb if muted.

Grant **Microphone** access to Terminal in System Settings.

## Camera / vision

The conversation app exposes a **`camera` tool** (enabled on the default personality). The LLM calls it when you ask “what do you see?” or “look at me”.

1. **Do not** pass `--no-camera` (the bundled scripts leave camera **on**).
2. Start the daemon **with media** (not `--no-media`).
3. **macOS:** System Settings → **Privacy & Security → Camera** → allow **Terminal**.
4. In the UI: **Tools** → confirm **camera** is enabled for your personality.

### Which video source?

| Daemon mode | Script | What the robot “sees” |
|-------------|--------|------------------------|
| **MuJoCo 3D** `--sim` | `run_sim_daemon.sh` | **Simulated robot camera** (MuJoCo scene), not the Mac webcam |
| **Mockup sim** `--mockup-sim` only (not `--sim`) | `run_mockup_sim_daemon.sh` | **Laptop / Mac webcam** (`autovideosrc`) |
| Real Reachy Lite | desktop app / USB daemon | Robot camera or detected USB cam |

You cannot get MuJoCo 3D **and** Mac webcam in one daemon today; pick MuJoCo (robot POV in the sim) or mockup sim (webcam).

Audio-only (no vision tools): `reachy-mini-conversation-app --ui --no-camera`

## Logs (if started in background)

- Daemon: `/tmp/reachy_sim_daemon.log`
- Conversation app: `/tmp/reachy_conversation.log`
