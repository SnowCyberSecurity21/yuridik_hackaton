"""Davlat dashboardi API."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models import Alert, ProfileLink, TextbookChunk
from ..services import analytics, changes, knowledge, outreach
from ..services import profile as profile_svc


def require_admin(x_admin_token: str | None = Header(None)):
    token = get_settings().admin_token
    if token and x_admin_token != token:
        raise HTTPException(401, "admin token noto'g'ri")


router = APIRouter(prefix="/api/gov", tags=["gov"], dependencies=[Depends(require_admin)])


def _cards() -> dict[str, dict]:
    return {c["id"]: c for c in knowledge.cards.all()}


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    return analytics.overview(db, _cards())


@router.get("/topics")
def topics(limit: int = 10, db: Session = Depends(get_db)):
    return analytics.top_topics(db, _cards(), limit)


@router.get("/regions")
def regions(topic_id: str | None = None, db: Session = Depends(get_db)):
    return analytics.by_region(db, topic_id)


@router.get("/trend")
def trend(days: int = 28, topic_id: str | None = None, db: Session = Depends(get_db)):
    return analytics.trend(db, days, topic_id)


@router.get("/signals")
def signals(db: Session = Depends(get_db)):
    return analytics.signals(db, knowledge.claims(), _cards())


class ContentIn(BaseModel):
    topic_id: str


@router.post("/content")
async def content(body: ContentIn):
    card = knowledge.cards.get(body.topic_id)
    if not card:
        raise HTTPException(404, "mavzu topilmadi")
    return await outreach.generate(card)


@router.get("/changes")
def list_changes(db: Session = Depends(get_db)):
    return changes.list_changes(db)


class SimulateIn(BaseModel):
    change_id: str | None = None


@router.post("/simulate-amendment")
async def simulate(body: SimulateIn | None = None, db: Session = Depends(get_db)):
    res = await changes.apply_change(db, body.change_id if body else None)
    if res is None:
        raise HTTPException(409, "Barcha o'zgarishlar allaqachon qo'llangan — 'Demo'ni tiklash' tugmasini bosing")
    return res


@router.post("/reset-demo")
def reset_demo(db: Session = Depends(get_db)):
    changes.reset_demo(db)
    return {"ok": True}


@router.get("/alerts")
def alerts(db: Session = Depends(get_db)):
    rows = db.query(Alert).order_by(Alert.ts.desc()).limit(50).all()
    return [{"id": a.id, "ts": a.ts.isoformat(), "change_id": a.change_id, "topic_id": a.topic_id,
             "to_subscriber": a.chat_id is not None, "delivered": a.delivered, "text": a.text} for a in rows]


@router.get("/textbook")
def textbook(db: Session = Depends(get_db)):
    rows = db.query(TextbookChunk).order_by(TextbookChunk.id).all()
    return [{"id": r.id, "textbook": r.textbook_title, "title": r.title, "text": r.text, "refs": r.refs,
             "status": r.status, "change_id": r.change_id, "diff": r.diff, "suggested_text": r.suggested_text}
            for r in rows]


@router.get("/profiles")
def profiles(db: Session = Depends(get_db)):
    """Demo profillar va ularga ulangan foydalanuvchilar soni (shaxsiy ma'lumotsiz)."""
    counts: dict[str, int] = {}
    for (pid,) in db.query(ProfileLink.profile_id).all():
        counts[pid] = counts.get(pid, 0) + 1
    out = []
    for p in knowledge.mock_profiles().values():
        eligible, _ = profile_svc.benefits_of(p)
        out.append({"profile_id": p["id"], "icon": p.get("icon"), "persona": p.get("persona_uz"),
                    "linked_users": counts.get(p["id"], 0), "benefits": [b["title"] for b in eligible],
                    "refs": sorted(profile_svc.relevant_refs(p))})
    return out
