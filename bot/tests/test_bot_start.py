"""Bot /start: ikki yo'l (OneID / anonim), anonim maqom tanlovi, link_<token> orqali hisobni ulash."""
from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse

_tmp = Path(tempfile.mkdtemp())
os.environ.setdefault("DATABASE_URL", f"sqlite:///{(_tmp / 'bot_start.db').as_posix()}")
for _k in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "TELEGRAM_BOT_TOKEN", "INTERNAL_API_TOKEN"):
    os.environ[_k] = ""
os.environ["STT_PROVIDER"] = "none"
os.environ["TTS_PROVIDER"] = "none"
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bot"))
sys.path.insert(0, str(ROOT / "backend"))

import httpx  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import account_handlers as ah  # noqa: E402
import backend_client  # noqa: E402
from app.main import app, bootstrap  # noqa: E402

CHAT = 515151


class Chat:
    def __init__(self, cid):
        self.id = cid


class FakeMessage:
    def __init__(self, cid=CHAT):
        self.chat = Chat(cid)
        self.sent: list[tuple[str, object]] = []

    async def answer(self, text, reply_markup=None, **kw):
        self.sent.append((text, reply_markup))

    async def edit_reply_markup(self, reply_markup=None):
        self.sent.append(("<edit>", reply_markup))


class FakeCb:
    def __init__(self, data, cid=CHAT):
        self.data, self.message = data, FakeMessage(cid)

    async def answer(self, *a, **kw):
        pass


class Cmd:
    def __init__(self, args):
        self.args = args


@pytest.fixture(autouse=True)
def wire_backend(monkeypatch):
    bootstrap()
    monkeypatch.setattr(backend_client, "_client", None)
    monkeypatch.setattr(backend_client, "client", lambda: httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://backend", timeout=10))
    yield


def run(c):
    return asyncio.run(c)


def buttons(kb):
    return [b for row in (kb.inline_keyboard if kb else []) for b in row]


def test_start_shows_two_paths():
    m = FakeMessage(CHAT + 1)
    run(ah.send_start(m, CHAT + 1))
    text, kb = m.sent[-1]
    btns = buttons(kb)
    assert "OneID" in btns[0].text and btns[0].url and "/kirish?next=oneid" in btns[0].url
    assert btns[1].callback_data == "m:anon" and "Anonim" in btns[1].text
    assert "saqlanmaydi" in text


def test_anonymous_path_status_and_rights():
    cid = CHAT + 2
    cb = FakeCb("m:anon", cid)
    run(ah.cb_anon(cb))
    assert [b.callback_data for b in buttons(cb.message.sent[-1][1])] == ["st:uz_citizen", "st:foreign", "st:stateless", "st:unknown"]
    run(ah.cb_status(FakeCb("st:foreign", cid)))
    run(ah.cb_situation(FakeCb("si:parent", cid)))
    done = FakeCb("si:done", cid)
    run(ah.cb_situation(done))
    assert "saqlanmaydi" in done.message.sent[-1][0]
    assert ah.legal_status_of(cid) == "foreign" and ah.anon[cid]["situations"] == ["parent"]
    r = FakeCb("an:rights", cid)
    run(ah.cb_anon_section(r))
    assert "Chet el fuqarosi" in r.message.sent[-1][0] and "lex.uz/docs/5443899" in r.message.sent[-1][0]


def test_start_link_token_connects_verified_account():
    c = TestClient(app)
    c.post("/api/auth/register", json={"username": "botuser1", "password": "parol12345"})
    loc = c.get("/api/oneid/start", follow_redirects=False).headers["location"]
    q = {k: v[0] for k, v in parse_qs(urlparse(loc).query).items()}
    form = {"client_id": q["client_id"], "redirect_uri": q["redirect_uri"], "state": q["state"]}
    c.post("/oneid-demo/login", data={**form, "login": "Karim", "password": "12345678"})
    r = c.post("/oneid-demo/consent", data={**form, "decision": "allow"}, follow_redirects=False)
    c.get(r.headers["location"], follow_redirects=False)
    tok = c.post("/api/me/telegram/link").json()["url"].split("link_", 1)[1]

    m = FakeMessage(CHAT + 3)
    run(ah.start_deep(m, Cmd("link_" + tok)))
    text, kb = m.sent[-1]
    assert "Salom, Karim ota!" in text
    assert "v:benefits" in [b.callback_data for b in buttons(kb)]
    # qayta ishlatib bo'lmaydi
    m2 = FakeMessage(CHAT + 4)
    run(ah.start_deep(m2, Cmd("link_" + tok)))
    assert "yaroqsiz" in m2.sent[-1][0]
    # keyingi /start — tasdiqlangan salom
    m3 = FakeMessage(CHAT + 3)
    run(ah.send_start(m3, CHAT + 3))
    assert m3.sent[-1][0].startswith("Salom, Karim ota!")
    sec = FakeCb("v:rights", CHAT + 3)
    run(ah.cb_verified(sec))
    assert "O'zbekiston fuqarosi" in sec.message.sent[-1][0]
