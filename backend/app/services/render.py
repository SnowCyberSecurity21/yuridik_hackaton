"""Javoblarni matn ko'rinishiga keltirish (≤ 8 qator) va manba/badge bloklari."""
from __future__ import annotations

import re

from .i18n import t
from .textutil import to_script

TODO = "TODO_LAWYER"
_TODO_PREFIX = re.compile(r"TODO_LAWYER:\s*")


_TODO_IN_PARENS = re.compile(r"\(TODO_LAWYER:\s*([^)]*)\)")


def show_todo(s: str, lang: str) -> str:
    """Foydalanuvchiga TODO_LAWYER o'rniga halol izoh ko'rsatamiz (ma'lumot to'qilmaydi)."""
    note = t(lang, "todo_display")
    if TODO not in s:
        return s
    s = _TODO_IN_PARENS.sub(lambda m: f"({m.group(1).strip()} — {note})", s)
    if TODO not in s:
        return s
    if s.strip() == TODO:
        return f"({note})"
    had_prefix = bool(_TODO_PREFIX.search(s))
    s = _TODO_PREFIX.sub("", s)
    s = s.replace(TODO, f"({note})")
    if had_prefix and f"({note})" not in s:
        s = f"{s} ({note})"
    return s


def _dmy(iso: str | None) -> str:
    try:
        y, m, d = str(iso)[:10].split("-")
        return f"{d}.{m}.{y}"
    except ValueError:
        return str(iso or "")


def badge(card_or_item: dict, lang: str) -> str:
    """Belgi: qonun o'zgargan > huquqshunos tasdiqlagan (verified_by) > manba tekshirilgan > tekshirilmagan."""
    if card_or_item.get("needs_reverification"):
        return t(lang, "badge_reverify")
    if card_or_item.get("verified") and card_or_item.get("verified_by"):
        return t(lang, "badge_verified")
    if card_or_item.get("source_checked"):
        return f'{t(lang, "badge_source_checked")} {_dmy(card_or_item.get("source_checked_at"))}'
    return t(lang, "badge_unverified")


def sources_of(item: dict) -> list[dict]:
    out = []
    for b in item.get("legal_basis", []):
        out.append({"ref_id": b.get("ref_id"), "doc": b.get("doc", ""), "article": b.get("article", ""),
                    "url": b.get("lex_url") or "https://lex.uz/", "verified": bool(item.get("verified"))})
    return out


def source_line(item: dict, lang: str) -> str:
    parts = []
    for b in item.get("legal_basis", [])[:2]:
        doc = show_todo(b.get("doc", ""), lang)
        art = b.get("article", "")
        if not art or (TODO in art and t(lang, "todo_display") in doc):
            art_txt = ""  # izoh hujjat nomida allaqachon bor
        elif TODO in art:
            art_txt = f" ({t(lang, 'todo_display')})"
        elif any(w in art for w in ("modda", "band", "ilova")):
            art_txt = f", {art}"
        else:
            art_txt = f", {art}-modda"
        parts.append(f"{doc}{art_txt} — {b.get('lex_url') or 'https://lex.uz/'}")
    return f"{t(lang, 'source')}: " + "; ".join(parts) + f"  [{badge(item, lang)}]"


def _title(card: dict, lang: str) -> str:
    if lang == "ru" and card.get("title_ru"):
        return card["title_ru"]
    if lang == "uz_cyrl" and card.get("title_cyrl"):
        return card["title_cyrl"]
    return card["title_uz"]


def card_body_lines(card: dict, lang: str) -> list[str]:
    """Shablon javob tanasi (manba va disclaimer'siz). Matn kartadan, hech narsa qo'shilmaydi."""
    L = "uz" if lang == "ru" else lang  # ru uchun karta matni o'zbekcha (izoh bilan)

    def j(items, sep="; ", n=3):
        return sep.join(show_todo(x, L) for x in items[:n])

    lines = [
        f"{t(L, 'law_says')}: {card.get('plain_explanation_uz', '')}",
        f"{t(L, 'reasons')}: {j(card.get('common_reasons', []))}",
        f"{t(L, 'steps')}: {j(card.get('steps', []), ' → ', 4)}",
        f"{t(L, 'documents')}: {j(card.get('documents', []))} | {t(L, 'deadlines')}: {j(card.get('deadlines', []), '; ', 2)}",
    ]
    where = card.get("where_to_go", [])[:2]
    if where:
        lines.append(f"{t(L, 'where')}: " + "; ".join(f"{show_todo(w['name'], L)} ({w['url']})" for w in where))
    return [to_script(x, lang) if lang == "uz_cyrl" else x for x in lines]


def compose(header: str, body: list[str], footer: list[str]) -> str:
    return "\n".join([header, *body, *footer]).strip()


QUOTE_MAX = 280


def quote_lines(quote: dict | None, lang: str) -> list[str]:
    """Qonundan asl iqtibos (lex.uz'dan aynan, o'zgartirilmaydi) + oddiy tildagi izoh (AI soddalashtirgan)."""
    if not quote:
        return []
    orig = " ".join(p for p in quote["original_text"].split("\n") if p.strip() != "…")
    if len(orig) > QUOTE_MAX:
        orig = orig[:QUOTE_MAX].rsplit(" ", 1)[0] + " …"
    ref = ", ".join(x for x in (quote.get("article"), quote.get("paragraph")) if x)
    plain = quote.get("plain_ru") if lang == "ru" and quote.get("plain_ru") else quote.get("plain_uz", "")
    if lang == "uz_cyrl":
        plain = to_script(plain, lang)
    lines = [f"📖 {t(lang, 'quote_law')} ({ref}): «{orig}»"]
    if plain:
        lines.append(f"💬 {t(lang, 'quote_plain')}: {plain}")
    return lines


def card_answer_text(card: dict, lang: str, body: list[str] | None = None, quote: dict | None = None) -> str:
    header = f"📌 {_title(card, lang)}"
    if lang == "ru":
        header += f"\n{t('ru', 'ru_note')}"
    body = body if body is not None else card_body_lines(card, lang)
    footer = [*quote_lines(quote, lang), source_line(card, lang), t(lang, "disclaimer")]
    return compose(header, body, footer)
