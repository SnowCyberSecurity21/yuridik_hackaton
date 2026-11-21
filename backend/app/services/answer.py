"""Javob pipeline'i (xavfsizlik uchun muhim).

1) Klassifikatsiya -> karta (ishonch >= threshold) -> FAQAT kartadan javob (LLM faqat qayta ifodalaydi).
2) Aks holda -> lex keshidan RAG (iqtibos bilan).
3) Hech narsa yo'q -> "tasdiqlangan ma'lumot topilmadi" + yo'naltirish. To'qilgan qonun yo'q.
Har bir javobda manba havolasi va disclaimer bor.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import date

from sqlalchemy.orm import Session

from ..config import get_settings
from . import analytics, classifier, knowledge, llm, rag, render, rights, sms_parser
from .i18n import t
from .textutil import detect_lang, to_script

log = logging.getLogger("javob.answer")

FACTCHECK_THRESHOLD = 0.45
_NUM = re.compile(r"\d+")
# JSON ichida ham to'g'ri ajratsin: qo'shtirnoq, qavs, vergul havolaga qo'shilmaydi
_URL = re.compile(r"https?://[^\s)\]\"'<>,]+")


def card_quotes(card: dict | None, lang: str, limit: int = 3) -> list[dict]:
    """Karta bog'langan lex.uz abzaslari: asl matn (aynan) + oddiy til. Abzas bo'lmasa — bo'sh ro'yxat."""
    if not card:
        return []
    return rights.excerpts_by_ids((card.get("excerpt_ids") or [])[:limit], "ru" if lang == "ru" else "uz")


def _buttons(kind: str, card_id: str | None, event_id: int | None) -> list[dict]:
    if kind in ("card", "sms"):
        btns = [
            {"action": "audio", "event_id": event_id},
            {"action": "source", "card_id": card_id},
            {"action": "ok", "event_id": event_id},
            {"action": "disagree", "card_id": card_id, "event_id": event_id},
            {"action": "share", "card_id": card_id},
            {"action": "subscribe", "card_id": card_id},
        ]
        if kind == "sms":
            btns.append({"action": "remind"})
        return btns
    if kind == "factcheck":
        return [{"action": "audio", "event_id": event_id}, {"action": "share"}]
    return [{"action": "audio", "event_id": event_id}]


# ------------------------------------------------------------------ LLM xavfsizligi

def _llm_output_is_safe(output: str, card: dict) -> bool:
    """LLM kartada yo'q raqam yoki havola qo'shmasligi kerak (modda/summa/muddat to'qilmasin)."""
    card_text = json.dumps(card, ensure_ascii=False)
    card_nums = set(_NUM.findall(card_text))
    for n in _NUM.findall(output):
        if n not in card_nums:
            log.warning("LLM javobi rad etildi: kartada yo'q raqam %s", n)
            return False
    card_urls = {u.rstrip("/.,;:") for u in _URL.findall(card_text)}
    for u in _URL.findall(output):
        if u.rstrip("/.,;:") not in card_urls:
            log.warning("LLM javobi rad etildi: kartada yo'q havola %s", u)
            return False
    return True


async def _llm_body(card: dict, question: str, lang: str) -> list[str] | None:
    if not llm.is_available():
        return None
    system = llm.load_prompt("system_answer") + "\n\n" + llm.load_prompt("answer_from_card")
    lang_name = {"uz": "o'zbek (lotin)", "uz_cyrl": "o'zbek (kirill)", "ru": "rus"}[lang]
    payload = {k: v for k, v in card.items() if not k.startswith("_")}
    user = (f"JAVOB TILI: {lang_name}\nFUQARO SAVOLI: {question}\n\nVAZIYAT KARTASI (yagona ruxsat etilgan manba):\n"
            f"{json.dumps(payload, ensure_ascii=False, indent=1)}")
    out = await llm.complete(system, user, max_tokens=900)
    if not out or not _llm_output_is_safe(out, card):
        return None
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()][:6]
    return lines or None


