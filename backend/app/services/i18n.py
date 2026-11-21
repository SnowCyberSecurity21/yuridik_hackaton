"""UI matnlari: uz (lotin, standart), uz_cyrl (lotindan avtomatik), ru."""
from __future__ import annotations

import json
from functools import lru_cache

from ..config import get_settings
from .textutil import lat_to_cyr

LANGS = ("uz", "uz_cyrl", "ru")


@lru_cache
def _load(lang: str) -> dict[str, str]:
    base = get_settings().knowledge_dir / "i18n"
    try:
        uz = json.loads((base / "uz.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        uz = {}
    if lang == "ru":
        try:
            return {**uz, **json.loads((base / "ru.json").read_text(encoding="utf-8"))}
        except (OSError, json.JSONDecodeError):
            return uz
    if lang == "uz_cyrl":
        return {k: lat_to_cyr(v) for k, v in uz.items()}
    return uz


def strings(lang: str) -> dict[str, str]:
    return _load(lang if lang in LANGS else "uz")


def t(lang: str, key: str, **kw) -> str:
    s = strings(lang).get(key) or strings("uz").get(key, key)
    return s.format(**kw) if kw else s
