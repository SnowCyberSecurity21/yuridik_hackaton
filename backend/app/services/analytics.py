"""Anonim analitika: faqat mavzu, hudud (ixtiyoriy), til, kanal, vaqt, foydali/yo'q.
PINFL, pasport, F.I.Sh., telefon, savol matni — HECH QACHON saqlanmaydi.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..config import REGION_IDS, REGIONS
from ..models import Event, utcnow


def clean_region(region: str | None) -> str | None:
    return region if region in REGION_IDS else None


def log_event(db: Session, *, kind: str, topic_id: str | None = None, region: str | None = None, lang: str = "uz",
              channel: str = "api", answer_type: str | None = None, confidence: float | None = None,
              verdict: str | None = None, claim_id: str | None = None) -> int | None:
    try:
        ev = Event(kind=kind, topic_id=topic_id, region=clean_region(region), lang=lang, channel=channel,
                   answer_type=answer_type, confidence=confidence, verdict=verdict, claim_id=claim_id)
        db.add(ev)
        db.commit()
        return ev.id
    except Exception:  # analitika hech qachon javobni buzmasin
        db.rollback()
        return None


def feedback(db: Session, event_id: int, *, helpful: bool | None = None, appeal: bool = False) -> bool:
    ev = db.get(Event, event_id)
    if not ev:
        return False
    if helpful is not None:
        ev.was_helpful = helpful
    if appeal:
        ev.appeal_requested = True
        ev.was_helpful = False
    db.commit()
    return True


# ---------------- Dashboard agregatlari ----------------

def _since(days: int):
    return utcnow() - timedelta(days=days)


def overview(db: Session, cards_by_id: dict[str, dict]) -> dict:
    q = db.query(Event)
    total = q.filter(Event.kind.in_(["ask", "sms"])).count()
    week = q.filter(Event.kind.in_(["ask", "sms"]), Event.ts >= _since(7)).count()
    prev = q.filter(Event.kind.in_(["ask", "sms"]), Event.ts >= _since(14), Event.ts < _since(7)).count()
    # "Konsultatsiya talab qiluvchi" murojaatlar oldi olindi: kartadan javob berildi va murojaat so'ralmadi
    deflected = q.filter(Event.kind.in_(["ask", "sms"]), Event.answer_type.in_(["card", "sms"]),
                         Event.appeal_requested.is_(False)).count()
    appeals = q.filter(Event.appeal_requested.is_(True)).count()
    helpful = q.filter(Event.was_helpful.is_(True)).count()
    rated = q.filter(Event.was_helpful.isnot(None)).count()
    fact = q.filter(Event.kind == "factcheck").count()
    return {
        "total_questions": total, "week_questions": week, "prev_week_questions": prev,
        "wow_change_pct": round((week - prev) / prev * 100, 1) if prev else None,
        "deflected": deflected, "appeals_generated": appeals,
        "helpful_rate": round(helpful / rated * 100, 1) if rated else None,
        "factchecks": fact, "topics_total": len(cards_by_id),
    }


def top_topics(db: Session, cards_by_id: dict[str, dict], limit: int = 10) -> list[dict]:
    rows = (db.query(Event.topic_id, func.count(Event.id))
            .filter(Event.kind.in_(["ask", "sms"]), Event.topic_id.isnot(None))
            .group_by(Event.topic_id).all())
    week = dict(db.query(Event.topic_id, func.count(Event.id))
                .filter(Event.kind.in_(["ask", "sms"]), Event.ts >= _since(7)).group_by(Event.topic_id).all())
    prev = dict(db.query(Event.topic_id, func.count(Event.id))
                .filter(Event.kind.in_(["ask", "sms"]), Event.ts >= _since(14), Event.ts < _since(7))
                .group_by(Event.topic_id).all())
    not_helpful = dict(db.query(Event.topic_id, func.count(Event.id))
                       .filter(Event.was_helpful.is_(False)).group_by(Event.topic_id).all())
    rated = dict(db.query(Event.topic_id, func.count(Event.id))
                 .filter(Event.was_helpful.isnot(None)).group_by(Event.topic_id).all())
    out = []
    for tid, cnt in rows:
        c = cards_by_id.get(tid, {})
        w, p = week.get(tid, 0), prev.get(tid, 0)
        r = rated.get(tid, 0)
        out.append({
            "topic_id": tid, "title": c.get("title_uz", tid), "category": c.get("category"),
            "count": cnt, "week": w, "prev_week": p,
            "wow_change_pct": round((w - p) / p * 100, 1) if p else None,
            "misunderstanding_rate": round(not_helpful.get(tid, 0) / r * 100, 1) if r else None,
            "verified": c.get("verified", False), "source_checked": bool(c.get("source_checked")), "needs_reverification": c.get("needs_reverification", False),
        })
    out.sort(key=lambda x: x["count"], reverse=True)
    return out[:limit]


def by_region(db: Session, topic_id: str | None = None) -> list[dict]:
    q = db.query(Event.region, func.count(Event.id)).filter(Event.kind.in_(["ask", "sms"]), Event.region.isnot(None))
    if topic_id:
        q = q.filter(Event.topic_id == topic_id)
    counts = dict(q.group_by(Event.region).all())
    # har hudud bo'yicha eng ko'p so'ralgan mavzu
    tq = (db.query(Event.region, Event.topic_id, func.count(Event.id))
          .filter(Event.kind.in_(["ask", "sms"]), Event.region.isnot(None), Event.topic_id.isnot(None))
          .group_by(Event.region, Event.topic_id).all())
    best: dict[str, tuple[str, int]] = {}
    for reg, tid, cnt in tq:
        if reg not in best or cnt > best[reg][1]:
            best[reg] = (tid, cnt)
    return [{"region": r["id"], "name": r["name"], "count": counts.get(r["id"], 0),
             "top_topic": best.get(r["id"], (None, 0))[0]} for r in REGIONS]


def trend(db: Session, days: int = 28, topic_id: str | None = None) -> list[dict]:
    from datetime import datetime

    start = utcnow().date() - timedelta(days=days)
    q = db.query(Event.ts).filter(Event.kind.in_(["ask", "sms"]), Event.ts >= datetime.combine(start, datetime.min.time()))
    if topic_id:
        q = q.filter(Event.topic_id == topic_id)
    c = Counter(ts.date().isoformat() for (ts,) in q.all())
    # Bugungi (tugallanmagan) kun kiritilmaydi — aks holda trend oxirida soxta "tushish" ko'rinadi
    return [{"date": (start + timedelta(days=i)).isoformat(), "count": c.get((start + timedelta(days=i)).isoformat(), 0)}
            for i in range(days)]


def signals(db: Session, claims: list[dict], cards_by_id: dict[str, dict]) -> dict:
    claim_by_id = {c["id"]: c for c in claims}
    rows = (db.query(Event.claim_id, Event.verdict, func.count(Event.id))
            .filter(Event.kind == "factcheck", Event.claim_id.isnot(None), Event.ts >= _since(14))
            .group_by(Event.claim_id, Event.verdict).all())
    region_rows = (db.query(Event.claim_id, Event.region, func.count(Event.id))
                   .filter(Event.kind == "factcheck", Event.claim_id.isnot(None), Event.region.isnot(None))
                   .group_by(Event.claim_id, Event.region).all())
    top_regions: dict[str, list] = defaultdict(list)
    for cid, reg, cnt in region_rows:
        top_regions[cid].append((reg, cnt))
    fakes = []
    for cid, verdict, cnt in rows:
        if verdict not in ("notogri", "qisman"):
            continue
        cl = claim_by_id.get(cid, {})
        regs = sorted(top_regions.get(cid, []), key=lambda x: -x[1])[:3]
        fakes.append({"claim_id": cid, "claim": cl.get("claim_uz", cid), "verdict": verdict, "count": cnt,
                      "top_regions": [r for r, _ in regs]})
    fakes.sort(key=lambda x: -x["count"])
    topics = top_topics(db, cards_by_id, limit=50)
    misunderstood = sorted([t for t in topics if t["misunderstanding_rate"] is not None and t["count"] >= 5],
                           key=lambda x: -x["misunderstanding_rate"])[:5]
    return {"fake_claims": fakes, "misunderstood_topics": misunderstood}
