"""Qonun o'zgarishlarini kuzatish (2 va 6-muammolar).

O'zgarish -> (a) FAQAT ta'sir qiladigan profillarga (va mavzuga ochiq obuna bo'lganlarga) alert,
(b) darslik bo'laklari "ESKIRGAN" (ta'lim moduli hozircha to'xtatilgan — UI'da ko'rsatilmaydi),
(c) karta "qayta tekshirish kerak". Dashboard'dagi "Simulyatsiya" tugmasi butun zanjirni jonli ishga tushiradi.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import Alert, AppliedChange, Card, ProfileLink, Subscription, TextbookChunk
from . import knowledge, llm, notifier
from . import profile as profile_svc
from .textutil import to_script


def list_changes(db: Session) -> list[dict]:
    applied = {a.id: a for a in db.query(AppliedChange).all()}
    return [{**c, "applied": c["id"] in applied,
             "applied_at": applied[c["id"]].applied_at.isoformat() if c["id"] in applied else None}
            for c in knowledge.changes_feed()]


async def _suggest_update(chunk: TextbookChunk, change: dict) -> str:
    if change["old_text"] in chunk.text:
        return chunk.text.replace(change["old_text"], change["new_text"])
    if llm.is_available():
        out = await llm.complete(
            llm.load_prompt("textbook_update"),
            f"DARSLIK BO'LAGI:\n{chunk.text}\n\nESKI TAHRIR:\n{change['old_text']}\n\nYANGI TAHRIR:\n{change['new_text']}",
            max_tokens=600)
        if out:
            return out.strip()
    return chunk.text + f"\n\n[YANGILASH KERAK] {change['new_text']}"


async def apply_change(db: Session, change_id: str | None = None, audience: str = "all") -> dict | None:
    """audience="demo" — davlat kabinetidan: xabar FAQAT demo ID bilan tasdiqlangan hisoblarga ulangan chatlarga."""
    feed = knowledge.changes_feed()
    applied = {a.id for a in db.query(AppliedChange).all()}
    change = next((c for c in feed if c["id"] == change_id), None) if change_id else \
        next((c for c in feed if c["id"] not in applied), None)
    if change is None:
        return None
    ref = change["ref_id"]

    # (c) kartalar -> qayta tekshirish
    affected_cards = []
    for row in db.query(Card).all():
        if any(b.get("ref_id") == ref for b in row.data.get("legal_basis", [])):
            row.needs_reverification = True
            row.reverify_reason = f"{change['date']}: {change['summary_uz']}"
            affected_cards.append({"id": row.id, "title": row.data.get("title_uz")})

    # (b) darslik bo'laklari -> ESKIRGAN
    chunks_out = []
    for ch in db.query(TextbookChunk).all():
        if ref in (ch.refs or []):
            ch.status = "outdated"
            ch.change_id = change["id"]
            ch.diff = {"old": change["old_text"], "new": change["new_text"]}
            ch.suggested_text = await _suggest_update(ch, change)
            chunks_out.append({"id": ch.id, "title": ch.title, "textbook": ch.textbook_title,
                               "old_text": ch.text, "suggested_text": ch.suggested_text, "diff": ch.diff})

    # (a) alertlar: profil bo'yicha nishonlash — faqat ta'sir qiladigan profillar
    impact = profile_svc.change_impact(change)
    affected_profiles = {i["profile_id"]: i for i in impact if i["affected"]}
    notified: set[str] = set()
    profile_alerts = 0
    links_by_profile: dict[str, int] = {}
    for link in (db.query(ProfileLink).all() if audience != "demo" else []):
        links_by_profile[link.profile_id] = links_by_profile.get(link.profile_id, 0) + 1
        info = affected_profiles.get(link.profile_id)
        if not info or link.user_key in notified:
            continue
        db.add(Alert(change_id=change["id"], topic_id=(affected_cards[0]["id"] if affected_cards else ref),
                     chat_id=link.user_key, profile_id=link.profile_id,
                     text=profile_svc.alert_text(change, info["reason"], link.lang),
                     # web foydalanuvchi xabarni ilova ichida ko'radi (Telegram'ga yuborilmaydi)
                     delivered=not link.user_key.lstrip("-").isdigit()))
        notified.add(link.user_key)
        profile_alerts += 1
    for i in impact:
        i["linked_users"] = links_by_profile.get(i["profile_id"], 0)

    # mavzuga ochiq obuna bo'lganlar (o'zi rozilik bilan tanlagan) — takrorlanmasdan
    subscriber_alerts = 0
    preview = None
    for card in affected_cards:
        base_text = (f"🔔 Qonun o'zgardi: {card['title']}\n{change['summary_uz']}\n"
                     f"Sana: {change['date']}. Yangilangan tushuntirish: botga mavzuni qayta so'rang.")
        preview = preview or base_text
        for s in (db.query(Subscription).filter(Subscription.topic_id == card["id"]).all() if audience != "demo" else []):
            if s.chat_id in notified:
                continue
            db.add(Alert(change_id=change["id"], topic_id=card["id"], chat_id=s.chat_id, text=to_script(base_text, s.lang)))
            notified.add(s.chat_id)
            subscriber_alerts += 1
    # demo ID bilan tasdiqlangan hisoblar (faqat ularga ulangan Telegram chatlar) — limit bilan
    verified = _verified_account_alerts(db, change, notified)
    # dashboard uchun umumiy yozuv (chat_id'siz)
    db.add(Alert(change_id=change["id"], topic_id=affected_cards[0]["id"] if affected_cards else ref, chat_id=None,
                 text=preview or f"🔔 {change['summary_uz']} ({change['date']})", delivered=True))
    first = next(iter(affected_profiles.values()), None)
    profile_preview = profile_svc.alert_text(change, first["reason"], "uz") if first else None
    alerts_created = profile_alerts + subscriber_alerts + verified["sent"]

    summary = {"cards": affected_cards, "chunks": [c["id"] for c in chunks_out], "alerts_created": alerts_created,
               "profiles": [i["profile_id"] for i in impact if i["affected"]]}
    if change["id"] in applied:
        db.get(AppliedChange, change["id"]).summary = summary
    else:
        db.add(AppliedChange(id=change["id"], summary=summary))
    db.commit()
    knowledge.cards.refresh(db)
    delivered = await notifier.deliver_pending(db) if notifier.enabled() else {"alerts": 0}

    return {"change": change, "affected_cards": affected_cards, "outdated_chunks": chunks_out,
            "profiles": impact,
            "alerts": {"subscribers_notified": alerts_created, "profile_users_notified": profile_alerts,
                       "topic_subscribers_notified": subscriber_alerts,
                       "verified_accounts_notified": verified["sent"], "verified_affected": verified["affected"],
                       "audience": audience,
                       "delivered_via_telegram": delivered["alerts"], "telegram_enabled": notifier.enabled(),
                       "preview": profile_preview or preview}}


def reset_demo(db: Session) -> None:
    db.query(AppliedChange).delete()
    db.query(Alert).delete()
    for row in db.query(Card).all():
        row.needs_reverification = False
        row.reverify_reason = None
    db.commit()
    knowledge.reset_textbooks(db)
    knowledge.cards.refresh(db)


def _verified_account_alerts(db: Session, change: dict, notified: set[str]) -> dict:
    """Demo ID orqali tasdiqlangan hisoblar: shaxsga ta'sir qilsa va Telegram ulangan bo'lsa — alert (maks. sim_max_messages)."""
    from ..config import get_settings
    from ..models import Account, TelegramLink
    from . import accounts, cabinet

    cap = max(1, get_settings().sim_max_messages)
    sent = affected = 0
    for link in db.query(TelegramLink).all():
        if sent >= cap:
            break
        acc = db.get(Account, link.account_id)
        person = accounts.person_of(db, acc)
        if not person or link.chat_id in notified:
            continue
        reason = profile_svc.relevant_refs(cabinet.as_profile(person)).get(change.get("ref_id"))
        if not reason:
            continue
        affected += 1
        db.add(Alert(change_id=change["id"], topic_id=change.get("ref_id") or "-", chat_id=link.chat_id,
                     profile_id=person.get("sub"), text=profile_svc.alert_text(change, reason, "uz")))
        notified.add(link.chat_id)
        sent += 1
    return {"sent": sent, "affected": affected}
