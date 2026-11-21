"""Huquqiy maqom va holat bo'yicha huquqlar, majburiyatlar va «Siz uchun qonunlar».

MANBA QOIDASI: yozuv faqat rasmiy manbaga (lex.uz yoki *.gov.uz) aniq URL, `retrieved_at` va `source_verified: true`
bilan bog'langan bo'lsa ko'rsatiladi. Manbasi yo'q yoki tekshirilmagan yozuv UI'ga CHIQMAYDI.
"""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from urllib.parse import urlparse

from ..config import get_settings

log = logging.getLogger("javob.rights")

STATUS_IDS = ["uz_citizen", "foreign", "stateless", "unknown"]
SITUATION_IDS = ["student", "mother", "parent", "pensioner", "driver", "entrepreneur", "worker", "civil_servant"]
# «Mening huquqlarim» asosiy toifalari (anonim rejimda ham ochiq)
ANON_SITUATIONS = ["student", "mother", "entrepreneur", "pensioner", "driver"]
ITEM_KINDS = ("benefit", "right", "duty", "document", "info")
TODO = "TODO_LAWYER"
# maqomga sezgir kartalar toifalari: javobda «siz uchun boshqacha bo'lishi mumkin» eslatmasi
STATUS_SENSITIVE_CATEGORIES = {"ijtimoiy_himoya", "oila", "mehnat"}


def official_url(url: str | None) -> bool:
    try:
        u = urlparse(url or "")
    except ValueError:
        return False
    host = (u.hostname or "").lower()
    return u.scheme == "https" and (host == "lex.uz" or host == "gov.uz" or host.endswith(".gov.uz"))


def law_is_sourced(law: dict) -> bool:
    return bool(law.get("source_verified") is True and law.get("retrieved_at") and official_url(law.get("url"))
                and law.get("title_uz") and law.get("date"))


