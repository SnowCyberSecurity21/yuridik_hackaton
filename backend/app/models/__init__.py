"""DB modellari. Hech qayerda PINFL, pasport, F.I.Sh., telefon saqlanmaydi."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Card(Base):
    """Vaziyat kartasi (manba: /knowledge/cards/*.json)."""

    __tablename__ = "cards"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    category: Mapped[str] = mapped_column(String(60), index=True)
    data: Mapped[dict] = mapped_column(JSON)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    needs_reverification: Mapped[bool] = mapped_column(Boolean, default=False)
    reverify_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Event(Base):
    """Anonim analitika hodisasi."""

    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    kind: Mapped[str] = mapped_column(String(20), index=True)  # ask|sms|factcheck|appeal
    topic_id: Mapped[str | None] = mapped_column(String(80), index=True, nullable=True)
    region: Mapped[str | None] = mapped_column(String(40), index=True, nullable=True)
    lang: Mapped[str] = mapped_column(String(10), default="uz")
    channel: Mapped[str] = mapped_column(String(20), default="api")  # telegram|miniapp|web|api|cli
    answer_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # card|rag|not_found
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    verdict: Mapped[str | None] = mapped_column(String(20), nullable=True)  # fact-check uchun
    claim_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    was_helpful: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    appeal_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)


class Subscription(Base):
    """Foydalanuvchi roziligi bilan mavzu bo'yicha obuna (alertlar uchun)."""

    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[str] = mapped_column(String(40), index=True)
    topic_id: Mapped[str] = mapped_column(String(80), index=True)
    lang: Mapped[str] = mapped_column(String(10), default="uz")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Reminder(Base):
    """Chegirma muddati eslatmasi (faqat sana va summa, shaxsiy ma'lumotsiz)."""

    __tablename__ = "reminders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[str] = mapped_column(String(40), index=True)
    remind_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    text: Mapped[str] = mapped_column(Text)
    sent: Mapped[bool] = mapped_column(Boolean, default=False)


class Alert(Base):
    """Qonun o'zgarishi haqidagi xabar (obunachiga yoki dashboard uchun)."""

    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    change_id: Mapped[str] = mapped_column(String(80), index=True)
    topic_id: Mapped[str] = mapped_column(String(80))
    chat_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    profile_id: Mapped[str | None] = mapped_column(String(80), nullable=True)  # profil orqali nishonlangan bo'lsa
    text: Mapped[str] = mapped_column(Text)
    delivered: Mapped[bool] = mapped_column(Boolean, default=False)


class ProfileLink(Base):
    """Foydalanuvchi <-> (MyGov/OneID) profil bog'lanishi va rozilik yozuvi.

    Profil MA'LUMOTLARI bu yerda SAQLANMAYDI: faqat kalit (Telegram chat_id yoki web:<uuid>),
    profil identifikatori va rozilik (vaqt, doira, matn versiyasi). Real tizimda profil_id o'rniga
    OneID sessiyasi bo'ladi, ma'lumotlar esa har so'rovda integratsiya platformasidan o'qiladi.
    """

    __tablename__ = "profile_links"
    user_key: Mapped[str] = mapped_column(String(80), primary_key=True)
    profile_id: Mapped[str] = mapped_column(String(80), index=True)
    lang: Mapped[str] = mapped_column(String(10), default="uz")
    channel: Mapped[str] = mapped_column(String(20), default="telegram")
    consent_scope: Mapped[list] = mapped_column(JSON, default=list)
    consent_version: Mapped[str] = mapped_column(String(20), default="v1-demo")
    consent_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class TextbookChunk(Base):
    """Darslik bo'lagi (Textbook Guardian)."""

    __tablename__ = "textbook_chunks"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    textbook_id: Mapped[str] = mapped_column(String(80), index=True)
    textbook_title: Mapped[str] = mapped_column(String(200))
    title: Mapped[str] = mapped_column(String(200))
    text: Mapped[str] = mapped_column(Text)
    refs: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(20), default="ok")  # ok|outdated
    change_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    diff: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    suggested_text: Mapped[str | None] = mapped_column(Text, nullable=True)


class AppliedChange(Base):
    __tablename__ = "applied_changes"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    summary: Mapped[dict] = mapped_column(JSON, default=dict)


# ================================================================== Huquqim hisoblari (A tizim)

class Account(Base):
    """Huquqim platformasi hisobi. Shaxsiy ma'lumot YO'Q: faqat login, parol xeshi va OneID bog'lanishi/rozilik.

    OneID (demo) ma'lumotlari bu yerda saqlanmaydi — kerak bo'lganda demo ID servisidan `oneid_token` bilan olinadi.
    """

    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    oneid_sub: Mapped[str | None] = mapped_column(String(60), nullable=True, index=True)
    oneid_token: Mapped[str | None] = mapped_column(String(100), nullable=True)
    oneid_linked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    consent_scope: Mapped[list | None] = mapped_column(JSON, nullable=True)
    consent_version: Mapped[str | None] = mapped_column(String(20), nullable=True)


class WebSession(Base):
    __tablename__ = "web_sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_id: Mapped[int] = mapped_column(Integer, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    oneid_state: Mapped[str | None] = mapped_column(String(64), nullable=True)


class TelegramLink(Base):
    """Telegram chat <-> Huquqim hisobi (kabinetdagi bir martalik token orqali)."""

    __tablename__ = "telegram_links"
    chat_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    account_id: Mapped[int] = mapped_column(Integer, index=True)
    linked_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class BotLinkToken(Base):
    __tablename__ = "bot_link_tokens"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_id: Mapped[int] = mapped_column(Integer, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
