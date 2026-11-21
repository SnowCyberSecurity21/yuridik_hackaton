"""Yagona sozlamalar manbai: hamma narsa .env orqali."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]

# Mahsulot nomi bitta joyda (loyiha brifi talabi)
APP_NAME = "Huquqim"

# 14 hudud (Qoraqalpog'iston Respublikasi, 12 viloyat, Toshkent shahri)
REGIONS: list[dict[str, str]] = [
    {"id": "qoraqalpogiston", "name": "Qoraqalpog'iston Resp."},
    {"id": "andijon", "name": "Andijon"},
    {"id": "buxoro", "name": "Buxoro"},
    {"id": "fargona", "name": "Farg'ona"},
    {"id": "jizzax", "name": "Jizzax"},
    {"id": "xorazm", "name": "Xorazm"},
    {"id": "namangan", "name": "Namangan"},
    {"id": "navoiy", "name": "Navoiy"},
    {"id": "qashqadaryo", "name": "Qashqadaryo"},
    {"id": "samarqand", "name": "Samarqand"},
    {"id": "sirdaryo", "name": "Sirdaryo"},
    {"id": "surxondaryo", "name": "Surxondaryo"},
    {"id": "toshkent_vil", "name": "Toshkent viloyati"},
    {"id": "toshkent_sh", "name": "Toshkent shahri"},
]
REGION_IDS = {r["id"] for r in REGIONS}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"), env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = APP_NAME
    env: str = "dev"
    log_level: str = "INFO"

    database_url: str = f"sqlite:///{(ROOT_DIR / 'data' / 'huquqim.db').as_posix()}"

    # LLM provayderi: anthropic | gemini (kalit bo'lmasa — shablon javob)
    llm_provider: str = "anthropic"
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_fallback_model: str = "gemini-3.1-flash-lite"
    gemini_api_base: str = "https://generativelanguage.googleapis.com/v1beta"
    llm_model: str = "claude-sonnet-5-5"
    llm_effort: str = "low"
    llm_timeout: float = 8.0
    llm_max_tokens: int = 2000

    stt_provider: str = "none"
    stt_api_base: str = "https://api.openai.com/v1"
    stt_api_key: str = ""
    stt_model: str = "whisper-1"
    stt_language: str = "uz"
    stt_timeout: float = 30.0
    faster_whisper_size: str = "small"

    tts_provider: str = "edge"
    tts_voice_uz: str = "uz-UZ-MadinaNeural"
    tts_voice_ru: str = "ru-RU-SvetlanaNeural"
    tts_timeout: float = 15.0

    classifier_threshold: float = 0.35
    embeddings_enabled: bool = False
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"

    telegram_bot_token: str = ""
    public_base_url: str = ""
    webapp_url: str = ""

    cors_origins: str = "*"
    admin_token: str = ""
    # Bot -> backend ichki so'rovlari uchun (bo'sh bo'lsa demo rejim: Telegram chat_id tekshirilmaydi)
    internal_api_token: str = ""
    notifier_interval: int = 300
    # Davlat xodimi roli — OneID'dan emas, Huquqim admin ro'yxatidan (whitelist): OneID sub'lari, vergul bilan
    gov_staff_subs: str = "demo-id-0005"
    # Telegram bot username (deep link: https://t.me/<username>?start=link_<token>)
    bot_username: str = "Huquqim_official_bot"
    # Simulyatsiya cheklovi (davlat kabineti): necha soniyada 1 marta va bitta simulyatsiyada maksimal xabar
    sim_cooldown_s: int = 30
    sim_max_messages: int = 30

    knowledge_dir: Path = ROOT_DIR / "knowledge"
    prompts_dir: Path = ROOT_DIR / "prompts"
    data_dir: Path = ROOT_DIR / "data"
    frontend_dist: Path = ROOT_DIR / "frontend" / "dist"

    @property
    def llm_enabled(self) -> bool:
        if self.llm_provider.strip().lower() == "gemini":
            return bool(self.gemini_api_key.strip())
        return bool(self.anthropic_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.data_dir.mkdir(parents=True, exist_ok=True)
    return s