# ------------------------------------------------------------------ Asosiy savol

async def answer_question(db: Session, text: str, *, lang: str | None = None, region: str | None = None,
                          channel: str = "api", mode: str = "auto") -> dict:
    text = (text or "").strip()
    lang = lang or detect_lang(text)

    if mode == "factcheck":
        return await fact_check(db, text, lang=lang, region=region, channel=channel)
    if mode == "sms" or (mode == "auto" and sms_parser.detect_kind(text)):
        return await explain_sms(db, text, lang=lang, region=region, channel=channel)

    matches = classifier.classify(text)
    threshold = get_settings().classifier_threshold
    top = matches[0] if matches else None
    alternatives = [{"card_id": m.id, "title": (knowledge.cards.get(m.id) or {}).get("title_uz"), "score": m.score}
                    for m in matches[1:3] if m.score >= threshold * 0.7]

    if top and top.score >= threshold:
        card = knowledge.cards.get(top.id)
        body = await _llm_body(card, text, lang)
        used_llm = body is not None
        quotes = card_quotes(card, lang)
        answer_text = render.card_answer_text(card, lang, body, quote=quotes[0] if quotes else None)
        event_id = analytics.log_event(db, kind="ask", topic_id=card["id"], region=region, lang=lang,
                                       channel=channel, answer_type="card", confidence=top.score)
        return {
            "type": "card", "lang": lang, "text": answer_text, "card_id": card["id"], "title": card["title_uz"],
            "confidence": top.score, "sources": render.sources_of(card), "verified": card.get("verified", False),
            "needs_reverification": card.get("needs_reverification", False),
            "badge": render.badge(card, lang), "disclaimer": t(lang, "disclaimer"), "llm_used": used_llm,
            "quotes": quotes,
            "event_id": event_id, "buttons": _buttons("card", card["id"], event_id), "alternatives": alternatives,
        }

    # 2) RAG — faqat haqiqiy (placeholder bo'lmagan) lex parchalari ustida
    hits = rag.search(text)
    if hits:
        ex, score = hits[0]
        quote = ex["text"][:700]
        body = [f"📖 «{quote}»"]
        plain = (ex.get("plain_ru") if lang == "ru" else None) or ex.get("plain_uz")
        if plain:
            body.append(f"💬 {t(lang, 'quote_plain')}: {to_script(plain, lang) if lang == 'uz_cyrl' else plain}")
        if llm.is_available():
            expl = await llm.complete(llm.load_prompt("system_answer") + "\n\n" + llm.load_prompt("rag_answer"),
                                      f"TIL: {lang}\nSAVOL: {text}\nPARCHA ({ex['doc']}): {ex['text']}", max_tokens=500)
            if expl and _llm_output_is_safe(expl, ex):
                body.insert(0, expl.strip())
        src = {"legal_basis": [{"doc": ex["doc"], "article": ex.get("article", ""), "lex_url": ex["lex_url"]}],
               "verified": ex.get("verified", False), "verified_by": ex.get("verified_by"),
               "source_checked": ex.get("source_checked", False), "source_checked_at": ex.get("source_checked_at")}
        answer_text = render.compose("📌 " + to_script(ex["doc"], lang), body,
                                     [render.source_line(src, lang), t(lang, "disclaimer")])
        event_id = analytics.log_event(db, kind="ask", region=region, lang=lang, channel=channel,
                                       answer_type="rag", confidence=score)
        return {"type": "rag", "lang": lang, "text": answer_text, "card_id": None, "confidence": round(score, 3),
                "sources": render.sources_of(src), "verified": src["verified"], "badge": render.badge(src, lang),
                "disclaimer": t(lang, "disclaimer"), "event_id": event_id, "buttons": _buttons("rag", None, event_id),
                "quotes": rights.excerpts_by_ids([ex["id"]], "ru" if lang == "ru" else "uz"),
                "alternatives": alternatives}

    # 3) Topilmadi — taxmin qilmaymiz
    event_id = analytics.log_event(db, kind="ask", region=region, lang=lang, channel=channel,
                                   answer_type="not_found", confidence=top.score if top else 0.0)
    nf_sources = [{"doc": "Qonunchilik ma'lumotlari milliy bazasi", "article": "", "url": "https://lex.uz", "verified": True},
                  {"doc": "Prezidentning Virtual qabulxonasi", "article": "", "url": "https://pm.gov.uz", "verified": True}]
    lines = [f"❔ {t(lang, 'not_found')}", t(lang, "not_found_hint")]
    if alternatives:
        lines.append("🔎 " + "; ".join(to_script(a["title"] or "", lang) for a in alternatives))
    lines.append(f"{t(lang, 'source')}: https://lex.uz · https://pm.gov.uz")
    lines.append(t(lang, "disclaimer"))
    return {"type": "not_found", "lang": lang, "text": "\n".join(lines), "card_id": None,
            "confidence": top.score if top else 0.0, "sources": nf_sources, "verified": False,
            "badge": "", "disclaimer": t(lang, "disclaimer"), "event_id": event_id,
            "buttons": _buttons("not_found", None, event_id), "alternatives": alternatives}


