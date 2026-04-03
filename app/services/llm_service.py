import time
import logging
from typing import List, Optional

from openai import OpenAI
from app.config import config

logger = logging.getLogger(__name__)

client = OpenAI(base_url=config.LMSTUDIO_BASE_URL, api_key=config.LMSTUDIO_API_KEY)

_model_cache = {"ts": 0.0, "models": []}
MODEL_CACHE_TTL = 30.0

def _fetch_lmstudio_models() -> List[str]:
    try:
        response = client.models.list()
    except Exception as exc:
        logger.warning("Failed to fetch LM Studio models: %s", exc)
        return []

    data = getattr(response, "data", []) or []
    return [getattr(model, "id", "") for model in data if getattr(model, "id", "")]

def available_models(force_refresh: bool = False) -> List[str]:
    if config.LMSTUDIO_MODEL_NAME:
        return [config.LMSTUDIO_MODEL_NAME]

    now = time.monotonic()
    cached = _model_cache["models"]
    ts = _model_cache["ts"]
    if not force_refresh and cached and now - ts < MODEL_CACHE_TTL:
        return cached

    models = _fetch_lmstudio_models()
    if models:
        _model_cache["models"] = models
        _model_cache["ts"] = now
        return models

    return cached or []

def resolve_model_name(requested: Optional[str] = None) -> str:
    if requested:
        return requested

    models = available_models()
    if not models:
        raise RuntimeError("No LM Studio model is currently loaded.")
    return models[0]

def get_chat_completion(messages: List[dict], model_name: str, temperature: float, reminder_prompt: Optional[str] = None) -> str:
    if not messages:
        raise ValueError("messages array is required")

    messages_to_send = messages.copy()
    
    if reminder_prompt:
        if messages_to_send[0].get("role") == "system":
            messages_to_send[0]["content"] += f"\n\n[REMINDER]: {reminder_prompt}"
        else:
            messages_to_send.insert(0, {"role": "system", "content": f"[REMINDER]: {reminder_prompt}"})

    completion = client.chat.completions.create(
        model=model_name,
        messages=messages_to_send,
        temperature=temperature,
        stream=False
    )
    return completion.choices[0].message.content or ""
