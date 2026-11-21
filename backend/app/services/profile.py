"""«Mening huquqlarim»: MyGov (OneID) profili (hozircha MOCK) -> imtiyozlar, majburiyatlar, menga ta'sir qiluvchi o'zgarishlar.

Xavfsizlik qoidalari:
- Natija hech qachon "albatta olasiz" emas — faqat "Haqli bo'lishingiz mumkin" + tekshirilishi kerak bo'lgan shartlar.
- Qoida sharti TODO_LAWYER bo'lsa — u "noma'lum" hisoblanadi (taxmin qilinmaydi) va foydalanuvchiga ochiq ko'rsatiladi.
- Profil ma'lumotlari DB'ga yozilmaydi: har so'rovda manbadan (hozir JSON, keyin integratsiya platformasi) o'qiladi.
"""
from __future__ import annotations

import operator
from datetime import date, timedelta

from sqlalchemy.orm import Session

from ..config import APP_NAME, REGIONS
from ..models import AppliedChange, ProfileLink, utcnow
from . import knowledge, render
from .i18n import t
from .textutil import to_script

REGION_NAME = {r["id"]: r["name"] for r in REGIONS}
MINOR_AGE = 18  # "voyaga yetmagan" ta'rifi; loyiha brifi dalillari: "child allowance (under 18)"
SINGLE_PARENT_STATUSES = {"ajrashgan", "beva", "alohida yashaydi", "nikohda emas"}
CONSENT_SCOPE = ["family", "children_ages", "social_status", "fines_debts", "region"]

OPS = {"==": operator.eq, "!=": operator.ne, ">=": operator.ge, "<=": operator.le, ">": operator.gt, "<": operator.lt,
       "in": lambda a, b: a in b}


# ------------------------------------------------------------------ profil faktlari

def facts(profile: dict) -> dict:
    """Profil -> qoidalar uchun minimal faktlar (real tizimda aynan shu atributlar so'raladi)."""
    fam = profile.get("family") or {}
    soc = profile.get("social") or {}
    drv = profile.get("driver") or {}
    ages = [c.get("age") for c in fam.get("children", []) if isinstance(c.get("age"), int)]
    minors = sum(1 for a in ages if a < MINOR_AGE)
    obligations = profile.get("obligations") or []
    active_discount = sum(1 for o in obligations if o.get("kind") == "traffic_fine"
                          and isinstance(o.get("discount_due_in_days"), int) and o["discount_due_in_days"] >= 0)
    return {
        "minor_children": minors,
        "single_parent": minors > 0 and fam.get("marital_status") in SINGLE_PARENT_STATUSES,
        "low_income_registry": bool(soc.get("low_income_registry")),
        "is_pensioner": bool(soc.get("pensioner")),
        "lives_alone": bool(soc.get("lives_alone")),
        "has_license": bool(drv.get("has_license")),
        "fines_with_active_discount": active_discount,
        "region": profile.get("region"),
    }


def _label(cond: dict, lang: str) -> str:
    return cond.get("label_ru") if lang == "ru" and cond.get("label_ru") else cond.get("label_uz", "")


def evaluate(benefit: dict, f: dict, lang: str = "uz") -> dict:
    """Qoida: {"all": [shartlar]}. Har shart: bajarildi / bajarilmadi / noma'lum (TODO_LAWYER yoki fakt yo'q)."""
    met, failed, unknown, met_appeal = [], [], [], []
    for cond in (benefit.get("rule") or {}).get("all", []):
        label = _label(cond, lang)
        fact = cond.get("fact")
        if cond.get("todo") or not fact or fact not in f or cond.get("op") not in OPS:
            unknown.append(label)
            continue
        try:
            ok = OPS[cond["op"]](f[fact], cond.get("value"))
        except TypeError:
            unknown.append(label)
            continue
        (met if ok else failed).append(label)
        if ok:  # arizada birinchi shaxsda ("...bor", "...yashayman")
            met_appeal.append(cond.get("appeal_uz") or label)
    status = "mos_emas" if failed else "mumkin"
    return {"status": status, "met": met, "failed": failed, "to_check": unknown, "met_appeal": met_appeal}


# ------------------------------------------------------------------ ko'rinish (view)

def _title(item: dict, lang: str) -> str:
    return item.get("title_ru") if lang == "ru" and item.get("title_ru") else item.get("title_uz", item.get("id", ""))


def _fmt_money(n) -> str:
    try:
        return f"{int(n):,}".replace(",", " ") + " so'm"
    except (TypeError, ValueError):
        return "—"


