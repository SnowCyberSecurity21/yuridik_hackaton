# Huquqim — «Mening huquqlarim» va murojaatdan oldin huquqiy tushuntirish (LexHackathon 2026, 2-trek)

Fuqaro **MyGov (OneID) orqali kiradi** va bitta ekranda ko'radi:
- qaysi imtiyozlarga **haqli bo'lishi mumkin**;
- qanday muddatli majburiyatlari bor (jarima, MIB qarzi, kommunal qarz);
- qaysi qonun o'zgarishlari aynan unga ta'sir qiladi.

Har bir imtiyozdan bir bosishda tayyor ariza olinadi.
Bundan tashqari bot savollarga (nafaqa, aliment, jarima SMS, MIB…) **oddiy tilda, manba bilan** javob beradi.
Davlat uchun anonim analitika va targ'ibot kontenti tayyorlanadi.

- Hakamlar uchun qisqa ma'lumot (muammo → yechim, 5 muammo xaritasi, demo loginlar) — [`INFO.md`](INFO.md).
- Mentor qarori bilan MVP toraytirildi (pastdagi "Ustuvorlik" bo'limiga qarang).
- Arxitektura, shu jumladan OneID va integratsiya platformasiga ulanish rejasi — [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
- Mahsulot nomi bitta konstantada: `APP_NAME = "Huquqim"` (`backend/app/config.py`, frontend: `frontend/src/config.js`).

> ⚠️ **Huquqiy mazmun — huquqshunos tasdig'ini kutmoqda.**
> - Qonun abzaslari (`knowledge/lex/excerpts.json`, 63 ta) lex.uz'dan **aynan** olingan: `original_text`, `lex_url` (paragrafgacha), `retrieved_at`.
>   Tekshirish: `python scripts/verify_lex_excerpts.py` — har abzasni jonli lex.uz sahifasi bilan solishtiradi.
> - Oddiy tildagi matn (`plain_uz`, `plain_ru`) — AI soddalashtirgan (`simplified_by: "ai"`), UI'da rasmiy matn yonida, belgi bilan.
> - Kartalar, imtiyozlar va abzaslar `"verified": false`. Matnda yo'q modda, summa yoki muddat o'rnida `TODO_LAWYER` (UI'da «huquqshunos tasdiqlashi kutilmoqda»).
> - Natija hech qachon "albatta olasiz" emas. Faqat «Haqli bo'lishingiz mumkin» va "tekshirilishi kerak" bo'lgan shartlar ro'yxati ko'rsatiladi.
> - **MyGov/OneID — MOCK.** Demo shaxslar va dashboard analitikasi o'ylab topilgan.

## 2-bosqich: huquqiy kontent (21.11.2026)

| Qism | Nima qilindi | Qayerda |
|---|---|---|
| «Mening huquqlarim» | 5 toifa: Talaba, Bolali ona, Yuridik shaxs / tadbirkor, Pensioner, Haydovchi — imtiyozlar, huquqlar, majburiyatlar, hujjatlar, qayerga borish, yangiliklar. Har yozuv lex.uz abzasiga bog'langan | `knowledge/rights/situation_*.json`, `services/rights.py` → `GET /api/rights/categories`, `GET /api/rights/category/{id}` |
| Qoidalar dvigateli | talaba (stipendiya, yotoqxona), ona, yuridik shaxs (aylanma soliq) faktlari; noma'lum fakt — «tekshirilishi kerak» | `services/profile.py` (`facts`, `situations_of`), `knowledge/benefits/` |
| Qonun abzaslari | asl matn ↔ oddiy til (uz/ru), toifa va imtiyoz bo'yicha | `GET /api/lex/excerpts?category=student` · `?item=st_stipend` · `?ids=a,b`, `GET /api/lex/excerpts/{id}` |
| Savol-javob | yangi kartalar: stipendiya, yotoqxona, dekret, soliq tekshiruvi, soliq rejimi; javobda 📖 asl iqtibos + 💬 oddiy til + 📚 manba (`quotes` maydoni) | `POST /api/ask`, bot, `knowledge/cards/` |
| Murojaat shablonlari | har shablon o'z qonunini ko'rsatadi; rekvizitlar Murojaatlar to'g'risidagi Qonun (6, 16, 17, 19-m.), MJtK 316, Soliq kodeksi 232–233 dan; yangi: stipendiya, dekret, soliq tekshiruvi ustidan shikoyat (yuridik shaxs) | `knowledge/appeal_templates/`, `GET /api/appeal/templates`, `POST /api/appeal` |
| UI komponentlar | `LawView`, `RightsCategories`, `AskBox`, `AppealForm` (nusxa + PDF), `howItWorks` | `frontend/src/features/` — ulash yo'riqnomasi `features/index.js` da |

## 2026-11-21: Huquqim hisobi + DEMO ID (OneID simulyatsiyasi) + anonim rejim

- **Sayt:** `/` bosh sahifa → «OneID bilan tasdiqlash» (`/kirish` → `/kabinet`) yoki «Anonim foydalanish» (`/anonim`).
- **DEMO ID** — alohida modul `backend/app/oneid_demo/` (o'z jadvallari va sessiyasi), sahifa `/oneid-demo/authorize`.
  Shaxslar: `knowledge/oneid_demo/persons.json` (Azizbek, Malika, Jasur, Karim, Sardor, Dilnoza, Erlan; parol `12345678`).
- **Huquqiy maqom:** O'zbekiston fuqarosi · chet el fuqarosi · fuqaroligi bo'lmagan shaxs · bilmayman — `knowledge/rights/status_*.json`.
  Holatlar: `knowledge/rights/situation_*.json`. Qonunlar: `knowledge/laws/*.json` (lex.uz'da tekshirilgan, `retrieved_at` bilan).
  Generator: `python scripts/build_laws_rights.py`. Manbasiz yozuv UI'ga chiqmaydi (`services/rights.py`).
- **Bot:** `/start` ikki yo'l; hisobni ulash `?start=link_<token>` (10 daq, bir martalik).
- **Rollar:** Ta'lim (talaba — Azizbek), Davlat kabineti (`GOV_STAFF_SUBS` whitelist — Dilnoza; simulyatsiya faqat demo hisoblarga).
- Jonli smoke: `python scripts/smoke_accounts.py --base <url>`.

## Ustuvorlik (mentor fikridan keyin)
1. «Mening huquqlarim» profili: MyGov (OneID) orqali kirish (mock). 3 ta soxta profil: 2 bolali ona, pensioner, yosh haydovchi.
2. Imtiyozlar mexanizmi: `knowledge/benefits/*.json`, 5 ta imtiyoz/huquq. Har birida qoida (`rule`), hujjatlar, qayerga borish, `legal_basis` bor.
3. Profil ekrani botda (`/profilim`) va Mini App'da (`/miniapp`): imtiyozlar, majburiyatlar (muddat bilan), menga ta'sir qiluvchi o'zgarishlar. Har imtiyozdan bir bosishda ariza.
4. O'zgarishlar zanjiri profilga bog'langan: simulyatsiya qilingan o'zgarish **faqat ta'sir qiladigan profillarga** xabar yuboradi.
5. Obunalar, rozilik va profil tanlovi SQLite'da saqlanadi. Profil ma'lumotlari saqlanmaydi.
6. Ta'lim moduli (6–8-muammolar) **hozircha to'xtatilgan**. Kod (`Edu.jsx`, darslik bo'laklari) saqlangan, menyuda yo'q.

## Tez ishga tushirish (kalitlarsiz ishlaydi)

```bash
cp .env.example .env                       # kalitlar bo'sh qolishi mumkin
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt     # backend + bot birga; Linux/mac: .venv/bin/pip
cd frontend && npm install && npm run build && cd ..
.venv/Scripts/python scripts/seed_demo_data.py                                    # dashboard uchun demo analitika
.venv/Scripts/python -m uvicorn app.main:app --app-dir backend --port 8000
```

- **Mening huquqlarim (Mini App):** http://localhost:8000/miniapp — brauzerda ham ishlaydi
- Davlat dashboardi: http://localhost:8000/dashboard · API: http://localhost:8000/docs
- **Botni tokensiz sinash (CLI):** `.venv/Scripts/python bot/cli.py`
  - `/login` (profillar ro'yxati), `/login demo_mother`, `/profilim`, `/ariza benefit_child_allowance`, `/chiqish`
  - `/tekshir <matn>`, `/appeal`, `/region <id>`
- Telegram bot: `.env` ga `TELEGRAM_BOT_TOKEN` qo'ying → `.venv/Scripts/python bot/main.py`. Mini App uchun `WEBAPP_URL=https://<domen>/miniapp`.
- Docker: `docker compose up --build` (backend :8000, bot; webhook uchun :8081)
- `make` bo'lsa: `make install web seed dev`, `make bot`, `make test`, `make smoke`

> Eski `data/javob.db` endi ishlatilmaydi. Yangi baza — `data/huquqim.db`. Demo analitika uchun `seed_demo_data.py` ni bir marta ishga tushiring.

## Demo loginlar (DEMO ID, parol hammasiga `12345678`)

| Login | Kim | Nimani ko'rsatadi |
|---|---|---|
| `Azizbek` | Talaba (davlat OTM, kunduzgi, grant) | Ta'lim bo'limi + talaba imtiyozlari (stipendiya; yotoqxona — «mos emas», sababi bilan) |
| `Malika` | 2 bolali ona, Ijtimoiy reyestrda | Bolalar nafaqasi, aliment, «Bolali ona» toifasi, ariza |
| `Jasur` | Yuridik shaxs rahbari | Aylanma soliq rejimi, soliq tekshiruvida huquqlar, shikoyat shabloni |
| `Karim` | Pensioner | Pensiya huquqlari |
| `Sardor` | Haydovchi, YaTT | Jarima chegirmasi, MIB qarzi |
| `Erlan` | Chet el fuqarosi | Maqomga qarab huquqlar |
| `Dilnoza` | Adliya bo'limi mutaxassisi | Davlat kabineti |

## Testlar

```bash
.venv/Scripts/python -m pytest -q backend/tests bot/tests     # server kerak emas, LLM/STT/TTS o'chiq
.venv/Scripts/python scripts/verify_lex_excerpts.py            # qonun abzaslari ↔ jonli lex.uz (internet kerak)
.venv/Scripts/python scripts/smoke_test.py                     # ishlab turgan serverga: 3 ta demo so'rov + profil
.venv/Scripts/python scripts/smoke_accounts.py --base <url>    # 7 ta demo shaxs bilan to'liq oqim
```

Yangi testlar: `test_rights_categories.py` (5 toifa, har yozuv abzasga bog'langan, qoidalar, Jasur va Azizbek kabineti),
`test_lex_excerpts.py`, `test_ask_topics.py` (yangi mavzular + asl iqtibos), `test_appeal_templates.py` (rekvizitlar faqat tatbiq etiladigan qonundan).

`test_profiles.py` quyidagilarni tekshiradi:
- rozilik majburiy;
- har profil uchun to'g'ri imtiyozlar chiqadi, "albatta" so'zi yo'q, foydalanuvchiga xom TODO_LAWYER ko'rinmaydi;
- bir bosishda ariza tuziladi, mos kelmaydigan imtiyozga ariza berilmaydi;
- o'zgarish faqat ta'sir qiladigan profilga boradi;
- chiqish rozilikni bekor qiladi;
- Telegram initData imzosi tekshiriladi.

## Sozlamalar (.env) va fallback'lar

| O'zgaruvchi | Bo'sh / ishlamasa |
|---|---|
| `ANTHROPIC_API_KEY`, `LLM_MODEL` (standart `claude-sonnet-5-5`), `LLM_EFFORT`, `LLM_TIMEOUT` (8 s) | Kartadan shablon javob. LLM faqat qayta ifodalaydi; 8 s ichida javob bo'lmasa yoki xato bo'lsa — darhol shablon |
| `STT_PROVIDER` = `none` \| `openai` (+`STT_API_KEY`) \| `faster_whisper` | "Ovozli xabar hozircha qo'llab-quvvatlanmaydi" |
| `TTS_PROVIDER` = `edge` \| `none` | Faqat matn |
| `TELEGRAM_BOT_TOKEN`, `BOT_MODE` = `polling` \| `webhook`, `PUBLIC_BASE_URL` | Token yo'q → CLI rejimi; alertlar faqat dashboard va Mini App'da ko'rinadi |
| `WEBAPP_URL` | Botda Mini App tugmasi ko'rinmaydi (`/miniapp` brauzerda baribir ishlaydi) |
| `INTERNAL_API_TOKEN` | Bo'sh — demo: bot→backend profil so'rovlari imzolanmaydi. **Prod'da majburiy** |
| `DATABASE_URL` | SQLite `data/huquqim.db` (Postgres URL ham ishlaydi) |
| `ADMIN_TOKEN` | Bo'sh — `/api/gov/*` ochiq (demo). To'ldirilsa `X-Admin-Token` talab qilinadi |

## Demo ssenariysi (2 daqiqa)

1. **Telefon, bot:** `/profilim` → «MyGov (OneID) orqali kirish» → rozilik → «👩‍👧‍👦 2 bolali ona».
   - Ekranda: 2 ta imtiyoz «Haqli bo'lishingiz mumkin» (✓ bajarilgan shartlar, ❔ tekshirilishi kerak), gaz qarzi muddati bilan.
   - «📝 Nafaqa so'rash arizasi» → MyGov ma'lumotlari bilan to'ldirilgan tayyor ariza.
2. **Mini App** (`/miniapp`): xuddi shu profil kartochkalar ko'rinishida. «Yosh haydovchi»ga o'tish → jarima, chegirma muddati, ⏰ eslatma.
3. **Dashboard** → «⚡ O'zgarishni simulyatsiya qilish» (bolalar nafaqasi):
   - jadvalda faqat **ona**ga 🔔 xabar boradi, pensioner va haydovchi — «taalluqli emas»;
   - telefonga shaxsiy xabar keladi ("Nega sizga: …"), profilda «Menga ta'sir qiluvchi o'zgarishlar» paydo bo'ladi.
4. (Vaqt bo'lsa) Jarima SMS'ini joylash → tahlil. Feyk postni forward qilish → «Noto'g'ri» + manba.
5. «↺ Demo'ni tiklash».

## Tuzilma

```
requirements.txt  backend + bot bog'liqliklari (bitta fayl); INFO.md — hakamlar uchun
backend/app/  main.py, config.py, db.py, models/, api/{citizen,gov,profile,account,lex}.py
              oneid_demo/ — DEMO ID (OneID simulyatsiyasi), o'z jadvallari va sessiyasi
              services/ profile, rights (qoidalar dvigateli), accounts, cabinet, appeal, changes (profilga nishon),
                        classifier, answer, rag, llm, speech, sms_parser, outreach, analytics, notifier,
                        privacy, security, render, i18n, knowledge, edu
backend/tests/ test_smoke, test_profiles, test_accounts, test_llm_guard, test_gemini
bot/          main.py (polling/webhook/CLI), handlers.py, account_handlers.py, cli.py, backend_client.py, tests/
frontend/     React + Vite + Tailwind: / (sayt, kabinet, anonim), /miniapp, /dashboard (Recharts, alohida yuklanadi)
              src/features/ — huquqiy kontent komponentlari (LawView, RightsCategories, AskBox, AppealForm, howItWorks)
knowledge/    cards/, benefits/, rights/, laws/, mock_profiles/, oneid_demo/, appeal_templates/,
              factcheck/, lex/ (excerpts — lex.uz abzaslari, changes_feed), textbooks/, i18n/
prompts/      LLM uchun tizim va vazifa promptlari
deploy/       systemd servislar, nginx konfiguratsiyasi, constraints.txt (aniq versiyalar)
docs/         ARCHITECTURE.md — OneID + integratsiya platformasi rejasi: rozilik, minimal ma'lumot, saqlamaslik
scripts/      seed_demo_data.py, smoke_test.py, smoke_accounts.py, build_*.py, verify_card_sources.py,
              verify_lex_excerpts.py (abzaslar ↔ jonli lex.uz)
```

## Xavfsizlik qoidalari (kodda majburlangan)

- Javob faqat kartadan. Ishonch past bo'lsa — RAG, faqat haqiqiy lex parchalari bo'yicha. Bo'lmasa — "tasdiqlangan ma'lumot topilmadi". Fakt-tekshiruvda manba yo'q bo'lsa — "Tasdiqlanmagan".
- Imtiyozlar: hech qachon "albatta". `TODO_LAWYER` sharti taxmin qilinmaydi, "tekshirilishi kerak" deb ko'rsatiladi.
- Profil: rozilikdan oldin hech narsa o'qilmaydi. SQLite'da faqat "foydalanuvchi ↔ profil" bog'lanishi va rozilik yozuvi saqlanadi. Profil ma'lumotlari saqlanmaydi. «Chiqish» bog'lanishni o'chiradi.
- Har javobda manba havolasi va "AI tushuntiradi; rasmiy manba — qonun hujjatining o'zi" ogohlantirishi bor.
- Analitikada savol matni, PINFL, pasport, F.I.Sh. va telefon saqlanmaydi. SMS'dagi ism va tug'ilgan sana olib tashlanadi.
