# Reachy Mini camera, mic, and speaker

One path that works on this Mac: a **daemon** owns the hardware, and your script talks to it through `ReachyMini().media`. Pin the SDK to **`reachy-mini==1.8.0`** so it matches the desktop app and the project `.venv`.

You do not open the webcam with OpenCV, or the mic and speaker with `sounddevice` / PyAudio, while that daemon is running. Those libraries fight GStreamer for the same devices.

## Libraries

| Package | Role |
|---|---|
| `reachy-mini==1.8.0` | Robot connection, camera frames, mic chunks, speaker playback. Already in `requirements.txt`. |
| `numpy` | Installed with the SDK. Frames and audio samples are NumPy arrays. |
| GStreamer (`gi`) | Installed with the SDK. You never import it yourself. |

Save or display a frame with Pillow or `cv2.imwrite` only. Those calls do not open the camera.

## One-time setup

```bash
cd ~/Documents/GitHub/reachy
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

Use this venv’s `python`. Homebrew `python3` does not have the SDK, and importing it can sit there for a long time.

The first `import reachy_mini` takes about 10–30 seconds while GStreamer starts. That pause is normal.

macOS privacy, once:

**System Settings → Privacy & Security → Camera** and **Microphone** → allow **Terminal**.

If you use the Reachy Mini desktop app, allow that app too.

## Start the daemon (Terminal 1)

Only one process may listen on port **8000**. Quit **Reachy Mini Control** before starting a daemon from the terminal.

Pick the row that matches what you want the camera to see.

| What you want | Command | Camera picture |
|---|---|---|
| Laptop webcam | `reachy-mini-daemon --mockup-sim` | Mac camera (`autovideosrc`), 1280×720 @ 30 fps |
| MuJoCo 3D window | `mjpython -m reachy_mini.daemon.app.main --sim` | Simulated robot camera. Needs `uv pip install "reachy-mini[mujoco]==1.8.0"` once. |
| Real Reachy Lite | Open the Reachy Mini desktop app | Robot camera, or the USB camera the app detects |
| Head motion only | `reachy-mini-daemon --sim --headless --no-media` | No camera, mic, or speaker |

Wait until [http://localhost:8000/docs](http://localhost:8000/docs) loads.

`--sim` and `--mockup-sim` together force the MuJoCo camera and drop the Mac webcam. For the laptop camera, pass `--mockup-sim` alone.

MuJoCo still uses the Mac mic and speaker. The 3D window and the laptop webcam are two different daemons; run one of them.

The conversation-app scripts do the same thing from `reachy_mini_conversation_app/`:

- `./scripts/run_mockup_sim_daemon.sh` — laptop webcam
- `./scripts/run_sim_daemon.sh` — MuJoCo (`mjpython`)

## Talk to the devices (Terminal 2)

```bash
cd ~/Documents/GitHub/reachy
source .venv/bin/activate
python media_check.py
```

`media_check.py` grabs one frame, listens for one second, and plays a short beep. Read it next to the snippets below.

Leave the conversation app stopped while this script runs. It uses the same camera and mic pipeline.

### Connect

```python
from reachy_mini import ReachyMini

with ReachyMini(media_backend="local") as mini:
    frame = mini.media.get_frame()
```

`media_backend="local"` reads the camera over the local socket `/tmp/reachymini_camera_socket` and opens the Mac mic and speaker with GStreamer. Use this on the same machine as the daemon.

| `media_backend` | When |
|---|---|
| `"local"` | Your script and the daemon are both on this Mac. Use this. |
| `"default"` | SDK picks local if that socket exists, otherwise WebRTC. WebRTC on this machine often logs `Signalling error: receiver is gone` and then audio never plays. |
| `"webrtc"` | A script on another computer, streaming from the robot. |
| `"no_media"` | Motion only. The daemon releases the camera and mic. |

### Camera

```python
import time

frame = None
for _ in range(50):  # up to ~5 s for the pipeline to deliver a frame
    frame = mini.media.get_frame()
    if frame is not None:
        break
    time.sleep(0.1)

# frame: uint8 BGR, shape (height, width, 3). None means no camera yet.
print(frame.shape, frame.dtype)
```

`get_frame()` returns **BGR**, the same order OpenCV uses. Pillow wants RGB:

```python
from PIL import Image

