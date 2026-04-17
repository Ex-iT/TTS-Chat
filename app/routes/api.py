from flask import Blueprint, jsonify, request, current_app

from app.services.llm_service import available_models, resolve_model_name, get_chat_completion, generate_reminder_from_prompt
from app.services.tts_service import synthesize_audio, get_voice_info, voice_catalog, DEFAULT_VOICE

bp = Blueprint("api", __name__, url_prefix="/api")

@bp.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(force=True) or {}
    temperature = float(payload.get("temperature", 0.7))
    tts_enabled = payload.get("tts_enabled", True)
    requested_voice = payload.get("voice")

    if tts_enabled:
        try:
            resolved_voice, _ = get_voice_info(requested_voice)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
    else:
        resolved_voice = requested_voice or DEFAULT_VOICE

    try:
        model_name = resolve_model_name(payload.get("model"))
        messages = payload.get("messages", [])
        reminder_prompt = payload.get("reminder_prompt")
        
        content = get_chat_completion(messages, model_name, temperature, reminder_prompt)

    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        current_app.logger.error("LLM failure: %s", exc)
        return jsonify({"error": str(exc)}), 500

    audio_b64 = None
    if tts_enabled:
        try:
            audio_b64, resolved_voice = synthesize_audio(content, resolved_voice)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    result = {
        "content": content,
        "model": model_name,
        "voice": resolved_voice
    }
    if audio_b64:
        result["audio"] = audio_b64

    return jsonify(result)

@bp.route("/tts", methods=["POST"])
def tts():
    payload = request.get_json(force=True) or {}
    text = payload.get("text", "")
    voice = payload.get("voice")

    try:
        audio_b64, resolved_voice = synthesize_audio(text, voice)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({"audio": audio_b64, "voice": resolved_voice})

@bp.route("/models", methods=["GET"])
def list_models():
    models = available_models(force_refresh=True)
    return jsonify({"models": models})

@bp.route("/voices", methods=["GET"])
def list_voices():
    voices = [
        {"name": name, "lang_code": meta["lang"], "gender": meta.get("gender", "unknown")}
        for name, meta in sorted(voice_catalog.items())
    ]
    return jsonify({"voices": voices, "default": DEFAULT_VOICE})

@bp.route("/generate-reminder", methods=["POST"])
def generate_reminder():
    payload = request.get_json(force=True) or {}
    system_prompt = payload.get("system_prompt", "")
    
    try:
        model_name = resolve_model_name(payload.get("model"))
        reminder = generate_reminder_from_prompt(system_prompt, model_name)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception as exc:
        current_app.logger.error("Reminder generation failure: %s", exc)
        return jsonify({"error": str(exc)}), 500

    return jsonify({"reminder": reminder})
