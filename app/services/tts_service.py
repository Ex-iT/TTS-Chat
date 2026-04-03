import logging
import os
import re
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
from kokoro import KModel, KPipeline

from app.config import config
from app.utils.audio import audio_to_wav_base64
from app.utils.text import strip_markdown

logger = logging.getLogger(__name__)

def _parse_voice_catalog(path: Path, fallback_lang: str) -> Dict[str, Dict[str, str]]:
    voices: Dict[str, Dict[str, str]] = {}
    if not path.exists():
        return voices

    def _detect_gender(name: str, cells: list[str]) -> str:
        combined = " ".join(cells)
        if "🚺" in combined or "♀" in combined:
            return "female"
        if "🚹" in combined or "♂" in combined:
            return "male"
        prefix = name.split("_", 1)[0].lower()
        if prefix.endswith("f"):
            return "female"
        if prefix.endswith("m"):
            return "male"
        return "unknown"

    lang_code = fallback_lang
    lang_re = re.compile(r"lang_code='([a-z])'", re.IGNORECASE)

    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue

            lang_match = lang_re.search(line)
            if lang_match:
                lang_code = lang_match.group(1)
                continue

            if not line.startswith("|") or line.startswith("| Name") or line.startswith("| ----"):
                continue

            cells = [c.strip() for c in line.split("|")[1:-1]]
            if not cells:
                continue

            name_cell = cells[0]
            name = re.sub(r"[`*]", "", name_cell).replace("\\_", "_").strip()
            if not name or name.lower() == "name":
                continue

            gender = _detect_gender(name, cells)
            voices[name] = {"lang": lang_code, "gender": gender}

    return voices

voice_catalog = _parse_voice_catalog(config.VOICES_PATH, config.KOKORO_DEFAULT_LANG)

PREFERRED_DEFAULT_VOICE = "af_nicole"
if config.KOKORO_VOICE_CLI and config.KOKORO_VOICE_CLI in voice_catalog:
    DEFAULT_VOICE = config.KOKORO_VOICE_CLI
elif PREFERRED_DEFAULT_VOICE in voice_catalog:
    DEFAULT_VOICE = PREFERRED_DEFAULT_VOICE
else:
    DEFAULT_VOICE = next(iter(voice_catalog.keys()), PREFERRED_DEFAULT_VOICE)
    if DEFAULT_VOICE not in voice_catalog:
        voice_catalog[DEFAULT_VOICE] = {"lang": config.KOKORO_DEFAULT_LANG, "gender": "unknown"}

device = "cuda" if torch.cuda.is_available() else "cpu"
kokoro_model = KModel(repo_id=config.KOKORO_REPO_ID).to(device).eval()
tts_lock = threading.Lock()
pipelines: Dict[str, KPipeline] = {}

def get_voice_info(requested: Optional[str]) -> Tuple[str, str]:
    voice = (requested or DEFAULT_VOICE or "").strip()
    info = voice_catalog.get(voice)
    if not info:
        raise ValueError(f"Voice '{voice}' is not available.")
    return voice, info["lang"]

def get_pipeline(lang_code: str) -> KPipeline:
    pipeline = pipelines.get(lang_code)
    if pipeline is None:
        pipeline = KPipeline(
            lang_code=lang_code, repo_id=config.KOKORO_REPO_ID, model=kokoro_model
        )
        pipelines[lang_code] = pipeline
    return pipeline

def synthesize_audio(text: str, voice_name: Optional[str] = None) -> Tuple[str, str]:
    resolved_voice, lang_code = get_voice_info(voice_name)
    text = strip_markdown(text or "")
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("No text provided to synthesize.")

    last_error: Optional[Exception] = None
    for attempt in (0, 1):
        pipeline = get_pipeline(lang_code)
        try:
            with tts_lock:
                segments: List[np.ndarray] = []
                for chunk in pipeline(clean_text, voice=resolved_voice):
                    audio = chunk.audio
                    if isinstance(audio, torch.Tensor):
                        audio = audio.detach().cpu().numpy()
                    arr = np.asarray(audio, dtype=np.float32).flatten()
                    if arr.size:
                        segments.append(arr)
                if not segments:
                    raise RuntimeError("Kokoro returned empty audio.")
                audio = np.concatenate(segments)
            return audio_to_wav_base64(audio, config.SAMPLE_RATE), resolved_voice
        except Exception as exc:
            last_error = exc
            pipelines.pop(lang_code, None)
            if attempt == 0:
                continue
            logger.error(f"TTS failed for voice '{resolved_voice}': {exc}")
            raise RuntimeError(f"TTS failed for voice '{resolved_voice}': {exc}") from exc

    raise RuntimeError(f"TTS failed for voice '{resolved_voice}': {last_error}") from last_error
