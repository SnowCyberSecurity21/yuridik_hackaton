"""STT (ovoz -> matn) va TTS (matn -> ovoz). Har biri timeout + fallback bilan.

STT_PROVIDER: none | openai (Whisper-mos API) | faster_whisper (lokal) | gemini (GEMINI_API_KEY, audio inline_data)
TTS_PROVIDER: edge (edge-tts, uz-UZ ovozlari) | none
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import re
import tempfile
import time
from pathlib import Path

import httpx

from ..config import get_settings

log = logging.getLogger("javob.speech")

_tts_ok: bool | None = None  # startup tekshiruvidan keyin aniqlanadi
_fw_model = None


# ------------------------------------------------------------------ STT

GEMINI_STT_TIMEOUT = 15.0
GEMINI_STT_MAX_BYTES = 15 * 1024 * 1024  # inline_data chegarasi (~20 MB) dan pastroq
GEMINI_STT_PROMPT = ("Faqat aytilgan so'zlarni o'zbek tilida (yoki aytilgan tilda) yozib ber, hech narsa qo'shma. "
                     "Izoh, tarjima yoki javob yozma — faqat matn. Nutq bo'lmasa, bo'sh javob qaytar.")
_MIME = {".ogg": "audio/ogg", ".oga": "audio/ogg", ".opus": "audio/ogg", ".mp3": "audio/mp3", ".wav": "audio/wav",
         ".m4a": "audio/aac", ".aac": "audio/aac", ".flac": "audio/flac", ".webm": "audio/webm"}


def stt_available() -> bool:
    s = get_settings()
    if s.stt_provider == "gemini":
        return bool(s.gemini_api_key.strip())
    if s.stt_provider == "openai":
        return bool(s.stt_api_key.strip())
    if s.stt_provider == "faster_whisper":
        try:
            import faster_whisper  # noqa: F401
            return True
        except ImportError:
            return False
    return False


async def transcribe(audio: bytes, filename: str = "voice.ogg") -> str | None:
    s = get_settings()
    if not stt_available() or not audio:
        return None
    try:
        if s.stt_provider == "gemini":
            return await asyncio.wait_for(_gemini_transcribe(audio, filename), timeout=GEMINI_STT_TIMEOUT)
        if s.stt_provider == "openai":
            async with httpx.AsyncClient(timeout=s.stt_timeout) as c:
                r = await c.post(f"{s.stt_api_base.rstrip('/')}/audio/transcriptions",
                                 headers={"Authorization": f"Bearer {s.stt_api_key}"},
                                 data={"model": s.stt_model, "language": s.stt_language},
                                 files={"file": (filename, audio)})
                r.raise_for_status()
                return (r.json().get("text") or "").strip() or None
        if s.stt_provider == "faster_whisper":
            return await asyncio.wait_for(asyncio.to_thread(_fw_transcribe, audio), timeout=s.stt_timeout * 2)
    except Exception as e:  # noqa: BLE001
        log.warning("STT xatosi: %s", type(e).__name__)
    return None


async def _gemini_transcribe(audio: bytes, filename: str) -> str | None:
    """Gemini generateContent: audio inline_data (base64) + qat'iy "faqat transkripsiya" so'rovi."""
    import base64

    from . import llm

    s = get_settings()
    if len(audio) > GEMINI_STT_MAX_BYTES:
        log.warning("STT: audio juda katta (%s bayt)", len(audio))
        return None
    model = llm._gemini.get("model") or s.gemini_model.strip()
    mime = _MIME.get(Path(filename or "").suffix.lower(), "audio/ogg")
    body = {
        "contents": [{"role": "user", "parts": [
            {"text": GEMINI_STT_PROMPT},
            {"inline_data": {"mime_type": mime, "data": base64.b64encode(audio).decode("ascii")}},
        ]}],
        "generationConfig": {"temperature": 0.0, "maxOutputTokens": 1024},
    }
    url = f"{s.gemini_api_base.rstrip('/')}/models/{model}:generateContent"
    headers = {"x-goog-api-key": s.gemini_api_key.strip(), "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=GEMINI_STT_TIMEOUT) as c:
        r = await c.post(url, json=body, headers=headers)
    if r.status_code != 200:
        log.warning("Gemini STT HTTP %s", r.status_code)
        return None
    data = r.json()
    if (data.get("promptFeedback") or {}).get("blockReason"):
        log.warning("Gemini STT so'rovni blokladi")
        return None
    cands = data.get("candidates") or []
    if not cands or cands[0].get("finishReason") not in (None, "STOP", "MAX_TOKENS"):
        log.warning("Gemini STT javobi yo'q (%s)", cands[0].get("finishReason") if cands else "bo'sh")
        return None
    parts = (cands[0].get("content") or {}).get("parts") or []
    text = " ".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
    text = re.sub(r"\s+", " ", text).strip(" \"'«»")
    return text or None


def _fw_transcribe(audio: bytes) -> str | None:
    global _fw_model
    from faster_whisper import WhisperModel  # type: ignore

    s = get_settings()
    if _fw_model is None:
        _fw_model = WhisperModel(s.faster_whisper_size, device="cpu", compute_type="int8")
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
        f.write(audio)
        path = f.name
    try:
        segments, _ = _fw_model.transcribe(path, language=s.stt_language or None)
        return " ".join(seg.text for seg in segments).strip() or None
    finally:
        Path(path).unlink(missing_ok=True)


# ------------------------------------------------------------------ TTS

async def verify_tts() -> bool:
    """Startup'da: edge-tts ishlaydimi va uz-UZ ovozi bormi."""
    global _tts_ok
    s = get_settings()
    if s.tts_provider != "edge":
        _tts_ok = False
        return False
    try:
        import edge_tts

        voices = await asyncio.wait_for(edge_tts.list_voices(), timeout=s.tts_timeout)
        names = {v.get("ShortName") for v in voices}
        _tts_ok = s.tts_voice_uz in names
        if not _tts_ok:
            log.warning("TTS ovozi topilmadi: %s", s.tts_voice_uz)
    except Exception as e:  # noqa: BLE001
        log.warning("TTS tekshiruvi muvaffaqiyatsiz (faqat matn rejimi): %s %s", type(e).__name__, e)
        _tts_ok = False
    return _tts_ok


