"""FastAPI ilovasi: API + (build qilingan bo'lsa) React frontend."""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .api import account, citizen, gov, profile
from .oneid_demo import models as _oneid_models  # noqa: F401  (jadvallar)
from .oneid_demo import router as oneid_router
from .oneid_demo import service as oneid_service
from .config import APP_NAME, get_settings
from .db import SessionLocal, init_db
from .services import classifier, knowledge, llm, notifier, rag, speech

settings = get_settings()
logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("javob")


def bootstrap() -> None:
    """DB, kartalar, darsliklar, klassifikator va RAG indeksini tayyorlash (sinxron, testlarda ham)."""
    init_db()
    db = SessionLocal()
    try:
        n = knowledge.cards.sync(db)
        knowledge.sync_textbooks(db)
        oneid_service.seed(db)
    finally:
        db.close()
    classifier.build(knowledge.cards.all(), knowledge.claims())
    llm.is_available()  # LLM klienti (anthropic importi) oldindan — birinchi so'rov tez bo'lsin
    rag.build()
    log.info("%s: %d karta yuklandi", APP_NAME, n)


@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap()
    # TTS tekshiruvi startup'ni to'xtatmasin
    speech.start_verify()
    # Gemini model nomlari startup'da tekshiriladi (fon vazifasi; xato bo'lsa — shablon rejimi)
    if llm.provider() == "gemini":
        asyncio.create_task(llm.verify_gemini_models())
    task = asyncio.create_task(notifier.loop())
    log.info("LLM=%s (%s) STT=%s TTS=%s Telegram=%s", settings.llm_enabled, llm.provider(), speech.stt_available(),
             settings.tts_provider, notifier.enabled())
    yield
    task.cancel()


app = FastAPI(title=f"{APP_NAME} API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(citizen.router)
app.include_router(gov.router)
app.include_router(profile.router)
app.include_router(account.router)
app.include_router(oneid_router.router)


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    # Demo hech qachon qulamasin: kutilmagan xato -> muloyim javob
    log.exception("kutilmagan xato: %s", exc)
    return JSONResponse(status_code=500, content={"type": "error", "text": "Kechirasiz, ichki xato. Qayta urinib ko'ring."})


# ---- Frontend (frontend/dist) — /dashboard, /edu, /miniapp ----
dist = settings.frontend_dist
if (dist / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    async def spa(path: str):
        if path.startswith(("api/", "oneid-demo/")):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        f = dist / path
        if path and f.is_file():
            return FileResponse(f)
        return FileResponse(dist / "index.html")
else:
    @app.get("/", include_in_schema=False)
    async def root():
        return {"app": APP_NAME, "docs": "/docs", "note": "Frontend build topilmadi: cd frontend && npm run build"}
