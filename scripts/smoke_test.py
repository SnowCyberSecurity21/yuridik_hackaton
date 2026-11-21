"""Smoke test ishlab turgan serverga: /api/ask'ga 3 ta demo so'rov — javob va manba qaytishini tekshiradi.

Ishga tushirish:  python scripts/smoke_test.py [--base http://localhost:8000]
Chiqish kodi: 0 — hammasi o'tdi, 1 — xato bor.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

CASES = [
    ("Bola nafaqasi", {"text": "Bolamga nafaqa nega berilmadi?", "region": "samarqand", "channel": "cli"},
     {"type": "card", "card_id": "child_allowance_refused"}),
    ("Jarima SMS", {"text": "Aliyev Vali, 01.01.1990. Invoys 1234567890123. To'lov 15.11.2026dan. JARIMA 44 000.00 so'm, "
                            "30.12.2026gacha 22 000.00 so'm(50%). Organ YHXB DEMO / TOSHKENT", "channel": "cli"},
     {"type": "sms", "card_id": "traffic_fine"}),
    ("Feyk post", {"text": "1-yanvardan hamma mashinaga yangi soliq! Tarqating!", "mode": "factcheck", "channel": "cli"},
     {"type": "factcheck", "verdict": "notogri"}),
]


def post(base: str, path: str, body: dict) -> dict:
    req = urllib.request.Request(base.rstrip("/") + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def profile_case(base: str) -> int:
    """«Mening huquqlarim»: mock MyGov kirish -> imtiyoz "Haqli bo'lishingiz mumkin" -> bir bosishda ariza."""
    key = "web:smoke_test_user"
    try:
        v = post(base, "/api/profile/login", {"user_key": key, "profile_id": "demo_mother", "consent": True})
        a = post(base, "/api/profile/appeal", {"user_key": key, "benefit_id": "benefit_child_allowance"})
        post(base, "/api/profile/logout", {"user_key": key})
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"❌ Profil: xato ({e})")
        return 1
    problems = []
    if not v.get("benefits") or any(b.get("status_text") != "Haqli bo'lishingiz mumkin" for b in v["benefits"]):
        problems.append("imtiyoz holati noto'g'ri")
    if "albatta" in json.dumps(v, ensure_ascii=False).lower():
        problems.append("'albatta' so'zi bor")
    if "ARIZA" not in a.get("text", ""):
        problems.append("ariza yaratilmadi")
    print(f"\n{'✅' if not problems else '❌'} Profil (2 bolali ona): imtiyozlar={[b['title'] for b in v.get('benefits', [])]}")
    for p in problems:
        print(f"   ⚠️ {p}")
    return int(bool(problems))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8000")
    args = ap.parse_args()
    failed = 0
    for name, body, expect in CASES:
        try:
            res = post(args.base, "/api/ask", body)
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"❌ {name}: server bilan aloqa yo'q ({e})")
            failed += 1
            continue
        problems = [f"{k}={res.get(k)!r} (kutilgan {v!r})" for k, v in expect.items() if res.get(k) != v]
        sources = res.get("sources") or []
        if not sources or not all(str(s.get("url", "")).startswith("https://") for s in sources):
            problems.append("manba (sources) yo'q")
        if not res.get("text"):
            problems.append("javob matni bo'sh")
        if name == "Jarima SMS" and ("Aliyev" in res.get("text", "") or "1990" in res.get("text", "")):
            problems.append("shaxsiy ma'lumot javobga chiqdi")
        status = "✅" if not problems else "❌"
        failed += bool(problems)
        print(f"\n{status} {name}: type={res.get('type')} card={res.get('card_id')} "
              f"verdict={res.get('verdict')} manbalar={len(sources)}")
        for s in sources[:2]:
            print(f"   📚 {s.get('doc')} — {s.get('url')}")
        print("   " + "\n   ".join(res.get("text", "").splitlines()[:3]))
        for p in problems:
            print(f"   ⚠️ {p}")
    failed += profile_case(args.base)
    print(f"\n{'HAMMASI O‘TDI' if not failed else f'{failed} ta xato'} ({len(CASES)} ta so'rov + profil)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
