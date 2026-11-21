"""Telegram handlerlari: matn, ovoz, SMS, forward qilingan post, tugmalar."""
from __future__ import annotations

import logging
from collections import OrderedDict
from urllib.parse import quote

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import (BufferedInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message,
                           WebAppInfo)
from aiogram.utils.keyboard import InlineKeyboardBuilder

import backend_client as api
from config import settings
from texts import tr

log = logging.getLogger("javob.bot")
router = Router()


class LRU(OrderedDict):
    def __init__(self, cap: int = 2000):
        super().__init__()
        self.cap = cap

    def put(self, k, v):
        self[k] = v
        self.move_to_end(k)
        while len(self) > self.cap:
            self.popitem(last=False)


# Xotiradagi holat (shaxsiy ma'lumotsiz): hudud, til, oxirgi javoblar
user_region: dict[int, str | None] = {}
user_lang: dict[int, str] = {}
awaiting_factcheck: set[int] = set()
answers: LRU = LRU()  # event_id -> {"text","lang","card_id","parsed"}
BOT_USERNAME: str | None = None


# ------------------------------------------------------------------ klaviaturalar

def answer_keyboard(res: dict) -> InlineKeyboardMarkup:
    lang = res.get("lang", "uz")
    eid = res.get("event_id") or 0
    card = res.get("card_id") or ""
    actions = {b["action"] for b in res.get("buttons", [])}
    kb = InlineKeyboardBuilder()
    if "audio" in actions:
        kb.button(text=tr(lang, "btn_audio"), callback_data=f"a:{eid}")
    if "source" in actions and card:
        kb.button(text=tr(lang, "btn_source"), callback_data=f"s:{card}")
    if "ok" in actions:
        kb.button(text=tr(lang, "btn_ok"), callback_data=f"k:{eid}")
    if "disagree" in actions and card:
        kb.button(text=tr(lang, "btn_disagree"), callback_data=f"d:{card}:{eid}")
    if "remind" in actions and (res.get("parsed") or {}).get("reminder_date"):
        kb.button(text=tr(lang, "btn_remind"), callback_data=f"r:{eid}")
    if "subscribe" in actions and card:
        kb.button(text=tr(lang, "btn_subscribe"), callback_data=f"u:{card}")
    if "share" in actions:
        share_text = res.get("title") or (res.get("text", "").splitlines() or [""])[0]
        link = f"https://t.me/{BOT_USERNAME}" if BOT_USERNAME else "https://lex.uz"
        kb.button(text=tr(lang, "btn_share"),
                  url=f"https://t.me/share/url?url={quote(link)}&text={quote(share_text[:200])}")
    if settings.webapp_url:
        kb.button(text=tr(lang, "btn_miniapp"), web_app=WebAppInfo(url=settings.webapp_url))
    kb.adjust(2)
    return kb.as_markup()


async def region_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for r in await api.regions():
        kb.button(text=r["name"], callback_data=f"reg:{r['id']}")
    kb.button(text=tr(lang, "skip"), callback_data="reg:skip")
    kb.adjust(2)
    return kb.as_markup()


# ------------------------------------------------------------------ yordamchi

async def send_answer(message: Message, res: dict | None) -> None:
    uid = message.from_user.id if message.from_user else 0
    lang = (res or {}).get("lang") or user_lang.get(uid, "uz")
    if not res or "text" not in res:
        await message.answer(tr(lang, "error_generic"))
        return
    user_lang[uid] = lang
    if res.get("event_id"):
        answers.put(res["event_id"], {"text": res["text"], "lang": lang, "card_id": res.get("card_id"),
                                      "parsed": res.get("parsed")})
    await message.answer(res["text"], reply_markup=answer_keyboard(res), disable_web_page_preview=True)


# ------------------------------------------------------------------ buyruqlar

@router.message(CommandStart())
async def start(message: Message):
    lang = user_lang.get(message.from_user.id, "uz")
    await message.answer(tr(lang, "welcome", app=settings.app_name))
    await message.answer(tr(lang, "ask_region"), reply_markup=await region_keyboard(lang))


@router.message(Command("region"))
async def cmd_region(message: Message):
    lang = user_lang.get(message.from_user.id, "uz")
    await message.answer(tr(lang, "ask_region"), reply_markup=await region_keyboard(lang))


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(tr(user_lang.get(message.from_user.id, "uz"), "help"))


