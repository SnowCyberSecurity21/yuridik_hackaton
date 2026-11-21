"""/start: «OneID bilan tasdiqlab davom etish» yoki «Anonim davom etish»; hisobni botga ulash; tasdiqlangan menyu.

Anonim rejim: maqom va holat FAQAT shu jarayon xotirasida (bot qayta ishga tushsa o'chadi), backendga saqlanmaydi.
Shaxsiy ma'lumot so'ralmaydi.
"""
from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

import backend_client as api
from config import settings

log = logging.getLogger("javob.bot.account")
router = Router()

STATUSES = [("uz_citizen", "🏠 O'zbekiston fuqarosi"), ("foreign", "🌍 Chet el fuqarosi"),
            ("stateless", "🕊️ Fuqaroligi bo'lmagan shaxs"), ("unknown", "❔ Bilmayman")]
SITUATIONS = [("student", "🎓 Talaba"), ("mother", "👩‍👧 Bolali ona"), ("parent", "👨‍👩‍👧 Ota-ona"),
              ("entrepreneur", "🏢 Yuridik shaxs / tadbirkor"), ("pensioner", "👴 Pensioner"),
              ("driver", "🚗 Haydovchi")]

# Xotiradagi anonim tanlov (shaxsiy ma'lumot emas): chat_id -> {"status", "situations"}
anon: dict[int, dict] = {}
# Tasdiqlangan foydalanuvchining maqomi (javobga eslatma qo'shish uchun) — kesh
verified_status: dict[int, str] = {}


def site_url(path: str = "") -> str:
    base = (settings.public_base_url or "https://huquqim.zehnprotect.uz").rstrip("/")
    return base + path


def legal_status_of(chat_id: int) -> str | None:
    if chat_id in verified_status:
        return verified_status[chat_id]
    return (anon.get(chat_id) or {}).get("status")


def welcome_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ OneID bilan tasdiqlab davom etish", url=site_url("/kirish?next=oneid&from=tg"))
    kb.button(text="👤 Anonim davom etish", callback_data="m:anon")
    kb.adjust(1)
    return kb.as_markup()


def status_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for sid, label in STATUSES:
        kb.button(text=label, callback_data=f"st:{sid}")
    kb.adjust(1)
    return kb.as_markup()


