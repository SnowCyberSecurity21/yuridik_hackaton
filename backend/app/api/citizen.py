"""Fuqaro API (bot, Mini App, CLI shu endpointlardan foydalanadi)."""
from __future__ import annotations

from datetime import date, datetime, time

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..config import REGIONS
from ..db import get_db
from ..models import Reminder, Subscription
from ..services import analytics, answer, appeal, knowledge, llm, notifier, render, rights, speech
from ..services.i18n import strings, t
from ..services.textutil import detect_lang

router = APIRouter(prefix="/api", tags=["citizen"])


class AskIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    lang: str | None = Field(None, description="uz | uz_cyrl | ru (bo'sh bo'lsa avtomatik)")
    region: str | None = None
    channel: str = "api"
    mode: str = Field("auto", description="auto | question | sms | factcheck")
    legal_status: str | None = Field(None, description="uz_citizen | foreign | stateless | unknown (ixtiyoriy, saqlanmaydi)")


def with_status_note(res: dict, legal_status: str | None) -> dict:
    """Maqom hisobga olinadi: chet el fuqarosi / fuqaroligi yo'q shaxsga «siz uchun boshqacha bo'lishi mumkin»."""
    if not legal_status or res.get("type") not in ("card", "sms"):
        return res
    card = knowledge.cards.get(res.get("card_id"))
    note = rights.answer_note(legal_status, (card or {}).get("category"))
    specific = ((card or {}).get("status_notes") or {}).get(legal_status)
    if specific:
        note = (note + chr(10) + specific) if note else specific
    if note:
        res["status_note"] = note
        res["text"] = res["text"] + chr(10) * 2 + note
    return res


@router.post("/ask")
async def ask(body: AskIn, db: Session = Depends(get_db)):
    res = await answer.answer_question(db, body.text, lang=body.lang, region=body.region,
                                       channel=body.channel, mode=body.mode)
    return with_status_note(res, body.legal_status)


@router.post("/ask/voice")
async def ask_voice(file: UploadFile = File(...), region: str | None = Form(None), channel: str = Form("telegram"),
                    lang: str | None = Form(None), legal_status: str | None = Form(None), db: Session = Depends(get_db)):
    audio = await file.read()
    if not speech.stt_available():
        return {"type": "voice_unsupported", "text": t(lang or "uz", "voice_unsupported"), "transcript": None}
    transcript = await speech.transcribe(audio, file.filename or "voice.ogg")
    if not transcript:
        return {"type": "voice_unsupported", "text": t(lang or "uz", "voice_unsupported"), "transcript": None}
    res = await answer.answer_question(db, transcript, lang=lang, region=region, channel=channel)
    res["transcript"] = transcript
    return with_status_note(res, legal_status)


class TextIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    lang: str | None = None
    region: str | None = None
    channel: str = "api"


@router.post("/sms")
async def sms(body: TextIn, db: Session = Depends(get_db)):
    return await answer.explain_sms(db, body.text, lang=body.lang or detect_lang(body.text),
                                    region=body.region, channel=body.channel)


@router.post("/factcheck")
async def factcheck(body: TextIn, db: Session = Depends(get_db)):
    return await answer.fact_check(db, body.text, lang=body.lang, region=body.region, channel=body.channel)


class FeedbackIn(BaseModel):
    event_id: int
    helpful: bool


@router.post("/feedback")
def feedback(body: FeedbackIn, db: Session = Depends(get_db)):
    return {"ok": analytics.feedback(db, body.event_id, helpful=body.helpful)}


class AppealIn(BaseModel):
    card_id: str
    event_id: int | None = None
    lang: str = "uz"
    fields: dict[str, str] = Field(default_factory=dict,
                                   description="applicant_name, address, contact, region, situation, attachments")


@router.post("/appeal")
async def make_appeal(body: AppealIn, db: Session = Depends(get_db)):
    res = await appeal.generate(body.card_id, body.fields, body.lang)
    if res is None:
        raise HTTPException(404, "karta topilmadi")
    if body.event_id:
        analytics.feedback(db, body.event_id, appeal=True)
    else:
        eid = analytics.log_event(db, kind="appeal", topic_id=body.card_id, lang=body.lang, channel="api")
        if eid:
            analytics.feedback(db, eid, appeal=True)
    return res


class SubscribeIn(BaseModel):
    chat_id: str
    topic_id: str
    lang: str = "uz"


@router.post("/subscribe")
def subscribe(body: SubscribeIn, db: Session = Depends(get_db)):
    if not knowledge.cards.get(body.topic_id):
        raise HTTPException(404, "mavzu topilmadi")
    exists = db.query(Subscription).filter_by(chat_id=body.chat_id, topic_id=body.topic_id).first()
    if not exists:
        db.add(Subscription(chat_id=body.chat_id, topic_id=body.topic_id, lang=body.lang))
        db.commit()
    return {"ok": True, "text": t(body.lang, "subscribed")}


class ReminderIn(BaseModel):
    chat_id: str
    remind_on: date
    text: str = Field(..., max_length=500)
    lang: str = "uz"


@router.post("/reminders")
def add_reminder(body: ReminderIn, db: Session = Depends(get_db)):
    db.add(Reminder(chat_id=body.chat_id, remind_at=datetime.combine(body.remind_on, time(9, 0)), text=body.text))
    db.commit()
    return {"ok": True, "text": t(body.lang, "reminder_set", date=body.remind_on.strftime("%d.%m.%Y")),
            "telegram_enabled": notifier.enabled()}


class TTSIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    lang: str = "uz"


@router.post("/tts")
async def tts(body: TTSIn):
    audio = await speech.synthesize(body.text, body.lang)
    if not audio:
        raise HTTPException(503, "TTS hozircha mavjud emas (faqat matn)")
    return Response(content=audio, media_type="audio/mpeg")


@router.post("/stt")
async def stt(file: UploadFile = File(...)):
    if not speech.stt_available():
        raise HTTPException(503, "STT sozlanmagan (STT_PROVIDER)")
    text = await speech.transcribe(await file.read(), file.filename or "voice.ogg")
    if not text:
        raise HTTPException(502, "ovozni tanib bo'lmadi")
    return {"text": text}


@router.get("/cards")
def list_cards():
    return [{"id": c["id"], "category": c["category"], "title_uz": c["title_uz"], "title_cyrl": c.get("title_cyrl"),
             "title_ru": c.get("title_ru"), "verified": c.get("verified", False), "source_checked": bool(c.get("source_checked")),
             "needs_reverification": c.get("needs_reverification", False)} for c in knowledge.cards.all()]


@router.get("/cards/{card_id}")
def get_card(card_id: str, lang: str = "uz"):
    card = knowledge.cards.get(card_id)
    if not card:
        raise HTTPException(404, "karta topilmadi")
    return {"card": {k: v for k, v in card.items() if not k.startswith("_")},
            "text": render.card_answer_text(card, lang), "sources": render.sources_of(card),
            "badge": render.badge(card, lang)}


@router.get("/regions")
def regions():
    return REGIONS


@router.get("/i18n/{lang}")
def i18n(lang: str):
    return strings(lang)


@router.get("/health")
def health():
    return {"ok": True, "cards": len(knowledge.cards.all()), "llm": llm.is_available(), "llm_info": llm.status(),
            "stt": speech.stt_available(), "tts": speech.tts_available(), "telegram": notifier.enabled()}
