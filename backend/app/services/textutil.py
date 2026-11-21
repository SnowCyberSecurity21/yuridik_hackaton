"""Matn yordamchilari: transliteratsiya (lotin<->kirill), normalizatsiya, til aniqlash."""
from __future__ import annotations

import re
import unicodedata

APOSTROPHES = "ʻʼ’‘`´'ʹ"
_APOS_RE = re.compile(f"[{re.escape(APOSTROPHES)}]")

# --- Kirill -> lotin (o'zbek + rus harflari) -------------------------------
_CYR2LAT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo", "ж": "j",
    "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
    "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "x", "ц": "ts",
    "ч": "ch", "ш": "sh", "щ": "sh", "ъ": "'", "ы": "i", "ь": "", "э": "e", "ю": "yu",
    "я": "ya", "ў": "o'", "қ": "q", "ғ": "g'", "ҳ": "h",
}


def cyr_to_lat(text: str) -> str:
    out = []
    for ch in text:
        low = ch.lower()
        if low in _CYR2LAT:
            rep = _CYR2LAT[low]
            if ch != low and rep:
                rep = rep[0].upper() + rep[1:]
            out.append(rep)
        else:
            out.append(ch)
    return "".join(out)


# --- Lotin -> kirill (o'zbek) ----------------------------------------------
_LAT2CYR_MULTI = [
    ("o'", "ў"), ("g'", "ғ"), ("sh", "ш"), ("ch", "ч"), ("yo", "ё"), ("yu", "ю"),
    ("ya", "я"), ("ye", "е"), ("ts", "ц"),
]
_LAT2CYR_SINGLE = {
    "a": "а", "b": "б", "d": "д", "e": "е", "f": "ф", "g": "г", "h": "ҳ", "i": "и",
    "j": "ж", "k": "к", "l": "л", "m": "м", "n": "н", "o": "о", "p": "п", "q": "қ",
    "r": "р", "s": "с", "t": "т", "u": "у", "v": "в", "x": "х", "y": "й", "z": "з",
    "'": "ъ",
}


def lat_to_cyr(text: str) -> str:
    """O'zbek lotin -> kirill. URL va TODO_LAWYER kabi texnik so'zlarga tegmaydi."""
    parts = re.split(r"(https?://\S+|TODO_LAWYER|[A-Z]{2,}[_A-Z0-9]*)", text)
    return "".join(p if i % 2 else _lat_to_cyr_plain(p) for i, p in enumerate(parts))


def _lat_to_cyr_plain(text: str) -> str:
    text = _APOS_RE.sub("'", text)
    res: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        low_pair = text[i : i + 2].lower()
        matched = False
        for lat, cyr in _LAT2CYR_MULTI:
            if low_pair == lat:
                rep = cyr.upper() if ch.isupper() else cyr
                res.append(rep)
                i += 2
                matched = True
                break
        if matched:
            continue
        low = ch.lower()
        if low == "e" and (i == 0 or not text[i - 1].isalpha()):
            rep = "э"  # so'z boshidagi e -> э
        elif low in _LAT2CYR_SINGLE:
            rep = _LAT2CYR_SINGLE[low]
        else:
            res.append(ch)
            i += 1
            continue
        res.append(rep.upper() if ch.isupper() else rep)
        i += 1
    return "".join(res)


# --- Normalizatsiya ---------------------------------------------------------
_NON_WORD = re.compile(r"[^0-9a-z' ]+")


def normalize(text: str) -> str:
    """Klassifikatsiya uchun: kichik harf, kirill->lotin, apostroflarni birlashtirish."""
    text = unicodedata.normalize("NFC", text or "")
    text = cyr_to_lat(text).lower()
    text = _APOS_RE.sub("'", text)
    text = _NON_WORD.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


# --- Til / yozuv aniqlash ---------------------------------------------------
_UZ_CYR_ONLY = set("ўқғҳЎҚҒҲ")
_RU_MARKERS = set("ыэщъЫЭЩЪ")
_RU_WORDS = {"что", "как", "почему", "мне", "не", "мой", "моя", "где", "есть", "это", "для", "нет", "штраф", "пособие"}


def detect_lang(text: str) -> str:
    """'uz' (lotin), 'uz_cyrl' yoki 'ru'."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return "uz"
    cyr = sum(1 for c in letters if "Ѐ" <= c <= "ӿ")
    if cyr / len(letters) < 0.5:
        return "uz"
    if any(c in _UZ_CYR_ONLY for c in text):
        return "uz_cyrl"
    words = set(re.findall(r"[а-яё]+", text.lower()))
    if any(c in _RU_MARKERS for c in text) or words & _RU_WORDS:
        return "ru"
    return "uz_cyrl"


def to_script(text: str, lang: str) -> str:
    """Lotin matnni foydalanuvchi yozuviga moslash."""
    return lat_to_cyr(text) if lang == "uz_cyrl" else text