# ------------------------------------------------------------------ SMS tushuntirish

async def explain_sms(db: Session, text: str, *, lang: str = "uz", region: str | None = None,
                      channel: str = "api", today: date | None = None) -> dict:
    parsed = sms_parser.parse(text, today=today)
    card_id = sms_parser.kind_to_card(parsed.get("kind")) or "traffic_fine"
    card = knowledge.cards.get(card_id)
    L = lang if lang != "ru" else "ru"
    lines: list[str] = [f"{t(L, 'sms_title')}  [{render.badge(card, L)}]"]
    if parsed.get("kind") == "suspicious":
        lines.append(t(L, "sms_suspicious"))
        for s in parsed.get("suspicious_signals", [])[:3]:
            lines.append(f"• {s}")
    if parsed.get("amount") is not None:
        label = t(L, "sms_amount") if parsed.get("kind") == "fine" else t(L, "sms_sum")
        lines.append(f"• {label}: {sms_parser.fmt_money(parsed['amount'])}")
    if parsed.get("discount_amount") is not None:
        dl = parsed.get("discount_deadline")
        dl_txt = date.fromisoformat(dl).strftime("%d.%m.%Y") if dl else "—"
        days = parsed.get("days_left")
        left = (f"{days} {t(L, 'sms_days_left')}" if days is not None and days >= 0 else t(L, "sms_expired"))
        lines.append(f"• {t(L, 'sms_discount')}: {sms_parser.fmt_money(parsed['discount_amount'])} "
                     f"({parsed.get('discount_percent')}%) — {dl_txt} ({left})")
    if parsed.get("organ"):
        lines.append(f"• {t(L, 'sms_organ')}: {parsed['organ']}" + (f" / {parsed['city']}" if parsed.get("city") else ""))
    if parsed.get("invoice"):
        lines.append(f"• {t(L, 'sms_invoice')}: {parsed['invoice']}")
    steps = card.get("steps", [])
    lines.append(f"{t(L, 'steps')}: " + " → ".join(render.show_todo(s, L) for s in steps[:3]))
    dispute = [s for s in steps if any(k in s.lower() for k in ("e'tiroz", "shikoyat"))]
    if dispute and parsed.get("kind") != "suspicious":
        dl = [render.show_todo(d, L) for d in card.get("deadlines", []) if "e'tiroz" in d.lower() or "shikoyat" in d.lower()]
        step = re.sub(r"^rozi bo'lmasangiz\s*[—-]\s*", "", dispute[0], flags=re.I)
        lines.append(f"⚖️ {t(L, 'sms_dispute')}: {render.show_todo(step, L)}" + (f" ({dl[0]})" if dl else ""))
    quotes = card_quotes(card, L) if parsed.get("kind") != "suspicious" else []
    if quotes:
        lines += render.quote_lines(quotes[0], L)
    lines.append(render.source_line(card, L))
    lines.append(t(L, "disclaimer"))
    out_text = "\n".join(to_script(x, L) if L == "uz_cyrl" else x for x in lines)
    event_id = analytics.log_event(db, kind="sms", topic_id=card_id, region=region, lang=lang, channel=channel,
                                   answer_type="sms", confidence=1.0 if parsed.get("kind") else 0.5)
    return {"type": "sms", "lang": lang, "text": out_text, "card_id": card_id, "title": card["title_uz"],
            "parsed": parsed, "sources": render.sources_of(card), "verified": card.get("verified", False),
            "badge": render.badge(card, L), "disclaimer": t(L, "disclaimer"), "event_id": event_id,
            "quotes": quotes, "buttons": _buttons("sms", card_id, event_id)}


