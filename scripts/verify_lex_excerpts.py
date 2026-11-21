"""Qonun abzaslarini lex.uz bilan solishtirish: har `original_text` rasmiy sahifada AYNAN bormi.

Ishlatish:  python scripts/verify_lex_excerpts.py            # hammasi
            python scripts/verify_lex_excerpts.py ex_stip_def  # bittasi
lex.uz sekin yoki ochilmasa — o'sha hujjat «tekshirib bo'lmadi» deb belgilanadi (yozuv o'zgartirilmaydi).
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urldefrag

import httpx

ROOT = Path(__file__).resolve().parents[1]
PARA = re.compile(r'<div class="([A-Z_]+) lx_elem"[^>]*>.*?<div name="(-?\d+)" id="\2">(.*?)</div>', re.S)
NOISE = re.compile(r'<div class="(?:COMMENT|CHANGES_ORIGINS|INDEXES_ON_REF)[^"]*".*?</div>', re.S)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def page_paragraphs(url: str, client: httpx.Client) -> list[str] | None:
    try:
        r = client.get(url)
        r.raise_for_status()
    except httpx.HTTPError as e:
        print(f"  ⚠️ {url}: {e!r}")
        return None
    raw = NOISE.sub("", r.text)
    return [norm(html.unescape(re.sub(r"<[^>]+>", "", m.group(3)))) for m in PARA.finditer(raw)]


def main(only: list[str]) -> int:
    data = json.loads((ROOT / "knowledge" / "lex" / "excerpts.json").read_text(encoding="utf-8"))
    items = [e for e in data["excerpts"] if e.get("original_text") and (not only or e["id"] in only)]
    cache: dict[str, list[str] | None] = {}
    bad = unreachable = 0
    with httpx.Client(timeout=90, headers={"User-Agent": "Mozilla/5.0 (Huquqim lex verifier)"}, follow_redirects=True) as c:
        for e in items:
            url, _ = urldefrag(e["lex_url"])
            if url not in cache:
                cache[url] = page_paragraphs(url, c)
            paras = cache[url]
            if paras is None:
                unreachable += 1
                continue
            parts = [norm(p) for p in e["original_text"].split("\n") if p.strip() and p.strip() != "…"]
            joined = " ".join(paras)  # bir necha qo'shni paragraf bitta qatorga yozilgan bo'lishi mumkin
            missing = [p for p in parts if p not in paras and p not in joined]
            if missing:
                bad += 1
                print(f"❌ {e['id']}: {len(missing)} ta paragraf topilmadi — «{missing[0][:90]}…»")
            else:
                print(f"✅ {e['id']} ({e['article']})")
    print(f"\nJami {len(items)}; mos kelmadi: {bad}; tekshirib bo'lmadi: {unreachable}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
