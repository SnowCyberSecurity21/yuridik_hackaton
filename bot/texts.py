"""Bot UI matnlari: knowledge/i18n'dan (uz, ru); kirill — lotindan avtomatik."""
from __future__ import annotations

import json
from functools import lru_cache

from config import settings

_CYR = [("o'", "ў"), ("g'", "ғ"), ("sh", "ш"), ("ch", "ч"), ("yo", "ё"), ("yu", "ю"), ("ya", "я")]
_MAP = dict(zip("abdefghijklmnopqrstuvxyz'", "абдэфгҳижклмнопқрстувхйзъ"))

_FALLBACK = {
    "error_generic": "Kechirasiz, hozir javob bera olmadim. Birozdan keyin qayta urinib ko'ring.",
    "voice_unsupported": "🎙 Ovozli xabar hozircha qo'llab-quvvatlanmaydi. Iltimos, savolingizni yozib yuboring.",
}


def _to_cyr(s: str) -> str:
    out, i = [], 0
    low = s.lower()
    while i < len(s):
        for lat, cyr in _CYR:
            if low[i:i + 2] == lat:
                out.append(cyr.upper() if s[i].isupper() else cyr)
                i += 2
                break
        else:
            ch = s[i]
            c = _MAP.get(ch.lower())
            if ch.lower() == "e" and i > 0 and s[i - 1].isalpha():
                c = "е"  # so'z o'rtasida — е, boshida — э
            out.append((c.upper() if ch.isupper() else c) if c else ch)
            i += 1
    return "".join(out)


@lru_cache
def _load(lang: str) -> dict:
    base = {}
    try:
        base = json.loads((settings.i18n_dir / "uz.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    if lang == "ru":
        try:
            base = {**base, **json.loads((settings.i18n_dir / "ru.json").read_text(encoding="utf-8"))}
        except (OSError, json.JSONDecodeError):
            pass
    if lang == "uz_cyrl":
        base = {k: _to_cyr(v) for k, v in base.items()}
    return {**_FALLBACK, **base}


def tr(lang: str | None, key: str, **kw) -> str:
    s = _load(lang or "uz").get(key) or _load("uz").get(key) or key
    return s.format(**kw) if kw else s
