"""Targ'ibot kontenti generatori (3-muammo): video ssenariy, infografika, Telegram post, 3 savollik quiz.
Faqat karta mazmunidan. LLM bo'lmasa — shablon."""
from __future__ import annotations

import json

from ..config import APP_NAME
from . import llm, render

_DISTRACT_STEP = ["Hech narsa qilmaslik va kutish", "Faqat ijtimoiy tarmoqdagi guruhga yozish"]
_DISTRACT_WHERE = ["Hech qayerga — masala o'z-o'zidan hal bo'ladi", "Faqat tanishlar orqali"]
_DISTRACT_DOC = ["Hech qanday hujjat kerak emas", "Faqat og'zaki tushuntirish yetarli"]


def _clean(s: str) -> str:
    return render.show_todo(s, "uz")


def template_content(card: dict) -> dict:
    title = card["title_uz"]
    steps = [_clean(s) for s in card.get("steps", [])]
    where = card.get("where_to_go", [{"name": "my.gov.uz", "url": "https://my.gov.uz"}])
    docs = [_clean(d) for d in card.get("documents", [])]
    src = render.source_line(card, "uz")
    return {
        "video_script": [
            {"t": "0-5 s", "scene": "Muammo kadri", "text": f"«{title}» — tanish vaziyatmi?"},
            {"t": "5-15 s", "scene": "Oddiy tushuntirish", "text": card.get("plain_explanation_uz", "")},
            {"t": "15-25 s", "scene": "3 qadam", "text": " → ".join(steps[:3])},
            {"t": "25-30 s", "scene": "Yakun", "text": f"Batafsil: {where[0]['url']} · Savol bo'lsa — {APP_NAME} botiga yozing."},
        ],
        "infographic": {
            "headline": title,
            "blocks": [
                {"title": "Qonun nima deydi", "text": card.get("plain_explanation_uz", "")},
                {"title": "Nima qilish kerak", "text": "; ".join(steps[:4])},
                {"title": "Hujjatlar", "text": "; ".join(docs[:3])},
                {"title": "Qayerga", "text": "; ".join(w["name"] for w in where[:2])},
            ],
            "footer": src,
        },
        "telegram_post": (f"📌 {title}\n\n{card.get('plain_explanation_uz', '')}\n\n👣 Nima qilish kerak:\n"
                          + "\n".join(f"{i + 1}) {s}" for i, s in enumerate(steps[:4]))
                          + f"\n\n📍 {where[0]['name']}: {where[0]['url']}\n{src}\n\n#huquqiy_savodxonlik"),
        "quiz": [
            {"q": f"«{title}» holatida birinchi navbatda nima qilish kerak?",
             "options": [steps[0] if steps else "Rasmiy organga murojaat qilish", *_DISTRACT_STEP], "answer": 0},
            {"q": "Qayerga murojaat qilish mumkin?",
             "options": [_DISTRACT_WHERE[0], where[0]["name"], _DISTRACT_WHERE[1]], "answer": 1},
            {"q": "Qaysi hujjat kerak bo'ladi?",
             "options": [_DISTRACT_DOC[0], _DISTRACT_DOC[1], docs[0] if docs else "Shaxsni tasdiqlovchi hujjat"], "answer": 2},
        ],
    }


async def generate(card: dict) -> dict:
    base = template_content(card)
    result = {"card_id": card["id"], "title": card["title_uz"], "verified": card.get("verified", False),
              "generated_by": "template", **base}
    if not llm.is_available():
        return result
    payload = {k: v for k, v in card.items() if not k.startswith("_")}
    data = await llm.complete_json(llm.load_prompt("outreach"), json.dumps(payload, ensure_ascii=False), max_tokens=2500)
    if data and all(k in data for k in ("video_script", "infographic", "telegram_post", "quiz")):
        quiz_ok = isinstance(data["quiz"], list) and len(data["quiz"]) >= 3 and all(
            isinstance(q, dict) and {"q", "options", "answer"} <= q.keys() for q in data["quiz"])
        if quiz_ok:
            # Manba qatori har doim koddan — LLM uni o'zgartira olmaydi
            src = render.source_line(card, "uz")
            post = str(data["telegram_post"])
            if src not in post:
                post += f"\n\n{src}"
            result.update(video_script=data["video_script"], infographic=data["infographic"],
                          telegram_post=post, quiz=data["quiz"][:3], generated_by="llm")
    return result