def _read(path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        log.error("o'qib bo'lmadi %s: %s", path, e)
        return None


@lru_cache
def laws() -> dict[str, dict]:
    out = {}
    for p in sorted((get_settings().knowledge_dir / "laws").glob("*.json")):
        d = _read(p)
        if not isinstance(d, dict) or "id" not in d:
            continue
        if not law_is_sourced(d):
            log.warning("manbasiz qonun yozuvi yashirildi: %s", d.get("id"))
            continue
        out[d["id"]] = d
    return out


@lru_cache
def _rights_files() -> dict[str, dict]:
    out = {}
    for p in sorted((get_settings().knowledge_dir / "rights").glob("*.json")):
        d = _read(p)
        if isinstance(d, dict) and "id" in d and "type" in d:
            out[f"{d['type']}:{d['id']}"] = d
    return out


def reload() -> None:
    laws.cache_clear()
    _rights_files.cache_clear()
    excerpts.cache_clear()


# ------------------------------------------------------------------ qonun abzaslari (lex.uz'dan aynan)

def excerpt_is_sourced(e: dict) -> bool:
    """Ko'rsatish sharti: asl matn bor, TODO emas, rasmiy URL va olingan sana bor."""
    text = e.get("original_text") or e.get("text") or ""
    return bool(text and not text.startswith(TODO) and official_url(e.get("lex_url")) and e.get("retrieved_at"))


@lru_cache
def excerpts() -> dict[str, dict]:
    path = get_settings().knowledge_dir / "lex" / "excerpts.json"
    data = _read(path) or {}
    return {e["id"]: e for e in data.get("excerpts", []) if isinstance(e, dict) and "id" in e and excerpt_is_sourced(e)}


def excerpt_public(e: dict, lang: str = "uz") -> dict:
    plain = (e.get("plain_ru") if lang == "ru" else None) or e.get("plain_uz") or ""
    return {
        "id": e["id"], "doc": e.get("doc", ""), "article": e.get("article") or None,
        "paragraph": e.get("paragraph") or None,
        "original_text": e.get("original_text") or e.get("text", ""),
        "plain": plain, "plain_uz": e.get("plain_uz") or "", "plain_ru": e.get("plain_ru") or "",
        "lex_url": e["lex_url"], "retrieved_at": e["retrieved_at"],
        "simplified_by": e.get("simplified_by", "ai") if plain else None,
        "verified": bool(e.get("verified") and e.get("verified_by")),
        "categories": e.get("categories", []), "law_id": e.get("law_id"),
    }


def excerpts_by_ids(ids: list[str] | None, lang: str = "uz") -> list[dict]:
    ex = excerpts()
    return [excerpt_public(ex[i], lang) for i in (ids or []) if i in ex]


def find_excerpts(category: str | None = None, item_id: str | None = None, ids: list[str] | None = None,
                  lang: str = "uz") -> list[dict]:
    """Abzaslar: id'lar bo'yicha, toifa bo'yicha yoki toifa ichidagi imtiyoz/huquq bo'yicha."""
    if ids:
        return excerpts_by_ids(ids, lang)
    if item_id:
        for g in _rights_files().values():
            for it in g.get("items", []):
                if it.get("id") == item_id:
                    return excerpts_by_ids(it.get("excerpt_ids"), lang)
        b = _benefit(item_id)
        return excerpts_by_ids((b or {}).get("excerpt_ids"), lang)
    return [excerpt_public(e, lang) for e in excerpts().values()
            if not category or category in e.get("categories", [])]


def _benefit(bid: str) -> dict | None:
    from . import knowledge  # aylanma import bo'lmasin

    return knowledge.benefits().get(bid)


def _dmy(iso: str) -> str:
    try:
        y, m, d = iso.split("-")
        return f"{d}.{m}.{y}"
    except (ValueError, AttributeError):
        return iso or ""


def law_public(law: dict) -> dict:
    number = law.get("number") or TODO
    needs_check = TODO in str(number)
    return {
        "id": law["id"], "title": law["title_uz"], "title_official": law.get("title_official"),
        "number": None if needs_check else number, "number_needs_check": needs_check,
        "date": law["date"], "date_text": _dmy(law["date"]), "url": law["url"], "retrieved_at": law["retrieved_at"],
        "source_type": law.get("source_type", "lex.uz"), "plain": law.get("plain_uz", ""),
    }


def source_text(law: dict, article: str = "") -> str:
    num = law.get("number")
    num_txt = "" if not num or TODO in str(num) or num == "—" else f", {num}"
    art = f", {article}" if article else ""
    return f"Manba: «{law['title_uz']}»{num_txt} ({_dmy(law['date'])}){art} — {law['url']}"


def _items(group: dict, lang: str = "uz") -> list[dict]:
    L = laws()
    out = []
    for it in group.get("items", []):
        law = L.get(it.get("law_id"))
        if not law:  # manbasiz -> ko'rsatilmaydi
            continue
        exs = excerpts_by_ids(it.get("excerpt_ids"), lang)
        if it.get("excerpt_ids") and not exs:  # abzasi topilmagan yozuv ko'rsatilmaydi
            continue
        title = (it.get("title_ru") if lang == "ru" else None) or it["title_uz"]
        out.append({"id": it["id"], "kind": it.get("kind", "right"), "title": title, "plain": it["plain_uz"],
                    "article": it.get("article") or None, "excerpt": it.get("excerpt") or None,
                    "conditions": it.get("conditions_uz", []), "excerpts": exs,
                    "law": law_public(law), "source": source_text(law, it.get("article", "")),
                    "verified_by_lawyer": False})
    return out


def _news(sid: str, group: dict, lang: str = "uz") -> list[dict]:
    """Toifa yangiliklari: (1) lex.uz'dagi haqiqiy normalar (sana bilan), (2) o'zgarishlar lentasi (DEMO)."""
    from . import knowledge

    out = []
    for n in group.get("news", []):
        law = laws().get(n.get("law_id"))
        exs = excerpts_by_ids(n.get("excerpt_ids"), lang)
        if law and exs:
            out.append({"id": n["id"], "date": n["date"], "date_text": _dmy(n["date"]), "title": n["title_uz"],
                        "plain": n["plain_uz"], "excerpts": exs, "law": law_public(law), "is_demo": False})
    for c in knowledge.changes_feed():
        if sid in c.get("categories", []):
            out.append({"id": c["id"], "date": c["date"], "date_text": _dmy(c["date"]), "title": c["summary_uz"],
                        "plain": c.get("new_text", ""), "excerpts": [], "law": None, "is_demo": True,
                        "lex_url": c.get("lex_url")})
    return sorted(out, key=lambda x: x["date"], reverse=True)


def category_view(sid: str, lang: str = "uz") -> dict | None:
    """«Mening huquqlarim» toifasi: imtiyozlar, huquqlar, majburiyatlar, hujjatlar, qayerga borish, yangiliklar."""
    g = _rights_files().get(f"situation:{sid}")
    if not g:
        return None
    # Toifa ko'rinishida faqat lex.uz abzasiga bog'langan yozuvlar (asl matn + oddiy til yonma-yon)
    items = [i for i in _items(g, lang) if i["excerpts"]]
    by = {k: [i for i in items if i["kind"] == k] for k in ITEM_KINDS}
    title = (g.get("title_ru") if lang == "ru" else None) or g["title_uz"]
    return {
        "id": sid, "title": title, "icon": g.get("icon", ""), "intro": g.get("intro_uz", ""),
        "benefits": by["benefit"], "rights": by["right"] + by["info"], "duties": by["duty"],
        "documents": by["document"], "where_to_go": g.get("where_to_go", []), "news": _news(sid, g, lang),
        "laws": [law_public(x) for x in laws().values() if sid in x.get("situations", [])],
        "benefit_note": "Haqli bo'lishingiz mumkin — yakuniy qarorni vakolatli organ qabul qiladi. Shartlarni tekshiring.",
        "disclaimer": "Oddiy tildagi matnni AI soddalashtirgan — rasmiy matn yonida. Huquqiy xulosa emas; rasmiy manba — qonun hujjatining o'zi.",
    }


def categories(lang: str = "uz") -> list[dict]:
    out = []
    for sid in ANON_SITUATIONS:
        v = category_view(sid, lang)
        if v:
            out.append({"id": sid, "title": v["title"], "icon": v["icon"], "intro": v["intro"],
                        "counts": {k: len(v[k]) for k in ("benefits", "rights", "duties", "documents", "news")}})
    return out


def category_text(sid: str, per_group: int = 5, footer: bool = True) -> str:
    """Bot uchun qisqa matn (Telegram limiti ichida)."""
    v = category_view(sid)
    if not v:
        return ""
    L = [f"{v['icon']} {v['title']}", v["intro"], ""]
    for key, head in (("benefits", "🎁 Imtiyozlar (haqli bo'lishingiz mumkin)"), ("rights", "✅ Huquqlar"),
                      ("duties", "📌 Majburiyatlar"), ("documents", "📄 Kerakli hujjatlar")):
        if v[key]:
            L.append(head + ":")
            for i in v[key][:per_group]:
                ex = i["excerpts"][0] if i["excerpts"] else None
                src = f"{ex['doc'].split(' — ')[0]}, {ex['article']}: {ex['lex_url']}" if ex else i["law"]["url"]
                L.append(f"• {i['title']} — {i['plain']}\n  📚 {src}")
            L.append("")
    if v["where_to_go"]:
        L.append("📍 Qayerga: " + "; ".join(f"{w['name']} ({w['url']})" for w in v["where_to_go"][:3]))
    if v["news"]:
        n = v["news"][0]
        L.append(f"🔔 Yangilik ({n['date_text']}): {n['title']}{' [DEMO]' if n['is_demo'] else ''}")
    if footer:
        L += ["", "⚠️ " + v["benefit_note"], "AI soddalashtirdi — rasmiy matn manbada. TEKSHIRILMAGAN (demo)."]
    return "\n".join(L).strip()


def statuses() -> list[dict]:
    files = _rights_files()
    return [{"id": s, "title": files[f"status:{s}"]["title_uz"], "icon": files[f"status:{s}"].get("icon", "")}
            for s in STATUS_IDS if f"status:{s}" in files]


def situations(ids: list[str] | None = None) -> list[dict]:
    files = _rights_files()
    return [{"id": s, "title": files[f"situation:{s}"]["title_uz"], "icon": files[f"situation:{s}"].get("icon", ""),
             "intro": files[f"situation:{s}"].get("intro_uz", "")}
            for s in (ids or SITUATION_IDS) if f"situation:{s}" in files]


def normalize_status(status: str | None) -> str | None:
    return status if status in STATUS_IDS else None


def status_view(status: str | None) -> dict | None:
    s = normalize_status(status)
    g = _rights_files().get(f"status:{s}") if s else None
    if not g:
        return None
    items = _items(g)
    return {"id": s, "title": g["title_uz"], "icon": g.get("icon", ""), "intro": g.get("intro_uz", ""),
            "rights": [i for i in items if i["kind"] != "duty"], "duties": [i for i in items if i["kind"] == "duty"],
            "suggested_questions": [{"q": q["q"], "article": q.get("article")} for q in g.get("suggested_questions", [])]}


def situation_views(ids: list[str]) -> list[dict]:
    out = []
    for sid in ids:
        g = _rights_files().get(f"situation:{sid}")
        if not g:
            continue
        items = _items(g)
        if items:
            # "rights" — eski ko'rinish uchun (majburiyatdan boshqa hammasi); yangi UI guruhlangan kalitlardan foydalanadi
            out.append({"id": sid, "title": g["title_uz"], "icon": g.get("icon", ""), "intro": g.get("intro_uz", ""),
                        "rights": [i for i in items if i["kind"] != "duty"], "duties": [i for i in items if i["kind"] == "duty"],
                        "benefits": [i for i in items if i["kind"] == "benefit"],
                        "documents": [i for i in items if i["kind"] == "document"],
                        "where_to_go": g.get("where_to_go", [])})
    return out


def laws_for(status: str | None, situation_ids: list[str], limit: int = 6) -> list[dict]:
    s = normalize_status(status) or "unknown"
    picked: list[dict] = []
    seen = set()
    # avval maqomga oid (chet el fuqarosi uchun O'RQ-692 birinchi), keyin holatga oid
    status_laws = sorted((x for x in laws().values() if s in x.get("statuses", [])),
                         key=lambda x: (0 if x["id"] == "foreign_status_law" else 1 if x["id"] == "constitution" else 2))
    for law in status_laws[:3]:
        picked.append(law)
        seen.add(law["id"])
    for law in laws().values():
        if any(x in law.get("situations", []) for x in situation_ids) and law["id"] not in seen:
            picked.append(law)
            seen.add(law["id"])
    for law in status_laws[3:]:
        if law["id"] not in seen:
            picked.append(law)
            seen.add(law["id"])
    picked = picked[:limit]
    if len(picked) < 3:
        for law in laws().values():
            if law["id"] not in seen and len(picked) < 3:
                picked.append(law)
                seen.add(law["id"])
    return [law_public(x) for x in picked]


def answer_note(status: str | None, card_category: str | None) -> str | None:
    s = normalize_status(status)
    if not s or s == "uz_citizen":
        return None
    if card_category and card_category not in STATUS_SENSITIVE_CATEGORIES:
        return None
    g = _rights_files().get(f"status:{s}")
    return (g or {}).get("answer_note_uz")


def rights_text(status: str | None, situation_ids: list[str]) -> str:
    """Bot uchun qisqa matn."""
    v = status_view(status) or status_view("unknown")
    lines = [f"{v['icon']} {v['title']}", v["intro"], ""]
    lines.append("✅ Huquqlar:")
    for i in v["rights"][:6]:
        art = f", {i['article']}" if i["article"] else ""
        lines.append(f"• {i['title']} — {i['plain']}\n  📚 {i['law']['title']}{art}: {i['law']['url']}")
    if v["duties"]:
        lines += ["", "📌 Majburiyatlar:"]
        for i in v["duties"][:4]:
            art = f", {i['article']}" if i["article"] else ""
            lines.append(f"• {i['title']}\n  📚 {i['law']['title']}{art}: {i['law']['url']}")
    for sv in situation_views(situation_ids):
        if any(i.get("excerpts") for i in sv["rights"] + sv["duties"]):
            lines += ["", category_text(sv["id"], per_group=2, footer=False)]
            continue
        lines += ["", f"{sv['icon']} {sv['title']}:"]
        for i in (sv["rights"] + sv["duties"])[:3]:
            art = f", {i['article']}" if i["article"] else ""
            lines.append(f"• {i['title']}\n  📚 {i['law']['title']}{art}: {i['law']['url']}")
    lines += ["", "⚠️ Sodda izoh — huquqiy xulosa emas. Rasmiy manba — qonun hujjatining o'zi."]
    return "\n".join(lines)


def laws_text(status: str | None, situation_ids: list[str]) -> str:
    lines = ["📚 Siz uchun qonunlar:"]
    for law in laws_for(status, situation_ids):
        num = law["number"] if law["number"] else "raqami: tekshirilishi kerak"
        lines.append(f"• {law['title']} ({num}, {law['date_text']})\n  {law['plain']}\n  Manba: {law['url']}")
    lines.append("\nTekshirilgan sana: lex.uz, " + _dmy(next(iter(laws().values()))["retrieved_at"]) if laws() else "")
    return "\n".join(lines)
