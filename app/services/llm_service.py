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

    # Deep copy to avoid mutating the caller's message dicts
    messages_to_send = [msg.copy() for msg in messages]

    if reminder_prompt:
        # Insert as a system message just before the last user message
        # so it sits fresh in the LLM's attention window
        insert_idx = len(messages_to_send) - 1
        messages_to_send.insert(insert_idx, {"role": "system", "content": reminder_prompt})

    completion = client.chat.completions.create(
        model=model_name,
        messages=messages_to_send,
        temperature=temperature,
        stream=False
    )
    return completion.choices[0].message.content or ""


_REMINDER_GEN_PROMPT = """You are a writing assistant. Given the system prompt below, distill it into a short, punchy reminder (2-4 sentences max) that an AI can refer to mid-conversation to stay on track.

Focus on:
- The character's name, personality, and speaking style
- Key behavioral rules or constraints
- The setting or scenario if relevant

Do NOT include any preamble or explanation — output ONLY the reminder text itself.

System prompt:
\"\"\"
{system_prompt}
\"\"\""""


def generate_reminder_from_prompt(system_prompt: str, model_name: str) -> str:
    """Ask the LLM to distill a system prompt into a concise reminder."""
    if not system_prompt.strip():
        raise ValueError("System prompt is empty")

    completion = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": _REMINDER_GEN_PROMPT.format(system_prompt=system_prompt)}],
        temperature=0.4,
        stream=False
    )
    return (completion.choices[0].message.content or "").strip()