@router.message(Command("tekshir"))
async def cmd_check(message: Message, command: CommandObject):
    uid = message.from_user.id
    if command.args:
        res = await api.ask(command.args, region=user_region.get(uid), mode="factcheck")
        await send_answer(message, res)
    else:
        awaiting_factcheck.add(uid)
        await message.answer("🕵️ Tekshiriladigan post matnini yuboring yoki postni forward qiling.")


# ------------------------------------------------------------------ «Mening huquqlarim» (MyGov/OneID — DEMO)

def _ukey(chat_id: int) -> str:
    return str(chat_id)


async def login_keyboard(lang: str) -> tuple[str, InlineKeyboardMarkup]:
    data = await api.demo_profiles(lang) or {}
    kb = InlineKeyboardBuilder()
    for p in data.get("profiles", []):
        kb.button(text=f"{p['icon']} {p['persona']} — {p['display_name']}", callback_data=f"p:in:{p['id']}")
    kb.adjust(1)
    text = tr(lang, "pf_login_intro") + "\n\n" + (data.get("consent_text") or tr(lang, "pf_consent"))
    return text, kb.as_markup()


def profile_keyboard(v: dict, lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for b in v.get("benefits", []):
        kb.button(text=f"📝 {b['appeal_label']}", callback_data=f"pb:{b['id']}")
    for o in v.get("obligations", []):
        if o.get("reminder_date"):
            short = o["title"].split(" — ")[0].split(" (")[0][:28]
            kb.button(text=f"{tr(lang, 'btn_pf_remind')}: {short}", callback_data=f"po:{o['id']}")
    if settings.webapp_url:
        kb.button(text=tr(lang, "btn_pf_open"), web_app=WebAppInfo(url=settings.webapp_url))
    kb.button(text=tr(lang, "btn_pf_switch"), callback_data="p:switch")
    kb.button(text=tr(lang, "btn_pf_logout"), callback_data="p:out")
    kb.adjust(1)
    return kb.as_markup()


async def show_profile(message: Message, chat_id: int, lang: str) -> None:
    v = await api.profile_me(_ukey(chat_id), lang)
    if v is None:
        await message.answer(tr(lang, "error_generic"))
        return
    if not v.get("linked"):
        text, kb = await login_keyboard(lang)
        await message.answer(text, reply_markup=kb)
        return
    await message.answer(v["text"], reply_markup=profile_keyboard(v, lang), disable_web_page_preview=True)


async def login_command(arg: str | None, chat_id: int, lang: str) -> tuple[str, InlineKeyboardMarkup | None]:
    """/login [profil_id] — CLI'dagi kabi: faqat knowledge/mock_profiles dagi demo profillar.

    Argumentsiz — profil tugmalari. Noma'lum id — "Bunday demo profil yo'q" + tugmalar.
    To'g'ri id — rozilik qayd etiladi (backend ProfileLink) va profil ko'rsatiladi.
    """
    arg = (arg or "").strip()
    if not arg:
        return await login_keyboard(lang)
    data = await api.demo_profiles(lang)
    if data is None:
        return tr(lang, "error_generic"), None
    if arg not in {p["id"] for p in data.get("profiles", [])}:
        _, kb = await login_keyboard(lang)
        return tr(lang, "pf_no_such_profile"), kb
    v = await api.profile_post("login", {"user_key": _ukey(chat_id), "profile_id": arg, "consent": True,
                                         "lang": lang, "channel": "telegram"})
    if not v:
        return tr(lang, "error_generic"), None
    return tr(lang, "pf_consent_recorded") + "\n\n" + v["text"], profile_keyboard(v, lang)


async def logout_command(chat_id: int, lang: str) -> str:
    res = await api.profile_post("logout", {"user_key": _ukey(chat_id), "lang": lang})
    if not res:
        return tr(lang, "error_generic")
    return res["text"] if res.get("ok") else tr(lang, "pf_not_linked")


@router.message(Command("login"))
async def cmd_login(message: Message, command: CommandObject):
    text, kb = await login_command(command.args, message.chat.id, user_lang.get(message.from_user.id, "uz"))
    await message.answer(text, reply_markup=kb, disable_web_page_preview=True)


@router.message(Command("chiqish", "logout"))
async def cmd_logout(message: Message):
    await message.answer(await logout_command(message.chat.id, user_lang.get(message.from_user.id, "uz")))


@router.message(Command("profilim", "profil", "huquqlarim"))
async def cmd_profile(message: Message):
    await show_profile(message, message.chat.id, user_lang.get(message.from_user.id, "uz"))


@router.callback_query(F.data.startswith("p:"))
async def cb_profile(cb: CallbackQuery):
    lang = user_lang.get(cb.from_user.id, "uz")
    key = _ukey(cb.message.chat.id)
    parts = cb.data.split(":")
    action = parts[1]
    if action == "in" and len(parts) == 3:
        # Profil tugmasini bosish = rozilik (matnda aniq aytilgan)
        v = await api.profile_post("login", {"user_key": key, "profile_id": parts[2], "consent": True, "lang": lang,
                                             "channel": "telegram"})
        await cb.answer()
        if not v:
            await cb.message.answer(tr(lang, "error_generic"))
            return
        await cb.message.answer(v["text"], reply_markup=profile_keyboard(v, lang), disable_web_page_preview=True)
    elif action == "switch":
        await cb.answer()
        text, kb = await login_keyboard(lang)
        await cb.message.answer(text, reply_markup=kb)
    elif action == "out":
        res = await api.profile_post("logout", {"user_key": key, "lang": lang})
        await cb.answer()
        await cb.message.answer((res or {}).get("text") or tr(lang, "error_generic"))
    else:
        await cb.answer()


@router.callback_query(F.data.startswith("pb:"))
async def cb_benefit_appeal(cb: CallbackQuery):
    lang = user_lang.get(cb.from_user.id, "uz")
    benefit_id = cb.data.split(":", 1)[1]
    await cb.answer("📝 ...")
    res = await api.profile_post("appeal", {"user_key": _ukey(cb.message.chat.id), "benefit_id": benefit_id,
                                            "lang": lang, "channel": "telegram"})
    if not res:
        await cb.message.answer(tr(lang, "error_generic"))
        return
    chans = " · ".join(f"{c['name']}: {c['url']}" for c in res.get("submit_channels", []))
    head = f"{res['header']} — {res.get('title', '')}\n{res['hint']}: {chans}"
    if res.get("to_check"):
        head += f"\n❔ {tr(lang, 'pf_to_check')}: " + "; ".join(res["to_check"])
    await cb.message.answer(head, disable_web_page_preview=True)
    await cb.message.answer(res["text"])


@router.callback_query(F.data.startswith("po:"))
async def cb_obligation_remind(cb: CallbackQuery):
    lang = user_lang.get(cb.from_user.id, "uz")
    res = await api.profile_post("remind", {"user_key": _ukey(cb.message.chat.id),
                                            "obligation_id": cb.data.split(":", 1)[1], "lang": lang})
    await cb.answer((res or {}).get("text") or tr(lang, "error_generic"), show_alert=True)


@router.message(F.voice | F.audio)
async def on_voice(message: Message, bot: Bot):
    uid = message.from_user.id
    lang = user_lang.get(uid, "uz")
    media = message.voice or message.audio
    try:
        buf = await bot.download(media)
        audio = buf.read() if buf else b""
    except Exception as e:  # noqa: BLE001
        log.warning("ovozni yuklab bo'lmadi: %s", e)
        audio = b""
    res = await api.ask_voice(audio, region=user_region.get(uid), legal_status=_legal(message)) if audio else None
    if not res or res.get("type") == "voice_unsupported":
        await message.answer((res or {}).get("text") or tr(lang, "voice_unsupported"))
        return
    if res.get("transcript"):
        await message.answer(f"{tr(res.get('lang'), 'voice_heard')}: «{res['transcript']}»")
    await send_answer(message, res)


@router.message(F.text | F.caption)
async def on_text(message: Message):
    uid = message.from_user.id
    text = message.text or message.caption or ""
    forwarded = message.forward_origin is not None
    mode = "auto"
    if forwarded or uid in awaiting_factcheck:
        mode = "factcheck"
        awaiting_factcheck.discard(uid)
    res = await api.ask(text, region=user_region.get(uid), mode=mode, legal_status=_legal(message))
    await send_answer(message, res)


def _legal(message: Message) -> str | None:
    import account_handlers
    return account_handlers.legal_status_of(message.chat.id)


# ------------------------------------------------------------------ tugmalar

@router.callback_query(F.data.startswith("reg:"))
async def cb_region(cb: CallbackQuery):
    rid = cb.data.split(":", 1)[1]
    user_region[cb.from_user.id] = None if rid == "skip" else rid
    lang = user_lang.get(cb.from_user.id, "uz")
    await cb.answer(tr(lang, "region_saved"))
    if cb.message:
        await cb.message.edit_text(tr(lang, "region_saved"))


@router.callback_query(F.data.startswith("a:"))
async def cb_audio(cb: CallbackQuery):
    eid = int(cb.data.split(":")[1] or 0)
    item = answers.get(eid)
    lang = (item or {}).get("lang", "uz")
    if not item:
        await cb.answer(tr(lang, "error_generic"), show_alert=True)
        return
    await cb.answer("🔊 ...")
    audio = await api.post_bytes("/api/tts", json={"text": item["text"], "lang": lang})
    if not audio:
        await cb.message.answer("🔇 Audio hozircha mavjud emas — matnli javobdan foydalaning.")
        return
    await cb.message.answer_audio(BufferedInputFile(audio, filename="javob.mp3"), title=settings.app_name)


@router.callback_query(F.data.startswith("s:"))
async def cb_source(cb: CallbackQuery):
    card_id = cb.data.split(":", 1)[1]
    lang = user_lang.get(cb.from_user.id, "uz")
    data = await api.card(card_id, lang)
    await cb.answer()
    if not data:
        await cb.message.answer(tr(lang, "error_generic"))
        return
    lines = [f"📚 {tr(lang, 'source')} [{data.get('badge', '')}]"]
    for s in data.get("sources", []):
        art = s.get("article") or ""
        art = "" if "TODO_LAWYER" in art else f", {art}"
        doc = s.get("doc", "").replace("TODO_LAWYER:", "").replace("TODO_LAWYER", "").strip()
        lines.append(f"• {doc}{art}\n  {s.get('url')}")
    await cb.message.answer("\n".join(lines), disable_web_page_preview=True)


@router.callback_query(F.data.startswith("k:"))
async def cb_ok(cb: CallbackQuery):
    eid = int(cb.data.split(":")[1] or 0)
    if eid:
        await api.post("/api/feedback", json={"event_id": eid, "helpful": True})
    await cb.answer(tr(user_lang.get(cb.from_user.id, "uz"), "thanks_ok"))


@router.callback_query(F.data.startswith("d:"))
async def cb_disagree(cb: CallbackQuery):
    _, card_id, eid = cb.data.split(":")
    lang = user_lang.get(cb.from_user.id, "uz")
    await cb.answer()
    res = await api.post("/api/appeal", json={"card_id": card_id, "event_id": int(eid) if eid.isdigit() and int(eid) else None,
                                              "lang": lang})
    if not res:
        await cb.message.answer(tr(lang, "error_generic"))
        return
    chans = " · ".join(f"{c['name']}: {c['url']}" for c in res.get("submit_channels", []))
    await cb.message.answer(f"{res['header']}\n{res['hint']}: {chans}", disable_web_page_preview=True)
    await cb.message.answer(res["text"])


@router.callback_query(F.data.startswith("u:"))
async def cb_subscribe(cb: CallbackQuery):
    card_id = cb.data.split(":", 1)[1]
    lang = user_lang.get(cb.from_user.id, "uz")
    res = await api.post("/api/subscribe", json={"chat_id": str(cb.message.chat.id), "topic_id": card_id, "lang": lang})
    await cb.answer((res or {}).get("text") or tr(lang, "error_generic"), show_alert=True)


@router.callback_query(F.data.startswith("r:"))
async def cb_remind(cb: CallbackQuery):
    eid = int(cb.data.split(":")[1] or 0)
    item = answers.get(eid) or {}
    lang = item.get("lang", "uz")
    parsed = item.get("parsed") or {}
    if not parsed.get("reminder_date"):
        await cb.answer(tr(lang, "error_generic"), show_alert=True)
        return
    text = (f"⏰ Eslatma: jarimani chegirma bilan to'lash muddati {parsed.get('discount_deadline')} gacha. "
            f"Chegirmali summa: {parsed.get('discount_amount'):,.0f} so'm.".replace(",", " "))
    res = await api.post("/api/reminders", json={"chat_id": str(cb.message.chat.id), "remind_on": parsed["reminder_date"],
                                                 "text": text, "lang": lang})
    await cb.answer((res or {}).get("text") or tr(lang, "error_generic"), show_alert=True)
