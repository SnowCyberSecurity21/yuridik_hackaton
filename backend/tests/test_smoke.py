"""Smoke test: /api/ask'ga 3 ta demo savol (bola nafaqasi, jarima SMS, feyk post) — javob va manba qaytadimi.

Ishga tushirish:  cd backend && python -m pytest -q
LLM/STT/TTS kalitlari kerak emas (test ularni o'chiradi) — shablon rejimi tekshiriladi.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# Test uchun alohida vaqtinchalik DB va tashqi xizmatlar o'chiq
_tmp = Path(tempfile.mkdtemp())
os.environ["DATABASE_URL"] = f"sqlite:///{(_tmp / 'test.db').as_posix()}"
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["TELEGRAM_BOT_TOKEN"] = ""
os.environ["STT_PROVIDER"] = "none"
os.environ["TTS_PROVIDER"] = "none"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

FINE_SMS = ("Aliyev Vali, 01.01.1990. Invoys 1234567890123. To'lov 15.11.2026dan. JARIMA 44 000.00 so'm, "
            "30.12.2099gacha 22 000.00 so'm(50%). Organ YHXB DEMO / TOSHKENT")


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _has_source(res: dict) -> None:
    assert res["sources"], "manba yo'q"
    assert all(s["url"].startswith("https://") for s in res["sources"])
    assert "lex.uz" in res["text"] or "gov.uz" in res["text"]
    assert res["disclaimer"]


def test_child_allowance(client):
    r = client.post("/api/ask", json={"text": "Bolamga nafaqa nega berilmadi?", "region": "samarqand", "channel": "cli"})
    assert r.status_code == 200
    res = r.json()
    assert res["type"] == "card"
    assert res["card_id"] == "child_allowance_refused"
    assert res["verified"] is False and "Manba tekshirildi: lex.uz, 21.11.2026" in res["text"]  # huquqshunos tasdig'i alohida
    assert "TODO_LAWYER" not in res["text"]  # foydalanuvchiga halol izoh ko'rsatiladi
    _has_source(res)
    actions = {b["action"] for b in res["buttons"]}
    assert {"audio", "source", "ok", "disagree", "share"} <= actions

    # "Baribir rozi emasman" -> tayyor murojaat
    a = client.post("/api/appeal", json={"card_id": res["card_id"], "event_id": res["event_id"]}).json()
    assert "ARIZA" in a["text"] and a["addressee"] and a["submit_channels"]


def test_fine_sms(client):
    res = client.post("/api/ask", json={"text": FINE_SMS}).json()
    assert res["type"] == "sms"
    p = res["parsed"]
    assert p["kind"] == "fine"
    assert p["amount"] == 44000 and p["discount_amount"] == 22000 and p["discount_percent"] == 50
    assert p["discount_deadline"] == "2099-12-30"
    assert p["organ"].startswith("YHXB") and p["invoice"] == "1234567890123"
    assert "Aliyev" not in res["text"] and "1990" not in res["text"]  # shaxsiy ma'lumot chiqmaydi
    _has_source(res)


def test_fake_post(client):
    res = client.post("/api/ask", json={"text": "1-yanvardan hamma mashinaga yangi soliq! Tarqating!",
                                        "mode": "factcheck"}).json()
    assert res["type"] == "factcheck"
    assert res["verdict"] == "notogri"
    _has_source(res)


def test_unknown_claim_is_not_guessed(client):
    res = client.post("/api/factcheck", json={"text": "Ertadan boshlab barcha mushuklar pasport oladi"}).json()
    assert res["verdict"] == "tasdiqlanmagan"


def test_unknown_question_not_found(client):
    res = client.post("/api/ask", json={"text": "Kosmosga uchish uchun litsenziya qanday olinadi?"}).json()
    assert res["type"] == "not_found"
    _has_source(res)


def test_cyrillic_and_russian(client):
    cyr = client.post("/api/ask", json={"text": "Болага нафақа нега берилмади?"}).json()
    assert cyr["card_id"] == "child_allowance_refused" and cyr["lang"] == "uz_cyrl"
    ru = client.post("/api/ask", json={"text": "Почему мне отказали в детском пособии?"}).json()
    assert ru["card_id"] == "child_allowance_refused" and ru["lang"] == "ru"


def test_dashboard_and_amendment(client):
    assert client.get("/api/gov/overview").status_code == 200
    assert len(client.get("/api/gov/regions").json()) == 14
    c = client.post("/api/gov/content", json={"topic_id": "child_allowance_refused"}).json()
    assert c["telegram_post"] and len(c["quiz"]) == 3 and c["video_script"]
    sim = client.post("/api/gov/simulate-amendment", json={"change_id": "chg_demo_child_allowance"}).json()
    assert sim["outdated_chunks"] and sim["affected_cards"]
    card = client.get("/api/cards/child_allowance_refused").json()["card"]
    assert card["needs_reverification"] is True
    assert client.post("/api/gov/reset-demo").json()["ok"]
