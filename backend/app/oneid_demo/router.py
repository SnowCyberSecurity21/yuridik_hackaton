"""DEMO ID servisining sahifalari va API'si (/oneid-demo/*).

Dizayn ATAYLAB neytral: haqiqiy OneID/id.egov.uz nomi, logotipi, ranglari yoki domeni ishlatilmaydi.
"""
from __future__ import annotations

from html import escape
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..services.security import RateLimiter, client_ip
from . import service

router = APIRouter(prefix="/oneid-demo", tags=["demo-id"])
COOKIE = "demoid_sid"
login_ip_limiter = RateLimiter(20, 300)
login_user_limiter = RateLimiter(8, 300)

WARNING = "DEMO identifikatsiya — haqiqiy OneID login va parolingizni kiritmang."

CSS = """
:root{--bg:#f3f1fb;--card:#fff;--ink:#1f1640;--muted:#5d5678;--line:#ddd8ef;--acc:#5b3fd1;--acc-ink:#fff;--warn:#fff1c7;--warn-ink:#5c4300;--err:#fde3e3;--err-ink:#8a1f1e}
@media (prefers-color-scheme:dark){:root{--bg:#15122a;--card:#1f1b3a;--ink:#efecff;--muted:#b9b2db;--line:#3a3466;--acc:#9a86ff;--acc-ink:#15122a;--warn:#3b300c;--warn-ink:#f5d27a;--err:#3d1716;--err-ink:#f3a3a2}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
.wrap{max-width:440px;margin:0 auto;padding:16px}
.brand{display:flex;align-items:center;gap:10px;margin:8px 0 14px}.logo{width:44px;height:36px;border-radius:10px;background:var(--acc);color:var(--acc-ink);display:grid;place-items:center;font-weight:800;font-size:11px;letter-spacing:.02em}
.brand b{font-size:18px}.brand small{display:block;color:var(--muted);font-size:12px}
.warn{background:var(--warn);color:var(--warn-ink);border-radius:12px;padding:10px 12px;font-weight:700;font-size:14px;margin-bottom:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px;margin-bottom:14px}
label{display:block;font-size:13px;color:var(--muted);margin:10px 0 4px}
input{width:100%;padding:12px;border-radius:10px;border:1px solid var(--line);background:var(--bg);color:var(--ink);font-size:16px}
.btn{display:block;width:100%;padding:13px;border-radius:12px;border:0;background:var(--acc);color:var(--acc-ink);font-weight:700;font-size:16px;margin-top:14px;cursor:pointer;text-align:center;text-decoration:none}
.btn.sec{background:transparent;color:var(--ink);border:1px solid var(--line)}
.err{background:var(--err);color:var(--err-ink);border-radius:10px;padding:8px 10px;font-size:14px;margin-top:10px}
.persons button{display:flex;gap:10px;align-items:center;width:100%;text-align:left;padding:10px;border-radius:12px;border:1px solid var(--line);background:var(--bg);color:var(--ink);margin-top:8px;cursor:pointer;font-size:14px}
.persons .ic{font-size:22px}.muted{color:var(--muted);font-size:13px}ul{padding-left:18px;margin:8px 0}li{margin:3px 0}
h1{font-size:20px;margin:0 0 6px}h2{font-size:16px;margin:0 0 8px}
"""


def _page(title: str, body: str) -> HTMLResponse:
    html = f"""<!doctype html><html lang="uz"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} — DEMO ID</title><meta name="robots" content="noindex"><style>{CSS}</style></head><body><div class="wrap">
<div class="brand"><div class="logo">DEMO</div><div><b>DEMO ID</b><small>Identifikatsiya simulyatori (hakaton maketi)</small></div></div>
<div class="warn">⚠️ {escape(WARNING)}</div>{body}
<p class="muted">Bu sahifa davlat tizimi EMAS. Barcha shaxslar va ma'lumotlar o'ylab topilgan.</p></div></body></html>"""
    return HTMLResponse(html, headers={"Cache-Control": "no-store", "X-Frame-Options": "DENY",
                                       "Referrer-Policy": "no-referrer"})


