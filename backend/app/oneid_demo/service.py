"""DEMO ID servisi — tashqi davlat identifikatsiya tizimining SIMULYATSIYASI.

Real tizimda bu boshqa server bo'ladi va Huquqim u bilan HTTP (OAuth2/OIDC) orqali gaplashadi.
Demo'da ishonchlilik uchun Huquqim shu moduldagi `exchange_code`, `userinfo`, `revoke` funksiyalarini to'g'ridan-to'g'ri
chaqiradi; xuddi shu funksiyalar /oneid-demo/api/* HTTP endpointlari sifatida ham ochiq.
"""
from __future__ import annotations

import json
from datetime import timedelta

from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import utcnow
from ..services.security import hash_password, new_token, token_hash, verify_password
from .models import DemoIdCode, DemoIdGrant, DemoIdSession, DemoIdUser

CLIENTS = {
    # client_id -> ruxsat etilgan redirect_uri'lar (nisbiy yo'l — o'sha domen)
    "huquqim": {"redirect_uris": ["/api/oneid/callback"], "name": "Huquqim"},
}
SCOPE = ["full_name", "birth_date", "citizenship", "region", "family", "social", "driver", "obligations", "occupation"]
SCOPE_LABELS_UZ = {
    "full_name": "F.I.Sh.",
    "birth_date": "Tug'ilgan sana",
    "citizenship": "Fuqarolik / huquqiy maqom va shaxsni tasdiqlovchi hujjat turi",
    "region": "Yashash hududi",
    "family": "Oila tarkibi va bolalar yoshi",
    "social": "Ijtimoiy holat (pensiya, kam ta'minlanganlar reestri, bandlik)",
    "driver": "Haydovchilik guvohnomasi bor-yo'qligi",
    "obligations": "Jarima, MIB va kommunal qarzlar",
    "occupation": "Mashg'ulot (o'qish yoki ish joyi)",
}
CODE_TTL = timedelta(minutes=5)
SESSION_TTL = timedelta(minutes=30)


def persons_file() -> list[dict]:
    path = get_settings().knowledge_dir / "oneid_demo" / "persons.json"
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("persons", [])
    except (OSError, json.JSONDecodeError):
        return []


def seed(db: Session) -> int:
    """Demo shaxslarni o'z jadvaliga yuklash (parol xeshlanadi). Mavjud bo'lsa — ma'lumot yangilanadi."""
    n = 0
    for p in persons_file():
        data = {k: v for k, v in p.items() if k not in ("password",)}
        row = db.get(DemoIdUser, p["sub"])
        if row is None:
            db.add(DemoIdUser(sub=p["sub"], login=p["login"].lower(), password_hash=hash_password(p["password"]), data=data))
        else:
            row.data = data
            if not verify_password(p["password"], row.password_hash):
                row.password_hash = hash_password(p["password"])
        n += 1
    db.commit()
    return n


def public_persons() -> list[dict]:
    """Login sahifasidagi «Demo shaxslar» ro'yxati (parollar ataylab ochiq — demo)."""
    return [{"login": p["login"], "password": p["password"], "icon": p.get("icon", "👤"), "persona": p.get("persona_uz", "")}
            for p in persons_file()]


def authenticate(db: Session, login: str, password: str) -> DemoIdUser | None:
    row = db.query(DemoIdUser).filter(DemoIdUser.login == (login or "").strip().lower()).first()
    if row and verify_password(password or "", row.password_hash):
        return row
    return None


def create_session(db: Session, sub: str) -> str:
    tok = new_token()
    db.add(DemoIdSession(token_hash=token_hash(tok), sub=sub, expires_at=utcnow() + SESSION_TTL))
    db.commit()
    return tok


def session_sub(db: Session, tok: str | None) -> str | None:
    if not tok:
        return None
    row = db.get(DemoIdSession, token_hash(tok))
    if not row or row.expires_at < utcnow():
        return None
    return row.sub


def end_session(db: Session, tok: str | None) -> None:
    if tok:
        row = db.get(DemoIdSession, token_hash(tok))
        if row:
            db.delete(row)
            db.commit()


def valid_client(client_id: str, redirect_uri: str) -> bool:
    c = CLIENTS.get(client_id)
    return bool(c) and redirect_uri in c["redirect_uris"]


def issue_code(db: Session, sub: str, client_id: str, redirect_uri: str) -> str:
    code = new_token()
    db.add(DemoIdCode(code_hash=token_hash(code), sub=sub, client_id=client_id, redirect_uri=redirect_uri,
                      scope=list(SCOPE), expires_at=utcnow() + CODE_TTL))
    db.commit()
    return code


def exchange_code(db: Session, code: str, client_id: str, redirect_uri: str) -> dict | None:
    """Kod -> {sub, access_token, scope}. Kod bir martalik va 5 daqiqa amal qiladi."""
    row = db.get(DemoIdCode, token_hash(code or ""))
    if not row or row.used or row.expires_at < utcnow() or row.client_id != client_id or row.redirect_uri != redirect_uri:
        return None
    row.used = True
    access = new_token(32)
    db.add(DemoIdGrant(token_hash=token_hash(access), sub=row.sub, client_id=client_id, scope=list(row.scope)))
    db.commit()
    return {"sub": row.sub, "access_token": access, "scope": list(row.scope)}


def userinfo(db: Session, access_token: str | None) -> dict | None:
    """Faqat amaldagi grant bo'yicha: rozilik doirasidagi maydonlar. Grant bekor qilingan bo'lsa — None."""
    if not access_token:
        return None
    grant = db.get(DemoIdGrant, token_hash(access_token))
    if not grant:
        return None
    user = db.get(DemoIdUser, grant.sub)
    if not user:
        return None
    d = user.data
    out = {"sub": user.sub, "is_demo": True}
    for k in ("icon", "persona_uz", "first_name", "situations"):
        out[k] = d.get(k)
    for k in grant.scope:
        if k in d:
            out[k] = d[k]
    return out


def revoke(db: Session, access_token: str | None) -> bool:
    if not access_token:
        return False
    grant = db.get(DemoIdGrant, token_hash(access_token))
    if not grant:
        return False
    db.delete(grant)
    db.commit()
    return True
