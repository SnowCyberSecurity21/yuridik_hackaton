"""Huquqim hisobi, OneID (demo) orqali tasdiqlash, kabinet, Telegram ulash, anonim huquqlar, davlat va ta'lim kabinetlari."""
from __future__ import annotations

import hmac
import time
from datetime import date, datetime
from datetime import time as dtime
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models import Account, Reminder
from ..oneid_demo import service as oneid
from ..services import accounts, analytics, appeal, cabinet, changes, edu, knowledge, notifier, outreach, rights
from ..services import profile as profile_svc
from ..services.security import RateLimiter, client_ip
from .profile import verify_init_data

router = APIRouter(tags=["account"])
COOKIE = "hq_sid"
login_ip_limiter = RateLimiter(20, 300)
login_user_limiter = RateLimiter(8, 300)
register_limiter = RateLimiter(10, 3600)
link_limiter = RateLimiter(10, 600)
_sim_last = {"t": 0.0}


# ------------------------------------------------------------------ yordamchilar

def _secure(request: Request) -> bool:
    return request.url.scheme == "https"


def _set_cookie(resp, request: Request, tok: str) -> None:
    resp.set_cookie(COOKIE, tok, max_age=7 * 24 * 3600, httponly=True, samesite="lax", secure=_secure(request), path="/")


def session_account(request: Request, db: Session) -> Account | None:
    return accounts.account_by_session(db, request.cookies.get(COOKIE))


def any_account(request: Request, db: Session, init_data: str | None) -> Account | None:
    """Web: sessiya cookie. Mini App: Telegram initData -> ulangan hisob."""
    acc = session_account(request, db)
    if acc:
        return acc
    if init_data:
        uid = verify_init_data(init_data, get_settings().telegram_bot_token)
        if uid is None:
            raise HTTPException(401, "Telegram initData tasdiqlanmadi")
        return accounts.account_by_chat(db, str(uid))
    return None


def require_internal(x_internal_token: str | None) -> None:
    tok = get_settings().internal_api_token
    if tok and not hmac.compare_digest(x_internal_token or "", tok):
        raise HTTPException(401, "ichki token noto'g'ri")


def _verified(db: Session, acc: Account | None) -> tuple[Account, dict, list[str]]:
    if not acc:
        raise HTTPException(401, "Avval Huquqim hisobingizga kiring")
    person = accounts.person_of(db, acc)
    if not person:
        raise HTTPException(409, "Hisob OneID (demo) orqali tasdiqlanmagan")
    return acc, person, accounts.roles_of(acc, person)


def _me_payload(db: Session, acc: Account | None) -> dict:
    if not acc:
        return {"logged_in": False}
    person = accounts.person_of(db, acc)
    tg = accounts.telegram_of(db, acc)
    return {"logged_in": True, "username": acc.username, "verified": person is not None,
            "roles": accounts.roles_of(acc, person), "telegram_linked": tg is not None,
            "consent_at": acc.oneid_linked_at.isoformat() if acc.oneid_linked_at else None,
            "consent_scope": [oneid.SCOPE_LABELS_UZ.get(s, s) for s in (acc.consent_scope or [])],
            "first_name": (person or {}).get("first_name"), "icon": (person or {}).get("icon")}


# ------------------------------------------------------------------ ro'yxatdan o'tish / kirish

class Creds(BaseModel):
    username: str = Field(..., max_length=40)
    password: str = Field(..., max_length=128)


@router.post("/api/auth/register")
def register(body: Creds, request: Request, db: Session = Depends(get_db)):
    if not register_limiter.hit(client_ip(request)):
        raise HTTPException(429, "Juda ko'p urinish. Keyinroq qayta urinib ko'ring.")
    try:
        acc = accounts.register(db, body.username, body.password)
    except accounts.AuthError as e:
        raise HTTPException(400, str(e)) from e
    from fastapi.responses import JSONResponse
    resp = JSONResponse(_me_payload(db, acc))
    _set_cookie(resp, request, accounts.create_session(db, acc))
    return resp


@router.post("/api/auth/login")
def login(body: Creds, request: Request, db: Session = Depends(get_db)):
    if not login_ip_limiter.hit(client_ip(request)) or not login_user_limiter.hit(body.username.strip().lower()):
        raise HTTPException(429, "Juda ko'p urinish. 5 daqiqadan keyin qayta urinib ko'ring.")
    acc = accounts.authenticate(db, body.username, body.password)
    if not acc:
        raise HTTPException(401, "Login yoki parol noto'g'ri")
    from fastapi.responses import JSONResponse
    resp = JSONResponse(_me_payload(db, acc))
    _set_cookie(resp, request, accounts.create_session(db, acc))
    return resp


