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
SITUATION_IDS = ["student", "parent", "pensioner", "driver", "entrepreneur", "worker", "civil_servant"]
ANON_SITUATIONS = ["student", "parent", "pensioner", "driver", "entrepreneur"]
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


def _items(group: dict) -> list[dict]:
    L = laws()
    out = []
    for it in group.get("items", []):
        law = L.get(it.get("law_id"))
        if not law:  # manbasiz -> ko'rsatilmaydi
            continue
        out.append({"id": it["id"], "kind": it.get("kind", "right"), "title": it["title_uz"], "plain": it["plain_uz"],
                    "article": it.get("article") or None, "excerpt": it.get("excerpt") or None,
                    "law": law_public(law), "source": source_text(law, it.get("article", "")),
                    "verified_by_lawyer": False})
    return out


def statuses() -> list[dict]:
    files = _rights_files()
    return [{"id": s, "title": files[f"status:{s}"]["title_uz"], "icon": files[f"status:{s}"].get("icon", "")}
            for s in STATUS_IDS if f"status:{s}" in files]


def situations(ids: list[str] | None = None) -> list[dict]:
    files = _rights_files()
    return [{"id": s, "title": files[f"situation:{s}"]["title_uz"], "icon": files[f"situation:{s}"].get("icon", "")}
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
            out.append({"id": sid, "title": g["title_uz"], "icon": g.get("icon", ""),
                        "rights": [i for i in items if i["kind"] != "duty"], "duties": [i for i in items if i["kind"] == "duty"]})
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