def obligations_of(profile: dict, today: date, lang: str = "uz") -> list[dict]:
    out = []
    for o in profile.get("obligations") or []:
        due = today + timedelta(days=o["due_in_days"]) if isinstance(o.get("due_in_days"), int) else None
        disc = today + timedelta(days=o["discount_due_in_days"]) if isinstance(o.get("discount_due_in_days"), int) else None
        nearest = disc or due
        remind = max(today, nearest - timedelta(days=2)) if nearest else None
        out.append({
            "id": o["id"], "kind": o.get("kind"), "title": _title(o, lang), "issuer": o.get("issuer"),
            "amount": o.get("amount"), "amount_text": _fmt_money(o.get("amount")),
            "deadline": due.isoformat() if due else None, "days_left": o.get("due_in_days"),
            "discount_amount": o.get("discount_amount"), "discount_pct": o.get("discount_pct"),
            "discount_deadline": disc.isoformat() if disc else None, "discount_days_left": o.get("discount_due_in_days"),
            "reminder_date": remind.isoformat() if remind else None,
            "warning": o.get("warning_uz"), "card_id": o.get("card_id"), "invoice": o.get("invoice"),
        })
    out.sort(key=lambda x: (x["discount_days_left"] if x["discount_days_left"] is not None
                            else x["days_left"] if x["days_left"] is not None else 10**6))
    return out


def benefits_of(profile: dict, lang: str = "uz") -> tuple[list[dict], list[dict]]:
    f = facts(profile)
    eligible, not_eligible = [], []
    for b in knowledge.benefits().values():
        ev = evaluate(b, f, lang)
        item = {
            "id": b["id"], "icon": b.get("icon", "🎁"), "kind": b.get("kind", "benefit"), "title": _title(b, lang),
            "summary": render.show_todo(b.get("summary_uz", ""), lang),
            "amount": render.show_todo(str(b.get("amount", "")), lang),
            "status": ev["status"],
            # HECH QACHON "albatta" emas
            "status_text": t(lang, "benefit_maybe") if ev["status"] == "mumkin" else t(lang, "benefit_no"),
            "met": ev["met"], "failed": ev["failed"], "to_check": ev["to_check"],
            "documents": [render.show_todo(d, lang) for d in b.get("documents", [])],
            "where_to_go": [{"name": render.show_todo(w["name"], lang), "url": w["url"]} for w in b.get("where_to_go", [])],
            "sources": render.sources_of(b), "source_line": render.source_line(b, lang),
            "verified": bool(b.get("verified") and b.get("verified_by")), "badge": render.badge(b, lang),
            "source_checked": bool(b.get("source_checked")),
            "related_card_id": b.get("related_card_id"),
            "appeal_label": b.get("appeal_label_uz") or t(lang, "btn_benefit_appeal"),
        }
        (eligible if ev["status"] == "mumkin" else not_eligible).append(item)
    return eligible, not_eligible


def relevant_refs(profile: dict) -> dict[str, str]:
    """ref_id -> nega bu profilga taalluqli (imtiyoz yoki majburiyat nomi). O'zgarishlarni nishonlash uchun."""
    refs: dict[str, str] = {}
    eligible, _ = benefits_of(profile)
    for item in eligible:
        for s in item["sources"]:
            if s.get("ref_id"):
                refs.setdefault(s["ref_id"], f"«{item['title']}»")
    for o in profile.get("obligations") or []:
        card = knowledge.cards.get(o.get("card_id"))
        for b in (card or {}).get("legal_basis", []):
            if b.get("ref_id"):
                refs.setdefault(b["ref_id"], f"«{o.get('title_uz', o['id'])}»")
    return refs


def changes_for(db: Session, profile: dict, lang: str = "uz") -> list[dict]:
    applied = {a.id: a for a in db.query(AppliedChange).all()}
    refs = relevant_refs(profile)
    out = []
    for c in knowledge.changes_feed():
        if c["id"] in applied and c.get("ref_id") in refs:
            out.append({"id": c["id"], "date": c["date"], "summary": c["summary_uz"],
                        "reason": t(lang, "change_reason", what=refs[c["ref_id"]]),
                        "applied_at": applied[c["id"]].applied_at.isoformat()})
    return out


def summary_lines(profile: dict, lang: str = "uz") -> list[str]:
    fam = profile.get("family") or {}
    soc = profile.get("social") or {}
    drv = profile.get("driver") or {}
    ages = [str(c["age"]) for c in fam.get("children", []) if isinstance(c.get("age"), int)]
    lines = [f"📍 {REGION_NAME.get(profile.get('region'), '—')}"]
    fam_txt = f"👨‍👩‍👧 {fam.get('marital_status', '—')}, {t(lang, 'pf_household', n=fam.get('household_size', '—'))}"
    if ages:
        fam_txt += f"; {t(lang, 'pf_children', ages=', '.join(ages))}"
    lines.append(fam_txt)
    soc_txt = f"💼 {soc.get('employment', '—')}"
    if soc.get("low_income_registry"):
        soc_txt += f" · {t(lang, 'pf_low_income')}"
    lines.append(soc_txt)
    if drv.get("has_license"):
        lines.append(f"🚗 {t(lang, 'pf_license', year=drv.get('license_year', '—'))}")
    return lines


