"""Ta'lim: AI simulyator (fuqaro bilan maslahat suhbati + baho) va hujjat trenajyori.

LLM bo'lsa — rol o'ynash va tahlil LLM orqali; bo'lmasa yoki xato bo'lsa — kartadan shablon (demo hech qachon to'xtamaydi).
Faktlar faqat vaziyat kartasidan olinadi.
"""
from __future__ import annotations

import json
import re

from . import knowledge, llm

RUBRIC = [
    ("greet", "Salomlashdi va o'zini tanishtirdi", r"\b(assalom|salom|xush kelibsiz|ismim|men .*(yurist|maslahatchi|talaba))"),
    ("facts", "Vaziyatni aniqlovchi savollar berdi", r"\?"),
    ("docs", "Kerakli hujjatlarni so'radi yoki aytdi", r"(hujjat|guvohnoma|ma'lumotnoma|pasport|ariza|qaror)"),
    ("deadline", "Muddat haqida gapirdi", r"(muddat|kun ichida|oy ichida|qachon|sana)"),
    ("basis", "Huquqiy asosni (qonun/modda/manba) tilga oldi", r"(qonun|modda|kodeks|lex\.uz|manba)"),
    ("steps", "Keyingi qadamlarni tushuntirdi", r"(murojaat|shikoyat|boring|yuboring|my\.gov|qadam|avval|keyin)"),
]


def cases() -> list[dict]:
    return [{"id": c["id"], "title": c["title_uz"]} for c in knowledge.cards.all()]


def _persona(card: dict) -> str:
    reasons = [r for r in card.get("common_reasons", []) if "TODO_LAWYER" not in r]
    return (f"Assalomu alaykum. Muammom shu: «{card['title_uz']}». Nima qilishimni bilmayapman. "
            + (f"Ehtimol sababi: {reasons[0].lower()}." if reasons else ""))


def start(card_id: str) -> dict | None:
    card = knowledge.cards.get(card_id)
    if not card:
        return None
    return {"card_id": card_id, "title": card["title_uz"], "reply": _persona(card),
            "brief": "Siz yuridik maslahatchisiz. Fuqaroni tinglang, savol bering, hujjat va muddatlarni aniqlang, huquqiy asosni ayting."}


def _fallback_reply(card: dict, student_text: str, turn: int) -> str:
    low = student_text.lower()
    if re.search(r"hujjat|guvohnoma|ma'lumotnoma", low):
        docs = [d for d in card.get("documents", []) if "TODO_LAWYER" not in d][:2]
        return "Menda " + (", ".join(docs).lower() if docs else "faqat pasportim") + " bor. Yana nima kerak?"
    if re.search(r"qachon|muddat|sana", low):
        return "Bu ishga bir oycha bo'ldi. Muddat o'tib ketmadimi?"
    if re.search(r"qayerga|kimga|murojaat|ariza", low):
        return "Qayerga borishim kerak? Internet orqali yuborsa bo'ladimi?"
    steps = [s for s in card.get("steps", []) if "TODO_LAWYER" not in s]
    if turn >= 3:
        return "Rahmat, tushunarli bo'ldi. Demak, avval nima qilaman?"
    return "Tushunmadim, oddiyroq tushuntiring. " + (f"Masalan, «{steps[0].lower()}» degani nima?" if steps else "")


async def reply(card_id: str, history: list[dict]) -> dict | None:
    card = knowledge.cards.get(card_id)
    if not card:
        return None
    history = [h for h in history if isinstance(h, dict)][-12:]
    last = next((h.get("text", "") for h in reversed(history) if h.get("role") == "student"), "")
    turn = sum(1 for h in history if h.get("role") == "student")
    if llm.is_available():
        system = ("Sen O'zbekistonlik oddiy fuqarosan va yuridik maslahatchi (talaba) bilan gaplashyapsan. "
                  "Faqat quyidagi vaziyat kartasidagi faktlarga tayan, yangi qonun, modda yoki summa to'qima. "
                  "Qisqa (1–3 gap), sodda o'zbek tilida (lotin) javob ber. Sen maslahat bermaysan — sen mijozsan.")
        conv = "\n".join(f"{'MASLAHATCHI' if h.get('role') == 'student' else 'FUQARO'}: {h.get('text', '')}" for h in history)
        out = await llm.complete(system, f"KARTA: {json.dumps({k: card.get(k) for k in ('title_uz', 'common_reasons', 'documents')}, ensure_ascii=False)}\n\nSUHBAT:\n{conv}\nFUQARO:", max_tokens=200)
        if out and len(out) < 600:
            return {"reply": out.strip(), "llm_used": True}
    return {"reply": _fallback_reply(card, last, turn), "llm_used": False}


