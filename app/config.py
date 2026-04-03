import argparse
import os
from pathlib import Path

class Config:
    def __init__(self):
        parser = argparse.ArgumentParser(description="LM-Studio Chatbot with Kokoro TTS")
        parser.add_argument("--base-url", default=os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1"), help="Base URL for the LM Studio API")
        parser.add_argument("--api-key", default=os.getenv("LMSTUDIO_API_KEY", "lm-studio"), help="API key for LM Studio")
        parser.add_argument("--model-name", default=os.getenv("LMSTUDIO_MODEL_NAME"), help="Force a specific model ID")
        parser.add_argument("--repo-id", default=os.getenv("KOKORO_REPO_ID", "hexgrad/Kokoro-82M"), help="Hugging Face repo for Kokoro weights")
        parser.add_argument("--lang", default=os.getenv("KOKORO_LANG", "a"), help="Default language code used when parsing VOICES.md")
        parser.add_argument("--voice", default=os.getenv("KOKORO_VOICE"), help="Default voice name; must exist in VOICES.md")
        parser.add_argument("--sample-rate", type=int, default=int(os.getenv("KOKORO_SAMPLE_RATE", "24000")), help="Output sample rate")
        parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "5000")), help="Server port")
        
        args = parser.parse_args()

        self.LMSTUDIO_BASE_URL = args.base_url
        self.LMSTUDIO_API_KEY = args.api_key
        self.LMSTUDIO_MODEL_NAME = args.model_name
        
        self.KOKORO_REPO_ID = args.repo_id
        self.KOKORO_DEFAULT_LANG = args.lang
        self.KOKORO_VOICE_CLI = args.voice
        self.SAMPLE_RATE = args.sample_rate
        
        self.PORT = args.port

        self.VOICES_PATH = Path(__file__).resolve().parent / "services" / "VOICES.md"
        self.STATIC_DIR = Path(__file__).resolve().parents[1] / "web"

config = Config()
