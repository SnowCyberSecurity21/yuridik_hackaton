"""Gemini provayderi: model nomlarini startup'da tekshirish, fallback -> shablon, LLM'ga shaxsiy ma'lumot ketmasligi.

Tarmoq ishlatilmaydi: httpx.MockTransport.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("DATABASE_URL", f"sqlite:///{(Path(tempfile.mkdtemp()) / 'gem.db').as_posix()}")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx  # noqa: E402
import pytest  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.db import SessionLocal  # noqa: E402
from app.main import bootstrap  # noqa: E402
from app.services import answer, llm  # noqa: E402
from app.services.privacy import scrub  # noqa: E402

KEY = "test-gemini-key-0123456789abcdefghij"


class Fake:
    def __init__(self, models=("gemini-3.5-flash-lite", "gemini-3.1-flash-lite"), reply="📘 Qonun nima deydi: test.",
                 delay=0.0, status=200, block=False):
        self.models, self.reply, self.delay, self.status, self.block = models, reply, delay, status, block
        self.requests: list[httpx.Request] = []

    async def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        assert request.headers.get("x-goog-api-key") == KEY and KEY not in str(request.url)  # kalit URL'da emas
        if request.method == "GET" and request.url.path.endswith("/models"):
            return httpx.Response(200, json={"models": [
                {"name": f"models/{m}", "supportedGenerationMethods": ["generateContent"]} for m in self.models]})
        await asyncio.sleep(self.delay)
        if self.status != 200:
            return httpx.Response(self.status, json={"error": {"message": "x"}})
        if self.block:
            return httpx.Response(200, json={"promptFeedback": {"blockReason": "SAFETY"}})
        return httpx.Response(200, json={"candidates": [{"finishReason": "STOP",
                                                         "content": {"parts": [{"text": self.reply}]}}]})


@pytest.fixture
def gemini(monkeypatch):
    bootstrap()
    s = get_settings()
    for k, v in dict(llm_provider="gemini", gemini_api_key=KEY, gemini_model="gemini-3.5-flash-lite",
                     gemini_fallback_model="gemini-3.1-flash-lite", llm_timeout=0.5).items():
        monkeypatch.setattr(s, k, v)
    monkeypatch.setitem(llm._gemini, "model", None)
    monkeypatch.setitem(llm._gemini, "checked", False)
    real = httpx.AsyncClient

    def install(**kw):
        fake = Fake(**kw)
        monkeypatch.setattr(httpx, "AsyncClient",
                            lambda **a: real(transport=httpx.MockTransport(fake.handler), timeout=a.get("timeout")))
        return fake
    return install


def run(c):
    return asyncio.run(c)


def ask(text="Bolamga nafaqa nega berilmadi?"):
    db = SessionLocal()
    try:
        return run(answer.answer_question(db, text, channel="cli"))
    finally:
        db.close()


def test_primary_model_selected(gemini):
    gemini()
    assert run(llm.verify_gemini_models()) == "gemini-3.5-flash-lite"
    assert llm.status() == {"provider": "gemini", "model": "gemini-3.5-flash-lite", "status": "ok"}


def test_fallback_model_selected(gemini):
    gemini(models=("gemini-3.1-flash-lite", "gemini-other"))
    assert run(llm.verify_gemini_models()) == "gemini-3.1-flash-lite"
    assert llm.status()["status"] == "zaxira model"


def test_no_model_disables_llm_and_uses_template(gemini):
    gemini(models=("gemini-unrelated",))
    assert run(llm.verify_gemini_models()) is None
    assert llm.is_available() is False
    res = ask()
    assert res["type"] == "card" and res["llm_used"] is False and res["sources"]


def test_gemini_answer_used_with_source(gemini):
    gemini(reply="📘 Qonun nima deydi: Rad etish sababini yozma so'rashingiz mumkin.")
    run(llm.verify_gemini_models())
    res = ask()
    assert res["llm_used"] is True and "lex.uz" in res["text"]


@pytest.mark.parametrize("kw", [dict(delay=3), dict(status=500), dict(block=True),
                                dict(reply="📘 nafaqa 999 999 so'm, https://fake.example.com")])
def test_gemini_failures_fall_back_to_template(gemini, kw):
    gemini(**kw)
    run(llm.verify_gemini_models())
    res = ask()
    assert res["llm_used"] is False and "999 999" not in res["text"] and res["sources"]


def test_no_personal_data_sent_to_llm(gemini):
    fake = gemini()
    run(llm.verify_gemini_models())
    q = ("Aliyev Vali, 01.01.1990. Telefonim +998 90 123 45 67, PINFL 12345678901234, pasport AB1234567, "
         "karta 8600 1234 5678 9012, pochta vali@example.com. Bolamga nafaqa nega berilmadi?")
    ask(q)
    sent = [json.loads(r.content) for r in fake.requests if r.method == "POST"]
    assert sent, "LLM chaqirilmadi"
    blob = json.dumps(sent, ensure_ascii=False)
    for pii in ("Aliyev", "1990", "123 45 67", "12345678901234", "AB1234567", "8600 1234", "vali@example.com"):
        assert pii not in blob, pii


def test_scrub_examples():
    s = scrub("Karimov Anvar o'g'li 05.03.1985 tug'ilgan, tel 90-123-45-67. Jarima 44 000 so'm.")
    assert "Karimov" not in s and "1985" not in s and "123-45-67" not in s
    assert "44 000 so'm" in s  # summa saqlanadi


def test_card_url_in_llm_answer_is_allowed(gemini):
    """Regressiya: kartadagi havola (my.gov.uz) rad etilmasin; begona havola rad etilsin."""
    gemini(reply="🏛 Qayerga: Yagona portal — https://my.gov.uz.")
    run(llm.verify_gemini_models())
    assert ask()["llm_used"] is True


def test_url_regex_does_not_glue_json_punctuation():
    from app.services.answer import _URL
    assert _URL.findall('{"url": "https://my.gov.uz"}, "x"') == ["https://my.gov.uz"]
