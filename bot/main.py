"""Bot kirish nuqtasi. BOT_MODE=polling|webhook (.env). Token yo'q bo'lsa — CLI rejimi."""
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import settings  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("javob.bot")


def build():
    from aiogram import Bot, Dispatcher
    from aiogram.client.default import DefaultBotProperties

    import account_handlers
    import handlers

    bot = Bot(settings.telegram_bot_token, default=DefaultBotProperties(link_preview_is_disabled=True))
    dp = Dispatcher()
    dp.include_router(account_handlers.router)  # /start, anonim/tasdiqlangan rejim — birinchi
    dp.include_router(handlers.router)
    return bot, dp


async def _set_username(bot) -> None:
    import handlers

    try:
        me = await bot.get_me()
        handlers.BOT_USERNAME = me.username
    except Exception as e:  # noqa: BLE001
        log.warning("get_me xatosi: %s", e)
    try:
        from aiogram.types import BotCommand

        await bot.set_my_commands([
            BotCommand(command="start", description="Boshlash: OneID bilan yoki anonim"),
            BotCommand(command="tekshir", description="Postni tekshirish"),
            BotCommand(command="region", description="Hududni tanlash"),
            BotCommand(command="help", description="Yordam"),
        ])
    except Exception as e:  # noqa: BLE001
        log.warning("buyruqlar menyusi o'rnatilmadi: %s", e)


async def setup_menu_button(bot) -> bool:
    """WEBAPP_URL bo'lsa — chat menyusiga Mini App tugmasi ("Huquqim"). Bo'sh bo'lsa — hech narsa, xato ham yo'q."""
    url = (settings.webapp_url or "").strip()
    if not url:
        return False
    try:
        from aiogram.types import MenuButtonWebApp, WebAppInfo

        await bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text=settings.app_name, web_app=WebAppInfo(url=url)))
        log.info("Mini App menyu tugmasi o'rnatildi: %s", url)
        return True
    except Exception as e:  # noqa: BLE001 — bot baribir ishlashda davom etadi
        log.warning("Menyu tugmasi o'rnatilmadi: %s", e)
        return False


async def run_polling() -> None:
    bot, dp = build()
    await _set_username(bot)
    await setup_menu_button(bot)
    await bot.delete_webhook(drop_pending_updates=False)
    log.info("Bot polling rejimida ishga tushdi")
    await dp.start_polling(bot)


def run_webhook() -> None:
    from aiohttp import web
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

    if not settings.public_base_url:
        raise SystemExit("BOT_MODE=webhook uchun PUBLIC_BASE_URL kerak (.env)")
    bot, dp = build()
    url = settings.public_base_url.rstrip("/") + settings.bot_webhook_path

    async def on_startup(_):
        await _set_username(bot)
        await setup_menu_button(bot)
        await bot.set_webhook(url, secret_token=settings.bot_webhook_secret or None, drop_pending_updates=False)
        log.info("Webhook o'rnatildi: %s", url)

    dp.startup.register(on_startup)
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot,
                         secret_token=settings.bot_webhook_secret or None).register(app, path=settings.bot_webhook_path)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=settings.bot_host, port=settings.bot_port)


def main() -> None:
    if not settings.telegram_bot_token.strip():
        if not sys.stdin.isatty():
            # Docker/servis: interaktiv terminal yo'q — qayta ishga tushish sikliga tushmaslik uchun toza chiqamiz
            log.warning("TELEGRAM_BOT_TOKEN yo'q va terminal interaktiv emas — bot o'chiq. "
                        "Sinov uchun: http://localhost:8000/docs (/api/ask) yoki `python bot/cli.py`.")
            return
        log.warning("TELEGRAM_BOT_TOKEN yo'q — CLI rejimi ishga tushadi (backend /api/ask orqali).")
        import cli

        asyncio.run(cli.repl())
        return
    if settings.bot_mode == "webhook":
        run_webhook()
    else:
        asyncio.run(run_polling())


if __name__ == "__main__":
    main()
