"""Mavjud kartalar va imtiyozlardagi legal_basis'ni lex.uz'da tekshirilgan hujjat havolalari bilan yangilaydi.

Faqat hujjat darajasida (modda raqami TODO_LAWYER bo'lib qoladi). Tekshirilmagan hujjatlar o'zgarmaydi
va «manba topilmadi» ro'yxatiga chiqariladi.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "knowledge"
VERIFIED = {  # hujjat nomidagi kalit so'z -> (lex.uz URL, rasmiy nom, sana)
    "Oila kodeksi": ("https://lex.uz/docs/104720", "O'zbekiston Respublikasining Oila kodeksi", "1998-04-30"),
    "Ma'muriy javobgarlik to'g'risidagi kodeks": ("https://lex.uz/docs/97664", "O'zbekiston Respublikasining Ma'muriy javobgarlik to'g'risidagi kodeksi", "1994-09-22"),
    "Mehnat kodeksi": ("https://lex.uz/docs/6257288", "O'zbekiston Respublikasining Mehnat kodeksi", "2022-10-28"),
    "davlat pensiya ta'minoti": ("https://lex.uz/docs/112314", "Fuqarolarning davlat pensiya ta'minoti to'g'risida (938-XII)", "1993-09-03"),
}
not_found = []
for folder in ("cards", "benefits"):
    for p in sorted((ROOT / folder).glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        changed = False
        for b in d.get("legal_basis", []):
            hit = next((v for k, v in VERIFIED.items() if k in (b.get("doc") or "")), None)
            if hit:
                b["lex_url"], b["doc"], b["doc_date"] = hit[0], hit[1], hit[2]
                b["retrieved_at"], b["source_type"], b["source_verified"] = "2026-11-21", "lex.uz", True
                changed = True
            elif not b.get("source_verified"):
                not_found.append(f"{folder}/{p.name}: {b.get('doc')}")
        if changed:
            p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("MANBA TOPILMADI:")
print("\n".join(sorted(set(not_found))))
