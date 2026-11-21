"""Gemini STT: Telegram .ogg -> generateContent (inline_data audio/ogg), timeout va xatoda None.

Tarmoq ishlatilmaydi: httpx.MockTransport.
"""
from __future__ import annotations

import asyncio
import base64
import json
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("DATABASE_URL", f"sqlite:///{(Path(tempfile.mkdtemp()) / 'stt.db').as_posix()}")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.services import llm, speech  # noqa: E402

KEY = "test-gemini-key-0123456789abcdefghij"
AUDIO = b"OggS\x00\x02fake-opus-voice"


class Fake:
    def __init__(self, reply="Bolamga nafaqa nega berilmadi?", status=200, delay=0.0, block=False):
        self.reply, self.status, self.delay, self.block = reply, status, delay, block
        self.requests: list[httpx.Request] = []

    async def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        await asyncio.sleep(self.delay)
        if self.status != 200:
            return httpx.Response(self.status, json={"error": {"message": "x"}})
        if self.block:
            return httpx.Response(200, json={"promptFeedback": {"blockReason": "SAFETY"}})
        return httpx.Response(200, json={"candidates": [{"finishReason": "STOP",
                                                         "content": {"parts": [{"text": self.reply}]}}]})


@pytest.fixture
def stt(monkeypatch):
    s = get_settings()
    monkeypatch.setattr(s, "stt_provider", "gemini")
    monkeypatch.setattr(s, "gemini_api_key", KEY)
    monkeypatch.setattr(s, "gemini_model", "gemini-3.5-flash-lite")
    monkeypatch.setitem(llm._gemini, "model", None)
    real = httpx.AsyncClient

    def install(**kw):
        fake = Fake(**kw)
        monkeypatch.setattr(httpx, "AsyncClient",
                            lambda **a: real(transport=httpx.MockTransport(fake.handler), timeout=a.get("timeout")))
        return fake
    return install


def test_available_only_with_key(stt, monkeypatch):
    stt()
    assert speech.stt_available()
    monkeypatch.setattr(get_settings(), "gemini_api_key", " ")
    assert not speech.stt_available()


def test_transcribe_sends_inline_ogg(stt):
    fake = stt(reply=' "Bolamga nafaqa nega berilmadi?"\n')
    text = asyncio.run(speech.transcribe(AUDIO, "voice.ogg"))
    assert text == "Bolamga nafaqa nega berilmadi?"
    req = fake.requests[0]
    assert req.url.path.endswith("/models/gemini-3.5-flash-lite:generateContent")
    assert req.headers["x-goog-api-key"] == KEY and KEY not in str(req.url)
    parts = json.loads(req.content)["contents"][0]["parts"]
    assert "hech narsa qo'shma" in parts[0]["text"]
    inline = parts[1]["inline_data"]
    assert inline["mime_type"] == "audio/ogg" and base64.b64decode(inline["data"]) == AUDIO


def test_uses_verified_model(stt, monkeypatch):
    fake = stt()
    monkeypatch.setitem(llm._gemini, "model", "gemini-3.1-flash-lite")
    asyncio.run(speech.transcribe(AUDIO))
    assert fake.requests[0].url.path.endswith("/models/gemini-3.1-flash-lite:generateContent")


@pytest.mark.parametrize("kw", [dict(status=500), dict(status=429), dict(block=True), dict(reply="  ")])
def test_errors_return_none(stt, kw):
    stt(**kw)
    assert asyncio.run(speech.transcribe(AUDIO)) is None


def test_timeout_returns_none(stt, monkeypatch):
    monkeypatch.setattr(speech, "GEMINI_STT_TIMEOUT", 0.05)
    stt(delay=1.0)
    assert asyncio.run(speech.transcribe(AUDIO)) is None


def test_voice_endpoint_falls_back_to_unsupported(stt):
    from app.main import app

    stt(status=503)
    with TestClient(app) as c:
        r = c.post("/api/ask/voice", files={"file": ("voice.ogg", AUDIO, "audio/ogg")})
    body = r.json()
    assert r.status_code == 200 and body["type"] == "voice_unsupported" and body["transcript"] is None
