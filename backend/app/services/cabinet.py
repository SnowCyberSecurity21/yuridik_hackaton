"""Tasdiqlangan kabinet: demo ID ma'lumoti -> imtiyozlar, huquqlar, majburiyatlar, qonunlar, o'zgarishlar."""
from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from . import profile as profile_svc
from . import rights
from .i18n import t

STATUS_BENEFIT_NOTE = {
    "foreign": "ℹ️ Siz chet el fuqarosisiz: bu imtiyoz shartlari siz uchun boshqacha bo'lishi mumkin — ariza berishdan oldin tekshiring.",
    "stateless": "ℹ️ Siz fuqaroligi bo'lmagan shaxssiz: bu imtiyoz shartlari siz uchun boshqacha bo'lishi mumkin — tekshiring.",
    "unknown": "ℹ️ Maqomingiz aniq emas: bu imtiyoz faqat fuqarolar uchun bo'lishi mumkin — tekshiring.",
}


def person_status(person: dict) -> str:
    return rights.normalize_status((person.get("citizenship") or {}).get("status")) or "unknown"


def person_situations(person: dict) -> list[str]:
    sits = list(person.get("situations") or [])
    f = profile_svc.facts(person)
    if f["minor_children"] and "parent" not in sits:
        sits.append("parent")
    if f["has_license"] and "driver" not in sits:
        sits.append("driver")
    if f["is_pensioner"] and "pensioner" not in sits:
        sits.append("pensioner")
    return [s for s in sits if s in rights.SITUATION_IDS]


def as_profile(person: dict) -> dict:
    """profile_svc funksiyalari kutadigan shakl (display_name va h.k.)."""
    return {**person, "id": person["sub"], "display_name": person.get("full_name"), "persona_uz": person.get("persona_uz")}


def view(db: Session, person: dict, roles: list[str], lang: str = "uz", today: date | None = None) -> dict:
    today = today or date.today()
    prof = as_profile(person)
    status = person_status(person)
    sits = person_situations(person)
    eligible, not_eligible = profile_svc.benefits_of(prof, lang)
    note = STATUS_BENEFIT_NOTE.get(status)
    for b in eligible:
        b["status_note"] = note
    cit = person.get("citizenship") or {}
    st = rights.status_view(status)
    data = {
        "person": {"first_name": person.get("first_name"), "full_name": person.get("full_name"), "icon": person.get("icon", "👤"),
                   "persona": person.get("persona_uz"), "birth_date": person.get("birth_date"),
                   "region": person.get("region"), "region_name": profile_svc.REGION_NAME.get(person.get("region")),
                   "status": status, "status_title": st["title"] if st else status, "document": cit.get("document"),
                   "residence": cit.get("residence"), "occupation": (person.get("occupation") or {}).get("title"),
                   "summary": profile_svc.summary_lines(prof, lang), "is_demo": True},
        "roles": roles,
        "situations": rights.situations(sits),
        "benefits": eligible,
        "not_eligible": [{"id": b["id"], "title": b["title"], "failed": b["failed"]} for b in not_eligible],
        "rights": {"status": st, "situations": rights.situation_views(sits)},
        "obligations": profile_svc.obligations_of(prof, today, lang),
        "laws": rights.laws_for(status, sits),
        "changes": profile_svc.changes_for(db, prof, lang),
        "disclaimer": t(lang, "disclaimer"),
        "source": "DEMO ID (OneID simulyatsiyasi) — o'ylab topilgan shaxs, ma'lumotlar Huquqim bazasida saqlanmaydi",
    }
    return data


# ------------------------------------------------------------------ bot uchun matnlar

def _dmy(iso: str | None) -> str:
    try:
        return date.fromisoformat(iso).strftime("%d.%m.%Y")
    except (TypeError, ValueError):
        return iso or "—"


def section_text(v: dict, section: str) -> str:
    p = v["person"]
    if section == "benefits":
        L = [f"🎁 Mening imtiyozlarim — {p['first_name']}", ""]
        if not v["benefits"]:
            L.append("Hozircha mos imtiyoz topilmadi.")
        for i, b in enumerate(v["benefits"], 1):
            L.append(f"{i}) {b['icon']} {b['title']} — {b['status_text']}")
            if b["met"]:
                L.append("   ✓ " + "; ".join(b["met"]))
            if b["to_check"]:
                L.append("   ❔ Tekshirilishi kerak: " + "; ".join(b["to_check"]))
            if b.get("status_note"):
                L.append("   " + b["status_note"])
            L.append(f"   📚 {b['source_line']}")
        L += ["", "⚠️ «Haqli bo'lishingiz mumkin» — yakuniy qarorni vakolatli organ qabul qiladi. TEKSHIRILMAGAN (demo)."]
        return "\n".join(L)
    if section == "rights":
        return rights.rights_text(p["status"], [s["id"] for s in v["situations"]])
    if section == "obligations":
        L = ["📅 Majburiyatlar (muddat bilan)", ""]
        if not v["obligations"]:
            L.append("Muddatli majburiyat yo'q ✅")
        for o in v["obligations"]:
            line = f"• {o['title']}: {o['amount_text']}"
            if o["discount_deadline"]:
                line += f" — chegirma bilan {o['discount_amount']:,} so'm {_dmy(o['discount_deadline'])} gacha ({o['discount_days_left']} kun qoldi)".replace(",", " ")
            elif o["deadline"]:
                line += f" — {_dmy(o['deadline'])} gacha ({o['days_left']} kun qoldi)"
            L.append(line)
            if o.get("warning"):
                L.append(f"  ⚠️ {o['warning']}")
        st = v["rights"]["status"]
        if st and st["duties"]:
            L += ["", "📌 Umumiy majburiyatlar (maqomingiz bo'yicha):"]
            for d in st["duties"]:
                L.append(f"• {d['title']} — {d['law']['title']}{', ' + d['article'] if d['article'] else ''}")
        return "\n".join(L)
    if section == "laws":
        return rights.laws_text(p["status"], [s["id"] for s in v["situations"]])
    if section == "changes":
        L = ["🔔 Menga ta'sir qiluvchi o'zgarishlar", ""]
        if not v["changes"]:
            L.append("Hozircha yo'q. Sizga taalluqli qonun o'zgarsa, shu yerda va xabar sifatida ko'rasiz.")
        for c in v["changes"]:
            L.append(f"• {_dmy(c['date'])}: {c['summary']}\n  {c['reason']}")
        return "\n".join(L)
    return ""