def situation_kb(chosen: list[str]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for sid, label in SITUATIONS:
        kb.button(text=("☑️ " if sid in chosen else "") + label, callback_data=f"si:{sid}")
    kb.button(text="➡️ Tayyor", callback_data="si:done")
    kb.adjust(2)
    return kb.as_markup()


# Tayyor savollar — tekshirilgan manba (O'RQ-692, 15/18/22-moddalar) asosida, knowledge/rights/status_foreign.json bilan bir xil
SUGGESTED = {"foreign": ["Chet el fuqarosi O'zbekistonda ishlashi mumkinmi?", "Chet el fuqarosi O'zbekistonda o'qiy oladimi?",
                         "Chet el fuqarosi davlat organiga murojaat qila oladimi?"]}


def anon_menu_kb(status: str | None = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for i, q in enumerate(SUGGESTED.get(status or "", [])):
        kb.button(text=f"💬 {q}", callback_data=f"aq:{i}")
    kb.button(text="⚖️ Huquqlarim (maqomga oid)", callback_data="an:rights")
    kb.button(text="📚 Siz uchun qonunlar", callback_data="an:laws")
    kb.button(text="🔄 Maqomni o'zgartirish", callback_data="m:anon")
    kb.button(text="✅ OneID bilan tasdiqlash", url=site_url("/kirish?next=oneid&from=tg"))
    kb.adjust(1)
    return kb.as_markup()


def verified_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🎁 Mening imtiyozlarim", callback_data="v:benefits")
    kb.button(text="⚖️ Huquqlarim", callback_data="v:rights")
    kb.button(text="📅 Majburiyatlar", callback_data="v:obligations")
    kb.button(text="📚 Siz uchun qonunlar", callback_data="v:laws")
    kb.button(text="🔔 O'zgarishlar", callback_data="v:changes")
    if settings.webapp_url:
        kb.button(text="📱 Kabinet (Mini App)", web_app=WebAppInfo(url=settings.webapp_url))
    kb.button(text="🔌 Hisobni botdan uzish", callback_data="v:unlink")
    kb.adjust(2)
    return kb.as_markup()


HOW_TO = ("✍️ Savol yozing yoki 🎙 ovozli xabar yuboring.\n🧾 Jarima/MIB SMS'ini shu yerga joylang.\n"
          "🕵️ Shubhali postni forward qiling — tekshiraman.")


def verified_greeting(me: dict) -> str:
    return (f"Salom, {me.get('first_name') or me.get('username')}! ✅ Hisobingiz OneID (DEMO) orqali tasdiqlangan.\n\n"
            f"Quyidagi bo'limlardan birini tanlang.\n\n{HOW_TO}")


async def send_start(message: Message, chat_id: int) -> None:
    me = await api.bot_me(chat_id) or {}
    if me.get("verified"):
        verified_status[chat_id] = me.get("status") or "unknown"
        await message.answer(verified_greeting(me), reply_markup=verified_menu_kb())
        return
    verified_status.pop(chat_id, None)
    extra = ("\n\n⚠️ Hisobingiz botga ulangan, lekin OneID orqali hali tasdiqlanmagan — saytda tasdiqlang."
             if me.get("linked") else "")
    await message.answer(
        f"Assalomu alaykum! Men — {settings.app_name}. Huquqlaringizni oddiy tilda, rasmiy manba bilan tushuntiraman.\n\n"
        "Qanday davom etamiz?\n"
        "• ✅ OneID bilan — shaxsiy imtiyozlar, majburiyatlar va sizga ta'sir qiluvchi o'zgarishlar.\n"
        "• 👤 Anonim — savol, SMS va feyk tekshiruvi, umumiy huquqlar. Shaxsiy ma'lumot so'ralmaydi va saqlanmaydi." + extra,
        reply_markup=welcome_kb())


@router.message(CommandStart(deep_link=True))
async def start_deep(message: Message, command: CommandObject):
    arg = (command.args or "").strip()
    chat_id = message.chat.id
    if arg.startswith("link_"):
        res = await api.bot_link(chat_id, arg[5:])
        if not res:
            await message.answer("Kechirasiz, hozir ulab bo'lmadi. Birozdan keyin qayta urinib ko'ring.")
            return
        if not res.get("ok"):
            await message.answer(res.get("text") or "Havola yaroqsiz.")
            return
        anon.pop(chat_id, None)
        if res.get("verified"):
            verified_status[chat_id] = res.get("status") or "unknown"
            await message.answer("🔗 Hisob botga ulandi.\n\n" + verified_greeting(res), reply_markup=verified_menu_kb())
        else:
            await message.answer("🔗 Hisob botga ulandi. Shaxsiy bo'limlar uchun saytda OneID orqali tasdiqlang.",
                                 reply_markup=welcome_kb())
        return
    await send_start(message, chat_id)


@router.message(CommandStart())
async def start_plain(message: Message):
    await send_start(message, message.chat.id)


# ------------------------------------------------------------------ anonim

@router.callback_query(F.data == "m:anon")
async def cb_anon(cb: CallbackQuery):
    await cb.answer()
    me = await api.bot_me(cb.message.chat.id) or {}
    if me.get("verified"):
        await cb.message.answer("Siz tasdiqlangan rejimdasiz. Anonim davom etish uchun avval «🔌 Hisobni botdan uzish».",
                                reply_markup=verified_menu_kb())
        return
    anon[cb.message.chat.id] = {"status": None, "situations": []}
    await cb.message.answer("👤 Anonim rejim. Huquqiy maqomingizni tanlang (ixtiyoriy — javoblar shunga moslashadi):",
                            reply_markup=status_kb())


@router.callback_query(F.data.startswith("st:"))
async def cb_status(cb: CallbackQuery):
    sid = cb.data.split(":", 1)[1]
    st = anon.setdefault(cb.message.chat.id, {"status": None, "situations": []})
    st["status"] = sid if sid in dict(STATUSES) else "unknown"
    await cb.answer("✓")
    await cb.message.answer("Holatingiz (ixtiyoriy, bir nechtasini tanlash mumkin):", reply_markup=situation_kb(st["situations"]))


@router.callback_query(F.data.startswith("si:"))
async def cb_situation(cb: CallbackQuery):
    sid = cb.data.split(":", 1)[1]
    st = anon.setdefault(cb.message.chat.id, {"status": "unknown", "situations": []})
    if sid == "done":
        await cb.answer()
        label = dict(STATUSES).get(st.get("status") or "unknown")
        sits = ", ".join(dict(SITUATIONS)[s] for s in st["situations"]) or "—"
        await cb.message.answer(f"✅ Tayyor. Maqom: {label}. Holat: {sits}.\n(Bu tanlov faqat suhbat davomida yodda turadi, saqlanmaydi.)\n\n{HOW_TO}",
                                reply_markup=anon_menu_kb(st.get("status")))
        return
    if sid in dict(SITUATIONS):
        st["situations"] = [s for s in st["situations"] if s != sid] if sid in st["situations"] else st["situations"] + [sid]
    await cb.answer("✓")
    try:
        await cb.message.edit_reply_markup(reply_markup=situation_kb(st["situations"]))
    except Exception:  # noqa: BLE001  (o'zgarmagan klaviatura)
        pass


@router.callback_query(F.data.startswith("an:"))
async def cb_anon_section(cb: CallbackQuery):
    st = anon.get(cb.message.chat.id) or {"status": "unknown", "situations": []}
    res = await api.rights(st.get("status") or "unknown", st.get("situations") or [])
    await cb.answer()
    if not res:
        await cb.message.answer("Kechirasiz, hozir ma'lumot olib bo'lmadi.")
        return
    text = res["laws_text"] if cb.data == "an:laws" else res["text"]
    await cb.message.answer(text[:4000], disable_web_page_preview=True, reply_markup=anon_menu_kb(st.get("status")))


@router.callback_query(F.data.startswith("aq:"))
async def cb_suggested(cb: CallbackQuery):
    st = anon.get(cb.message.chat.id) or {}
    qs = SUGGESTED.get(st.get("status") or "", [])
    try:
        q = qs[int(cb.data.split(":", 1)[1])]
    except (ValueError, IndexError):
        await cb.answer()
        return
    await cb.answer("💬 ...")
    res = await api.ask(q, region=None, legal_status=st.get("status"))
    if not res or "text" not in res:
        await cb.message.answer("Kechirasiz, hozir javob bera olmadim.")
        return
    await cb.message.answer(f"💬 {q}" + chr(10) * 2 + res["text"][:4000], disable_web_page_preview=True, reply_markup=anon_menu_kb(st.get("status")))


# ------------------------------------------------------------------ tasdiqlangan

@router.callback_query(F.data.startswith("v:"))
async def cb_verified(cb: CallbackQuery):
    section = cb.data.split(":", 1)[1]
    chat_id = cb.message.chat.id
    await cb.answer()
    if section == "unlink":
        res = await api.bot_post("unlink", {"chat_id": str(chat_id)})
        verified_status.pop(chat_id, None)
        await cb.message.answer("🔌 Hisob botdan uzildi. Qayta ulash: saytdagi kabinet → «Telegram'ni ulash»."
                                if (res or {}).get("ok") else "Hisob ulanmagan edi.", reply_markup=welcome_kb())
        return
    res = await api.bot_section(chat_id, section)
    if not res:
        await cb.message.answer("Hisob ulanmagan yoki tasdiqlanmagan. /start", reply_markup=welcome_kb())
        return
    kb = InlineKeyboardBuilder()
    for b in res.get("benefits", []):
        kb.button(text=f"📝 {b['label']}", callback_data=f"vb:{b['id']}")
    for o in res.get("obligations", []):
        kb.button(text=f"⏰ Eslatma: {o['title'].split(' — ')[0][:28]}", callback_data=f"vo:{o['id']}")
    kb.button(text="⬅️ Menyu", callback_data="v:menu")
    kb.adjust(1)
    if section == "menu":
        me = await api.bot_me(chat_id) or {}
        await cb.message.answer(verified_greeting(me), reply_markup=verified_menu_kb())
        return
    await cb.message.answer(res["text"][:4000], disable_web_page_preview=True, reply_markup=kb.as_markup())


@router.callback_query(F.data.startswith("vb:"))
async def cb_v_appeal(cb: CallbackQuery):
    await cb.answer("📝 ...")
    res = await api.bot_post("appeal", {"chat_id": str(cb.message.chat.id), "benefit_id": cb.data.split(":", 1)[1]})
    if not res:
        await cb.message.answer("Kechirasiz, arizani tayyorlab bo'lmadi.")
        return
    chans = " · ".join(f"{c['name']}: {c['url']}" for c in res.get("submit_channels", []))
    head = f"{res['header']} — {res.get('title', '')}\n{res['hint']}: {chans}"
    if res.get("to_check"):
        head += "\n❔ Tekshirilishi kerak: " + "; ".join(res["to_check"])
    await cb.message.answer(head[:4000], disable_web_page_preview=True)
    await cb.message.answer(res["text"][:4000])


@router.callback_query(F.data.startswith("vo:"))
async def cb_v_remind(cb: CallbackQuery):
    res = await api.bot_post("remind", {"chat_id": str(cb.message.chat.id), "obligation_id": cb.data.split(":", 1)[1]})
    await cb.answer((res or {}).get("text") or "Kechirasiz, xatolik.", show_alert=True)
