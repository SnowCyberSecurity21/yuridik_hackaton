"""Huquqim hisobi + DEMO ID (OneID simulyatsiyasi), maqomlar, anonim rejim, Telegram link tokeni, simulyatsiya cheklovi.

Ishga tushirish:  .venv/Scripts/python -m pytest -q backend/tests
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlparse

_tmp = Path(tempfile.mkdtemp())
os.environ["DATABASE_URL"] = f"sqlite:///{(_tmp / 'accounts.db').as_posix()}"
for _k in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "TELEGRAM_BOT_TOKEN", "INTERNAL_API_TOKEN"):
    os.environ[_k] = ""
os.environ["TTS_PROVIDER"] = "none"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.api import account as account_api  # noqa: E402
from app.db import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models import (Account, Alert, BotLinkToken, ProfileLink, Subscription, TelegramLink,  # noqa: E402
                        WebSession, utcnow)
from app.oneid_demo import router as oneid_router  # noqa: E402
from app.oneid_demo import service as oneid  # noqa: E402
from app.services import rights  # noqa: E402

PW = "12345678"
_n = {"i": 0}


@pytest.fixture(scope="module")
def app_ready():
    with TestClient(app):
        yield


@pytest.fixture(autouse=True)
def no_limits():
    for lim in (account_api.login_ip_limiter, account_api.login_user_limiter, account_api.register_limiter,
                account_api.link_limiter, oneid_router.login_ip_limiter, oneid_router.login_user_limiter):
        lim.reset()
    account_api._sim_last["t"] = 0.0
    yield


def new_client(app_ready) -> TestClient:
    c = TestClient(app)
    _n["i"] += 1
    r = c.post("/api/auth/register", json={"username": f"user{_n['i']}", "password": "parol12345"})
    assert r.status_code == 200, r.text
    return c


def verify(c: TestClient, login: str, decision: str = "allow") -> str:
    r = c.get("/api/oneid/start", follow_redirects=False)
    assert r.status_code == 303
    loc = r.headers["location"]
    assert loc.startswith("/oneid-demo/authorize?")
    q = {k: v[0] for k, v in parse_qs(urlparse(loc).query).items()}
    page = c.get(loc)
    assert "DEMO identifikatsiya — haqiqiy OneID login va parolingizni kiritmang." in page.text.replace("&#x27;", "'")
    form = {"client_id": q["client_id"], "redirect_uri": q["redirect_uri"], "state": q["state"]}
    r = c.post("/oneid-demo/login", data={**form, "login": login, "password": PW}, follow_redirects=False)
    assert r.status_code == 303
    consent = c.get(r.headers["location"])
    assert "Huquqim</b> quyidagi ma" in consent.text
    r = c.post("/oneid-demo/consent", data={**form, "decision": decision}, follow_redirects=False)
    r = c.get(r.headers["location"], follow_redirects=False)
    return r.headers["location"]


# ------------------------------------------------------------------ ro'yxat va kirish

def test_register_login_logout(app_ready):
    c = TestClient(app)
    r = c.post("/api/auth/register", json={"username": "Malika94", "password": "qisqa"})
    assert r.status_code == 400
    r = c.post("/api/auth/register", json={"username": "Malika94", "password": "uzunparol1"})
    assert r.status_code == 200 and r.json()["logged_in"] and not r.json()["verified"]
    assert "hq_sid" in r.cookies or c.cookies.get("hq_sid")
    assert c.post("/api/auth/register", json={"username": "malika94", "password": "uzunparol1"}).status_code == 400
    c2 = TestClient(app)
    assert c2.post("/api/auth/login", json={"username": "malika94", "password": "notogri00"}).status_code == 401
    assert c2.post("/api/auth/login", json={"username": "malika94", "password": "uzunparol1"}).status_code == 200
    assert c2.get("/api/auth/me").json()["username"] == "malika94"
    db = SessionLocal()
    try:
        acc = db.query(Account).filter(Account.username == "malika94").one()
        assert acc.password_hash.startswith("scrypt$") and "uzunparol1" not in acc.password_hash
    finally:
        db.close()
    c2.post("/api/auth/logout")
    assert c2.get("/api/auth/me").json()["logged_in"] is False


def test_login_rate_limit(app_ready):
    c = TestClient(app)
    codes = [c.post("/api/auth/login", json={"username": "kimdir", "password": "xxxxxxxx"}).status_code for _ in range(10)]
    assert 429 in codes


def test_demo_id_login_rate_limit(app_ready):
    c = new_client(app_ready)
    loc = c.get("/api/oneid/start", follow_redirects=False).headers["location"]
    q = {k: v[0] for k, v in parse_qs(urlparse(loc).query).items()}
    form = {"client_id": q["client_id"], "redirect_uri": q["redirect_uri"], "state": q["state"], "login": "Azizbek", "password": "yomon"}
    texts = [c.post("/oneid-demo/login", data=form).text for _ in range(10)]
    assert any("Juda ko" in t and "urinish" in t for t in texts)


# ------------------------------------------------------------------ OneID oqimi

def test_oneid_flow_consent_and_revoke(app_ready):
    c = new_client(app_ready)
    assert c.get("/api/me/cabinet").status_code == 409
    assert verify(c, "Malika") == "/kabinet?oneid=ok"
    me = c.get("/api/auth/me").json()
    assert me["verified"] and me["first_name"] == "Malika" and me["consent_scope"]
    v = c.get("/api/me/cabinet").json()
    assert v["person"]["status"] == "uz_citizen"
    assert any(b["id"] == "benefit_child_allowance" for b in v["benefits"])
    assert 3 <= len(v["laws"]) <= 6 and all(law["url"].startswith("https://lex.uz/") for law in v["laws"])
    # OneID ma'lumotlari Huquqim jadvalida saqlanmaydi
    db = SessionLocal()
    try:
        acc = db.query(Account).filter(Account.oneid_sub == "demo-id-0002").first()
        cols = {k: getattr(acc, k) for k in ("username", "oneid_sub", "consent_scope")}
        assert "Sobirova" not in json.dumps(cols, default=str)
    finally:
        db.close()
    # tayyor ariza
    r = c.post("/api/me/appeal", json={"benefit_id": "benefit_child_allowance"})
    assert r.status_code == 200 and "Malika Sobirova (DEMO)" in r.json()["text"]
    # bekor qilish
    assert c.post("/api/oneid/revoke").json()["ok"]
    assert c.get("/api/auth/me").json()["verified"] is False
    assert c.get("/api/me/cabinet").status_code == 409


def test_oneid_deny_and_bad_state(app_ready):
    c = new_client(app_ready)
    assert verify(c, "Karim", decision="deny") == "/kabinet?oneid=denied"
    assert c.get("/api/auth/me").json()["verified"] is False
    r = c.get("/api/oneid/callback?code=abc&state=xyz", follow_redirects=False)
    assert r.headers["location"] == "/kabinet?oneid=error"


def test_demo_id_rejects_unknown_client(app_ready):
    c = TestClient(app)
    r = c.get("/oneid-demo/authorize?client_id=evil&redirect_uri=https://evil.example/cb&state=s")
    assert "Noto'g'ri so'rov" in r.text


def test_code_is_single_use(app_ready):
    db = SessionLocal()
    try:
        code = oneid.issue_code(db, "demo-id-0001", "huquqim", "/api/oneid/callback")
        assert oneid.exchange_code(db, code, "huquqim", "/api/oneid/callback")
        assert oneid.exchange_code(db, code, "huquqim", "/api/oneid/callback") is None
    finally:
        db.close()


# ------------------------------------------------------------------ anonim rejim

def test_anonymous_mode_stores_no_personal_data(app_ready):
    c = TestClient(app)
    db = SessionLocal()
    try:
        before = {m.__name__: db.query(m).count() for m in (Account, WebSession, ProfileLink, Subscription, TelegramLink)}
    finally:
        db.close()
    r = c.post("/api/ask", json={"text": "Bolamga nafaqa nega berilmadi?", "legal_status": "foreign", "channel": "web"})
    assert r.status_code == 200
    assert c.get("/api/rights?status=stateless&situations=parent").status_code == 200
    db = SessionLocal()
    try:
        after = {m.__name__: db.query(m).count() for m in (Account, WebSession, ProfileLink, Subscription, TelegramLink)}
        from app.models import Event
        ev = db.query(Event).order_by(Event.id.desc()).first()
        assert "legal_status" not in Event.__table__.columns and ev.topic_id
    finally:
        db.close()
    assert before == after
    assert "hq_sid" not in c.cookies


# ------------------------------------------------------------------ maqomlar

def test_status_sections_and_answer_note(app_ready):
    f = c_get = TestClient(app).get
    foreign = f("/api/rights?status=foreign").json()
    assert any(i["law"]["id"] == "foreign_status_law" and i["article"] == "16-modda" for i in foreign["status"]["rights"])
    citizen = c_get("/api/rights?status=uz_citizen").json()
    assert all(i["law"]["id"] != "foreign_status_law" for i in citizen["status"]["rights"] + citizen["status"]["duties"])
    stateless = f("/api/rights?status=stateless").json()
    assert stateless["status"]["id"] == "stateless" and stateless["status"]["rights"]
    assert f("/api/rights?status=hacker").json()["status"]["id"] == "unknown"

    c = TestClient(app)
    q = "Bolamga nafaqa nega berilmadi?"
    r_f = c.post("/api/ask", json={"text": q, "legal_status": "foreign"}).json()
    r_c = c.post("/api/ask", json={"text": q, "legal_status": "uz_citizen"}).json()
    assert r_f.get("status_note") and "boshqacha bo'lishi mumkin" in r_f["text"]
    assert not r_c.get("status_note")


def test_verified_foreign_person_gets_status_rules(app_ready):
    c = new_client(app_ready)
    verify(c, "Erlan")
    v = c.get("/api/me/cabinet").json()
    assert v["person"]["status"] == "foreign"
    assert v["laws"][0]["id"] == "foreign_status_law"
    assert v["rights"]["status"]["id"] == "foreign"


# ------------------------------------------------------------------ manba qoidasi

def test_unsourced_entries_are_hidden(app_ready, tmp_path, monkeypatch):
    from app.config import get_settings
    (tmp_path / "laws").mkdir()
    (tmp_path / "rights").mkdir()
    good = {"id": "good", "title_uz": "Yaxshi", "date": "2020-01-01", "url": "https://lex.uz/docs/1", "retrieved_at": "2026-11-21",
            "source_verified": True, "statuses": ["unknown"]}
    bad_domain = {**good, "id": "bad_domain", "url": "https://example.com/law"}
    no_check = {**good, "id": "no_check", "source_verified": False}
    no_date = {**good, "id": "no_retrieved", "retrieved_at": None}
    for d in (good, bad_domain, no_check, no_date):
        (tmp_path / "laws" / f"{d['id']}.json").write_text(json.dumps(d), encoding="utf-8")
    (tmp_path / "rights" / "status_unknown.json").write_text(json.dumps({"id": "unknown", "type": "status", "title_uz": "Bilmayman", "items": [
        {"id": "a", "kind": "right", "title_uz": "Manbali", "plain_uz": "x", "law_id": "good", "article": "1-modda"},
        {"id": "b", "kind": "right", "title_uz": "Manbasiz", "plain_uz": "y", "law_id": "bad_domain", "article": ""},
        {"id": "c", "kind": "right", "title_uz": "Yo'q qonun", "plain_uz": "z", "law_id": "missing", "article": ""}]}), encoding="utf-8")
    monkeypatch.setattr(get_settings(), "knowledge_dir", tmp_path)
    rights.reload()
    try:
        assert set(rights.laws()) == {"good"}
        v = TestClient(app).get("/api/rights?status=unknown").json()
        titles = [i["title"] for i in v["status"]["rights"]]
        assert titles == ["Manbali"]
        assert [x["id"] for x in TestClient(app).get("/api/laws").json()] == ["good"]
    finally:
        monkeypatch.undo()
        rights.reload()
    # haqiqiy bazada: har bir qonun rasmiy manbali
    for law in rights.laws().values():
        assert rights.law_is_sourced(law)


# ------------------------------------------------------------------ Telegram link tokeni

def test_link_token_single_use_and_expiry(app_ready):
    c = new_client(app_ready)
    verify(c, "Sardor")
    url = c.post("/api/me/telegram/link").json()["url"]
    assert url.startswith("https://t.me/Huquqim_official_bot?start=link_")
    tok = url.split("link_", 1)[1]
    r = c.post("/api/bot/link", json={"chat_id": "777001", "token": tok}).json()
    assert r["ok"] and r["verified"] and r["first_name"] == "Sardor"
    assert c.post("/api/bot/link", json={"chat_id": "777002", "token": tok}).json()["ok"] is False  # qayta ishlatilmaydi
    me = c.get("/api/bot/me?chat_id=777001").json()
    assert me["verified"] and me["status"] == "uz_citizen"
    sec = c.get("/api/bot/section?chat_id=777001&section=obligations").json()
    assert "jarima" in sec["text"].lower() and sec["obligations"]
    # muddati o'tgan token
    tok2 = c.post("/api/me/telegram/link").json()["url"].split("link_", 1)[1]
    db = SessionLocal()
    try:
        from app.services.security import token_hash
        row = db.get(BotLinkToken, token_hash(tok2))
        row.expires_at = utcnow() - timedelta(seconds=1)
        db.commit()
    finally:
        db.close()
    assert c.post("/api/bot/link", json={"chat_id": "777003", "token": tok2}).json()["ok"] is False
    # uzish
    assert c.post("/api/me/telegram/unlink").json()["ok"]
    assert c.get("/api/bot/me?chat_id=777001").json()["linked"] is False


# ------------------------------------------------------------------ rollar va simulyatsiya cheklovi

def test_roles_gov_and_student(app_ready):
    stud = new_client(app_ready)
    verify(stud, "Azizbek")
    assert "student" in stud.get("/api/auth/me").json()["roles"]
    assert stud.get("/api/edu/cases").status_code == 200
    assert stud.post("/api/edu/trainer/check", json={"text": "ARIZA"}).status_code == 200
    assert stud.get("/api/cabinet/gov/overview").status_code == 403
    assert stud.post("/api/cabinet/gov/simulate-amendment", json={}).status_code == 403
    gov = new_client(app_ready)
    verify(gov, "Dilnoza")
    assert "gov" in gov.get("/api/auth/me").json()["roles"]
    assert gov.get("/api/edu/cases").status_code == 403
    assert gov.get("/api/cabinet/gov/overview").status_code == 200
    anon = TestClient(app)
    assert anon.get("/api/cabinet/gov/overview").status_code == 401


def test_simulation_only_demo_accounts_and_rate_limited(app_ready):
    TestClient(app).post("/api/gov/reset-demo")
    # oddiy (real) foydalanuvchi mavzuga obuna bo'lgan
    db = SessionLocal()
    try:
        db.add(Subscription(chat_id="999000111", topic_id="child_allowance_refused", lang="uz"))
        db.commit()
    finally:
        db.close()
    mother = new_client(app_ready)
    verify(mother, "Malika")
    tok = mother.post("/api/me/telegram/link").json()["url"].split("link_", 1)[1]
    assert mother.post("/api/bot/link", json={"chat_id": "555123", "token": tok}).json()["ok"]

    gov = new_client(app_ready)
    verify(gov, "Dilnoza")
    r = gov.post("/api/cabinet/gov/simulate-amendment", json={"change_id": "chg_demo_child_allowance"})
    assert r.status_code == 200, r.text
    assert r.json()["alerts"]["audience"] == "demo"
    assert gov.post("/api/cabinet/gov/simulate-amendment", json={}).status_code == 429  # cooldown
    db = SessionLocal()
    try:
        chats = {a.chat_id for a in db.query(Alert).filter(Alert.change_id == "chg_demo_child_allowance").all() if a.chat_id}
    finally:
        db.close()
    assert "555123" in chats and "999000111" not in chats
    v = mother.get("/api/me/cabinet").json()
    assert any(ch["id"] == "chg_demo_child_allowance" for ch in v["changes"])
    TestClient(app).post("/api/gov/reset-demo")  # boshqa testlar uchun holatni tiklash
    db = SessionLocal()
    try:
        db.query(Subscription).filter(Subscription.chat_id == "999000111").delete()
        db.commit()
    finally:
        db.close()


# ------------------------------------------------------------------ 2026-11-21: tekshirilgan manbalar

def test_checked_cards_have_official_sources_and_separate_lawyer_field(app_ready):
    from app.services import knowledge, render
    for cid in ("child_allowance_refused", "alimony", "mib_debt_travel_ban", "consumer_refund"):
        card = knowledge.cards.get(cid)
        assert card["source_checked"] is True and card["source_checked_at"] == "2026-11-21"
        assert card["verified"] is False and card["verified_by"] is None  # huquqshunos maydoni bo'sh qoldi
        assert render.badge(card, "uz") == "📚 Manba tekshirildi: lex.uz, 21.11.2026"
        for b in card["legal_basis"]:
            assert b["source_verified"] and b["retrieved_at"] == "2026-11-21" and rights.official_url(b["lex_url"])
    # bekor qilingan hujjat (VM 44, 2013) hech qayerda manba sifatida qolmadi
    import glob
    for f in glob.glob(str(Path(__file__).resolve().parents[2] / "knowledge" / "**" / "*.json"), recursive=True):
        assert "docs/-2134701" not in Path(f).read_text(encoding="utf-8"), f
    # huquqshunos to'ldirsa — belgi o'zgaradi
    assert render.badge({"verified": True, "verified_by": "F.I.Sh."}, "uz") == "✅ Tekshirilgan manba"
    assert render.badge({"verified": True, "verified_by": None, "source_checked": False}, "uz").startswith("⚠️")


def test_foreign_suggested_questions_are_grounded(app_ready):
    c = TestClient(app)
    sq = c.get("/api/rights?status=foreign").json()["status"]["suggested_questions"]
    assert [s["article"] for s in sq] == ["15-modda", "18-modda", "22-modda"]
    for s in sq:
        r = c.post("/api/ask", json={"text": s["q"], "legal_status": "foreign"}).json()
        assert r["type"] == "rag", (s, r["type"])
        assert "lex.uz/docs/-5443899" in r["text"] and s["article"] in r["text"]
    assert TestClient(app).get("/api/rights?status=uz_citizen").json()["status"]["suggested_questions"] == []