@router.post("/api/auth/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    accounts.end_session(db, request.cookies.get(COOKIE))
    from fastapi.responses import JSONResponse
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(COOKIE, path="/")
    return resp


@router.get("/api/auth/me")
def me(request: Request, db: Session = Depends(get_db), x_telegram_init_data: str | None = Header(None)):
    return _me_payload(db, any_account(request, db, x_telegram_init_data))


# ------------------------------------------------------------------ OneID (demo) oqimi

@router.get("/api/oneid/start", include_in_schema=False)
def oneid_start(request: Request, db: Session = Depends(get_db)):
    tok = request.cookies.get(COOKIE)
    if not accounts.session_row(db, tok):
        return RedirectResponse("/kirish?next=oneid", status_code=303)
    state = accounts.start_oneid(db, tok)
    q = urlencode({"client_id": "huquqim", "redirect_uri": "/api/oneid/callback", "state": state, "scope": " ".join(oneid.SCOPE)})
    return RedirectResponse(f"/oneid-demo/authorize?{q}", status_code=303)


@router.get("/api/oneid/callback", include_in_schema=False)
def oneid_callback(request: Request, code: str = "", state: str = "", error: str = "", db: Session = Depends(get_db)):
    tok = request.cookies.get(COOKIE)
    if error:
        row = accounts.session_row(db, tok)
        if row:
            row.oneid_state = None
            db.commit()
        return RedirectResponse("/kabinet?oneid=denied", status_code=303)
    acc = accounts.finish_oneid(db, tok, code, state)
    if not acc:
        return RedirectResponse("/kabinet?oneid=error", status_code=303)
    return RedirectResponse("/kabinet?oneid=ok", status_code=303)


@router.post("/api/oneid/revoke")
def oneid_revoke(request: Request, db: Session = Depends(get_db)):
    acc = session_account(request, db)
    if not acc:
        raise HTTPException(401, "Avval kiring")
    ok = accounts.revoke_oneid(db, acc)
    return {"ok": ok, "text": "Rozilik bekor qilindi: OneID (demo) bilan bog'lanish uzildi. Shaxsiy ma'lumot saqlanmagan."}


# ------------------------------------------------------------------ kabinet

@router.get("/api/me/cabinet")
def my_cabinet(request: Request, lang: str = "uz", db: Session = Depends(get_db),
               x_telegram_init_data: str | None = Header(None)):
    acc, person, roles = _verified(db, any_account(request, db, x_telegram_init_data))
    v = cabinet.view(db, person, roles, lang)
    v["telegram_linked"] = accounts.telegram_of(db, acc) is not None
    return v


class BenefitIn(BaseModel):
    benefit_id: str
    lang: str = "uz"


async def _appeal(db: Session, person: dict, benefit_id: str, lang: str, channel: str) -> dict:
    prof = cabinet.as_profile(person)
    res = await appeal.generate_for_benefit(benefit_id, prof, lang)
    if res is None:
        raise HTTPException(404, "imtiyoz topilmadi yoki sizga mos emas")
    benefit = knowledge.benefits()[benefit_id]
    note = cabinet.STATUS_BENEFIT_NOTE.get(cabinet.person_status(person))
    if note:
        res["to_check"] = list(res.get("to_check") or []) + [note]
    eid = analytics.log_event(db, kind="appeal", topic_id=benefit.get("related_card_id") or benefit_id,
                              region=person.get("region"), lang=lang, channel=channel)
    if eid:
        analytics.feedback(db, eid, appeal=True)
    return res


@router.post("/api/me/appeal")
async def my_appeal(body: BenefitIn, request: Request, db: Session = Depends(get_db),
                    x_telegram_init_data: str | None = Header(None)):
    _, person, _ = _verified(db, any_account(request, db, x_telegram_init_data))
    return await _appeal(db, person, body.benefit_id, body.lang, "miniapp" if x_telegram_init_data else "web")


class ObligationIn(BaseModel):
    obligation_id: str
    lang: str = "uz"


def _remind(db: Session, acc: Account, person: dict, obligation_id: str, lang: str) -> dict:
    obs = profile_svc.obligations_of(cabinet.as_profile(person), date.today(), lang)
    ob = next((o for o in obs if o["id"] == obligation_id), None)
    if not ob or not ob["reminder_date"]:
        raise HTTPException(404, "muddatli majburiyat topilmadi")
    tg = accounts.telegram_of(db, acc)
    deadline = date.fromisoformat(ob["discount_deadline"] or ob["deadline"]).strftime("%d.%m.%Y")
    what = (f"chegirma bilan {ob['discount_amount']:,} so'm".replace(",", " ") if ob["discount_deadline"] else ob["amount_text"])
    remind_on = date.fromisoformat(ob["reminder_date"])
    if tg:
        db.add(Reminder(chat_id=tg.chat_id, remind_at=datetime.combine(remind_on, dtime(9, 0)),
                        text=f"⏰ Eslatma: «{ob['title']}» — {deadline} gacha ({what})."))
        db.commit()
    return {"ok": True, "telegram_linked": tg is not None,
            "text": (f"⏰ {remind_on.strftime('%d.%m.%Y')} kuni Telegram'da eslatamiz." if tg
                     else "Eslatma Telegram orqali keladi — avval kabinetda «Telegram'ni ulash» tugmasini bosing.")}


@router.post("/api/me/remind")
def my_remind(body: ObligationIn, request: Request, db: Session = Depends(get_db),
              x_telegram_init_data: str | None = Header(None)):
    acc, person, _ = _verified(db, any_account(request, db, x_telegram_init_data))
    return _remind(db, acc, person, body.obligation_id, body.lang)


@router.post("/api/me/telegram/link")
def tg_link(request: Request, db: Session = Depends(get_db)):
    acc = session_account(request, db)
    if not acc:
        raise HTTPException(401, "Avval kiring")
    if not link_limiter.hit(str(acc.id)):
        raise HTTPException(429, "Juda ko'p so'rov. Birozdan keyin urinib ko'ring.")
    tok = accounts.create_link_token(db, acc)
    return {"url": accounts.deep_link(tok), "expires_in": int(accounts.LINK_TTL.total_seconds())}


@router.post("/api/me/telegram/unlink")
def tg_unlink(request: Request, db: Session = Depends(get_db)):
    acc = session_account(request, db)
    if not acc:
        raise HTTPException(401, "Avval kiring")
    return {"ok": accounts.unlink_telegram(db, acc)}


# ------------------------------------------------------------------ bot (server -> server)

class ChatIn(BaseModel):
    chat_id: str = Field(..., pattern=r"^-?\d{1,20}$")
    lang: str = "uz"


class LinkIn(ChatIn):
    token: str = Field(..., max_length=80)


@router.post("/api/bot/link")
def bot_link(body: LinkIn, db: Session = Depends(get_db), x_internal_token: str | None = Header(None)):
    require_internal(x_internal_token)
    acc = accounts.consume_link_token(db, body.token, body.chat_id)
    if not acc:
        return {"ok": False, "text": "Havola yaroqsiz yoki muddati o'tgan (10 daqiqa, bir martalik). Kabinetdan yangisini oling."}
    return {"ok": True, **_bot_me(db, acc)}


def _bot_me(db: Session, acc: Account | None) -> dict:
    if not acc:
        return {"linked": False}
    person = accounts.person_of(db, acc)
    if not person:
        return {"linked": True, "verified": False, "username": acc.username}
    return {"linked": True, "verified": True, "username": acc.username, "first_name": person.get("first_name"),
            "status": cabinet.person_status(person), "situations": cabinet.person_situations(person),
            "roles": accounts.roles_of(acc, person)}


@router.get("/api/bot/me")
def bot_me(chat_id: str, db: Session = Depends(get_db), x_internal_token: str | None = Header(None)):
    require_internal(x_internal_token)
    return _bot_me(db, accounts.account_by_chat(db, chat_id))


@router.get("/api/bot/section")
def bot_section(chat_id: str, section: str, lang: str = "uz", db: Session = Depends(get_db),
                x_internal_token: str | None = Header(None)):
    require_internal(x_internal_token)
    acc, person, roles = _verified(db, accounts.account_by_chat(db, chat_id))
    v = cabinet.view(db, person, roles, lang)
    return {"text": cabinet.section_text(v, section),
            "benefits": [{"id": b["id"], "label": b["appeal_label"]} for b in v["benefits"]] if section == "benefits" else [],
            "obligations": [{"id": o["id"], "title": o["title"]} for o in v["obligations"] if o.get("reminder_date")]
            if section == "obligations" else []}


@router.post("/api/bot/unlink")
def bot_unlink(body: ChatIn, db: Session = Depends(get_db), x_internal_token: str | None = Header(None)):
    require_internal(x_internal_token)
    acc = accounts.account_by_chat(db, body.chat_id)
    return {"ok": accounts.unlink_telegram(db, acc) if acc else False}


class BotBenefitIn(ChatIn):
    benefit_id: str


@router.post("/api/bot/appeal")
async def bot_appeal(body: BotBenefitIn, db: Session = Depends(get_db), x_internal_token: str | None = Header(None)):
    require_internal(x_internal_token)
    _, person, _ = _verified(db, accounts.account_by_chat(db, body.chat_id))
    return await _appeal(db, person, body.benefit_id, body.lang, "telegram")


class BotObligationIn(ChatIn):
    obligation_id: str


@router.post("/api/bot/remind")
def bot_remind(body: BotObligationIn, db: Session = Depends(get_db), x_internal_token: str | None = Header(None)):
    require_internal(x_internal_token)
    acc, person, _ = _verified(db, accounts.account_by_chat(db, body.chat_id))
    return _remind(db, acc, person, body.obligation_id, body.lang)


# ------------------------------------------------------------------ anonim: maqom va holat bo'yicha huquqlar

@router.get("/api/rights/meta")
def rights_meta():
    return {"statuses": rights.statuses(), "situations": rights.situations(rights.ANON_SITUATIONS)}


@router.get("/api/rights")
def rights_view(status: str = "unknown", situations: str = ""):
    """Anonim: hech narsa saqlanmaydi (parametrlar faqat so'rov ichida)."""
    sits = [s for s in situations.split(",") if s in rights.SITUATION_IDS][:5]
    st = rights.status_view(status) or rights.status_view("unknown")
    return {"status": st, "situations": rights.situation_views(sits), "laws": rights.laws_for(st["id"], sits),
            "text": rights.rights_text(st["id"], sits), "laws_text": rights.laws_text(st["id"], sits),
            "note": "Sodda izoh — huquqiy xulosa emas. Rasmiy manba — qonun hujjatining o'zi."}


@router.get("/api/laws")
def all_laws():
    return [rights.law_public(x) for x in rights.laws().values()]


# ------------------------------------------------------------------ davlat kabineti (Dilnoza: gov whitelist)

def _gov(request: Request, db: Session) -> Account:
    acc, person, roles = _verified(db, session_account(request, db))
    if "gov" not in roles:
        raise HTTPException(403, "Davlat kabineti faqat admin ro'yxatidagi xodimlar uchun")
    return acc


def _cards() -> dict[str, dict]:
    return {c["id"]: c for c in knowledge.cards.all()}


@router.get("/api/cabinet/gov/overview")
def gov_overview(request: Request, db: Session = Depends(get_db)):
    _gov(request, db)
    return analytics.overview(db, _cards())


@router.get("/api/cabinet/gov/topics")
def gov_topics(request: Request, limit: int = 10, db: Session = Depends(get_db)):
    _gov(request, db)
    return analytics.top_topics(db, _cards(), limit)


@router.get("/api/cabinet/gov/regions")
def gov_regions(request: Request, topic_id: str | None = None, db: Session = Depends(get_db)):
    _gov(request, db)
    return analytics.by_region(db, topic_id)


@router.get("/api/cabinet/gov/trend")
def gov_trend(request: Request, days: int = 28, topic_id: str | None = None, db: Session = Depends(get_db)):
    _gov(request, db)
    return analytics.trend(db, days, topic_id)


@router.get("/api/cabinet/gov/signals")
def gov_signals(request: Request, db: Session = Depends(get_db)):
    _gov(request, db)
    return analytics.signals(db, knowledge.claims(), _cards())


class ContentIn(BaseModel):
    topic_id: str


@router.post("/api/cabinet/gov/content")
async def gov_content(body: ContentIn, request: Request, db: Session = Depends(get_db)):
    _gov(request, db)
    card = knowledge.cards.get(body.topic_id)
    if not card:
        raise HTTPException(404, "mavzu topilmadi")
    return await outreach.generate(card)


@router.get("/api/cabinet/gov/changes")
def gov_changes(request: Request, db: Session = Depends(get_db)):
    _gov(request, db)
    return changes.list_changes(db)


@router.get("/api/cabinet/gov/profiles")
def gov_profiles(request: Request, db: Session = Depends(get_db)):
    """Demo shaxslar va ularga ulangan (tasdiqlangan + Telegram) hisoblar soni."""
    _gov(request, db)
    from ..models import TelegramLink
    counts: dict[str, int] = {}
    for link in db.query(TelegramLink).all():
        a = db.get(Account, link.account_id)
        if a and a.oneid_sub:
            counts[a.oneid_sub] = counts.get(a.oneid_sub, 0) + 1
    out = []
    for p in oneid.persons_file():
        eligible, _ = profile_svc.benefits_of(cabinet.as_profile(p))
        out.append({"profile_id": p["sub"], "icon": p.get("icon"), "persona": p.get("persona_uz"),
                    "linked_users": counts.get(p["sub"], 0), "benefits": [b["title"] for b in eligible],
                    "refs": sorted(profile_svc.relevant_refs(cabinet.as_profile(p)))})
    return out


class SimulateIn(BaseModel):
    change_id: str | None = None


@router.post("/api/cabinet/gov/simulate-amendment")
async def gov_simulate(request: Request, body: SimulateIn | None = None, db: Session = Depends(get_db)):
    """XAVFSIZLIK: parollar ommaga ma'lum — xabar FAQAT demo ID hisoblari va ularga ulangan chatlarga, cheklov bilan."""
    _gov(request, db)
    now = time.monotonic()
    cooldown = get_settings().sim_cooldown_s
    if now - _sim_last["t"] < cooldown:
        raise HTTPException(429, f"Simulyatsiya {cooldown} soniyada 1 marta. Biroz kuting.")
    _sim_last["t"] = now
    res = await changes.apply_change(db, body.change_id if body else None, audience="demo")
    if res is None:
        raise HTTPException(409, "Barcha o'zgarishlar allaqachon qo'llangan — «Demo'ni tiklash»ni bosing")
    ref = res["change"].get("ref_id")
    res["profiles"] = [{"profile_id": p["sub"], "icon": p.get("icon"), "persona": p.get("persona_uz"),
                        "reason": (r := profile_svc.relevant_refs(cabinet.as_profile(p)).get(ref)), "affected": r is not None}
                       for p in oneid.persons_file()]
    return res


@router.post("/api/cabinet/gov/reset-demo")
def gov_reset(request: Request, db: Session = Depends(get_db)):
    _gov(request, db)
    changes.reset_demo(db)
    return {"ok": True}


# ------------------------------------------------------------------ ta'lim (Azizbek: talaba)

def _student(request: Request, db: Session) -> None:
    _, _, roles = _verified(db, session_account(request, db))
    if "student" not in roles:
        raise HTTPException(403, "Ta'lim bo'limi talabalar uchun")


@router.get("/api/edu/textbook")
def edu_textbook(request: Request, db: Session = Depends(get_db)):
    _student(request, db)
    from ..models import TextbookChunk
    rows = db.query(TextbookChunk).order_by(TextbookChunk.id).all()
    return [{"id": r.id, "textbook": r.textbook_title, "title": r.title, "text": r.text, "refs": r.refs,
             "status": r.status, "change_id": r.change_id, "diff": r.diff, "suggested_text": r.suggested_text} for r in rows]


@router.get("/api/edu/cases")
def edu_cases(request: Request, db: Session = Depends(get_db)):
    _student(request, db)
    return edu.cases()


class SimIn(BaseModel):
    card_id: str
    history: list[dict] = Field(default_factory=list, max_length=40)


@router.post("/api/edu/sim/start")
def edu_sim_start(body: SimIn, request: Request, db: Session = Depends(get_db)):
    _student(request, db)
    res = edu.start(body.card_id)
    if not res:
        raise HTTPException(404, "holat topilmadi")
    return res


@router.post("/api/edu/sim/reply")
async def edu_sim_reply(body: SimIn, request: Request, db: Session = Depends(get_db)):
    _student(request, db)
    res = await edu.reply(body.card_id, body.history)
    if not res:
        raise HTTPException(404, "holat topilmadi")
    return res


@router.post("/api/edu/sim/score")
def edu_sim_score(body: SimIn, request: Request, db: Session = Depends(get_db)):
    _student(request, db)
    res = edu.score(body.card_id, body.history)
    if not res:
        raise HTTPException(404, "holat topilmadi")
    return res


class DocIn(BaseModel):
    card_id: str | None = None
    text: str = Field(..., max_length=8000)


@router.post("/api/edu/trainer/check")
def edu_trainer(body: DocIn, request: Request, db: Session = Depends(get_db)):
    _student(request, db)
    return edu.check_document(body.card_id, body.text)