def score(card_id: str, history: list[dict]) -> dict | None:
    card = knowledge.cards.get(card_id)
    if not card:
        return None
    student = " ".join(h.get("text", "") for h in history if isinstance(h, dict) and h.get("role") == "student").lower()
    items = []
    for key, label, rx in RUBRIC:
        ok = bool(re.search(rx, student))
        items.append({"id": key, "label": label, "ok": ok})
    got = sum(1 for i in items if i["ok"])
    total = round(got / len(items) * 10, 1)
    tips = [f"«{i['label']}» — bu bosqich o'tkazib yuborildi" for i in items if not i["ok"]]
    basis = [f"{b.get('doc')} {b.get('article') or ''}".strip() for b in card.get("legal_basis", [])
             if "TODO_LAWYER" not in (b.get("doc") or "")]
    return {"score": total, "max": 10, "rubric": items, "tips": tips,
            "reference": {"steps": [s for s in card.get("steps", []) if "TODO_LAWYER" not in s],
                          "legal_basis": basis or ["Tekshirilishi kerak (huquqshunos)"]},
            "note": "Baho rubrika bo'yicha avtomatik (demo). Yakuniy baho — o'qituvchida."}


CHECKS = [
    ("addressee", "Adresat (qaysi organ rahbariga) ko'rsatilgan", r"(rahbari|boshlig'i|direktori|hokimi|sudiga|bo'limiga|markaziga)ga?\b|\bga$",
     "Ariza boshida kimga yozilayotgani bo'lishi shart: organ nomi va rahbar lavozimi."),
    ("applicant", "Arizachi ma'lumotlari (F.I.Sh., manzil, aloqa) bor", r"(f\.?i\.?sh|manzil|telefon|yashovchi|dan\b)",
     "Kimdan ekanligi: F.I.Sh., yashash manzili va aloqa ma'lumoti yozilmasa, javob yuborib bo'lmaydi."),
    ("title", "Hujjat turi nomlangan (ARIZA / SHIKOYAT / DA'VO)", r"\b(ariza|shikoyat|da'vo|murojaat)\b",
     "Hujjat turi aniq yozilsin: ariza, shikoyat yoki da'vo arizasi."),
    ("facts", "Holat (faktlar) bayon qilingan", r".{120,}",
     "Nima bo'lgani qisqa va xronologik tartibda yozilishi kerak (kim, qachon, nima)."),
    ("basis", "Huquqiy asos ko'rsatilgan (qonun/modda)", r"(qonun|modda|kodeks)",
     "Talabingiz qaysi qonun yoki moddaga asoslanishini yozing (manbani lex.uz'dan tekshiring)."),
    ("request", "Aniq talab bor (so'rayman / talab qilaman)", r"(so'rayman|talab qilaman|iltimos qilaman|bekor qilishni|tayinlashni)",
     "Oxirida aniq nima so'ralayotgani bo'lsin: «...ni so'rayman»."),
    ("attachments", "Ilovalar ro'yxati", r"(ilova|ilovalar|nusxasi)", "Qo'shib yuborilayotgan hujjatlar ro'yxatini yozing."),
    ("date_sign", "Sana va imzo", r"(\d{1,2}[./]\d{1,2}[./]\d{2,4}|sana|imzo)", "Ariza oxirida sana va imzo bo'lishi shart."),
]


def check_document(card_id: str | None, text: str) -> dict:
    low = (text or "").lower()
    results = []
    for key, label, rx, why in CHECKS:
        ok = bool(re.search(rx, low, re.S | re.M))
        results.append({"id": key, "label": label, "ok": ok, "explain": None if ok else why})
    card = knowledge.cards.get(card_id) if card_id else None
    if card:
        tpl = knowledge.appeal_templates().get(card.get("appeal_template_id") or "", {})
        addressee = tpl.get("addressee_hint") or ""
        if addressee:
            results.append({"id": "card_addressee", "label": f"Kartaga mos adresat: {addressee}", "ok": addressee.lower()[:12] in low,
                            "explain": None if addressee.lower()[:12] in low else f"Bu vaziyatda odatda «{addressee}» ga yoziladi."})
    errors = [r for r in results if not r["ok"]]
    return {"ok_count": len(results) - len(errors), "total": len(results), "results": results,
            "errors": errors, "score": round((len(results) - len(errors)) / max(1, len(results)) * 10, 1),
            "note": "Tekshiruv checklist bo'yicha (demo). Huquqiy asos to'g'riligini huquqshunos tasdiqlaydi."}
