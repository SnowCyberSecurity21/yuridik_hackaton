"""Bot: /login [profil_id], /chiqish va Mini App menyu tugmasi.

Bot haqiqiy backend bilan ishlaydi (httpx ASGITransport — server shart emas).
Ishga tushirish:  .venv/Scripts/python -m pytest -q bot/tests
"""
from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from pathlib import Path

_tmp = Path(tempfile.mkdtemp())
os.environ.setdefault("DATABASE_URL", f"sqlite:///{(_tmp / 'bot.db').as_posix()}")
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["TELEGRAM_BOT_TOKEN"] = ""
os.environ["STT_PROVIDER"] = "none"
os.environ["TTS_PROVIDER"] = "none"
os.environ["INTERNAL_API_TOKEN"] = ""
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bot"))
sys.path.insert(0, str(ROOT / "backend"))

import httpx  # noqa: E402
import pytest  # noqa: E402

import backend_client  # noqa: E402
import handlers  # noqa: E402
import main as bot_main  # noqa: E402
from app.main import app, bootstrap  # noqa: E402

CHAT = 424242


@pytest.fixture(autouse=True)
def wire_backend(monkeypatch):
    bootstrap()
    monkeypatch.setattr(backend_client, "_client", None)
    monkeypatch.setattr(backend_client, "client", lambda: httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://backend", timeout=10))
    yield


def run(coro):
    return asyncio.run(coro)


def buttons(kb):
    return [b for row in (kb.inline_keyboard if kb else []) for b in row]


def me():
    return run(backend_client.profile_me(str(CHAT)))


def test_login_without_arg_shows_three_profile_buttons():
    text, kb = run(handlers.login_command(None, CHAT, "uz"))
    datas = [b.callback_data for b in buttons(kb)]
    assert datas == ["p:in:demo_mother", "p:in:demo_pensioner", "p:in:demo_driver"]
    assert "Rozilik" in text and "DEMO" in text


def test_login_unknown_profile_is_rejected():
    run(handlers.logout_command(CHAT, "uz"))
    for bad in ("demo_hacker", "../cards/alimony", "mother"):
        text, kb = run(handlers.login_command(bad, CHAT, "uz"))
        assert text.startswith("Bunday demo profil yo'q")
        assert len(buttons(kb)) == 3
    assert me()["linked"] is False  # rozilik yozuvi yaratilmadi


def test_login_valid_profile_records_consent_and_shows_profile():
    text, kb = run(handlers.login_command("demo_mother", CHAT, "uz"))
    assert "Rozilik qayd etildi" in text and "Malika (DEMO)" in text and "Haqli bo'lishingiz mumkin" in text
    datas = [b.callback_data for b in buttons(kb)]
    assert "pb:benefit_child_allowance" in datas and "p:out" in datas
    state = me()
    assert state["linked"] and state["profile"]["id"] == "demo_mother"

    from app.db import SessionLocal
    from app.models import ProfileLink
    db = SessionLocal()
    try:
        link = db.get(ProfileLink, str(CHAT))
        assert link.consent_scope and link.consent_at and link.channel == "telegram"
    finally:
        db.close()


def test_logout_flow_like_cli():
    run(handlers.login_command("demo_driver", CHAT, "uz"))
    assert "Rozilik bekor qilindi" in run(handlers.logout_command(CHAT, "uz"))
    assert me()["linked"] is False
    assert run(handlers.logout_command(CHAT, "uz")).startswith("Profil ulanmagan")


class FakeBot:
    def __init__(self, fail=False):
        self.calls, self.fail = [], fail

    async def set_chat_menu_button(self, **kw):
        if self.fail:
            raise RuntimeError("telegram down")
        self.calls.append(kw)


def test_menu_button_set_when_webapp_url(monkeypatch):
    monkeypatch.setattr(bot_main.settings, "webapp_url", "https://huquqim.example.uz/miniapp")
    bot = FakeBot()
    assert run(bot_main.setup_menu_button(bot)) is True
    btn = bot.calls[0]["menu_button"]
    assert btn.type == "web_app" and btn.text == "Huquqim" and btn.web_app.url.endswith("/miniapp")


def test_menu_button_skipped_without_webapp_url(monkeypatch):
    monkeypatch.setattr(bot_main.settings, "webapp_url", "")
    bot = FakeBot()
    assert run(bot_main.setup_menu_button(bot)) is False and bot.calls == []


def test_menu_button_error_does_not_crash(monkeypatch):
    monkeypatch.setattr(bot_main.settings, "webapp_url", "https://huquqim.example.uz/miniapp")
    assert run(bot_main.setup_menu_button(FakeBot(fail=True))) is False
