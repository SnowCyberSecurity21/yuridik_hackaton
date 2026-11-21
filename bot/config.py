from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ROOT / ".env"), env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Huquqim"
    telegram_bot_token: str = ""
    bot_mode: str = "polling"  # polling | webhook
    bot_webhook_path: str = "/tg/webhook"
    bot_webhook_secret: str = ""
    bot_host: str = "0.0.0.0"
    bot_port: int = 8081
    backend_url: str = "http://localhost:8000"
    backend_timeout: float = 25.0
    public_base_url: str = ""
    webapp_url: str = ""
    internal_api_token: str = ""  # backend /api/profile/* uchun X-Internal-Token
    i18n_dir: Path = ROOT / "knowledge" / "i18n"


settings = BotSettings()