Image.fromarray(frame[:, :, ::-1]).save("frame.jpg")
```

### Microphone

Call `start_recording()` once. Each `get_audio_sample()` pulls the next chunk and returns `None` when the queue is empty.

```python
import numpy as np

mini.media.start_recording()
time.sleep(0.3)  # let the pipeline fill

chunks = []
deadline = time.time() + 1.0
while time.time() < deadline:
    sample = mini.media.get_audio_sample()
    if sample is None:
        time.sleep(0.01)
        continue
    chunks.append(sample)

mini.media.stop_recording()
audio = np.concatenate(chunks, axis=0)  # float32, shape (n, 2), 16 kHz
```

Format, from the SDK:

- **16 000 Hz**, stereo, `float32`
- shape `(num_samples, 2)`, values about `-1.0` … `1.0`
- `mini.media.get_input_audio_samplerate()` → `16000`
- `mini.media.get_input_channels()` → `2`

A loud moment, without a speech model:

```python
def voice_active(samples: np.ndarray | None, threshold: float = 0.02) -> bool:
    if samples is None or samples.size == 0:
        return False
    return float(np.max(np.abs(samples))) >= threshold
```

Treat about eight hot chunks in a row (~250 ms) as “someone is talking”, so a single click does not count.

### Speaker

Two ways. Both go to the Mac default output when no Reachy USB audio card is plugged in.

**A file.** `play_sound` returns as soon as GStreamer hits PLAYING. Sleep for the length of the clip yourself.

```python
mini.media.play_sound("/absolute/path/to/clip.wav")
time.sleep(1.2)  # length of that clip
```

A bare filename such as `"wake_up.wav"` is resolved from the SDK assets folder. Anything else must be an absolute path that exists, or `play_sound` raises `FileNotFoundError`.

**Raw samples.** Mono `float32` is copied onto both speaker channels. Call `start_playing()` first.

```python
sr = mini.media.get_output_audio_samplerate()  # 16000
n = int(sr * 0.4)
t = np.arange(n) / sr
tone = (0.2 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)

mini.media.start_playing()
mini.media.push_audio_sample(tone)
time.sleep(0.5)
mini.media.stop_playing()
```

While a clip is playing, ignore the mic, and keep ignoring it for about 0.8 s after. Otherwise the robot hears its own speaker and treats that as a new utterance.

### Volume

The conversation app sets this on the daemon (0–100):

```bash
curl -s http://localhost:8000/api/volume/current
curl -s -X POST http://localhost:8000/api/volume/set \
  -H 'Content-Type: application/json' -d '{"volume": 60}'

curl -s http://localhost:8000/api/volume/microphone/current
curl -s -X POST http://localhost:8000/api/volume/microphone/set \
  -H 'Content-Type: application/json' -d '{"volume": 70}'
```

Setting the speaker volume plays a short confirmation beep.

## Logs that are fine

| Log | Meaning |
|---|---|
| `No Reachy Mini Audio USB device found` | No Reachy USB audio board. The daemon uses the Mac’s default mic and speaker. |
| `No Reachy Mini audio card found, using default audio source` | Same thing, from the daemon. |
| SDK / daemon version warning | Install the same `reachy-mini` version on both sides. This repo pins `1.8.0`. |

`Signalling error: receiver is gone` means the script took the WebRTC path. Motion can still work. Restart the script with `media_backend="local"`.

## Conversation app (voice chat)

That app is a separate program on top of the same daemon. It is how Reachy holds a spoken conversation. Your own scripts use `media` directly and stay stopped while the conversation app is running.

```bash
cd ~/Documents/GitHub/reachy/reachy_mini_conversation_app
./scripts/setup_mac_venv.sh          # once
./scripts/run_mockup_sim_daemon.sh   # Terminal 1, laptop camera
./scripts/run_conversation.sh        # Terminal 2
```

Open [http://localhost:7860](http://localhost:7860), pick a personality, press **Talk**. The **camera** tool is on for the default personality. Ask “what do you see?”. Details and the MuJoCo-plus-voice launcher are in `reachy_mini_conversation_app/scripts/START_HERE.md`.

`--no-camera` turns vision off. A daemon started with `--no-media` has no camera, mic, or speaker for the app to use.
