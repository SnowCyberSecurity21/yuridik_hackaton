"""DEMO ID servisining O'Z jadvallari (Huquqim jadvallaridan alohida, `oneid_demo_` prefiksi bilan)."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base
from ..models import utcnow


class DemoIdUser(Base):
    __tablename__ = "oneid_demo_users"
    sub: Mapped[str] = mapped_column(String(60), primary_key=True)
    login: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    data: Mapped[dict] = mapped_column(JSON)


class DemoIdSession(Base):
    __tablename__ = "oneid_demo_sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    sub: Mapped[str] = mapped_column(String(60))
    expires_at: Mapped[datetime] = mapped_column(DateTime)


class DemoIdCode(Base):
    """Bir martalik avtorizatsiya kodi (OAuth2 authorization code kabi)."""

    __tablename__ = "oneid_demo_codes"
    code_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    sub: Mapped[str] = mapped_column(String(60))
    client_id: Mapped[str] = mapped_column(String(40))
    redirect_uri: Mapped[str] = mapped_column(String(200))
    scope: Mapped[list] = mapped_column(JSON)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    used: Mapped[bool] = mapped_column(Boolean, default=False)


class DemoIdGrant(Base):
    """Foydalanuvchi bergan rozilik (grant). access token = grant tokeni; bekor qilinsa — o'chiriladi."""

    __tablename__ = "oneid_demo_grants"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    sub: Mapped[str] = mapped_column(String(60), index=True)
    client_id: Mapped[str] = mapped_column(String(40))
    scope: Mapped[list] = mapped_column(JSON)
    granted_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
