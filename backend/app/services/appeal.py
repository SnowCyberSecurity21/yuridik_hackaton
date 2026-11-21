"""Murojaat generatori: karta + shablon -> to'g'ri adresatga, to'g'ri formatda tayyor matn."""
from __future__ import annotations

from datetime import date

from . import knowledge, llm, render
from .i18n import t
from .textutil import to_script

PLACEHOLDERS = {
    "applicant_name": "[F.I.Sh.]",
    "address": "[yashash manzilingiz]",
    "contact": "[telefon yoki e-pochta]",
    "region": "[hudud]",
    "situation": "[vaziyatni qisqa yozing: qachon, nima bo'ldi, qaysi qaror]",
    "attachments": "",
}


def _legal_basis_text(card: dict) -> str:
    parts = []
    for b in card.get("legal_basis", []):
        doc = render.show_todo(b.get("doc", ""), "uz")
        art = b.get("article", "")
        if not art or "TODO_LAWYER" in art:
            art_txt = "[moddani lex.uz'dan aniqlang]"
        elif any(x in art for x in ("modda", "band", "ilova")):
            art_txt = art  # «2, 6-bandlar», «404-modda» — allaqachon to'liq
        else:
            art_txt = f"{art}-modda"
        parts.append(f"{doc}, {art_txt}")
    return "; ".join(parts) or "[huquqiy asos]"


def _fill(tpl: dict, item: dict, fields: dict, *, situation: str | None, lang: str, title: str = "") -> str:
    base = {**PLACEHOLDERS, **(tpl.get("placeholders") or {})}  # yuridik shaxs shablonida boshqacha belgilar
    values = {**base, **fields}
    values["situation"] = situation or base["situation"]
    values["attachments"] = fields.get("attachments") or "; ".join(
        render.show_todo(d, "uz") for d in item.get("documents", [])[:3])
    text = tpl["body"].format(
        addressee=render.show_todo(item.get("appeal_addressee") or "[adresat]", "uz"),
        doc_type=tpl["doc_type"], intro=tpl["intro"].replace("{title}", title), request=tpl["request"],
        legal_basis=_legal_basis_text(item), date=date.today().strftime("%d.%m.%Y"),
        **{k: values[k] for k in ("applicant_name", "address", "contact", "region", "situation", "attachments")},
    )
    return to_script(text, lang) if lang == "uz_cyrl" else text


def _template(template_id: str | None) -> dict:
    tpls = knowledge.appeal_templates()
    return tpls.get(template_id or "") or next(iter(tpls.values()))


async def _polish(situation: str | None) -> str | None:
    if situation and llm.is_available():
        polished = await llm.complete(llm.load_prompt("appeal_polish"), situation, max_tokens=400)
        # LLM yangi fakt qo'shmasin: uzunlik keskin oshsa — asl matn qoladi
        if polished and len(polished) <= len(situation) * 1.6 + 80:
            return polished.strip()
    return situation


def _result(tpl: dict, item: dict, text: str, fields: dict, lang: str, **extra) -> dict:
    from . import rights  # aylanma importsiz

    missing = [k for k in ("applicant_name", "address", "situation") if k not in fields]
    return {
        "addressee": render.show_todo(item.get("appeal_addressee") or "", lang), "template_id": tpl["id"],
        "title": tpl.get("title_uz"), "doc_type": tpl.get("doc_type"), "applicant_type": tpl.get("applicant_type", "individual"),
        "text": text, "checklist": tpl.get("checklist", []), "submit_channels": tpl.get("submit_channels", []),
        # Qonundagi rekvizitlar va muddat — faqat shu murojaatga tatbiq etiladigan qonundan (lex.uz abzasi bilan)
        "legal_regime": tpl.get("legal_regime_uz"), "requirements": tpl.get("requirements", []),
        "review_term": tpl.get("review_term_uz"), "excerpts": rights.excerpts_by_ids(tpl.get("excerpt_ids")),
        "missing_fields": missing, "verified": bool(item.get("verified") and tpl.get("verified")),
        "header": t(lang, "appeal_title"), "hint": t(lang, "appeal_hint"), **extra,
    }


async def generate(card_id: str, fields: dict | None = None, lang: str = "uz") -> dict | None:
    card = knowledge.cards.get(card_id)
    if not card:
        return None
    tpl = _template(card.get("appeal_template_id"))
    fields = {k: v for k, v in (fields or {}).items() if isinstance(v, str) and v.strip()}
    situation = await _polish(fields.get("situation"))
    text = _fill(tpl, card, fields, situation=situation, lang=lang)
    return _result(tpl, card, text, fields, lang, card_id=card_id)


async def generate_for_benefit(benefit_id: str, profile: dict, lang: str = "uz") -> dict | None:
    """Imtiyozdan bir bosishda ariza: MyGov (mock) profilidan hudud, ism va mos shartlar oldindan to'ldiriladi.

    Profil ma'lumoti faqat javob matniga qo'yiladi va hech qayerda saqlanmaydi.
    """
    from . import profile as profile_svc

    benefit = knowledge.benefits().get(benefit_id)
    if not benefit:
        return None
    ev = profile_svc.evaluate(benefit, profile_svc.facts(profile), "uz")
    if ev["status"] != "mumkin":
        return None
    tpl = _template(benefit.get("appeal_template_id"))
    parts = [f"OneID (DEMO) ma'lumotlariga ko'ra: " + "; ".join(ev["met_appeal"]) + "."]
    for o in profile.get("obligations") or []:
        if benefit.get("related_card_id") and o.get("card_id") == benefit["related_card_id"]:
            amount = f"{int(o['amount']):,}".replace(",", " ") if o.get("amount") else "—"
            inv = f", invoys {o['invoice']}" if o.get("invoice") else ""
            parts.append(f"{o.get('title_uz', '')}{inv}: {amount} so'm.")
    parts.append("[Qo'shimcha holatlarni o'zingiz yozing]")
    fields = {"applicant_name": profile.get("display_name") or PLACEHOLDERS["applicant_name"],
              "region": profile_svc.REGION_NAME.get(profile.get("region"), PLACEHOLDERS["region"])}
    text = _fill(tpl, benefit, fields, situation=" ".join(parts), lang=lang, title=benefit.get("title_uz", ""))
    res = _result(tpl, benefit, text, {**fields, "situation": "x"}, lang, benefit_id=benefit_id,
                  title=benefit.get("title_uz"), to_check=ev["to_check"])
    res["missing_fields"] = ["address", "contact"]
    res["hint"] = t(lang, "pf_appeal_hint")
    return res
