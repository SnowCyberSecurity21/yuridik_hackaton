"""Dashboard jonli ko'rinishi uchun SOXTA anonim analitika (14 hudud, 28 kun).

Hech qanday shaxsiy ma'lumot yo'q — hodisalarda faqat mavzu, hudud, til, kanal, vaqt.
Barcha yozuvlar is_demo=True; qayta ishga tushirilsa avvalgi demo yozuvlar o'chiriladi.

Ishga tushirish:  python scripts/seed_demo_data.py [--count 6000] [--clear]
"""
from __future__ import annotations

import argparse
import random
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.config import REGIONS  # noqa: E402
from app.db import SessionLocal, init_db  # noqa: E402
from app.models import Event, utcnow  # noqa: E402

# Nisbiy og'irliklar (demo uchun; real statistika emas)
TOPICS = {
    "child_allowance_refused": 30, "alimony": 22, "mib_debt_travel_ban": 12, "traffic_fine": 11,
    "unpaid_salary": 8, "utility_debt_court_order": 6, "online_loan_fraud": 4, "fake_mib_sms": 3,
    "mahalla_noise_waste_fine": 2, "consumer_refund": 2,
}
# "Tushunilmadi" ulushi (misunderstanding signal uchun)
NOT_HELPFUL = {"child_allowance_refused": 0.32, "alimony": 0.28, "mib_debt_travel_ban": 0.22,
               "utility_debt_court_order": 0.35, "traffic_fine": 0.12}
# Oxirgi haftada o'sayotgan mavzular (WoW trend ko'rinishi uchun)
GROWING = {"child_allowance_refused": 1.45, "online_loan_fraud": 1.6, "fake_mib_sms": 1.8}
REGION_W = {"toshkent_sh": 14, "samarqand": 11, "fargona": 11, "andijon": 10, "namangan": 9, "qashqadaryo": 10,
            "surxondaryo": 8, "toshkent_vil": 9, "buxoro": 6, "xorazm": 6, "qoraqalpogiston": 6, "jizzax": 4,
            "navoiy": 3, "sirdaryo": 3}
CLAIMS = {"claim_car_new_tax_jan1": ("notogri", 60), "claim_mib_sms_link_pay": ("notogri", 35),
          "claim_fine_discount_70": ("qisman", 25), "claim_alimony_stops_at_16": ("tasdiqlanmagan", 15)}
LANGS = (["uz"] * 70) + (["uz_cyrl"] * 18) + (["ru"] * 12)
CHANNELS = (["telegram"] * 85) + (["miniapp"] * 10) + (["web"] * 5)


def pick(weights: dict) -> str:
    return random.choices(list(weights), weights=list(weights.values()))[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=6000)
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--clear", action="store_true", help="faqat demo yozuvlarni o'chirish")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    random.seed(args.seed)

    init_db()
    db = SessionLocal()
    removed = db.query(Event).filter(Event.is_demo.is_(True)).delete()
    db.commit()
    print(f"o'chirildi: {removed} ta eski demo yozuv")
    if args.clear:
        return

    now = utcnow()
    assert set(REGION_W) == {r["id"] for r in REGIONS}
    rows = []
    for _ in range(args.count):
        topic = pick(TOPICS)
        day = random.random() ** 1.25 * args.days  # yaqin kunlarga biroz ko'proq (o'sish trendi)
        if topic in GROWING and day < 7 and random.random() < (GROWING[topic] - 1):
            day = random.random() * 7
        ts = now - timedelta(days=day, hours=random.random() * 3)
        helpful = None
        if random.random() < 0.55:
            helpful = random.random() >= NOT_HELPFUL.get(topic, 0.15)
        appeal = helpful is False and random.random() < 0.45
        is_sms = topic in ("traffic_fine", "fake_mib_sms") and random.random() < 0.6
        rows.append(Event(ts=ts, kind="sms" if is_sms else "ask", topic_id=topic, region=pick(REGION_W),
                          lang=random.choice(LANGS), channel=random.choice(CHANNELS),
                          answer_type="sms" if is_sms else "card", confidence=round(random.uniform(0.5, 0.97), 2),
                          was_helpful=helpful, appeal_requested=appeal, is_demo=True))
    # topilmagan savollar
    for _ in range(args.count // 25):
        rows.append(Event(ts=now - timedelta(days=random.random() * args.days), kind="ask", region=pick(REGION_W),
                          lang=random.choice(LANGS), channel="telegram", answer_type="not_found",
                          confidence=round(random.uniform(0.0, 0.3), 2), is_demo=True))
    # fakt-tekshiruvlar (feyk signal paneli)
    for cid, (verdict, n) in CLAIMS.items():
        for _ in range(n * max(1, args.count // 3000)):
            rows.append(Event(ts=now - timedelta(days=random.random() * 13), kind="factcheck", claim_id=cid,
                              verdict=verdict, region=pick(REGION_W), lang=random.choice(LANGS),
                              channel="telegram", answer_type="factcheck", is_demo=True))
    db.add_all(rows)
    db.commit()
    print(f"qo'shildi: {len(rows)} ta demo hodisa ({args.days} kun, 14 hudud). Shaxsiy ma'lumot yo'q.")


if __name__ == "__main__":
    main()
