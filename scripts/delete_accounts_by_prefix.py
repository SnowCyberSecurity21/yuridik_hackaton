"""Demo hisoblarni prefiks bo'yicha o'chirish (masalan smoke_). Standart — faqat ko'rsatadi; --apply bilan o'chiradi.

O'chiriladi: accounts, ularning web_sessions, telegram_links, bot_link_tokens va DEMO ID grantlari.
Ishlatish (serverda): python scripts/delete_accounts_by_prefix.py smoke_ [--apply]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.db import SessionLocal, init_db  # noqa: E402
from app.models import Account, BotLinkToken, TelegramLink, WebSession  # noqa: E402
from app.oneid_demo import service as oneid  # noqa: E402

prefix = sys.argv[1] if len(sys.argv) > 1 else ""
apply = "--apply" in sys.argv
if len(prefix) < 3 or not prefix.endswith("_"):
    sys.exit("prefiks kamida 3 belgi va '_' bilan tugashi kerak (masalan smoke_)")
init_db()
db = SessionLocal()
try:
    accs = db.query(Account).filter(Account.username.like(prefix.replace("_", r"\_") + "%", escape="\\")).all()
    accs = [a for a in accs if a.username.startswith(prefix)]
    print(f"topildi: {len(accs)} ta hisob ({prefix}*)", [a.username for a in accs][:50])
    total_other = db.query(Account).count() - len(accs)
    if apply:
        for a in accs:
            if a.oneid_token:
                oneid.revoke(db, a.oneid_token)
            db.query(WebSession).filter(WebSession.account_id == a.id).delete()
            db.query(TelegramLink).filter(TelegramLink.account_id == a.id).delete()
            db.query(BotLinkToken).filter(BotLinkToken.account_id == a.id).delete()
            db.delete(a)
        db.commit()
        print("o'chirildi:", len(accs))
    print("boshqa hisoblar (tegilmadi):", total_other)
finally:
    db.close()
