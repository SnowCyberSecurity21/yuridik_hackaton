"""Huquqim hisoblari: ro'yxatdan o'tish, kirish, sessiya, OneID (demo) bog'lanishi, Telegram ulash tokeni.

Huquqim faqat bog'lanish va rozilikni saqlaydi. Shaxs ma'lumotlari kerak bo'lganda demo ID servisidan olinadi.
"""
from __future__ import annotations

import re
from datetime import timedelta

from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Account, BotLinkToken, TelegramLink, WebSession, utcnow
from ..oneid_demo import service as oneid
from .security import hash_password, new_token, token_hash, verify_password

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")
SESSION_TTL = timedelta(days=7)
LINK_TTL = timedelta(minutes=10)
CONSENT_VERSION = "v2-demo-id"


class AuthError(ValueError):
    pass


def register(db: Session, username: str, password: str) -> Account:
    username = (username or "").strip()
    if not USERNAME_RE.match(username):
        raise AuthError("Login 3–30 belgi: lotin harflari, raqam, _ . -")
    if len(password or "") < 8 or len(password) > 128:
        raise AuthError("Parol kamida 8 belgi bo'lsin")
    if db.query(Account).filter(Account.username == username.lower()).first():
        raise AuthError("Bu login band")
    acc = Account(username=username.lower(), password_hash=hash_password(password))
    db.add(acc)
    db.commit()
    return acc


def authenticate(db: Session, username: str, password: str) -> Account | None:
    acc = db.query(Account).filter(Account.username == (username or "").strip().lower()).first()
    if acc and verify_password(password or "", acc.password_hash):
        return acc
    return None


def create_session(db: Session, acc: Account) -> str:
    tok = new_token(32)
    db.add(WebSession(token_hash=token_hash(tok), account_id=acc.id, expires_at=utcnow() + SESSION_TTL))
    db.commit()
    return tok


def session_row(db: Session, tok: str | None) -> WebSession | None:
    if not tok:
        return None
    row = db.get(WebSession, token_hash(tok))
    if not row or row.expires_at < utcnow():
        return None
    return row


def account_by_session(db: Session, tok: str | None) -> Account | None:
    row = session_row(db, tok)
    return db.get(Account, row.account_id) if row else None


def end_session(db: Session, tok: str | None) -> None:
    row = session_row(db, tok)
    if row:
        db.delete(row)
        db.commit()


# ------------------------------------------------------------------ OneID (demo) bog'lanishi

def start_oneid(db: Session, tok: str) -> str:
    row = session_row(db, tok)
    state = new_token(16)
    row.oneid_state = state
    db.commit()
    return state


def finish_oneid(db: Session, tok: str, code: str, state: str) -> Account | None:
    row = session_row(db, tok)
    if not row or not row.oneid_state or not state or row.oneid_state != state:
        return None
    row.oneid_state = None
    res = oneid.exchange_code(db, code, "huquqim", "/api/oneid/callback")
    if not res:
        db.commit()
        return None
    acc = db.get(Account, row.account_id)
    if acc.oneid_token:  # eski grantni bekor qilamiz
        oneid.revoke(db, acc.oneid_token)
    acc.oneid_sub, acc.oneid_token = res["sub"], res["access_token"]
    acc.oneid_linked_at, acc.consent_scope, acc.consent_version = utcnow(), res["scope"], CONSENT_VERSION
    db.commit()
    return acc


def revoke_oneid(db: Session, acc: Account) -> bool:
    if not acc.oneid_sub:
        return False
    oneid.revoke(db, acc.oneid_token)
    acc.oneid_sub = acc.oneid_token = None
    acc.oneid_linked_at = None
    acc.consent_scope = None
    acc.consent_version = None
    db.commit()
    return True


def person_of(db: Session, acc: Account | None) -> dict | None:
    """Demo ID servisidan (grant bo'yicha) shaxs ma'lumoti. Saqlanmaydi. Grant bekor bo'lsa — bog'lanish uziladi."""
    if not acc or not acc.oneid_token:
        return None
    info = oneid.userinfo(db, acc.oneid_token)
    if info is None:
        acc.oneid_sub = acc.oneid_token = None
        db.commit()
        return None
    return info


def gov_whitelist() -> set[str]:
    return {s.strip() for s in get_settings().gov_staff_subs.split(",") if s.strip()}


def roles_of(acc: Account | None, person: dict | None) -> list[str]:
    roles = []
    if person:
        roles.append("verified")
        if (person.get("occupation") or {}).get("type") == "student":
            roles.append("student")
        if acc and acc.oneid_sub in gov_whitelist():
            roles.append("gov")
    return roles


# ------------------------------------------------------------------ Telegram ulash

def create_link_token(db: Session, acc: Account) -> str:
    tok = new_token(18).replace("-", "a").replace("_", "b")  # Telegram start parametri: [A-Za-z0-9_-]{1,64}
    db.add(BotLinkToken(token_hash=token_hash(tok), account_id=acc.id, expires_at=utcnow() + LINK_TTL))
    db.commit()
    return tok


def consume_link_token(db: Session, tok: str, chat_id: str) -> Account | None:
    row = db.get(BotLinkToken, token_hash(tok or ""))
    if not row or row.used_at is not None or row.expires_at < utcnow():
        return None
    row.used_at = utcnow()
    db.query(TelegramLink).filter(TelegramLink.account_id == row.account_id).delete()
    existing = db.get(TelegramLink, chat_id)
    if existing:
        existing.account_id, existing.linked_at = row.account_id, utcnow()
    else:
        db.add(TelegramLink(chat_id=chat_id, account_id=row.account_id))
    db.commit()
    return db.get(Account, row.account_id)


def account_by_chat(db: Session, chat_id: str) -> Account | None:
    link = db.get(TelegramLink, str(chat_id))
    return db.get(Account, link.account_id) if link else None


def telegram_of(db: Session, acc: Account) -> TelegramLink | None:
    return db.query(TelegramLink).filter(TelegramLink.account_id == acc.id).first()


def unlink_telegram(db: Session, acc: Account) -> bool:
    n = db.query(TelegramLink).filter(TelegramLink.account_id == acc.id).delete()
    db.commit()
    return n > 0


def deep_link(tok: str) -> str:
    return f"https://t.me/{get_settings().bot_username}?start=link_{tok}"