def view(db: Session, profile_id: str, lang: str = "uz", today: date | None = None) -> dict | None:
    profile = knowledge.mock_profiles().get(profile_id)
    if not profile:
        return None
    today = today or date.today()
    eligible, not_eligible = benefits_of(profile, lang)
    obligations = obligations_of(profile, today, lang)
    changes = changes_for(db, profile, lang)
    data = {
        "profile": {"id": profile["id"], "icon": profile.get("icon", "👤"), "display_name": profile.get("display_name"),
                    "persona": profile.get("persona_ru") if lang == "ru" else profile.get("persona_uz"),
                    "region": profile.get("region"), "region_name": REGION_NAME.get(profile.get("region")),
                    "summary": summary_lines(profile, lang)},
        "source": t(lang, "pf_source"),
        "is_mock": True,
        "benefits": eligible, "not_eligible": [{"id": b["id"], "title": b["title"], "failed": b["failed"]}
                                               for b in not_eligible],
        "obligations": obligations, "changes": changes,
        "disclaimer": t(lang, "disclaimer"),
    }
    data["text"] = render_text(data, lang)
    return data


def render_text(v: dict, lang: str) -> str:
    """Bot uchun matn (Telegram limitiga sig'adi)."""
    p = v["profile"]
    L = [f"👤 {t(lang, 'pf_title')} — {p['display_name']}", f"🔐 {v['source']}", " · ".join(p["summary"]), ""]
    L.append(f"🎁 {t(lang, 'pf_benefits')} ({len(v['benefits'])})")
    if not v["benefits"]:
        L.append(f"• {t(lang, 'pf_no_benefits')}")
    for i, b in enumerate(v["benefits"], 1):
        L.append(f"{i}) {b['icon']} {b['title']} — {b['status_text']}")
        if b["met"]:
            L.append("   ✓ " + "; ".join(b["met"]))
        if b["to_check"]:
            L.append(f"   ❔ {t(lang, 'pf_to_check')}: " + "; ".join(b["to_check"]))
    L += ["", f"📅 {t(lang, 'pf_obligations')} ({len(v['obligations'])})"]
    if not v["obligations"]:
        L.append(f"• {t(lang, 'pf_no_obligations')}")
    for o in v["obligations"]:
        line = f"• {o['title']}: {o['amount_text']}"
        if o["discount_deadline"]:
            line += (f" — {t(lang, 'pf_discount', amount=_fmt_money(o['discount_amount']), pct=o.get('discount_pct') or '—')}"
                     f" {_dmy(o['discount_deadline'])} {t(lang, 'pf_until')} ({t(lang, 'pf_days_left', n=o['discount_days_left'])})")
        elif o["deadline"]:
            line += f" — {_dmy(o['deadline'])} {t(lang, 'pf_until')} ({t(lang, 'pf_days_left', n=o['days_left'])})"
        L.append(line)
        if o.get("warning"):
            L.append(f"  ⚠️ {o['warning']}")
    L += ["", f"🔔 {t(lang, 'pf_changes')}"]
    if not v["changes"]:
        L.append(f"• {t(lang, 'pf_no_changes')}")
    for c in v["changes"]:
        L.append(f"• {_dmy(c['date'])}: {c['summary']}\n  {c['reason']}")
    L += ["", f"{t(lang, 'badge_unverified')} · {v['disclaimer']}"]
    return to_script("\n".join(L), lang)


def _dmy(iso: str) -> str:
    try:
        return date.fromisoformat(iso).strftime("%d.%m.%Y")
    except (TypeError, ValueError):
        return iso or "—"


# ------------------------------------------------------------------ bog'lanish (SQLite)

def link(db: Session, user_key: str, profile_id: str, lang: str = "uz", channel: str = "telegram") -> ProfileLink:
    row = db.get(ProfileLink, user_key)
    if row is None:
        row = ProfileLink(user_key=user_key, profile_id=profile_id, lang=lang, channel=channel,
                          consent_scope=list(CONSENT_SCOPE))
        db.add(row)
    else:
        row.profile_id, row.lang, row.channel = profile_id, lang, channel
        row.consent_scope = list(CONSENT_SCOPE)
        row.consent_at = utcnow()
    db.commit()
    return row


def unlink(db: Session, user_key: str) -> bool:
    row = db.get(ProfileLink, user_key)
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True


def linked_profile_id(db: Session, user_key: str) -> str | None:
    row = db.get(ProfileLink, user_key)
    return row.profile_id if row else None


# ------------------------------------------------------------------ o'zgarishlar zanjiri uchun

def change_impact(change: dict) -> list[dict]:
    """Har bir profil uchun: shu o'zgarish unga ta'sir qiladimi va nega."""
    out = []
    for p in knowledge.mock_profiles().values():
        refs = relevant_refs(p)
        reason = refs.get(change.get("ref_id"))
        out.append({"profile_id": p["id"], "icon": p.get("icon", "👤"), "persona": p.get("persona_uz"),
                    "affected": reason is not None, "reason": reason})
    return out


def alert_text(change: dict, reason: str, lang: str) -> str:
    txt = t(lang, "pf_alert", app=APP_NAME, summary=change["summary_uz"], date=_dmy(change["date"]), what=reason)
    return to_script(txt, lang)
