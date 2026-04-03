import base64
import io
import wave
import numpy as np
import torch

def audio_to_wav_base64(audio: np.ndarray, sample_rate: int) -> str:
    """Convert Kokoro float audio to base64 wav bytes."""
    if isinstance(audio, torch.Tensor):
        audio = audio.detach().cpu().numpy()
    arr = np.asarray(audio, dtype=np.float32).flatten()
    arr = np.clip(arr, -1.0, 1.0)
    pcm = (arr * 32767.0).astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())

    return base64.b64encode(buf.getvalue()).decode("ascii")