# ------------------------------------------------------------------ Fakt-tekshiruv

async def fact_check(db: Session, text: str, *, lang: str | None = None, region: str | None = None,
                     channel: str = "api") -> dict:
    lang = lang or detect_lang(text)
    matches = classifier.match_claims(text)
    claims = {c["id"]: c for c in knowledge.claims()}
    top = matches[0] if matches else None
    lines = [t(lang, "fc_title")]

    if top and top.score >= FACTCHECK_THRESHOLD:
        claim = claims[top.id]
        verdict = claim["verdict"]
        lines += [f"{t(lang, 'fc_verdict')}: {t(lang, 'verdict_' + verdict)}  [{render.badge(claim, lang)}]",
                  f"💬 «{claim['claim_uz']}»",
                  render.show_todo(claim["explanation_uz"], lang),
                  render.source_line(claim, lang), t(lang, "disclaimer")]
        sources = render.sources_of(claim)
        claim_id, verified = claim["id"], claim.get("verified", False)
        related = claim.get("topic_id")
    else:
        # Manba topilmadi -> "Tasdiqlanmagan". Hech qachon taxmin qilmaymiz.
        verdict, claim_id, verified = "tasdiqlanmagan", None, False
        lines += [f"{t(lang, 'fc_verdict')}: {t(lang, 'verdict_tasdiqlanmagan')}", t(lang, "fc_unverified_text")]
        sources = [{"doc": "Qonunchilik ma'lumotlari milliy bazasi", "article": "", "url": "https://lex.uz", "verified": True}]
        related = None
        cm = classifier.classify(text)
        if cm and cm[0].score >= get_settings().classifier_threshold:
            related = cm[0].id
            card = knowledge.cards.get(related)
            lines.append(f"📌 {t(lang, 'fc_related')}: {card['title_uz']}")
            lines.append(render.source_line(card, lang))
            sources = render.sources_of(card) + sources
        else:
            lines.append(f"{t(lang, 'source')}: https://lex.uz")
        lines.append(t(lang, "disclaimer"))

    out_text = "\n".join(to_script(x, lang) if lang == "uz_cyrl" else x for x in lines)
    event_id = analytics.log_event(db, kind="factcheck", topic_id=related, region=region, lang=lang, channel=channel,
                                   answer_type="factcheck", confidence=top.score if top else 0.0,
                                   verdict=verdict, claim_id=claim_id)
    return {"type": "factcheck", "lang": lang, "text": out_text, "verdict": verdict, "claim_id": claim_id,
            "card_id": related, "confidence": top.score if top else 0.0, "sources": sources, "verified": verified,
            "disclaimer": t(lang, "disclaimer"), "event_id": event_id, "buttons": _buttons("factcheck", None, event_id)}
