# Windows'da make bo'lmasa — README'dagi buyruqlardan foydalaning.
PY ?= .venv/Scripts/python
ifeq ($(OS),)
PY = .venv/bin/python
endif

.PHONY: install dev bot cli web web-dev seed test smoke docker-up cards

install:            ## venv + python va node paketlari
	python -m venv .venv
	$(PY) -m pip install -r requirements.txt
	cd frontend && npm install

dev:                ## backend (API + build qilingan frontend) :8000
	$(PY) -m uvicorn app.main:app --app-dir backend --reload --port 8000

bot:                ## Telegram bot (token yo'q bo'lsa CLI)
	$(PY) bot/main.py

cli:                ## tokensiz lokal chat
	$(PY) bot/cli.py

web:                ## frontendni build qilish (FastAPI /dashboard da beradi)
	cd frontend && npm run build

web-dev:            ## Vite dev server :5173 (/api -> :8000)
	cd frontend && npm run dev

seed:               ## dashboard uchun soxta anonim analitika
	$(PY) scripts/seed_demo_data.py

cards:              ## seed kartalarni qayta yaratish (mavjudlarini o'zgartirmaydi)
	$(PY) scripts/build_seed_cards.py
	$(PY) scripts/build_seed_knowledge.py

test:               ## pytest (server kerak emas)
	cd backend && ../$(PY) -m pytest -q

smoke:              ## ishlab turgan serverga 3 ta demo so'rov
	$(PY) scripts/smoke_test.py

docker-up:
	docker compose up --build
