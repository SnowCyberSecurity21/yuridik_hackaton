"""Murojaat shablonlari: rekvizitlar faqat tatbiq etiladigan qonundan (lex.uz abzasi bilan), yangi shablonlar."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_tmp = Path(tempfile.mkdtemp())
os.environ["DATABASE_URL"] = f"sqlite:///{(_tmp / 'appeal.db').as_posix()}"
for _k in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "TELEGRAM_BOT_TOKEN", "INTERNAL_API_TOKEN"):
    os.environ[_k] = ""
os.environ["TTS_PROVIDER"] = "none"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.services import knowledge, rights  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_every_template_states_its_law_and_links_excerpts():
    ex = rights.excerpts()
    tpls = knowledge.appeal_templates()
    assert {"appeal_stipend", "appeal_maternity", "appeal_tax_audit_complaint"} <= tpls.keys()
    for t in tpls.values():
        assert t.get("legal_regime_uz"), t["id"]
        for r in t.get("requirements", []):
            assert r["excerpt_id"] in ex, (t["id"], r)
        for i in t.get("excerpt_ids", []):
            assert i in ex, (t["id"], i)


def test_appeals_law_requisites_only_where_applicable():
    tpls = knowledge.appeal_templates()
    # Ma'muriy / protsessual / soliq tartibi — Murojaatlar qonuni (6-modda) rekvizitlari qo'yilmaydi (2-modda)
    for tid in ("appeal_fine_dispute", "appeal_court_order_objection", "appeal_fraud", "appeal_tax_audit_complaint"):
        assert all(r["excerpt_id"] != "ex_appeals_6_requisites" for r in tpls[tid].get("requirements", [])), tid
    for tid in ("appeal_benefit_request", "appeal_social_benefit", "appeal_labor", "appeal_stipend"):
        assert any(r["excerpt_id"] == "ex_appeals_6_requisites" for r in tpls[tid]["requirements"]), tid
        assert "15 kun" in tpls[tid]["review_term_uz"]


def test_generate_stipend_appeal(client):
    r = client.post("/api/appeal", json={"card_id": "student_stipend",
                                         "fields": {"applicant_name": "Test Talaba (DEMO)", "address": "Toshkent",
                                                    "situation": "Bahorgi semestrda stipendiya tayinlanmadi."}}).json()
    assert r["template_id"] == "appeal_stipend"
    assert "rektoriga" in r["text"] and "Imzo" in r["text"] and "Test Talaba (DEMO)" in r["text"]
    assert "-bandlar-modda" not in r["text"] and "-moddalar-modda" not in r["text"]
    assert r["requirements"] and r["excerpts"] and r["review_term"]


def test_generate_legal_entity_tax_complaint(client):
    r = client.post("/api/appeal", json={"card_id": "business_tax_audit",
                                         "fields": {"applicant_name": "«Demo Savdo» MChJ (DEMO)"}}).json()
    assert r["template_id"] == "appeal_tax_audit_complaint" and r["applicant_type"] == "legal_entity"
    assert "Shikoyat beruvchi (yuridik shaxs): «Demo Savdo» MChJ (DEMO)" in r["text"]
    assert "[joylashgan yeri (pochta manzili)]" in r["text"]  # to'ldirilmagan rekvizit ochiq ko'rsatiladi
    assert "232" in r["legal_regime"] and any(e["article"] == "233-modda" for e in r["excerpts"])


def test_generate_maternity_appeal(client):
    r = client.post("/api/appeal", json={"card_id": "maternity_childcare"}).json()
    assert r["template_id"] == "appeal_maternity"
    assert "404" in r["text"] and "Ish beruvchi" in r["text"]


def test_templates_endpoint(client):
    r = client.get("/api/appeal/templates").json()["templates"]
    by = {t["id"]: t for t in r}
    assert any(c["card_id"] == "student_stipend" for c in by["appeal_stipend"]["cards"])
    assert by["appeal_tax_audit_complaint"]["applicant_type"] == "legal_entity"