def _params(client_id: str, redirect_uri: str, state: str) -> str:
    return urlencode({"client_id": client_id, "redirect_uri": redirect_uri, "state": state})


def _hidden(client_id: str, redirect_uri: str, state: str) -> str:
    return "".join(f'<input type="hidden" name="{k}" value="{escape(v)}">'
                   for k, v in (("client_id", client_id), ("redirect_uri", redirect_uri), ("state", state)))


def _login_page(client_id: str, redirect_uri: str, state: str, error: str | None = None, login: str = "") -> HTMLResponse:
    persons = "".join(
        f'<button type="button" data-l="{escape(p["login"])}" data-p="{escape(p["password"])}">'
        f'<span class="ic">{escape(p["icon"])}</span><span><b>{escape(p["login"])}</b><br>'
        f'<span class="muted">{escape(p["persona"])}</span></span></button>' for p in service.public_persons())
    err = f'<div class="err">{escape(error)}</div>' if error else ""
    client = service.CLIENTS.get(client_id, {}).get("name", client_id)
    body = f"""<div class="card"><h1>Kirish</h1><p class="muted">«{escape(client)}» xizmati shaxsingizni tasdiqlashni so'ramoqda.</p>
<form method="post" action="/oneid-demo/login" autocomplete="off">{_hidden(client_id, redirect_uri, state)}
<label for="l">Login</label><input id="l" name="login" value="{escape(login)}" required maxlength="40">
<label for="p">Parol</label><input id="p" name="password" type="password" required maxlength="100">{err}
<button class="btn" type="submit">Kirish</button></form></div>
<div class="card persons"><h2>Demo shaxslar</h2><p class="muted">Bir bosishda login va parol to'ldiriladi.</p>{persons}</div>
<script>document.querySelectorAll('.persons button').forEach(b=>b.onclick=()=>{{document.getElementById('l').value=b.dataset.l;document.getElementById('p').value=b.dataset.p;}});</script>"""
    return _page("Kirish", body)


def _consent_page(db: Session, sub: str, client_id: str, redirect_uri: str, state: str) -> HTMLResponse:
    user = db.get(service.DemoIdUser, sub)
    name = (user.data.get("full_name") if user else "") or ""
    client = service.CLIENTS[client_id]["name"]
    items = "".join(f"<li>{escape(service.SCOPE_LABELS_UZ[s])}</li>" for s in service.SCOPE)
    body = f"""<div class="card"><h1>Rozilik</h1><p class="muted">Siz: <b>{escape(name)}</b></p>
<p><b>{escape(client)}</b> quyidagi ma'lumotlarni oladi:</p><ul>{items}</ul>
<p class="muted">{escape(client)} bu ma'lumotlarni o'z bazasida saqlamaydi: kerak bo'lganda shu servisdan so'raydi.
Rozilikni istalgan vaqtda {escape(client)} kabinetida bekor qilishingiz mumkin.</p>
<form method="post" action="/oneid-demo/consent">{_hidden(client_id, redirect_uri, state)}
<button class="btn" name="decision" value="allow" type="submit">✅ Roziman</button>
<button class="btn sec" name="decision" value="deny" type="submit">Rad etish</button></form>
<form method="post" action="/oneid-demo/logout">{_hidden(client_id, redirect_uri, state)}
<button class="btn sec" type="submit">Boshqa shaxs bilan kirish</button></form></div>"""
    return _page("Rozilik", body)


def _bad_client() -> HTMLResponse:
    return _page("Xato", '<div class="card"><h1>Noto\'g\'ri so\'rov</h1><p class="muted">Xizmat (client_id) yoki qaytish manzili ro\'yxatda yo\'q.</p></div>')


def _secure(request: Request) -> bool:
    return request.url.scheme == "https"


