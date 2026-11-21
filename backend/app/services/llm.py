"""Provayderdan mustaqil LLM o'rami: LLM_PROVIDER = anthropic | gemini.

Qoidalar:
- har qanday xato / timeout (LLM_TIMEOUT, qat'iy) / refusal / blok -> None; chaqiruvchi shablon javobga o'tadi;
- LLM'ga yuboriladigan matndan shaxsiy ma'lumot oldin olib tashlanadi (privacy.scrub);
- Gemini: model nomlari startup'da ro'yxatdan tekshiriladi (GEMINI_MODEL -> GEMINI_FALLBACK_MODEL -> o'chiq);
- API kaliti URL'da emas, sarlavhada yuboriladi (loglarga tushmaydi).
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from functools import lru_cache
from pathlib import Path

from ..config import get_settings
from .privacy import scrub

log = logging.getLogger("javob.llm")

# Anthropic: server-side refusal fallback qo'llab-quvvatlanadigan modellar
_FALLBACK_MODELS = {"claude-opus-5-5", "claude-opus-5", "claude-fable-5-2", "claude-fable-5-1", "claude-sonnet-5-5"}
_FALLBACK_BETA = "server-side-fallback-2026-07-01"

# Gemini: startup tekshiruvidan keyin ishlatiladigan model (None — o'chiq, shablon rejimi)
_gemini: dict = {"model": None, "checked": False, "status": "tekshirilmagan"}


@lru_cache
def load_prompt(name: str) -> str:
    path: Path = get_settings().prompts_dir / f"{name}.md"
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        log.warning("prompt topilmadi: %s", path)
        return ""


def provider() -> str:
    return (get_settings().llm_provider or "anthropic").strip().lower()


# ------------------------------------------------------------------ Anthropic

@lru_cache
def _client():
    s = get_settings()
    if not s.anthropic_api_key.strip():
        return None
    try:
        import anthropic

        # Qayta urinish yo'q: umumiy kutish LLM_TIMEOUT dan oshmasin (bot javobi tez bo'lishi shart)
        return anthropic.AsyncAnthropic(api_key=s.anthropic_api_key, timeout=s.llm_timeout, max_retries=0)
    except Exception as e:  # paket yo'q yoki noto'g'ri sozlama
        log.warning("LLM klientini yaratib bo'lmadi: %s", e)
        return None


async def _anthropic_complete(system: str, user: str, max_tokens: int) -> str | None:
    client = _client()
    if client is None:
        return None
    s = get_settings()
    params = dict(model=s.llm_model, max_tokens=max_tokens, system=system,
                  messages=[{"role": "user", "content": user}], output_config={"effort": s.llm_effort})
    if s.llm_model in _FALLBACK_MODELS:
        call = client.beta.messages.create(betas=[_FALLBACK_BETA], fallbacks="default", **params)
    else:
        call = client.messages.create(**params)
    resp = await asyncio.wait_for(call, timeout=s.llm_timeout)
    if resp.stop_reason == "refusal":
        log.warning("LLM refusal")
        return None
    return "".join(b.text for b in resp.content if getattr(b, "type", None) == "text").strip() or None


# ------------------------------------------------------------------ Gemini (REST, httpx)

def _gemini_headers() -> dict:
    return {"x-goog-api-key": get_settings().gemini_api_key.strip(), "Content-Type": "application/json"}


async def verify_gemini_models() -> str | None:
    """Startup: mavjud modellar ro'yxatidan GEMINI_MODEL yoki GEMINI_FALLBACK_MODEL ni tanlash."""
    import httpx

    s = get_settings()
    _gemini["checked"] = True
    if provider() != "gemini" or not s.gemini_api_key.strip():
        _gemini.update(model=None, status="kalit yo'q")
        return None
    wanted = [m.strip() for m in (s.gemini_model, s.gemini_fallback_model) if m and m.strip()]
    available: set[str] = set()
    try:
        async with httpx.AsyncClient(timeout=s.llm_timeout) as c:
            token = None
            for _ in range(10):
                params = {"pageSize": 1000, **({"pageToken": token} if token else {})}
                r = await c.get(f"{s.gemini_api_base.rstrip('/')}/models", params=params, headers=_gemini_headers())
                if r.status_code != 200:
                    _gemini.update(model=None, status=f"models ro'yxati: HTTP {r.status_code}")
                    log.warning("Gemini modellari ro'yxati olinmadi (HTTP %s) — shablon rejimi", r.status_code)
                    return None
                data = r.json()
                for m in data.get("models", []):
                    if "generateContent" in (m.get("supportedGenerationMethods") or []):
                        available.add(str(m.get("name", "")).removeprefix("models/"))
                token = data.get("nextPageToken")
                if not token:
                    break
    except Exception as e:  # noqa: BLE001
        _gemini.update(model=None, status=f"tarmoq xatosi: {type(e).__name__}")
        log.warning("Gemini modellari tekshirilmadi (%s) — shablon rejimi", type(e).__name__)
        return None
    chosen = next((m for m in wanted if m in available), None)
    if chosen is None:
        _gemini.update(model=None, status=f"modellar topilmadi: {', '.join(wanted)}")
        log.warning("Gemini: %s mavjud emas — LLM o'chiq, shablon rejimi", ", ".join(wanted))
        return None
    _gemini.update(model=chosen, status="ok" if chosen == wanted[0] else "zaxira model")
    log.info("Gemini model: %s (%s)", chosen, _gemini["status"])
    return chosen


