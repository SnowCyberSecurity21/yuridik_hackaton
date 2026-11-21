"""Lex.uz keshidan (knowledge/lex/excerpts.json) qidiruv — faqat iqtibos bilan.

Placeholder (TODO_LAWYER) parchalar indeksga kirmaydi; mos parcha bo'lmasa — "topilmadi". To'qilgan qonun yo'q.
"""
from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from . import knowledge
from .textutil import normalize

RAG_THRESHOLD = 0.25

_vec = None
_mat = None
_items: list[dict] = []


def build() -> None:
    global _vec, _mat, _items
    _items = knowledge.lex_excerpts()
    if not _items:
        _vec = _mat = None
        return
    _vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
    _mat = _vec.fit_transform([normalize(" ".join((e["doc"], e["text"], e.get("plain_uz", ""), e.get("keywords", "")))) for e in _items])


def search(text: str, top_k: int = 2) -> list[tuple[dict, float]]:
    if _vec is None or not text.strip():
        return []
    sims = cosine_similarity(_vec.transform([normalize(text)]), _mat)[0]
    ranked = sorted(zip(_items, sims), key=lambda x: x[1], reverse=True)[:top_k]
    return [(e, float(s)) for e, s in ranked if s >= RAG_THRESHOLD]
