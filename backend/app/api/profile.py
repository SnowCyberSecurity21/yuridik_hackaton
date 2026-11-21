"""«Mening huquqlarim» API: MyGov (OneID) orqali kirish — hozircha MOCK (3 ta soxta profil).

Foydalanuvchi kaliti:
- Telegram Mini App: `X-Telegram-Init-Data` sarlavhasi (bot tokeni bilan HMAC tekshiriladi) -> Telegram user id
- Bot (server -> server): raqamli chat_id + `X-Internal-Token` (INTERNAL_API_TOKEN bo'sh bo'lsa — demo rejim)
- Oddiy brauzer: `web:<tasodifiy-id>` (Telegram chat_id nomidan ish ko'rib bo'lmaydi)
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import time
from datetime import date, datetime
from datetime import time as dtime
from urllib.parse import parse_qsl

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models import Reminder
from ..services import analytics, appeal, knowledge, notifier
from ..services import profile as profile_svc
from ..services.i18n import t

router = APIRouter(prefix="/api/profile", tags=["profile"])

WEB_KEY = re.compile(r"^web:[A-Za-z0-9_-]{8,64}$")
INIT_DATA_MAX_AGE = 24 * 3600


def verify_init_data(init_data: str, bot_token: str) -> int | None:
    """Telegram WebApp initData imzosini tekshirish (rasmiy algoritm: HMAC-SHA256, kalit = HMAC("WebAppData", token))."""
    if not bot_token or not init_data:
        return None
    try:
        pairs = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=True))
    except ValueError:
        return None
    received = pairs.pop("hash", "")
    check = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    calc = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    if not received or not hmac.compare_digest(calc, received):
        return None
    try:
        if time.time() - int(pairs.get("auth_date", "0")) > INIT_DATA_MAX_AGE:
            return None
        return int(json.loads(pairs.get("user", "{}"))["id"])
    except (ValueError, KeyError, TypeError):
        return None


def resolve_user(user_key: str | None, init_data: str | None, internal_token: str | None) -> str:
    s = get_settings()
    if init_data:
        uid = verify_init_data(init_data, s.telegram_bot_token)
        if uid is None:
            raise HTTPException(401, "Telegram initData tasdiqlanmadi")
        return str(uid)
    key = (user_key or "").strip()
    if WEB_KEY.match(key):
        return key
    if key.lstrip("-").isdigit():
        if s.internal_api_token and not hmac.compare_digest(internal_token or "", s.internal_api_token):
            raise HTTPException(401, "ichki token noto'g'ri")
        return key
    raise HTTPException(400, "user_key noto'g'ri (raqamli chat_id yoki web:<id>)")


def current_user(user_key: str | None = Query(None), x_telegram_init_data: str | None = Header(None),
                 x_internal_token: str | None = Header(None)) -> str:
    return resolve_user(user_key, x_telegram_init_data, x_internal_token)


class UserIn(BaseModel):
    user_key: str | None = None
    lang: str = "uz"


def body_user(body: UserIn, x_telegram_init_data: str | None, x_internal_token: str | None) -> str:
    return resolve_user(body.user_key, x_telegram_init_data, x_internal_token)


# ------------------------------------------------------------------ endpointlar

@router.get("/demo-profiles")
def demo_profiles(lang: str = "uz"):
    """Kirish ekrani uchun: soxta profillar ro'yxati va rozilik doirasi."""
    return {
        "is_mock": True,
        "consent_text": t(lang, "pf_consent"),
        "consent_scope": profile_svc.CONSENT_SCOPE,
        "profiles": [{"id": p["id"], "icon": p.get("icon", "👤"), "display_name": p.get("display_name"),
                      "persona": p.get("persona_ru") if lang == "ru" else p.get("persona_uz"),
                      "region_name": profile_svc.REGION_NAME.get(p.get("region"))}
                     for p in knowledge.mock_profiles().values()],
    }


class LoginIn(UserIn):
    profile_id: str
    consent: bool = Field(False, description="Foydalanuvchi rozilik berdimi (majburiy)")
    channel: str = "telegram"