async def _gemini_complete(system: str, user: str, max_tokens: int) -> str | None:
    import httpx

    model = _gemini["model"]
    if not model:
        return None
    s = get_settings()
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.2},
    }
    url = f"{s.gemini_api_base.rstrip('/')}/models/{model}:generateContent"
    async with httpx.AsyncClient(timeout=s.llm_timeout) as c:
        r = await asyncio.wait_for(c.post(url, json=body, headers=_gemini_headers()), timeout=s.llm_timeout)
    if r.status_code != 200:
        log.warning("Gemini HTTP %s — shablon javob", r.status_code)
        return None
    data = r.json()
    if (data.get("promptFeedback") or {}).get("blockReason"):
        log.warning("Gemini so'rovni blokladi — shablon javob")
        return None
    cands = data.get("candidates") or []
    if not cands or cands[0].get("finishReason") not in (None, "STOP", "MAX_TOKENS"):
        log.warning("Gemini javobi yo'q (%s) — shablon javob", cands[0].get("finishReason") if cands else "bo'sh")
        return None
    parts = (cands[0].get("content") or {}).get("parts") or []
    return "".join(p.get("text", "") for p in parts if not p.get("thought")).strip() or None


# ------------------------------------------------------------------ umumiy

def is_available() -> bool:
    if provider() == "gemini":
        s = get_settings()
        # startup tekshiruvigacha ham sozlangan model bilan urinib ko'riladi
        if not _gemini["checked"] and s.gemini_api_key.strip():
            _gemini["model"] = _gemini["model"] or s.gemini_model.strip() or None
        return bool(s.gemini_api_key.strip() and _gemini["model"])
    return _client() is not None


def status() -> dict:
    if provider() == "gemini":
        return {"provider": "gemini", "model": _gemini["model"], "status": _gemini["status"]}
    return {"provider": "anthropic", "model": get_settings().llm_model if _client() else None}


async def complete(system: str, user: str, *, max_tokens: int | None = None) -> str | None:
    """Bitta so'rov -> matn. Xatoda / vaqt o'tganda None (shablon javob ishlatiladi)."""
    if not is_available():
        return None
    s = get_settings()
    safe_user = scrub(user)  # shaxsiy ma'lumot LLM'ga yuborilmaydi
    try:
        if provider() == "gemini":
            return await _gemini_complete(system, safe_user, max_tokens or s.llm_max_tokens)
        return await _anthropic_complete(system, safe_user, max_tokens or s.llm_max_tokens)
    except asyncio.TimeoutError:
        log.warning("LLM %.1f s ichida javob bermadi — shablon javob ishlatiladi", s.llm_timeout)
        return None
    except Exception as e:  # noqa: BLE001 — har qanday xato fallback'ga olib keladi (kalit logga chiqmaydi)
        log.warning("LLM chaqiruvi muvaffaqiyatsiz (%s) — shablon javob", type(e).__name__)
        return None


async def complete_json(system: str, user: str, *, max_tokens: int | None = None) -> dict | None:
    """JSON javob kutiladigan so'rov. Parse bo'lmasa None."""
    text = await complete(system, user, max_tokens=max_tokens)
    if not text:
        return None
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        log.warning("LLM JSON parse xatosi")
        return None
