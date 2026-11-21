"""/api/ask: yangi mavzular (stipendiya, dekret, soliq tekshiruvi...) va javobda manba + asl iqtibos + oddiy til."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_tmp = Path(tempfile.mkdtemp())
os.environ["DATABASE_URL"] = f"sqlite:///{(_tmp / 'ask.db').as_posix()}"
for _k in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "TELEGRAM_BOT_TOKEN", "INTERNAL_API_TOKEN"):
    os.environ[_k] = ""
os.environ["TTS_PROVIDER"] = "none"
os.environ["STT_PROVIDER"] = "none"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.services import knowledge, rights  # noqa: E402

CASES = [
    ("Stipendiya nega berilmadi?", "student_stipend"),
    ("Почему не дали стипендию?", "student_stipend"),
    ("Yotoqxona pulini davlat qoplaydimi?", "student_dormitory"),
    ("Dekret ta'tili necha kun?", "maternity_childcare"),
    ("Homiladorman, ishdan bo'shatishdi", "maternity_childcare"),
    ("Soliq tekshiruvi keldi, nima qilay?", "business_tax_audit"),
    ("Aylanma soliq kimlarga?", "business_tax_regime"),
    ("Bolamga nafaqa nega berilmadi?", "child_allowance_refused"),
    ("Aliment qancha bo'ladi?", "alimony"),
]


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.mark.parametrize("question,card_id", CASES)
def test_new_topics_route_to_card_with_quote(client, question, card_id):
    r = client.post("/api/ask", json={"text": question, "channel": "web"}).json()
    assert r["type"] == "card" and r["card_id"] == card_id, (question, r.get("card_id"))
    assert r["quotes"], "asl iqtibos yo'q"
    q = r["quotes"][0]
    assert q["original_text"] and q["lex_url"].startswith("https://lex.uz/docs/")
    assert "📖" in r["text"] and "💬" in r["text"] and "📚" in r["text"]
    assert "lex.uz" in r["text"]


def test_quote_is_verbatim_from_excerpts(client):
    r = client.post("/api/ask", json={"text": "Stipendiya nega berilmadi?"}).json()
    ex = rights.excerpts()[r["quotes"][0]["id"]]
    assert r["quotes"][0]["original_text"] == ex["original_text"]


def test_new_cards_cite_only_known_excerpts():
    ex = rights.excerpts()
    for cid in ("student_stipend", "student_dormitory", "maternity_childcare", "business_tax_audit", "business_tax_regime"):
        card = knowledge.cards.get(cid)
        assert card and card["verified"] is False
        assert card["excerpt_ids"] and all(i in ex for i in card["excerpt_ids"])
        assert all(b["lex_url"].startswith("https://lex.uz/") for b in card["legal_basis"])


def test_sms_fine_cites_discount_article(client):
    sms = ("F.I.O., 01.01.2000. Invoys 123. JARIMA 44 000.00 so'm, 10.12.2026gacha 22 000.00 so'm(50%). "
           "Organ YHXB / TOSHKENT")
    r = client.post("/api/ask", json={"text": sms, "mode": "sms"}).json()
    assert r["type"] == "sms"
    assert r["quotes"] and r["quotes"][0]["article"] == "332¹-modda"
    assert "10 kun" in r["text"]


def test_unknown_still_not_found(client):
    r = client.post("/api/ask", json={"text": "Kosmik kema uchun litsenziya qanday olinadi?"}).json()
    assert r["type"] in ("not_found", "rag")
    if r["type"] == "not_found":
        assert not r.get("quotes")
