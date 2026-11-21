"""Jonli smoke test: anonim yo'l, 6 ta demo ID shaxsi bilan tasdiqlash, imtiyoz -> ariza, rollar, Telegram link havolasi.

Ishlatish:  python scripts/smoke_accounts.py --base https://huquqim.zehnprotect.uz
Har ishga tushirishda yangi demo hisoblar yaratiladi (smoke_<vaqt>_<login>).
"""
from __future__ import annotations

import argparse
import sys
import time
from urllib.parse import parse_qs, urlparse

import httpx

PERSONS = ["Azizbek", "Malika", "Karim", "Sardor", "Dilnoza", "Erlan", "Jasur"]
ok_all = True


def check(name: str, cond: bool, extra: str = "") -> None:
    global ok_all
    ok_all &= bool(cond)
    print(("✅" if cond else "❌"), name, extra)


def verify(base: str, login: str, tag: str) -> httpx.Client:
    c = httpx.Client(base_url=base, timeout=30, follow_redirects=False)
    r = c.post("/api/auth/register", json={"username": f"smoke_{tag}_{login.lower()}", "password": "smoke-parol-1"})
    r.raise_for_status()
    loc = c.get("/api/oneid/start").headers["location"]
    q = {k: v[0] for k, v in parse_qs(urlparse(loc).query).items()}
    form = {"client_id": q["client_id"], "redirect_uri": q["redirect_uri"], "state": q["state"]}
    page = c.get(loc).text
    assert "DEMO identifikatsiya" in page
    r = c.post("/oneid-demo/login", data={**form, "login": login, "password": "12345678"})
    c.get(r.headers["location"])
    r = c.post("/oneid-demo/consent", data={**form, "decision": "allow"})
    r = c.get(r.headers["location"])
    assert r.headers["location"] == "/kabinet?oneid=ok", r.headers.get("location")
    return c


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8000")
    base = ap.parse_args().base.rstrip("/")
    tag = time.strftime("%H%M%S")
    pub = httpx.Client(base_url=base, timeout=30, follow_redirects=False)

    for path in ("/", "/anonim", "/kirish", "/miniapp"):
        r = pub.get(path)
        check(f"GET {path}", r.status_code == 200 and "<div id=\"root\">" in r.text, str(r.status_code))
    check("/dashboard basic auth", pub.get("/dashboard").status_code == 401)
    check("/api/gov basic auth", pub.get("/api/gov/overview").status_code == 401)
    r = pub.post("/api/ask", json={"text": "Bolamga nafaqa nega berilmadi?", "legal_status": "foreign", "channel": "web"}).json()
    check("anonim savol + maqom eslatmasi", r.get("type") == "card" and bool(r.get("status_note")))
    r = pub.post("/api/ask", json={"text": "F.I.O., 01.01.2000. Invoys 123. JARIMA 44 000.00 so'm, 10.12.2026gacha 22 000.00 so'm(50%). Organ YHXB / TOSHKENT", "mode": "sms"}).json()
    check("anonim SMS", r.get("type") in ("sms", "card"), r.get("type", ""))
    r = pub.post("/api/ask", json={"text": "1-yanvardan hamma mashinaga yangi soliq", "mode": "factcheck"}).json()
    check("anonim feyk tekshiruvi", "text" in r)
    r = pub.get("/api/rights?status=stateless&situations=parent").json()
    check("anonim huquqlar (fuqaroligi yo'q)", r["status"]["id"] == "stateless" and len(r["laws"]) >= 3)

    for login in PERSONS:
        try:
            c = verify(base, login, tag)
            v = c.get("/api/me/cabinet").json()
            check(f"OneID: {login}", "person" in v, f"{v['person']['status']} · imtiyoz {len(v['benefits'])} · qonun {len(v['laws'])} · rollar {v['roles']}")
            if login == "Malika":
                b = v["benefits"][0]["id"]
                a = c.post("/api/me/appeal", json={"benefit_id": b}).json()
                check("imtiyoz -> ariza (Malika)", "ARIZA" in a.get("text", "").upper(), b)
            if login == "Dilnoza":
                check("Davlat kabineti (Dilnoza)", c.get("/api/cabinet/gov/overview").status_code == 200)
            if login == "Azizbek":
                check("Ta'lim (Azizbek)", c.get("/api/edu/cases").status_code == 200)
                check("Azizbek davlat kabinetiga kira olmaydi", c.get("/api/cabinet/gov/overview").status_code == 403)
            if login == "Sardor":
                link = c.post("/api/me/telegram/link").json()
                check("Telegram link havolasi (Sardor)", link["url"].startswith("https://t.me/"), link["url"])
            check(f"rozilikni bekor qilish ({login})", c.post("/api/oneid/revoke").json()["ok"]) if login == "Karim" else None
        except Exception as e:  # noqa: BLE001
            check(f"OneID: {login}", False, repr(e))
    print("\nHAMMASI O'TDI" if ok_all else "\nXATOLAR BOR")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
