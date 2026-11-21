"""LLM: qat'iy timeout va xavfsizlik filtri — vaqt o'tsa/xato bo'lsa/kartada yo'q fakt bo'lsa, shablon javob."""
from __future__ import annotations

import asyncio
import os
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("DATABASE_URL", f"sqlite:///{(Path(tempfile.mkdtemp()) / 'llm.db').as_posix()}")
os.environ["ANTHROPIC_API_KEY"] = ""
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.db import SessionLocal  # noqa: E402
from app.main import bootstrap  # noqa: E402
from app.services import answer, llm  # noqa: E402


class FakeMessages:
    def __init__(self, text=None, delay=0.0, exc=None):
        self.text, self.delay, self.exc = text, delay, exc

    async def create(self, **kw):
        await asyncio.sleep(self.delay)
        if self.exc:
            raise self.exc
        return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=self.text)])


def fake_client(**kw):
    m = FakeMessages(**kw)
    return SimpleNamespace(messages=m, beta=SimpleNamespace(messages=m))


@pytest.fixture
def llm_on(monkeypatch):
    bootstrap()
    s = get_settings()
    monkeypatch.setattr(s, "llm_timeout", 0.3)
    monkeypatch.setattr(s, "llm_model", "claude-sonnet-5-5")

    def install(**kw):
        monkeypatch.setattr(llm, "_client", lambda: fake_client(**kw))
    return install


def ask(text="Bolamga nafaqa nega berilmadi?"):
    db = SessionLocal()
    try:
        return asyncio.run(answer.answer_question(db, text, channel="cli"))
    finally:
        db.close()


def test_defaults_are_sonnet_and_8s():
    from app.config import Settings
    fields = Settings.model_fields
    assert fields["llm_model"].default == "claude-sonnet-5-5"
    assert fields["llm_timeout"].default == 8.0


def test_slow_llm_times_out_fast_and_falls_back(llm_on):
    llm_on(text="📘 Qonun nima deydi: ...", delay=5)
    t0 = time.monotonic()
    res = ask()
    assert time.monotonic() - t0 < 2  # 0.3 s chegara, 5 s kutilmaydi
    assert res["type"] == "card" and res["llm_used"] is False and res["sources"]


def test_llm_error_falls_back(llm_on):
    llm_on(exc=RuntimeError("API xatosi"))
    res = ask()
    assert res["llm_used"] is False and "Manba tekshirildi" in res["text"]


def test_llm_invented_number_or_link_rejected(llm_on):
    llm_on(text="📘 Qonun nima deydi: nafaqa 999 999 so'm, batafsil https://fake.example.com")
    res = ask()
    assert res["llm_used"] is False
    assert "999 999" not in res["text"] and "fake.example.com" not in res["text"]


def test_safe_llm_text_is_used_with_source_appended(llm_on):
    llm_on(text="📘 Qonun nima deydi: Rad etish sababini yozma so'rashingiz mumkin.")
    res = ask()
    assert res["llm_used"] is True
    assert "lex.uz" in res["text"] and res["disclaimer"]  # manba va ogohlantirish kod tomonidan qo'shiladi
