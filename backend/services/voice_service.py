"""
Voice service: STT + TTS with graceful fallbacks.

Priority (hackathon-safe, never crashes):
- TTS: ElevenLabs (eleven_multilingual_v2, hi/gu/en) -> edge-tts -> gTTS -> browser speechSynthesis
- STT: ElevenLabs scribe_v1 -> faster-whisper -> browser Web Speech (frontend)

Set `ELEVENLABS_API_KEY` in `.env` to enable ElevenLabs.
"""

import os
import structlog
import uuid

from backend.config import settings

logger = structlog.get_logger()

# ElevenLabs language codes map to our app locales — all 11 Indian languages
_LANG_MAP = {"en": "en", "hi": "hi", "gu": "gu", "bn": "bn", "ta": "ta", "te": "te", "kn": "kn", "ml": "ml", "pa": "pa", "or": "or", "as": "as"}


# ElevenLabs language codes — pass for all 11 (eleven_multilingual_v2 supports them); fallback to auto-detect if unknown
_SUPPORTED_LANG_CODES = {"en", "hi", "gu", "bn", "ta", "te", "kn", "ml", "pa", "or", "as"}


def _eleven_lang(language: str) -> str | None:
    code = _LANG_MAP.get(language, "hi")
    return code if code in _SUPPORTED_LANG_CODES else None


async def _elevenlabs_tts(text: str, language: str) -> dict | None:
    key = settings.ELEVENLABS_API_KEY
    if not key:
        return None
    import httpx
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}"
    payload = {
        "text": text[:1000],
        "model_id": settings.ELEVENLABS_MODEL_ID,
        "voice_settings": {"stability": 0.55, "similarity_boost": 0.75, "style": 0.2, "use_speaker_boost": True},
    }
    el = _eleven_lang(language)
    if el:
        payload["language_code"] = el
    async with httpx.AsyncClient(timeout=60.0, headers={"xi-api-key": key}) as c:
        r = await c.post(url, json=payload)
    if r.status_code != 200:
        logger.warning("elevenlabs tts failed", status=r.status_code, body=r.text[:150])
        return None
    out_dir = os.path.join(settings.UPLOAD_DIR, "audio")
    os.makedirs(out_dir, exist_ok=True)
    audio_id = str(uuid.uuid4())[:8]
    out_path = os.path.join(out_dir, f"tts_{audio_id}.mp3")
    with open(out_path, "wb") as f:
        f.write(r.content)
    return {"audio_url": f"/uploads/audio/tts_{audio_id}.mp3",
            "duration_seconds": round(len(text) / 12, 1), "source": "elevenlabs"}


async def _edge_tts(text: str, language: str) -> dict | None:
    try:
        import edge_tts
        voice = {
            "hi": "hi-IN-SwaraNeural", "gu": "gu-IN-DhwaniNeural", "en": "en-IN-NeerjaNeural",
            "bn": "bn-IN-TanishaaNeural", "ta": "ta-IN-PallaviNeural", "te": "te-IN-ShrutiNeural",
            "kn": "kn-IN-SapnaNeural", "ml": "ml-IN-SobhanaNeural", "pa": "pa-IN-...Neural", "or": "or-IN-SubhasiniNeural", "as": "as-IN-...Neural"
        }.get(language, "hi-IN-SwaraNeural")
        # Fallback for pa/as where edge-tts voice may not exist — use hi voice which handles similar phonetics
        if "Neural" not in voice or "..." in voice:
            voice = "hi-IN-SwaraNeural" if language in ("pa", "as") else voice
        audio_id = str(uuid.uuid4())[:8]
        out_dir = os.path.join(settings.UPLOAD_DIR, "audio")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"tts_{audio_id}.mp3")
        comm = edge_tts.Communicate(text[:500], voice)
        await comm.save(out_path)
        return {"audio_url": f"/uploads/audio/tts_{audio_id}.mp3",
                "duration_seconds": round(len(text) / 12, 1), "source": "edge-tts"}
    except Exception:
        return None


def _gtts(text: str, language: str) -> dict | None:
    try:
        from gtts import gTTS
        audio_id = str(uuid.uuid4())[:8]
        out_dir = os.path.join(settings.UPLOAD_DIR, "audio")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"tts_{audio_id}.mp3")
        gtts_lang = language if language in ("en", "hi", "gu", "bn", "ta", "te", "kn", "ml", "pa") else "hi"
        # gTTS fallback for or/as/oriya/assamese — closest phonetically is bn/hi
        if language in ("or", "as"):
            gtts_lang = "bn" if language == "or" else "hi"
        gTTS(text[:500], lang=gtts_lang).save(out_path)
        return {"audio_url": f"/uploads/audio/tts_{audio_id}.mp3",
                "duration_seconds": round(len(text) / 12, 1), "source": "gtts"}
    except Exception as e:
        logger.warning("gTTS failed", error=str(e))
        return None


async def _elevenlabs_stt(audio_path: str, language: str | None) -> dict | None:
    key = settings.ELEVENLABS_API_KEY
    if not key:
        return None
    import httpx
    url = "https://api.elevenlabs.io/v1/speech-to-text"
    with open(audio_path, "rb") as f:
        content = f.read()
    data = {"model_id": settings.ELEVENLABS_STT_MODEL}
    el = _eleven_lang(language) if language else None
    if el:
        data["language_code"] = el
    async with httpx.AsyncClient(timeout=90.0, headers={"xi-api-key": key}) as c:
        r = await c.post(url, files={"file": ("audio.webm", content, "audio/webm")}, data=data)
    if r.status_code != 200:
        logger.warning("elevenlabs stt failed", status=r.status_code, body=r.text[:150])
        return None
    j = r.json()
    text = (j.get("text") or "").strip()
    if not text:
        return None
    return {"transcript": text, "detected_language": j.get("language_code") or (language or "hi"),
            "confidence": 0.9, "source": "elevenlabs"}


async def transcribe(audio_path: str, language: str | None = None) -> dict:
    """Transcribe audio file. ElevenLabs -> faster-whisper -> browser hint."""
    r = await _elevenlabs_stt(audio_path, language)
    if r:
        return r
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("small", device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_path, language=language)
        text = " ".join(s.text for s in segments).strip()
        det = info.language if hasattr(info, "language") else (language or "hi")
        return {"transcript": text, "detected_language": det, "confidence": 0.9, "source": "faster-whisper"}
    except Exception as e:
        logger.warning("STT unavailable, use browser STT", error=str(e))
        return {"transcript": "", "detected_language": language or "hi",
                "confidence": 0.0, "source": "unavailable",
                "message": "Server STT not installed. Please use browser mic (Web Speech API) - frontend handles it."}


async def speak(text: str, language: str = "hi") -> dict:
    """Text -> audio file. ElevenLabs -> edge-tts -> gTTS -> browser fallback."""
    for provider in (_elevenlabs_tts, _edge_tts):
        r = await provider(text, language)
        if r:
            return r
    r = _gtts(text, language)
    if r:
        return r
    return {"audio_url": "", "duration_seconds": 0.0, "source": "browser-tts",
            "message": "Server TTS unavailable. Frontend will use browser speechSynthesis.",
            "text": text}