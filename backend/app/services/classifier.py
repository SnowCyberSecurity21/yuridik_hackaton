"""Vaziyat klassifikatori: trigger so'zlar + TF-IDF (char n-gram). Embedding — ixtiyoriy.

Kirill va rus matni normalizatsiyada lotinga o'giriladi, shuning uchun bitta indeks uchala yozuvga ishlaydi.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ..config import get_settings
from .textutil import normalize

log = logging.getLogger("javob.classifier")

W_TRIGGER, W_TFIDF, W_EMB = 0.6, 0.4, 0.3


@dataclass
class Match:
    id: str
    score: float
    trigger: float
    tfidf: float


def _stem(tok: str) -> str:
    return tok[:5] if len(tok) > 5 else tok


def trigger_score(text_norm: str, triggers: list[str]) -> float:
    """1.0 — trigger iborasi to'liq uchradi; aks holda so'z o'zaklari bo'yicha qisman moslik."""
    if not triggers:
        return 0.0
    tokens = {_stem(t) for t in text_norm.split()}
    padded = f" {text_norm} "
    best = 0.0
    for trig in triggers:
        tn = normalize(trig)
        if not tn:
            continue
        if f" {tn} " in padded:
            return 1.0
        ttoks = [_stem(t) for t in tn.split() if len(t) > 2]
        if not ttoks:
            continue
        frac = sum(1 for t in ttoks if t in tokens) / len(ttoks)
        if len(ttoks) == 1:
            frac *= 0.8  # bitta so'zli moslik biroz kuchsizroq
        best = max(best, frac * 0.85)
    return best


class Classifier:
    """Umumiy indeks: kartalar yoki claim'lar uchun qayta ishlatiladi."""

    def __init__(self, items: list[dict], doc_fn, trig_fn) -> None:
        self.items = items
        self.ids = [it["id"] for it in items]
        self.triggers = [trig_fn(it) for it in items]
        docs = [normalize(doc_fn(it)) for it in items]
        self.vec = None
        self.matrix = None
        self.emb = None
        if docs:
            self.vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
            self.matrix = self.vec.fit_transform(docs)
            self._maybe_embeddings([doc_fn(it) for it in items])

    def _maybe_embeddings(self, raw_docs: list[str]) -> None:
        s = get_settings()
        if not s.embeddings_enabled:
            return
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            self._st = SentenceTransformer(s.embedding_model)
            self.emb = self._st.encode(raw_docs, normalize_embeddings=True)
            log.info("embedding indeks tayyor (%d)", len(raw_docs))
        except Exception as e:  # noqa: BLE001
            log.warning("embedding o'chirildi (fallback: trigger+TF-IDF): %s", e)
            self.emb = None

    def rank(self, text: str, top_k: int = 3) -> list[Match]:
        if not self.items or not text.strip():
            return []
        tn = normalize(text)
        tf = cosine_similarity(self.vec.transform([tn]), self.matrix)[0]
        # TF-IDF o'xshashligi odatda 0..0.5 oralig'ida — 0..1 ga cho'zamiz
        tf_scaled = np.clip(tf * 2.0, 0, 1)
        emb = None
        if self.emb is not None:
            try:
                q = self._st.encode([text], normalize_embeddings=True)
                emb = (self.emb @ q[0]).clip(0, 1)
            except Exception:  # noqa: BLE001
                emb = None
        out = []
        for i, item_id in enumerate(self.ids):
            trg = trigger_score(tn, self.triggers[i])
            score = W_TRIGGER * trg + W_TFIDF * float(tf_scaled[i])
            if emb is not None:
                score = (score + W_EMB * float(emb[i])) / (1 + W_EMB)
            out.append(Match(item_id, round(score, 3), round(trg, 3), round(float(tf_scaled[i]), 3)))
        out.sort(key=lambda m: m.score, reverse=True)
        return out[:top_k]


def card_doc(card: dict) -> str:
    return " ".join([
        card.get("title_uz", ""), card.get("title_ru", ""), " ".join(card.get("triggers", [])),
        card.get("plain_explanation_uz", ""), " ".join(card.get("common_reasons", [])),
    ])


_card_clf: Classifier | None = None
_claim_clf: Classifier | None = None


def build(cards: list[dict], claims: list[dict]) -> None:
    global _card_clf, _claim_clf
    _card_clf = Classifier(cards, card_doc, lambda c: c.get("triggers", []))
    _claim_clf = Classifier(claims, lambda c: c.get("claim_uz", "") + " " + " ".join(c.get("triggers", [])),
                            lambda c: c.get("triggers", []))
    log.info("klassifikator: %d karta, %d claim", len(cards), len(claims))


def classify(text: str, top_k: int = 3) -> list[Match]:
    return _card_clf.rank(text, top_k) if _card_clf else []


def match_claims(text: str, top_k: int = 3) -> list[Match]:
    return _claim_clf.rank(text, top_k) if _claim_clf else []