@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db), x_telegram_init_data: str | None = Header(None),
          x_internal_token: str | None = Header(None)):
    key = body_user(body, x_telegram_init_data, x_internal_token)
    if not body.consent:
        raise HTTPException(400, t(body.lang, "pf_need_consent"))
    if body.profile_id not in knowledge.mock_profiles():
        raise HTTPException(404, "profil topilmadi")
    profile_svc.link(db, key, body.profile_id, lang=body.lang, channel=body.channel)
    return {"linked": True, "user_key": key, **profile_svc.view(db, body.profile_id, body.lang)}


@router.get("/me")
def me(lang: str = "uz", key: str = Depends(current_user), db: Session = Depends(get_db)):
    pid = profile_svc.linked_profile_id(db, key)
    if not pid:
        return {"linked": False, "user_key": key}
    v = profile_svc.view(db, pid, lang)
    if v is None:  # profil fayli o'chirilgan bo'lsa
        profile_svc.unlink(db, key)
        return {"linked": False, "user_key": key}
    return {"linked": True, "user_key": key, **v}


@router.post("/logout")
def logout(body: UserIn, db: Session = Depends(get_db), x_telegram_init_data: str | None = Header(None),
           x_internal_token: str | None = Header(None)):
    key = body_user(body, x_telegram_init_data, x_internal_token)
    return {"ok": profile_svc.unlink(db, key), "text": t(body.lang, "pf_logged_out")}


class BenefitAppealIn(UserIn):
    benefit_id: str
    channel: str = "telegram"


@router.post("/appeal")
async def benefit_appeal(body: BenefitAppealIn, db: Session = Depends(get_db),
                         x_telegram_init_data: str | None = Header(None), x_internal_token: str | None = Header(None)):
    key = body_user(body, x_telegram_init_data, x_internal_token)
    pid = profile_svc.linked_profile_id(db, key)
    if not pid:
        raise HTTPException(409, "Avval MyGov (OneID) orqali kiring")
    prof = knowledge.mock_profiles()[pid]
    res = await appeal.generate_for_benefit(body.benefit_id, prof, body.lang)
    if res is None:
        raise HTTPException(404, "imtiyoz topilmadi yoki profilingizga mos emas")
    benefit = knowledge.benefits()[body.benefit_id]
    eid = analytics.log_event(db, kind="appeal", topic_id=benefit.get("related_card_id") or body.benefit_id,
                              region=prof.get("region"), lang=body.lang, channel=body.channel)
    if eid:
        analytics.feedback(db, eid, appeal=True)
    return res


class RemindIn(UserIn):
    obligation_id: str


@router.post("/remind")
def remind(body: RemindIn, db: Session = Depends(get_db), x_telegram_init_data: str | None = Header(None),
           x_internal_token: str | None = Header(None)):
    key = body_user(body, x_telegram_init_data, x_internal_token)
    pid = profile_svc.linked_profile_id(db, key)
    if not pid:
        raise HTTPException(409, "Avval MyGov (OneID) orqali kiring")
    obs = profile_svc.obligations_of(knowledge.mock_profiles()[pid], date.today(), body.lang)
    ob = next((o for o in obs if o["id"] == body.obligation_id), None)
    if not ob or not ob["reminder_date"]:
        raise HTTPException(404, "muddatli majburiyat topilmadi")
    deadline = ob["discount_deadline"] or ob["deadline"]
    dl = date.fromisoformat(deadline).strftime("%d.%m.%Y")
    what = (f"chegirma bilan {ob['discount_amount']:,} so'm".replace(",", " ") if ob["discount_deadline"]
            else ob["amount_text"])
    text = f"⏰ Eslatma: «{ob['title']}» — {dl} gacha ({what})."
    remind_on = date.fromisoformat(ob["reminder_date"])
    db.add(Reminder(chat_id=key, remind_at=datetime.combine(remind_on, dtime(9, 0)), text=text))
    db.commit()
    return {"ok": True, "text": t(body.lang, "reminder_set", date=remind_on.strftime("%d.%m.%Y")),
            "telegram_enabled": notifier.enabled()}
