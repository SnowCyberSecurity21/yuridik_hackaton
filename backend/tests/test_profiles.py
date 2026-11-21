"""«Mening huquqlarim»: mock MyGov profillari, imtiyozlar qoidasi, profilga nishonlangan o'zgarishlar.

Ishga tushirish:  cd backend && python -m pytest -q
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urlencode

_tmp = Path(tempfile.mkdtemp())
os.environ["DATABASE_URL"] = f"sqlite:///{(_tmp / 'profiles.db').as_posix()}"
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["TELEGRAM_BOT_TOKEN"] = ""
os.environ["STT_PROVIDER"] = "none"
os.environ["TTS_PROVIDER"] = "none"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.api.profile import verify_init_data  # noqa: E402
from app.main import app  # noqa: E402

MOTHER, PENSIONER, DRIVER = "1001", "1002", "web:test_driver_01"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        c.post("/api/gov/reset-demo")
        yield c


def login(c, key, pid, consent=True):
    return c.post("/api/profile/login", json={"user_key": key, "profile_id": pid, "consent": consent})


def benefit_ids(view):
    return {b["id"] for b in view["benefits"]}


def test_consent_required(client):
    r = login(client, "1999", "demo_mother", consent=False)
    assert r.status_code == 400
    assert client.get("/api/profile/me", params={"user_key": "1999"}).json()["linked"] is False


def test_bad_user_key_rejected(client):
    assert login(client, "admin", "demo_mother").status_code == 400


def test_rules_per_profile(client):
    m = login(client, MOTHER, "demo_mother").json()
    p = login(client, PENSIONER, "demo_pensioner").json()
    d = login(client, DRIVER, "demo_driver").json()
    assert benefit_ids(m) == {"benefit_child_allowance", "benefit_alimony"}
    assert benefit_ids(p) == {"benefit_pension_recalc", "benefit_elderly_care"}  # kattalar farzandi -> nafaqa yo'q
    assert benefit_ids(d) == {"benefit_fine_discount"}
    for v in (m, p, d):
        blob = json.dumps(v, ensure_ascii=False).lower()
        assert "albatta" not in blob  # hech qachon "albatta olasiz"
        # foydalanuvchiga ko'rinadigan matnlarda TODO_LAWYER emas, halol izoh (xom "sources" — API ma'lumoti)
        shown = json.dumps([v["text"]] + [{k: x for k, x in b.items() if k != "sources"} for b in v["benefits"]],
                           ensure_ascii=False)
        assert "TODO_LAWYER" not in shown
        for b in v["benefits"]:
            assert b["status_text"] == "Haqli bo'lishingiz mumkin"
            assert b["to_check"], "TODO_LAWYER sharti 'tekshirilishi kerak' bo'lib chiqishi shart"
            assert b["verified"] is False and b["sources"]
    # majburiyatlar muddat bilan
    fine = next(o for o in d["obligations"] if o["id"] == "ob_driver_fine")
    assert fine["discount_deadline"] and fine["discount_days_left"] == 6 and fine["reminder_date"]
    assert p["obligations"] == []


def test_profile_persisted_in_sqlite(client):
    me = client.get("/api/profile/me", params={"user_key": MOTHER}).json()
    assert me["linked"] and me["profile"]["id"] == "demo_mother"


def test_one_click_appeal(client):
    a = client.post("/api/profile/appeal", json={"user_key": MOTHER, "benefit_id": "benefit_child_allowance"}).json()
    assert "ARIZA" in a["text"] and "Samarqand" in a["text"] and "TODO_LAWYER" not in a["text"]
    assert a["submit_channels"] and a["to_check"]
    # mos kelmaydigan imtiyozga ariza berilmaydi
    r = client.post("/api/profile/appeal", json={"user_key": PENSIONER, "benefit_id": "benefit_child_allowance"})
    assert r.status_code == 404


def test_obligation_reminder(client):
    r = client.post("/api/profile/remind", json={"user_key": DRIVER, "obligation_id": "ob_driver_fine"}).json()
    assert r["ok"]


def test_amendment_targets_only_affected_profiles(client):
    sim = client.post("/api/gov/simulate-amendment", json={"change_id": "chg_demo_child_allowance"}).json()
    impact = {i["profile_id"]: i["affected"] for i in sim["profiles"]}
    assert impact == {"demo_mother": True, "demo_pensioner": False, "demo_driver": False}
    assert sim["alerts"]["profile_users_notified"] == 1
    assert client.get("/api/profile/me", params={"user_key": MOTHER}).json()["changes"]
    assert client.get("/api/profile/me", params={"user_key": PENSIONER}).json()["changes"] == []

    sim = client.post("/api/gov/simulate-amendment", json={"change_id": "chg_demo_pension"}).json()
    assert {i["profile_id"] for i in sim["profiles"] if i["affected"]} == {"demo_pensioner"}

    sim = client.post("/api/gov/simulate-amendment", json={"change_id": "chg_demo_labor_salary"}).json()
    assert not any(i["affected"] for i in sim["profiles"])  # hech kimga taalluqli emas -> xabar yo'q
    assert sim["alerts"]["profile_users_notified"] == 0
    client.post("/api/gov/reset-demo")


def test_logout_revokes_consent(client):
    assert client.post("/api/profile/logout", json={"user_key": DRIVER}).json()["ok"]
    assert client.get("/api/profile/me", params={"user_key": DRIVER}).json()["linked"] is False


def test_telegram_init_data_verification():
    token = "123456:TEST_TOKEN"
    fields = {"auth_date": str(int(time.time())), "query_id": "AAA", "user": json.dumps({"id": 777, "first_name": "Demo"})}
    check = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    good = urlencode({**fields, "hash": hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()})
    assert verify_init_data(good, token) == 777
    assert verify_init_data(good, "999:OTHER") is None
    assert verify_init_data(good.replace("777", "778"), token) is None
