"""Backend API klienti: har bir chaqiruvda timeout va xatoda None (bot hech qachon qulamaydi)."""
from __future__ import annotations

import logging

import httpx

from config import settings

log = logging.getLogger("javob.bot.api")

_client: httpx.AsyncClient | None = None


def client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(base_url=settings.backend_url.rstrip("/"), timeout=settings.backend_timeout)
    return _client


async def post(path: str, **kw) -> dict | None:
    try:
        r = await client().post(path, **kw)
        if r.status_code >= 400:
            log.warning("%s -> %s %s", path, r.status_code, r.text[:200])
            return None
        return r.json()
    except Exception as e:  # noqa: BLE001
        log.warning("backend %s xatosi: %s", path, e)
        return None


async def post_bytes(path: str, **kw) -> bytes | None:
    try:
        r = await client().post(path, **kw)
        return r.content if r.status_code == 200 else None
    except Exception as e:  # noqa: BLE001
        log.warning("backend %s xatosi: %s", path, e)
        return None


async def ask(text: str, *, region: str | None, lang: str | None = None, mode: str = "auto",
              channel: str = "telegram", legal_status: str | None = None) -> dict | None:
    return await post("/api/ask", json={"text": text, "region": region, "lang": lang, "mode": mode, "channel": channel,
                                        "legal_status": legal_status})


async def ask_voice(audio: bytes, *, region: str | None, legal_status: str | None = None) -> dict | None:
    data = {"channel": "telegram"}
    if region:
        data["region"] = region
    if legal_status:
        data["legal_status"] = legal_status
    return await post("/api/ask/voice", files={"file": ("voice.ogg", audio, "audio/ogg")}, data=data)


async def regions() -> list[dict]:
    try:
        r = await client().get("/api/regions")
        return r.json() if r.status_code == 200 else []
    except Exception:  # noqa: BLE001
        return []


async def card(card_id: str, lang: str = "uz") -> dict | None:
    try:
        r = await client().get(f"/api/cards/{card_id}", params={"lang": lang})
        return r.json() if r.status_code == 200 else None
    except Exception:  # noqa: BLE001
        return None



# ---------------- «Mening huquqlarim» (profil) ----------------

def _internal_headers() -> dict:
    return {"X-Internal-Token": settings.internal_api_token} if settings.internal_api_token else {}


async def get_json(path: str, **kw) -> dict | None:
    try:
        r = await client().get(path, **kw)
        if r.status_code >= 400:
            log.warning("%s -> %s %s", path, r.status_code, r.text[:200])
            return None
        return r.json()
    except Exception as e:  # noqa: BLE001
        log.warning("backend %s xatosi: %s", path, e)
        return None


async def demo_profiles(lang: str = "uz") -> dict | None:
    return await get_json("/api/profile/demo-profiles", params={"lang": lang})


async def profile_me(user_key: str, lang: str = "uz") -> dict | None:
    return await get_json("/api/profile/me", params={"user_key": user_key, "lang": lang}, headers=_internal_headers())


async def profile_post(path: str, payload: dict) -> dict | None:
    return await post(f"/api/profile/{path}", json=payload, headers=_internal_headers())


# ---------------- Huquqim hisobi (OneID demo bilan tasdiqlangan) ----------------

async def bot_me(chat_id: int) -> dict | None:
    return await get_json("/api/bot/me", params={"chat_id": str(chat_id)}, headers=_internal_headers())


async def bot_link(chat_id: int, token: str) -> dict | None:
    return await post("/api/bot/link", json={"chat_id": str(chat_id), "token": token}, headers=_internal_headers())


async def bot_section(chat_id: int, section: str) -> dict | None:
    return await get_json("/api/bot/section", params={"chat_id": str(chat_id), "section": section}, headers=_internal_headers())


async def bot_post(path: str, payload: dict) -> dict | None:
    return await post(f"/api/bot/{path}", json=payload, headers=_internal_headers())


async def rights_meta() -> dict | None:
    return await get_json("/api/rights/meta")


async def rights(status: str, situations: list[str]) -> dict | None:
    return await get_json("/api/rights", params={"status": status, "situations": ",".join(situations)})
