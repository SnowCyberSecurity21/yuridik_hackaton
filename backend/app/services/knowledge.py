"""Bilimlar bazasini yuklash: kartalar (DB'ga sinxron), claim'lar, lex parchalari, lenta, darsliklar, shablonlar."""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path

from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Card, TextbookChunk, utcnow

log = logging.getLogger("javob.knowledge")

TODO = "TODO_LAWYER"


def _kdir() -> Path:
    return get_settings().knowledge_dir


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        log.error("JSON o'qib bo'lmadi %s: %s", path, e)
        return None


REQUIRED_CARD_FIELDS = {"id", "category", "title_uz", "triggers", "plain_explanation_uz", "legal_basis"}


def load_card_files() -> list[dict]:
    cards = []
    for p in sorted((_kdir() / "cards").glob("*.json")):
        data = _read_json(p)
        if not isinstance(data, dict):
            continue
        missing = REQUIRED_CARD_FIELDS - data.keys()
        if missing:
            log.error("karta %s da maydonlar yo'q: %s — o'tkazildi", p.name, missing)
            continue
        cards.append(data)
    return cards


class CardStore:
    """Kartalar xotirada (tez o'qish uchun); bayroqlar DB'da saqlanadi."""

    def __init__(self) -> None:
        self._cards: dict[str, dict] = {}

    def sync(self, db: Session) -> int:
        files = load_card_files()
        for data in files:
            row = db.get(Card, data["id"])
            if row is None:
                row = Card(id=data["id"], category=data["category"], data=data,
                           verified=bool(data.get("verified")))
                db.add(row)
            else:
                row.data = data
                row.category = data["category"]
                row.verified = bool(data.get("verified"))
                row.updated_at = utcnow()
        db.commit()
        self.refresh(db)
        return len(files)

    def refresh(self, db: Session) -> None:
        self._cards = {}
        for row in db.query(Card).all():
            card = dict(row.data)
            card["verified"] = row.verified
            card["needs_reverification"] = row.needs_reverification
            card["reverify_reason"] = row.reverify_reason
            self._cards[row.id] = card

    def get(self, card_id: str | None) -> dict | None:
        return self._cards.get(card_id or "")

    def all(self) -> list[dict]:
        return list(self._cards.values())


cards = CardStore()


@lru_cache
def claims() -> list[dict]:
    data = _read_json(_kdir() / "factcheck" / "known_claims.json") or {}
    return data.get("claims", [])


@lru_cache
def lex_excerpts() -> list[dict]:
    data = _read_json(_kdir() / "lex" / "excerpts.json") or {}
    # Placeholder parchalar (TODO_LAWYER) qidiruvga kirmaydi — to'qilgan qonun yo'q
    return [e for e in data.get("excerpts", []) if not str(e.get("text", "")).startswith(TODO)]


@lru_cache
def changes_feed() -> list[dict]:
    data = _read_json(_kdir() / "lex" / "changes_feed.json") or {}
    return data.get("changes", [])


@lru_cache
def appeal_templates() -> dict[str, dict]:
    out = {}
    for p in sorted((_kdir() / "appeal_templates").glob("*.json")):
        data = _read_json(p)
        if isinstance(data, dict) and "id" in data:
            out[data["id"]] = data
    return out


def sync_textbooks(db: Session) -> int:
    n = 0
    for p in sorted((_kdir() / "textbooks").glob("*.json")):
        book = _read_json(p)
        if not isinstance(book, dict):
            continue
        for ch in book.get("chunks", []):
            if db.get(TextbookChunk, ch["id"]) is None:
                db.add(TextbookChunk(id=ch["id"], textbook_id=book["id"], textbook_title=book.get("title", book["id"]),
                                     title=ch["title"], text=ch["text"], refs=ch.get("refs", [])))
                n += 1
    db.commit()
    return n


def reset_textbooks(db: Session) -> None:
    db.query(TextbookChunk).delete()
    db.commit()
    sync_textbooks(db)


# ---------------- Profil (MOCK MyGov/OneID) va imtiyozlar ----------------

@lru_cache
def mock_profiles() -> dict[str, dict]:
    """Soxta profillar: real tizimda bu ma'lumot har so'rovda integratsiya platformasidan o'qiladi."""
    out = {}
    for p in sorted((_kdir() / "mock_profiles").glob("*.json")):
        data = _read_json(p)
        if isinstance(data, dict) and "id" in data:
            out[data["id"]] = data
    return dict(sorted(out.items(), key=lambda kv: (kv[1].get("order", 99), kv[0])))


REQUIRED_BENEFIT_FIELDS = {"id", "title_uz", "rule", "legal_basis", "where_to_go"}


@lru_cache
def benefits() -> dict[str, dict]:
    out = {}
    for p in sorted((_kdir() / "benefits").glob("*.json")):
        data = _read_json(p)
        if not isinstance(data, dict):
            continue
        missing = REQUIRED_BENEFIT_FIELDS - data.keys()
        if missing:
            log.error("imtiyoz %s da maydonlar yo'q: %s — o'tkazildi", p.name, missing)
            continue
        out[data["id"]] = data
    return dict(sorted(out.items(), key=lambda kv: (kv[1].get("order", 99), kv[0])))
