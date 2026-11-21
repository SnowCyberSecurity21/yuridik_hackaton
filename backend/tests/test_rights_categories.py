"""«Mening huquqlarim» toifalari: talaba, bolali ona, yuridik shaxs/tadbirkor, pensioner, haydovchi.

Tekshiriladi: har yozuv lex.uz abzasiga bog'langan, qoidalar dvigateli yangi toifalarni to'g'ri beradi,
natija hech qachon «albatta» emas, Jasur (yuridik shaxs rahbari) demo ID orqali kira oladi.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse

_tmp = Path(tempfile.mkdtemp())
os.environ["DATABASE_URL"] = f"sqlite:///{(_tmp / 'rights.db').as_posix()}"
for _k in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "TELEGRAM_BOT_TOKEN", "INTERNAL_API_TOKEN"):
    os.environ[_k] = ""
os.environ["TTS_PROVIDER"] = "none"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.api import account as account_api  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.main import app  # noqa: E402
from app.oneid_demo import router as oneid_router  # noqa: E402
from app.services import knowledge, profile, rights  # noqa: E402

KDIR = get_settings().knowledge_dir
CATS = ["student", "mother", "entrepreneur", "pensioner", "driver"]


def persons() -> dict[str, dict]:
    data = json.loads((KDIR / "oneid_demo" / "persons.json").read_text(encoding="utf-8"))
    return {p["login"]: p for p in data["persons"]}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def no_limits():
    for lim in (account_api.login_ip_limiter, account_api.login_user_limiter, account_api.register_limiter,
                oneid_router.login_ip_limiter, oneid_router.login_user_limiter):
        lim.reset()
    yield


# ------------------------------------------------------------------ ma'lumotlar yaxlitligi

def test_every_category_item_has_lex_excerpt():
    ex = rights.excerpts()
    for sid in CATS:
        raw = json.loads((KDIR / "rights" / f"situation_{sid}.json").read_text(encoding="utf-8"))
        new_items = [i for i in raw["items"] if i.get("excerpt_ids")]
        assert new_items, sid
        for it in new_items:
            for eid in it["excerpt_ids"]:
                assert eid in ex, f"{sid}/{it['id']}: abzas {eid} yo'q"


def test_excerpts_have_required_fields_and_official_url():
    data = json.loads((KDIR / "lex" / "excerpts.json").read_text(encoding="utf-8"))
    new = [e for e in data["excerpts"] if e.get("original_text")]
    assert len(new) >= 40
    for e in new:
        for k in ("doc", "article", "original_text", "plain_uz", "plain_ru", "lex_url", "retrieved_at"):
            assert e.get(k), f"{e['id']}: {k} bo'sh"
        assert e["simplified_by"] == "ai" and e["verified"] is False
        assert rights.official_url(e["lex_url"]), e["lex_url"]
        assert "TODO_LAWYER" not in e["original_text"]


def test_categories_have_all_sections(client):
    r = client.get("/api/rights/categories").json()
    assert [c["id"] for c in r["categories"]] == CATS
    for sid in CATS:
        v = client.get(f"/api/rights/category/{sid}").json()
        assert v["benefits"] or v["rights"], sid
        assert v["where_to_go"], sid
        assert all(w["url"].startswith("https://") for w in v["where_to_go"])
        for group in ("benefits", "rights", "duties", "documents"):
            for it in v[group]:
                assert it["excerpts"], f"{sid}/{it['id']}"
    st = client.get("/api/rights/category/student").json()
    titles = " ".join(i["title"] for i in st["benefits"])
    assert "stipendiya" in titles.lower() and "Yotoqxona" in titles
    assert any("Akademik" in i["title"] for i in st["rights"]) and st["duties"] and st["documents"]
    assert any(n["date"] == "2027-01-01" for n in st["news"])
    mo = client.get("/api/rights/category/mother").json()
    ids = {i["id"] for i in mo["benefits"]}
    assert {"m_child_allowance", "m_maternity", "m_childcare", "m_alimony"} <= ids
    assert any(n["is_demo"] for n in mo["news"])  # changes_feed'dan
    en = client.get("/api/rights/category/entrepreneur").json()
    assert en["title"] == "Yuridik shaxs / tadbirkor"
    assert {"en_registration", "en_turnover_tax"} <= {i["id"] for i in en["benefits"]}
    assert any(i["id"] == "en_onsite_audit" for i in en["rights"])
    assert client.get("/api/rights/category/nope").status_code == 404


def test_category_text_for_bot():
    txt = rights.category_text("student")
    assert "Haqli bo'lishingiz mumkin" in txt and "lex.uz" in txt and len(txt) < 4000
    assert "albatta" not in txt.lower()


# ------------------------------------------------------------------ qoidalar dvigateli

def _eval(login: str) -> tuple[set[str], set[str]]:
    p = persons()[login]
    eligible, not_eligible = profile.benefits_of({**p, "id": p["sub"]})
    return {b["id"] for b in eligible}, {b["id"] for b in not_eligible}


def test_student_rules():
    ok, no = _eval("Azizbek")
    assert "benefit_student_stipend" in ok
    assert "benefit_student_dormitory" in no  # oila Ijtimoiy reyestrda emas
    assert "benefit_child_allowance" not in ok
    assert "student" in profile.situations_of(persons()["Azizbek"])


def test_mother_rules():
    p = persons()["Malika"]
    assert "mother" in profile.situations_of(p)
    ok, _ = _eval("Malika")
    assert "benefit_child_allowance" in ok
    assert "benefit_student_stipend" not in ok


def test_legal_entity_rules():
    p = persons()["Jasur"]
    assert p["password"] == "12345678" and p["occupation"]["type"] == "legal_entity_head"
    f = profile.facts(p)
    assert f["is_business"] and f["business_income_le_1bn"] is True
    assert "entrepreneur" in profile.situations_of(p)
    ok, _ = _eval("Jasur")
    assert "benefit_turnover_tax" in ok
    assert "benefit_student_stipend" not in ok


def test_unknown_income_is_to_check_not_guess():
    sardor = persons()["Sardor"]  # YaTT, daromad demo profilda yo'q
    b = knowledge.benefits()["benefit_turnover_tax"]
    ev = profile.evaluate(b, profile.facts(sardor))
    assert ev["status"] == "mumkin"
    assert any("1 mlrd" in x for x in ev["to_check"])


def test_irrelevant_category_not_listed():
    _, no = _eval("Karim")  # pensioner: talaba/tadbirkor imtiyozlari «mos emas» ro'yxatini to'ldirmaydi
    assert not any(x.startswith("benefit_student") or x == "benefit_turnover_tax" for x in no)


# ------------------------------------------------------------------ Jasur demo ID orqali

def _verify(c: TestClient, login: str) -> None:
    r = c.post("/api/auth/register", json={"username": f"t_{login.lower()}", "password": "parol12345"})
    assert r.status_code == 200, r.text
    loc = c.get("/api/oneid/start", follow_redirects=False).headers["location"]
    q = {k: v[0] for k, v in parse_qs(urlparse(loc).query).items()}
    form = {"client_id": q["client_id"], "redirect_uri": q["redirect_uri"], "state": q["state"]}
    r = c.post("/oneid-demo/login", data={**form, "login": login, "password": "12345678"}, follow_redirects=False)
    assert r.status_code == 303, r.text
    r = c.post("/oneid-demo/consent", data={**form, "decision": "allow"}, follow_redirects=False)
    r = c.get(r.headers["location"], follow_redirects=False)
    assert r.headers["location"] == "/kabinet?oneid=ok"


def test_jasur_cabinet(client):
    c = TestClient(app)
    _verify(c, "Jasur")
    v = c.get("/api/me/cabinet").json()
    assert v["person"]["first_name"] == "Jasur"
    assert "entrepreneur" in [s["id"] for s in v["situations"]]
    assert "benefit_turnover_tax" in {b["id"] for b in v["benefits"]}
    assert all("albatta" not in b["status_text"].lower() for b in v["benefits"])
    assert "student" not in v["roles"]


def test_azizbek_cabinet_keeps_edu_and_shows_student_benefits(client):
    c = TestClient(app)
    _verify(c, "Azizbek")
    v = c.get("/api/me/cabinet").json()
    assert "student" in v["roles"]  # Ta'lim bo'limi saqlanadi
    assert c.get("/api/edu/cases").status_code == 200
    assert "benefit_student_stipend" in {b["id"] for b in v["benefits"]}
    sv = {s["id"]: s for s in v["rights"]["situations"]}
    assert sv["student"]["benefits"] and sv["student"]["benefits"][0]["excerpts"]
