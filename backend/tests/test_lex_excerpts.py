"""Qonun abzaslari API: toifa / imtiyoz / id bo'yicha; asl matn + oddiy til + lex.uz havolasi."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_tmp = Path(tempfile.mkdtemp())
os.environ["DATABASE_URL"] = f"sqlite:///{(_tmp / 'lex.db').as_posix()}"
for _k in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "TELEGRAM_BOT_TOKEN", "INTERNAL_API_TOKEN"):
    os.environ[_k] = ""
os.environ["TTS_PROVIDER"] = "none"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.services import rights  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_by_category(client):
    r = client.get("/api/lex/excerpts", params={"category": "student"}).json()
    assert r["count"] >= 10
    e = r["excerpts"][0]
    for k in ("doc", "article", "original_text", "plain", "lex_url", "retrieved_at"):
        assert e[k], k
    assert e["simplified_by"] == "ai" and e["verified"] is False
    assert e["lex_url"].startswith("https://lex.uz/docs/")


def test_by_item_and_benefit(client):
    r = client.get("/api/lex/excerpts", params={"item": "st_stipend_grades"}).json()
    assert [e["id"] for e in r["excerpts"]] == ["ex_stip_grades"]
    assert "86 ball" in r["excerpts"][0]["original_text"]
    r = client.get("/api/lex/excerpts", params={"item": "benefit_student_stipend"}).json()
    assert r["count"] >= 1


def test_by_ids_and_lang(client):
    r = client.get("/api/lex/excerpts", params={"ids": "ex_labor_404_maternity,nope", "lang": "ru"}).json()
    assert r["count"] == 1
    assert r["excerpts"][0]["plain"] == r["excerpts"][0]["plain_ru"]
    assert client.get("/api/lex/excerpts/ex_family_99_amount").json()["article"] == "99-modda"
    assert client.get("/api/lex/excerpts/nope").status_code == 404


def test_placeholder_never_shown():
    assert all(not e["original_text"].startswith("TODO_LAWYER") for e in rights.find_excerpts())
    assert "ex_appeals_law_1" not in rights.excerpts()  # TODO placeholder