_last_check = 0.0
RECHECK_SECONDS = 600


def start_verify() -> None:
    """Startup'da fon rejimida tekshirish (startup'ni bloklamaydi)."""
    global _last_check
    _last_check = time.monotonic()
    asyncio.get_running_loop().create_task(verify_tts())


def tts_available() -> bool:
    """Startup'da ishlamagan bo'lsa, 10 daqiqada bir fon rejimida qayta tekshiradi (tarmoq tiklanishi mumkin)."""
    global _last_check
    if not _tts_ok and get_settings().tts_provider == "edge":
        now = time.monotonic()
        if now - _last_check > RECHECK_SECONDS:
            _last_check = now
            try:
                asyncio.get_running_loop().create_task(verify_tts())
            except RuntimeError:
                pass
    return bool(_tts_ok)


_EMOJI = re.compile(r"[\U0001F000-\U0001FAFF☀-➿️←-⇿]")
_URL = re.compile(r"https?://\S+")


def _speakable(text: str) -> str:
    text = _URL.sub("", text)
    text = _EMOJI.sub("", text)
    text = text.replace("TODO_LAWYER", "")
    return re.sub(r"[ \t]+", " ", text).strip()[:1500]


async def synthesize(text: str, lang: str = "uz") -> bytes | None:
    if not tts_available():
        return None
    s = get_settings()
    voice = s.tts_voice_ru if lang == "ru" else s.tts_voice_uz
    clean = _speakable(text)
    if not clean:
        return None
    cache_dir = s.data_dir / "tts_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(f"{voice}|{clean}".encode()).hexdigest()[:32]
    path = cache_dir / f"{key}.mp3"
    if path.exists():
        return path.read_bytes()
    try:
        import edge_tts

        async def _run() -> bytes:
            buf = bytearray()
            async for chunk in edge_tts.Communicate(clean, voice).stream():
                if chunk.get("type") == "audio":
                    buf.extend(chunk["data"])
            return bytes(buf)

        audio = await asyncio.wait_for(_run(), timeout=s.tts_timeout)
        if audio:
            path.write_bytes(audio)
            return audio
    except Exception as e:  # noqa: BLE001
        log.warning("TTS xatosi: %s", e)
    return None
