"""Tokensiz lokal sinov: bot xuddi Telegram'dagidek backend /api/ask orqali javob beradi.

Ishga tushirish:  python bot/cli.py        (backend http://localhost:8000 da ishlab turishi kerak)
Buyruqlar: /tekshir <matn> — fakt-tekshiruv, /appeal — oxirgi javob bo'yicha murojaat, /region <id>,
           /profilim — Mening huquqlarim, /login <profil_id> — MyGov (DEMO) kirish, /ariza <imtiyoz_id>, /chiqish, /exit
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import backend_client as api  # noqa: E402
from config import settings  # noqa: E402

try:  # Windows konsolida o'zbek/kirill harflari
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass


CLI_KEY = "web:cli_local_user"


async def profile_cmd(text: str) -> None:
    cmd, _, arg = text.partition(" ")
    arg = arg.strip()
    if cmd == "/login":
        if not arg:
            data = await api.demo_profiles() or {}
            print(data.get("consent_text", ""))
            for p in data.get("profiles", []):
                print(f"  /login {p['id']}  — {p['icon']} {p['persona']} ({p['display_name']})")
            return
        res = await api.profile_post("login", {"user_key": CLI_KEY, "profile_id": arg, "consent": True, "channel": "cli"})
    elif cmd == "/ariza":
        res = await api.profile_post("appeal", {"user_key": CLI_KEY, "benefit_id": arg, "channel": "cli"})
    elif cmd == "/chiqish":
        res = await api.profile_post("logout", {"user_key": CLI_KEY})
    else:
        res = await api.profile_me(CLI_KEY)
        if res and not res.get("linked"):
            print("Profil ulanmagan. Kirish: /login")
            return
    if not res:
        print("⚠️ Xato (backend yoki noto'g'ri id).")
        return
    print("\n" + res.get("text", ""))
    for b in res.get("benefits", []):
        print(f"[ariza: /ariza {b['id']}]")


async def repl() -> None:
    print(f"{settings.app_name} — CLI rejimi (backend: {settings.backend_url}). Chiqish: /exit")
    region = None
    last: dict | None = None
    while True:
        try:
            text = (await asyncio.to_thread(input, "\nSiz> ")).strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text:
            continue
        if text == "/exit":
            break
        if text.startswith("/region"):
            region = text.split(maxsplit=1)[1] if " " in text else None
            print(f"hudud: {region}")
            continue
        if text.startswith(("/profilim", "/login", "/ariza", "/chiqish")):
            await profile_cmd(text)
            continue
        if text == "/appeal":
            if not last or not last.get("card_id"):
                print("Avval savol bering.")
                continue
            res = await api.post("/api/appeal", json={"card_id": last["card_id"], "event_id": last.get("event_id")})
            print("\n" + (res or {}).get("text", "xato"))
            continue
        mode = "auto"
        if text.startswith("/tekshir"):
            mode, text = "factcheck", text[len("/tekshir"):].strip()
        res = await api.ask(text, region=region, mode=mode, channel="cli")
        if not res:
            print("⚠️ Backend javob bermadi. U ishga tushganini tekshiring.")
            continue
        last = res
        print("\nJavob>\n" + res["text"])
        btns = [b["action"] for b in res.get("buttons", [])]
        if btns:
            print(f"[tugmalar: {', '.join(btns)}]  (rozi bo'lmasangiz: /appeal)")


if __name__ == "__main__":
    asyncio.run(repl())
