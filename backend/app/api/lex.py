"""«Mening huquqlarim» toifalari va qonun abzaslari (lex.uz'dan aynan + oddiy til).

Hammasi anonim va faqat o'qish uchun: so'rov parametrlari saqlanmaydi.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..services import knowledge, rights

router = APIRouter(tags=["rights"])


def _lang(lang: str | None) -> str:
    return "ru" if lang == "ru" else "uz"


@router.get("/api/rights/categories")
def rights_categories(lang: str = "uz"):
    """Toifalar ro'yxati: Talaba, Bolali ona, Yuridik shaxs / tadbirkor, Pensioner, Haydovchi."""
    return {"categories": rights.categories(_lang(lang))}


@router.get("/api/rights/category/{sid}")
def rights_category(sid: str, lang: str = "uz"):
    v = rights.category_view(sid, _lang(lang))
    if not v:
        raise HTTPException(404, "toifa topilmadi")
    v["text"] = rights.category_text(sid)
    return v


@router.get("/api/lex/excerpts")
def lex_excerpts(category: str | None = None, item: str | None = None, ids: str | None = None, lang: str = "uz"):
    """Abzaslar: ?category=student | ?item=st_stipend (yoki imtiyoz id) | ?ids=ex_a,ex_b"""
    id_list = [i for i in (ids or "").split(",") if i][:50]
    items = rights.find_excerpts(category=category, item_id=item, ids=id_list or None, lang=_lang(lang))
    return {"excerpts": items, "count": len(items),
            "note": "«Qonunda» — lex.uz'dan aynan olingan matn. «Oddiy tilda» — AI soddalashtirgan, rasmiy matn yonida."}


@router.get("/api/lex/excerpts/{eid}")
def lex_excerpt(eid: str, lang: str = "uz"):
    items = rights.excerpts_by_ids([eid], _lang(lang))
    if not items:
        raise HTTPException(404, "abzas topilmadi")
    return items[0]


@router.get("/api/appeal/templates")
def appeal_templates():
    """Murojaat shablonlari: qaysi kartalar ishlatadi, qonundagi rekvizitlar, ko'rib chiqish muddati."""
    by_tpl: dict[str, list[dict]] = {}
    for c in knowledge.cards.all():
        tid = c.get("appeal_template_id")
        if tid:
            by_tpl.setdefault(tid, []).append({"card_id": c["id"], "title": c["title_uz"]})
    out = []
    for t in knowledge.appeal_templates().values():
        out.append({"id": t["id"], "title": t.get("title_uz") or t.get("doc_type"), "doc_type": t.get("doc_type"),
                    "applicant_type": t.get("applicant_type", "individual"),
                    "requirements": t.get("requirements", []), "review_term": t.get("review_term_uz"),
                    "checklist": t.get("checklist", []), "submit_channels": t.get("submit_channels", []),
                    "excerpts": rights.excerpts_by_ids(t.get("excerpt_ids")),
                    "cards": by_tpl.get(t["id"], [])})
    return {"templates": out}
