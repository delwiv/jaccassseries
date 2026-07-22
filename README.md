# jacasseries

Voice interface for LLM — talk to your AI like you'd chat with a friend.

## Overview

jacasseries is a desktop voice interface for conversing with a large language
model. Speech-to-text and text-to-speech run 100% locally (faster-whisper +
Piper TTS). The LLM can be remote (any OpenAI-compatible API, e.g. llama.cpp).

The name comes from the French *jacasser* — to chatter like a magpie.

## Features

- Push-to-talk floating button (FAB) — always-on-top, draggable, color-coded
- Real-time STT via faster-whisper (CUDA optional)
- Streaming TTS — audio starts before the LLM finishes generating
- Global keyboard shortcut (configurable via UI)
- System tray minimisation
- Configuration UI (API URL/key, model, voice, microphone, shortcut)
- Conversation history across turns
- MIT license, no cloud dependencies for voice

## Pipeline

```
[Keyboard Shortcut / Click] → [Audio Capture] → [faster-whisper STT]
                                     ↓
                             [LLM API (OpenAI-compatible, SSE)]
                                     ↓
                          [Sentence splitter] → [Piper TTS] → [Audio Output]
```

States: `idle → recording → transcribing → llm → tts → idle`

## Requirements

- Python ≥ 3.11
- Linux (macOS/Windows support planned)
- CUDA-capable GPU recommended but optional

## Installation

```bash
git clone https://github.com/your-username/jacasseries.git
cd jacasseries
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

For keyword-spotting support (future feature):

```bash
pip install -e ".[keyword]"
```

## Configuration

First launch creates `~/.config/jacasseries/config.toml`.
Edit through the GUI (right-click FAB → Config) or directly in the file.

| Key                | Default                     | Description                        |
|--------------------|-----------------------------|------------------------------------|
| `api.url`          | `http://localhost:8080`     | LLM server URL                     |
| `api.key`          | `""`                        | API key (`${ENV_VAR}` supported)   |
| `llm.model`        | first from `/v1/models`     | Model to use                       |
| `stt.language`     | `fr`                        | STT language                       |
| `stt.model_size`   | `small`                     | Whisper model size                 |
| `tts.voice`        | `fr_FR-siwis-medium`        | Piper voice                        |

System prompt (French) is hardcoded for now — plain text, no markdown, no emojis.

## Usage

```bash
python -m jacasseries
```

- **Click** the FAB → start / stop recording
- **Right-click** → New discussion / Config / Quit
- **Long-press** the FAB → reset conversation
- **Keyboard shortcut** (if configured) → toggle recording

## Project Structure

```
src/
├── main.py              Entry point
├── app.py               Application (wires all components)
├── config.py            TOML configuration manager
├── audio/
│   ├── capture.py       Sounddevice input streaming
│   ├── output.py        Sounddevice playback
│   └── vad.py           VAD stub (placeholder)
├── stt/
│   └── transcriber.py   faster-whisper wrapper
├── llm/
│   └── client.py        OpenAI-compatible API client (SSE)
├── tts/
│   └── synthesizer.py   Piper TTS wrapper
├── pipeline/
│   ├── orchestrator.py  State machine
│   └── streamer.py      Sentence-level TTS streaming engine
├── ui/
│   ├── fab.py           Floating action button
│   ├── tray.py          System tray icon
│   └── config_window.py Configuration dialog
└── keyword/
    └── spotter.py       Global keyboard shortcut (pynput)
```

## Roadmap

**Current (Phase 1-2):** Core pipeline working — record → STT → LLM → TTS → play.

**Upcoming:**
- Silero VAD for automatic silence detection
- openWakeWord keyword spotting for hands-free interruption
- Streaming partial transcriptions to LLM
- Cross-platform support (Windows, macOS)
- Audio spectrum animation on FAB
- Conversation context management

## License

MIT — see [LICENCE](LICENCE).
