# TTS Chat Assistant (LM Studio + Kokoro)

This is a modular Flask application that provides a modern chat interface powered by an [LM Studio](https://lmstudio.ai/) backend. It seamlessly integrates with [Kokoro](https://github.com/hexgrad/Kokoro) to synthesize high-quality text-to-speech for AI replies. The `web/` frontend communicates with a flexible backend API that provides text generation, model discovery, and speech synthesis.

## Requirements

- Python 3.10+ and below 3.14 with `pip`
- [LM Studio](https://lmstudio.ai/) running locally with a chat model loaded and the API server enabled (defaults to `http://127.0.0.1:1234/v1` and key `lm-studio`)

## Quickstart

- **Installation & Running:**

  ```bash
  python -m venv .venv
  source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
  pip install --upgrade pip
  pip install -r requirements.txt

  # Start LM Studio separately, then run the app:
  python run.py
  ```

  Then open http://localhost:5000 in your browser to use the chat UI.

## Config (Arguments & Environment Variables)

All settings can be passed as command-line arguments or environment variables. Arguments take precedence.

| Argument        | Env Variable          | Description                    | Default                    |
| :-------------- | :-------------------- | :----------------------------- | :------------------------- |
| `--base-url`    | `LMSTUDIO_BASE_URL`   | Base URL for the LM Studio API | `http://127.0.0.1:1234/v1` |
| `--api-key`     | `LMSTUDIO_API_KEY`    | API key for LM Studio          | `lm-studio`                |
| `--model-name`  | `LMSTUDIO_MODEL_NAME` | Force a specific model ID      | (auto-detect)              |
| `--repo-id`     | `KOKORO_REPO_ID`      | HF repo for Kokoro weights     | `hexgrad/Kokoro-82M`       |
| `--lang`        | `KOKORO_LANG`         | Default language code          | `a`                        |
| `--voice`       | `KOKORO_VOICE`        | Default voice name             | `af_nicole`                |
| `--sample-rate` | `KOKORO_SAMPLE_RATE`  | Output sample rate             | `24000`                    |
| `--port`        | `PORT`                | Server port                    | `5000`                     |

Example using arguments:

```bash
python run.py --port 5001 --voice af_bella
```

## Voice catalog

Available voices are parsed directly from `app/services/VOICES.md`. Each entry exposes a `name` and `lang_code` to the frontend dropdown. You can update that file to add or remove voices without touching any system code.

## Utility Scripts

I included a standalone script in `scripts/terminal_chat_stream.py` which allows you to chat interactively with your local model using your terminal. This script automatically streams spoken audio line-by-line using Kokoro as the LLM generates responses.

## How it works

- `/api/models` proxies LM Studio to list available model IDs.
- `/api/chat` sends the conversation to LM Studio, gets a text reply, and immediately synthesizes audio for the selected voice.
- `/api/voices` returns the Kokoro voices parsed from `VOICES.md`.
- `/api/tts` runs Kokoro TTS for arbitrary text (used by the "Speak" buttons).

Local chat history, selected model, voice, and temperature are cached in `localStorage` so your settings persist between refreshes.

## Tools and inspiration

- [Antigravity](https://antigravity.google/) - AI coding assistant
- [LM Studio](https://lmstudio.ai/) - Local LLM server
- [Kokoro](https://github.com/hexgrad/Kokoro) - High-quality text-to-speech
- [LM TTS (LM Studio + Kokoro)](https://github.com/AdmiralApple/LM-Studio-Chatbot) by [AdmiralApple](https://github.com/AdmiralApple) - Project combining LM Studio and Kokoro
