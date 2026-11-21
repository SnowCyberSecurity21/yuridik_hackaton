"""Jarima / MIB / sud SMS'larini tahlil qilish (regex; LLM — ixtiyoriy yordamchi).

Shaxsiy ma'lumot (F.I.Sh., tug'ilgan sana) natijaga ham, logga ham tushmaydi.
Namuna:
F.I.O., DD.MM.YYYY. Invoys <raqam>. To'lov <sana>dan. JARIMA 44 000.00 so'm, <sana>gacha 22 000.00 so'm(50%). Organ <ORGAN> / <SHAHAR>
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from urllib.parse import urlparse

from .textutil import APOSTROPHES, cyr_to_lat

_AP = re.compile(f"[{re.escape(APOSTROPHES)}]")
DATE = r"(\d{2}[./]\d{2}[./]\d{4})"
MONEY = r"(\d{1,3}(?:[  ]?\d{3})*(?:[.,]\d{1,2})?)"

RE_INVOICE = re.compile(r"invoys\s*(?:raqami)?\s*[:№#]?\s*([0-9A-Za-z\-]{4,})", re.I)
RE_FINE = re.compile(r"jarima\s*[:\-]?\s*" + MONEY + r"\s*so'?m", re.I)
RE_DISCOUNT = re.compile(DATE + r"\s*gacha\s*" + MONEY + r"\s*so'?m\s*\(?\s*(\d{1,3})\s*%", re.I)
RE_PAY_FROM = re.compile(r"to'?lov\s*" + DATE + r"\s*dan", re.I)
RE_ORGAN = re.compile(r"organ\s*[:\-]?\s*([^/\n]+?)\s*(?:/\s*([^\n.]+))?\s*\.?\s*$", re.I | re.M)
RE_DEBT = re.compile(r"(?:qarz(?:dorlik|ingiz)?|summa)\s*[:\-]?\s*" + MONEY + r"\s*so'?m", re.I)
RE_URL = re.compile(r"(https?://[^\s]+|www\.[^\s]+|\b[a-z0-9\-]+\.(?:com|net|org|info|xyz|top|site|online|click|link|uz)\b[^\s]*)", re.I)
RE_LEADING_PII = re.compile(r"^\s*[^,\n]{3,60},\s*\d{2}[./]\d{2}[./]\d{4}\.?\s*")

OFFICIAL_SUFFIXES = (".gov.uz", "gov.uz", "lex.uz", "sud.uz")
SCAM_WORDS = ["bloklan", "24 soat", "shoshiling", "karta raqam", "sms kod", "kodni yuboring", "cvv", "parol",
              "darhol to'lang", "havola orqali"]


def _clean(text: str) -> str:
    return _AP.sub("'", cyr_to_lat(text or ""))


def _money(s: str | None) -> float | None:
    if not s:
        return None
    s = s.replace(" ", " ").replace(" ", "")
    if "," in s and "." not in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _date(s: str | None) -> date | None:
    if not s:
        return None
    for fmt in ("%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def redact(text: str) -> str:
    """Boshidagi 'F.I.Sh., tug'ilgan sana.' qismini olib tashlaydi."""
    return RE_LEADING_PII.sub("", text or "", count=1)


def _domains(text: str) -> list[str]:
    out = []
    for u in RE_URL.findall(text):
        u2 = u if u.startswith("http") else "http://" + u
        host = (urlparse(u2).hostname or "").lower()
        if host:
            out.append(host)
    return out


def suspicious_signals(text: str) -> list[str]:
    t = _clean(text).lower()
    sig = []
    for host in _domains(t):
        if not host.endswith(OFFICIAL_SUFFIXES):
            sig.append(f"rasmiy bo'lmagan havola: {host}")
    for w in SCAM_WORDS:
        if w in t:
            sig.append(f"shubhali ibora: \"{w}\"")
    return sig


def detect_kind(text: str) -> str | None:
    """fine | mib | court | suspicious | None"""
    t = _clean(text).lower()
    sus = suspicious_signals(text)
    has_link = bool(_domains(t))
    if has_link and sus and any(k in t for k in ("mib", "ijro", "qarz", "jarima", "to'la")):
        return "suspicious"
    if "jarima" in t and ("invoys" in t or "so'm" in t or "som" in t):
        return "fine"
    if "sud buyrug" in t:
        return "court"
    if ("mib" in t or "majburiy ijro" in t) and ("qarz" in t or "so'm" in t):
        return "mib"
    return None


def parse(text: str, today: date | None = None) -> dict:
    today = today or date.today()
    raw = redact(_clean(text))
    kind = detect_kind(text)
    res: dict = {"kind": kind, "pii_removed": raw != _clean(text)}

    if m := RE_INVOICE.search(raw):
        res["invoice"] = m.group(1)
    if m := RE_FINE.search(raw):
        res["amount"] = _money(m.group(1))
    if m := RE_DISCOUNT.search(raw):
        d = _date(m.group(1).replace("/", "."))
        res["discount_deadline"] = d.isoformat() if d else None
        res["discount_amount"] = _money(m.group(2))
        res["discount_percent"] = int(m.group(3))
        if d:
            res["days_left"] = (d - today).days
            rem = d - timedelta(days=2)
            res["reminder_date"] = (rem if rem > today else today).isoformat()
    if m := RE_PAY_FROM.search(raw):
        d = _date(m.group(1).replace("/", "."))
        res["pay_from"] = d.isoformat() if d else None
    if m := RE_ORGAN.search(raw):
        res["organ"] = m.group(1).strip(" .,")
        if m.group(2):
            res["city"] = m.group(2).strip(" .,")
    if kind in ("mib", "court", "suspicious") and "amount" not in res:
        if m := RE_DEBT.search(raw):
            res["amount"] = _money(m.group(1))
    if kind == "suspicious":
        res["suspicious_signals"] = suspicious_signals(text)
    return res


def kind_to_card(kind: str | None) -> str | None:
    return {"fine": "traffic_fine", "mib": "mib_debt_travel_ban", "court": "utility_debt_court_order",
            "suspicious": "fake_mib_sms"}.get(kind or "")


def fmt_money(v: float | None) -> str:
    if v is None:
        return "—"
    return f"{v:,.0f}".replace(",", " ") + " so'm"
