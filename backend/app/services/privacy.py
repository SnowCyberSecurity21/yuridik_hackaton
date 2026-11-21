"""LLM'ga yuborishdan oldin shaxsiy ma'lumotni olib tashlash (har qanday provayder uchun markaziy filtr).

Olib tashlanadi: SMS boshidagi "F.I.Sh., tug'ilgan sana.", telefon, e-pochta, PINFL (14 raqam), pasport seriyasi,
bank karta raqami, sanalar (tug'ilgan sana bo'lishi mumkin), familiya shaklidagi so'zlar (-ov/-ova/-ev/-eva, o'g'li/qizi).
Cheklov: oddiy ism (familiyasiz) har doim ham aniqlanmaydi — shuning uchun javob baribir faqat kartadan olinadi.
"""
from __future__ import annotations

import re

from .sms_parser import redact as _redact_sms_header

_RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[e-pochta]"),
    (re.compile(r"(?<!\d)\d{14}(?!\d)"), "[PINFL]"),
    (re.compile(r"(?<!\d)(?:\d{4}[ -]?){3}\d{4}(?!\d)"), "[karta]"),
    (re.compile(r"\b[A-ZА-Я]{2}\s?\d{7}\b"), "[pasport]"),
    (re.compile(r"(?:\+?998[\s-]?)\(?\d{2}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}(?!\d)"), "[telefon]"),
    (re.compile(r"(?<![\d.])\(?(?:9\d|33|50|55|77|88|20|71)\)?[\s-]\d{3}[\s-]\d{2}[\s-]\d{2}(?!\d)"), "[telefon]"),
    (re.compile(r"(?<!\d)\d{1,2}[./]\d{1,2}[./](?:19|20)\d{2}(?!\d)"), "[sana]"),
    (re.compile(r"\b[A-ZА-ЯЎҚҒҲ][a-zа-яўқғҳ'ʻ’]+(?:ov|ova|ev|eva|yev|yeva|ова|ов|ева|ев)\b(?:\s+[A-ZА-ЯЎҚҒҲ][a-zа-яўқғҳ'ʻ’]+)?"),
     "[F.I.Sh.]"),
    (re.compile(r"\b[A-ZА-ЯЎҚҒҲ][a-zа-яўқғҳ'ʻ’]+\s+(?:o['ʻ’]g['ʻ’]li|qizi|ўғли|қизи)\b"), "[F.I.Sh.]"),
]


def scrub(text: str | None) -> str:
    s = _redact_sms_header(text or "")
    for rx, repl in _RULES:
        s = rx.sub(repl, s)
    return s
