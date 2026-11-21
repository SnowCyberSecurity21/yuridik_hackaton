"""Testlar haqiqiy .env dagi kalitlardan ajratilgan: hech qanday tashqi LLM/Telegram chaqiruvi bo'lmaydi."""
import os

for _k in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "TELEGRAM_BOT_TOKEN", "INTERNAL_API_TOKEN", "ADMIN_TOKEN", "WEBAPP_URL"):
    os.environ[_k] = ""
os.environ["LLM_PROVIDER"] = "anthropic"
os.environ["STT_PROVIDER"] = "none"
os.environ["TTS_PROVIDER"] = "none"
