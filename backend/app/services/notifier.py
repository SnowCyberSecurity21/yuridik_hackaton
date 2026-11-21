"""Telegram'ga xabar yuborish (alert va eslatmalar). Token yo'q bo'lsa — faqat DB'da qoladi."""
from __future__ import annotations

import asyncio
import logging

import httpx
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import SessionLocal
from ..models import Alert, Reminder, utcnow

log = logging.getLogger("javob.notifier")


def enabled() -> bool:
    return bool(get_settings().telegram_bot_token.strip())


async def send_telegram(chat_id: str, text: str) -> bool:
    if not enabled() or not chat_id or not str(chat_id).lstrip("-").isdigit():
        return False
    url = f"https://api.telegram.org/bot{get_settings().telegram_bot_token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(url, json={"chat_id": chat_id, "text": text[:4000]})
            return r.status_code == 200
    except Exception as e:  # noqa: BLE001
        log.warning("Telegram yuborilmadi: %s", e)
        return False


async def deliver_pending(db: Session) -> dict:
    sent_alerts = sent_rem = 0
    for a in db.query(Alert).filter(Alert.delivered.is_(False), Alert.chat_id.isnot(None)).limit(200).all():
        if await send_telegram(a.chat_id, a.text):
            a.delivered = True
            sent_alerts += 1
    for r in db.query(Reminder).filter(Reminder.sent.is_(False), Reminder.remind_at <= utcnow()).limit(200).all():
        if await send_telegram(r.chat_id, r.text):
            r.sent = True
            sent_rem += 1
    db.commit()
    return {"alerts": sent_alerts, "reminders": sent_rem}


async def loop() -> None:
    interval = max(30, get_settings().notifier_interval)
    while True:
        await asyncio.sleep(interval)
        if not enabled():
            continue
        db = SessionLocal()
        try:
            await deliver_pending(db)
        except Exception as e:  # noqa: BLE001
            log.warning("notifier xatosi: %s", e)
        finally:
            db.close()