@router.get("/authorize", include_in_schema=False)
def authorize(request: Request, client_id: str = "", redirect_uri: str = "", state: str = "", db: Session = Depends(get_db)):
    if not service.valid_client(client_id, redirect_uri) or not state or len(state) > 100:
        return _bad_client()
    sub = service.session_sub(db, request.cookies.get(COOKIE))
    if not sub:
        return _login_page(client_id, redirect_uri, state)
    return _consent_page(db, sub, client_id, redirect_uri, state)


@router.post("/login", include_in_schema=False)
def login(request: Request, login: str = Form(""), password: str = Form(""), client_id: str = Form(""),
          redirect_uri: str = Form(""), state: str = Form(""), db: Session = Depends(get_db)):
    if not service.valid_client(client_id, redirect_uri) or not state:
        return _bad_client()
    ip = client_ip(request)
    if not login_ip_limiter.hit(ip) or not login_user_limiter.hit((login or "").strip().lower()):
        return _login_page(client_id, redirect_uri, state, "Juda ko'p urinish. 5 daqiqadan keyin qayta urinib ko'ring.", login)
    user = service.authenticate(db, login, password)
    if not user:
        return _login_page(client_id, redirect_uri, state, "Login yoki parol noto'g'ri.", login)
    tok = service.create_session(db, user.sub)
    resp = RedirectResponse(f"/oneid-demo/authorize?{_params(client_id, redirect_uri, state)}", status_code=303)
    resp.set_cookie(COOKIE, tok, max_age=1800, httponly=True, samesite="lax", secure=_secure(request), path="/oneid-demo")
    return resp


@router.post("/consent", include_in_schema=False)
def consent(request: Request, decision: str = Form("deny"), client_id: str = Form(""), redirect_uri: str = Form(""),
            state: str = Form(""), db: Session = Depends(get_db)):
    if not service.valid_client(client_id, redirect_uri) or not state:
        return _bad_client()
    sub = service.session_sub(db, request.cookies.get(COOKIE))
    if not sub:
        return _login_page(client_id, redirect_uri, state, "Sessiya tugadi. Qayta kiring.")
    if decision != "allow":
        return RedirectResponse(f"{redirect_uri}?{urlencode({'error': 'access_denied', 'state': state})}", status_code=303)
    code = service.issue_code(db, sub, client_id, redirect_uri)
    # demo sessiya tugatiladi — keyingi tasdiqlashda qayta login so'raladi (umumiy kompyuterda xavfsizroq)
    service.end_session(db, request.cookies.get(COOKIE))
    resp = RedirectResponse(f"{redirect_uri}?{urlencode({'code': code, 'state': state})}", status_code=303)
    resp.delete_cookie(COOKIE, path="/oneid-demo")
    return resp


@router.post("/logout", include_in_schema=False)
def logout(request: Request, client_id: str = Form(""), redirect_uri: str = Form(""), state: str = Form(""),
           db: Session = Depends(get_db)):
    service.end_session(db, request.cookies.get(COOKIE))
    target = f"/oneid-demo/authorize?{_params(client_id, redirect_uri, state)}" if service.valid_client(client_id, redirect_uri) else "/"
    resp = RedirectResponse(target, status_code=303)
    resp.delete_cookie(COOKIE, path="/oneid-demo")
    return resp


# ---- server -> server API (real tizimda Huquqim backend shu endpointlarni chaqiradi) ----

class TokenIn(BaseModel):
    code: str
    client_id: str
    redirect_uri: str


@router.post("/api/token")
def api_token(body: TokenIn, db: Session = Depends(get_db)):
    res = service.exchange_code(db, body.code, body.client_id, body.redirect_uri)
    if not res:
        return JSONResponse(status_code=400, content={"error": "invalid_grant"})
    return res


@router.get("/api/userinfo")
def api_userinfo(request: Request, db: Session = Depends(get_db)):
    auth = request.headers.get("authorization", "")
    tok = auth[7:] if auth.lower().startswith("bearer ") else ""
    info = service.userinfo(db, tok)
    if not info:
        return JSONResponse(status_code=401, content={"error": "invalid_token"})
    return info
