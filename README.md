# Huquqim — murojaatdan oldin huquqingizni oddiy tilda biling

**LexHackathon 2026 · 2-trek: «Huquqiy targ'ibot va ta'lim»**

| | |
|---|---|
| 🌐 Sayt | https://huquqim.zehnprotect.uz |
| 🤖 Telegram bot | [@Huquqim_official_bot](https://t.me/Huquqim_official_bot) |
| 📱 Mini App | https://huquqim.zehnprotect.uz/miniapp |
| 📊 Taqdimot | [`Taqdimot_Huquqim.pdf`](Taqdimot_Huquqim.pdf) |
| 🔑 Hakamlar uchun demo hisoblar | [`DEMO_ACCOUNTS.md`](DEMO_ACCOUNTS.md) |
| 📝 Qisqa ma'lumot (1 sahifa) | [`INFO.md`](INFO.md) |

---

## 1. Huquqim nima

Huquqim — fuqaroning murojaatdan oldingi huquqiy yordamchisi. Fuqaro vaziyatini o'z so'zi bilan yozadi yoki aytadi:
nafaqa berilmadi, jarima SMS'i keldi, stipendiya kesildi, soliq tekshiruvi boshlandi. Huquqim qonun nima deyishini
oddiy tilda, **lex.uz'dagi asl matn yonida** tushuntiradi. Qaysi hujjat kerakligini va qayerga borishni ko'rsatadi.
Kerak bo'lsa, qonundagi rekvizitlar bilan tayyor ariza beradi.

Bitta backend uchta kanalga xizmat qiladi: Telegram bot (matn va ovoz), Telegram Mini App va sayt.
Har bir savol davlat uchun anonim signalga aylanadi: qaysi hududda qaysi qonun tushunilmayapti.
Shu signal asosida bir bosishda targ'ibot kontenti tayyorlanadi.

> Mahsulot nomi bitta konstantada: `APP_NAME = "Huquqim"` (`backend/app/config.py`, `frontend/src/config.js`).

---

## 2. Qaysi muammolarni hal qiladi

2-trekning muammolaridan beshtasi (1–5) beshta modulga mos keladi. Har bir modul tayyor murojaatga olib boradi.

| # | Trek muammosi | Huquqim moduli | Qanday hal qiladi |
|---|---|---|---|
| 1 | Qonun tili murakkab | **«Qonunda ↔ Oddiy tilda»** | lex.uz'dan aynan olingan abzas va yonida sodda izoh. Javob kartasi 8 qatordan oshmaydi: qonun nima deydi, sizga nima tegishli, hujjatlar, muddat, qayerga borish, manba |
| 2 | Yangi qonunlarni kech bilishadi | **«Mening huquqlarim»** | 5 toifa (talaba, bolali ona, tadbirkor, pensioner, haydovchi): shaxsiy imtiyozlar va yangiliklar. Qonun o'zgarsa, xabar **faqat ta'sir qiladigan** fuqaroga boradi |
| 3 | Targ'ibot formatlari eskirgan | **Kartochka, audio, davlat kabineti** | Qisqa, forward qilinadigan javob kartasi; 🔊 ovozli o'qish. Davlat xodimi uchun bir bosishda: 30 soniyalik video ssenariy, infografika matni, Telegram post, 3 savollik test |
| 4 | Uzoq hududlar, raqamli ko'nikma past | **Telegram + ovoz + anonim rejim** | Yangi ilova o'rnatish shart emas. Botga gapirasiz, lotin yoki kirill yozuvida yozasiz. Ro'yxatdan o'tmasdan anonim foydalanish mumkin |
| 5 | Ijtimoiy tarmoqda yolg'on ma'lumot | **Fakt-tekshiruv va SMS tahlili** | Postga hukm beriladi (To'g'ri / Qisman / Noto'g'ri / Tasdiqlanmagan) va aniq modda ko'rsatiladi. Jarima SMS'idan summa, chegirma, muddat va e'tiroz yo'li ajratiladi |
| ➕ | Har moduldan | **Tayyor murojaat** | 11 ta shablon. Rekvizitlar Murojaatlar to'g'risidagi Qonun, Soliq kodeksi va MJtK'dan olinadi. Nusxa olish yoki PDF |

**Asosiy qoida:** manbasiz javob yo'q. AI faqat soddalashtiradi: yangi modda, summa yoki muddat qo'shmaydi.
Savol matni va shaxsiy ma'lumot saqlanmaydi.

Huquqim mavjud xizmatlarni to'ldiradi, takrorlamaydi. LexAI umumiy savol-javob beradi. lex.uz bildirishnomalari xom
matn havolasini yuboradi. Road24, Payme va MIB to'lovni qabul qiladi, lekin huquq va e'tiroz yo'lini tushuntirmaydi.

---

## 3. Imkoniyatlar

### 3.1. Bosh sahifa — `/`
Mahsulot tavsifi, telefon maketi va ikkita yo'l: **«OneID bilan tasdiqlash»** yoki **«Anonim foydalanish»**.
Qorong'i va yorug' rejim bor.

### 3.2. Kirish — `/kirish`
Ikki bosqichli kirish:
1. **Huquqim hisobi** — login va parol bilan ro'yxatdan o'tish yoki kirish.
2. **«OneID bilan tasdiqlang»** → DEMO ID sahifasi (`/oneid-demo/authorize`) → DEMO ID login va paroli → rozilik ekrani → `/kabinet`.

DEMO ID — tashqi davlat identifikatsiyasining **simulyatsiyasi**. Unda haqiqiy OneID nomi, logotipi va domeni ishlatilmaydi.
Sahifada ogohlantirish bor: «DEMO identifikatsiya — haqiqiy OneID login va parolingizni kiritmang».
Demo shaxslar ro'yxati: [`DEMO_ACCOUNTS.md`](DEMO_ACCOUNTS.md).

### 3.3. Kabinet — `/kabinet`
OneID (DEMO) orqali tasdiqlangan fuqaroning shaxsiy sahifasi. Ma'lumot har so'rovda DEMO ID'dan rozilik (grant)
bo'yicha olinadi, Huquqim bazasida saqlanmaydi.

| Bo'lim | Nima ko'rinadi |
|---|---|
| Profil | Ism, hudud, oila tarkibi, bandlik, huquqiy maqom (masalan, «O'zbekiston fuqarosi» yoki «Chet el fuqarosi») |
| Toifalar | Profilga mos holatlar: Talaba, Bolali ona, Ota-ona, Yuridik shaxs / tadbirkor, Pensioner, Haydovchi, Yollanib ishlovchi, Davlat xizmatchisi |
| 🎁 Imtiyozlarim | «Haqli bo'lishingiz mumkin»: ✓ bajarilgan shartlar va ❔ tekshirilishi kerak bo'lgan shartlar. Mos kelmaganlari sababi bilan ko'rsatiladi. Natija hech qachon «albatta olasiz» emas |
| ⚖️ Huquqlarim | Maqom bo'yicha umumiy huquqlar (Konstitutsiya) va toifa bo'yicha huquqlar. Har yozuv lex.uz abzasiga bog'langan |
| 📅 Majburiyatlar | Muddatli majburiyatlar (jarima, MIB qarzi, kommunal qarz): summa, chegirma, muddat va qolgan kunlar. ⏰ eslatma qo'yish mumkin |
| Hujjatlar va qayerga | Har imtiyoz uchun kerakli hujjatlar va rasmiy portal (masalan, my.gov.uz) |
| 📚 Siz uchun qonunlar | Profilga tegishli qonunlar: rasmiy nom, sana, lex.uz havolasi, sodda tavsif |
| 🔔 O'zgarishlar | Sizga ta'sir qiladigan qonun o'zgarishlari (demo lenta) |
| «Qonunda ↔ Oddiy tilda» | Asl abzas (lex.uz) va yonida AI soddalashtirgan matn, «AI soddalashtirdi» belgisi bilan |
| Tayyor ariza | Imtiyoz yonidagi «Ariza» tugmasi → profil bilan to'ldirilgan ariza → **Nusxa olish** yoki **PDF** |
| Telegram'ni ulash | Bir martalik havola (10 daqiqa amal qiladi) → botda shaxsiy menyu ochiladi |
| Rozilikni bekor qilish | Rozilik yozuvi va OneID bog'lanishi o'chiriladi |
| Ta'lim / Davlat kabineti | Faqat tegishli rolda: talaba uchun ta'lim bo'limi, davlat xodimi uchun davlat kabineti (3.9) |

**Qanday ishlatiladi:** `/kirish` → hisob ochish → «OneID bilan tasdiqlang» → masalan `Malika` / `12345678` →
«✅ Roziman» → kabinetda «Bolalar nafaqasi» → «Ariza» → «Nusxa olish» yoki PDF.

### 3.4. Anonim rejim — `/anonim`
Hisobsiz va shaxsiy ma'lumotsiz foydalanish.
1. Huquqiy maqomni tanlang: O'zbekiston fuqarosi · Chet el fuqarosi · Fuqaroligi bo'lmagan shaxs · Bilmayman.
2. Holatni tanlang (ixtiyoriy, bir nechtasini tanlash mumkin): Talaba, Bolali ona, Ota-ona, Tadbirkor, Pensioner, Haydovchi.
3. Shu maqom va holatga mos umumiy huquqlar, qonunlar va tayyor savollar chiqadi. Pastda «Savol · SMS · Feyk» bloki bor.

Tanlov faqat brauzerda qoladi va serverga saqlanmaydi.

### 3.5. Savol bering
Sayt, Mini App va botda ishlaydi. Vaziyatni o'z so'zingiz bilan yozasiz: lotin, kirill yoki rus tilida.
Javobda quyidagilar bo'ladi: qonun nima deydi, sabablar, nima qilish kerak, hujjatlar, qayerga borish,
📖 qonundan iqtibos, 💬 oddiy tildagi izoh va 📚 manba.

15 ta vaziyat kartasi. Har bir namunaviy savol jonli saytda shu kartaga tushishi tekshirilgan (21.11.2026):

| Mavzu (karta) | Namunaviy savol |
|---|---|
| Bola nafaqasi berilmadi (`child_allowance_refused`) | Bolamga nafaqa nega berilmadi? |
| Aliment (`alimony`) | Sobiq erim aliment to'lamayapti, nima qilay? |
| Dekret, bola parvarishi (`maternity_childcare`) | Dekret ta'tili necha kun? |
| Stipendiya (`student_stipend`) | Stipendiya nega berilmadi? |
| Yotoqxona to'lovini qoplash (`student_dormitory`) | Yotoqxona to'lovini davlat qoplaydimi? |
| Soliq tekshiruvi (`business_tax_audit`) | Soliq tekshiruvi keldi, nima qilay? |
| Soliq rejimi: aylanma soliq yoki QQS (`business_tax_regime`) | Aylanma soliq yoki QQS, qaysi biri menga to'g'ri keladi? |
| Yo'l harakati jarimasi (`traffic_fine`) | Jarimani chegirma bilan qachongacha to'lash mumkin? |
| MIB qarzi va chet elga chiqish (`mib_debt_travel_ban`) | MIB qarzim bor, chet elga chiqa olamanmi? |
| MIB nomidan soxta SMS (`fake_mib_sms`) | MIB nomidan havolali SMS keldi, bu rostmi? |
| Nomimga onlayn kredit (`online_loan_fraud`) | Nomimga men olmagan onlayn kredit rasmiylashtirilgan |
| Ish haqi berilmayapti (`unpaid_salary`) | Ish beruvchi 3 oydan beri oylik bermayapti |
| Kommunal qarz va sud buyrug'i (`utility_debt_court_order`) | Gaz qarzi uchun sud buyrug'i keldi |
| Mahallada shovqin yoki chiqindi jarimasi (`mahalla_noise_waste_fine`) | Mahallada chiqindi uchun jarima yozishdi |
| Sifatsiz tovar, pulni qaytarish (`consumer_refund`) | Sifatsiz telefon sotib oldim, do'kon pulimni qaytarmayapti |

Kartaga tushmagan savol lex.uz abzaslari bo'yicha qidiriladi (RAG). Masalan, «Chet el fuqarosi O'zbekistonda
ishlashi mumkinmi?» savoliga O'RQ-692 dan iqtibos bilan javob beriladi. Mos manba topilmasa, javob:
«Bu bo'yicha tasdiqlangan ma'lumot topilmadi» va bepul yuridik yordam yoki murojaat yo'li tavsiya qilinadi.

### 3.6. SMS tahlili va fakt-tekshiruv
- **SMS tahlili.** Jarima yoki MIB SMS'ini joylaysiz. Javobda: summa, chegirmali summa (50%) va uning muddati (necha kun qolgani),
  organ, invoys raqami, nima qilish kerak, e'tiroz yo'li (10 kun) va MJtK 332¹-moddadan iqtibos.
  SMS'dagi ism va tug'ilgan sana saqlashdan oldin olib tashlanadi.
- **Fakt-tekshiruv.** Shubhali post matnini joylaysiz yoki botga forward qilasiz. Hukm: ✅ To'g'ri / 🟡 Qisman /
  ❌ Noto'g'ri / ❔ Tasdiqlanmagan, manba bilan. Manba topilmasa, javob doim «Tasdiqlanmagan» bo'ladi, taxmin qilinmaydi.

Namunaviy SMS va post: [`DEMO_ACCOUNTS.md`](DEMO_ACCOUNTS.md#telegram-bot).

### 3.7. Telegram bot — [@Huquqim_official_bot](https://t.me/Huquqim_official_bot)
1. `/start` → ikki yo'l:
   - **✅ OneID bilan tasdiqlab davom etish** — saytdagi `/kirish` sahifasiga o'tadi. Tasdiqlangandan keyin kabinetdagi
     «Telegram'ni ulash» tugmasi botga `?start=link_<token>` havolasini ochadi (10 daqiqa, bir martalik).
     Shundan keyin botda shaxsiy menyu ochiladi: 🎁 Mening imtiyozlarim (ariza tugmalari bilan) · ⚖️ Huquqlarim ·
     📅 Majburiyatlar (⏰ eslatma) · 📚 Siz uchun qonunlar · 🔔 O'zgarishlar · 🔌 Hisobni botdan uzish.
   - **👤 Anonim davom etish** — maqom (4 variant) → holat (6 variant, ixtiyoriy) → ⚖️ Huquqlarim · 📚 Siz uchun qonunlar.
     Tanlov faqat bot jarayoni xotirasida saqlanadi.
2. **Matn yoki 🎙 ovozli xabar** yuborasiz. Ovoz matnga aylantiriladi (STT), bot «🎙 Eshitdim: «…»» deb yozadi va javob beradi.
3. Javob ostidagi tugmalar: **🔊 Audio** (javobni o'qib beradi) · **📄 Manba** · **✅ Tushundim** · **❌ Baribir rozi emasman**
   (to'g'ri adresatga tayyor ariza) · **📤 Ulashish**. Mavzuga qarab **🔔 O'zgarsa xabar ber** va **⏰ Muddatdan oldin eslat** ham chiqadi.
4. **Jarima yoki MIB SMS'ini** joylasangiz, avtomatik tahlil qilinadi.
5. **Postni forward qilsangiz** yoki `/tekshir <matn>` yozsangiz, fakt-tekshiruv ishlaydi.
6. Boshqa buyruqlar: `/region` (hududni tanlash, anonim statistika uchun), `/help`.

### 3.8. Mini App — `/miniapp`
Telegram ichida ochiladigan ilova. Oddiy brauzerda ham ishlaydi («Brauzer rejimi»). Kirish Telegram `initData`
imzosi bilan tekshiriladi. Ichida: toifalar, imtiyozlar va shartlar, «Qayerga borish», «Yangiliklar»,
«lex.uz'da ochish», «Ariza tayyorlash». Shaxsiy kabinet uchun «Saytda tasdiqlash» tugmasi bor.

### 3.9. Davlat kabineti va dashboard
Ikki kirish yo'li bor:
- **`/kabinet` → Davlat kabineti** — `gov` roli bilan. Rol OneID'dan emas, Huquqim'ning whitelist'idan beriladi
  (`GOV_STAFF_SUBS`, demo'da `Dilnoza`).
- **`/dashboard`** — server tomonida basic auth bilan yopilgan. Login va parol hakamlarga alohida beriladi.

Imkoniyatlar:
- **Analitika:** jami savollar, 7 kunlik o'zgarish, «Huquqiy tushunmovchilik xaritasi — 14 hudud», 28 kunlik trend,
  Top-10 mavzu (qatorni bossangiz, xarita va trend shu mavzu bo'yicha filtrlanadi), «Konsultatsiya murojaati oldi olindi»
  hisoblagichi, rasmiy statistika bloki.
- **Signallar:** 🚨 tarqalayotgan feyk da'volar (fakt-tekshiruv loglari, 14 kun), 🧩 eng ko'p tushunilmayotgan
  mavzular → «✏️ Soddalashtirish».
- **Targ'ibot kontenti** (mavzu bo'yicha bir bosishda): 🎬 30 soniyalik video ssenariy · 🖼 infografika matni ·
  📣 Telegram post · ❓ 3 savollik test.
- **«O'zgarishni simulyatsiya qilish»:** demo lentadan o'zgarish tanlanadi. Natijada qaysi DEMO ID shaxslariga
  🔔 xabar borishi va qaysilariga 🔕 «taalluqli emas»ligi ko'rinadi. Bog'liq kartalar «qayta tekshiruvga» belgilanadi.
  Xabar faqat demo hisoblarga ulangan chatlarga boradi. Cheklov: 30 soniyada 1 marta, bitta simulyatsiyada ko'pi bilan 30 xabar.
- **«Demo'ni tiklash»** — simulyatsiya natijalarini qaytaradi.

### 3.10. Ta'lim bo'limi (talaba roli)
DEMO ID'da `occupation.type = student` bo'lgan shaxs (`Azizbek`) kabinetida ochiladi. Ichida amaliy keyslar,
AI «fuqaro» bilan suhbat simulyatori va hujjat trenajyori bor. Bu modul trekning 6–8-muammolariga tegishli.
MVP fuqaro va davlat tomoniga qaratilgan, shuning uchun bu bo'lim qo'shimcha hisoblanadi.

---

## 4. Arxitektura

```
 Fuqaro ──► Telegram bot (aiogram 3) ──────┐
 Fuqaro ──► Sayt / Mini App (React, Vite) ──┼──► FastAPI backend ──► SQLite (Postgres'ga tayyor)
 Davlat ──► /kabinet (gov) va /dashboard ───┘          │
                                                       ├─ klassifikator (kalit so'zlar + TF-IDF char 3–5) → vaziyat kartasi
                                                       ├─ RAG: lex.uz abzaslari (knowledge/lex/excerpts.json)
                                                       ├─ LLM (Gemini yoki Anthropic): faqat qayta ifodalaydi
                                                       │     └─ himoya: kartada yo'q raqam yoki havola bo'lsa — javob rad etiladi
                                                       ├─ «Mening huquqlarim»: toifalar (knowledge/rights) + qoidalar dvigateli (knowledge/benefits)
                                                       ├─ murojaat shablonlari (knowledge/appeal_templates)
                                                       ├─ SMS tahlili (regex + PII tozalash), fakt-tekshiruv (knowledge/factcheck)
                                                       ├─ o'zgarishlar zanjiri: changes_feed → ta'sir qiladigan profil → xabar
                                                       ├─ STT (Gemini / Whisper-mos API / faster-whisper), TTS (edge-tts, uz-UZ)
                                                       ├─ anonim analitika va targ'ibot kontenti generatori
                                                       └─ DEMO ID moduli (/oneid-demo): OAuth2'ga o'xshash OneID simulyatsiyasi
```

**Stack:** Python 3.11+, FastAPI, SQLAlchemy 2, Pydantic, scikit-learn, httpx, aiogram 3, edge-tts ·
React 18, Vite 6, Tailwind CSS 4, Recharts, Motion · SQLite · nginx + systemd.

### Javob pipeline'i
1. **Yo'naltirish.** Forward qilingan post yoki `/tekshir` buyrug'i fakt-tekshiruvga ketadi. SMS ko'rinishidagi matn SMS tahliliga ketadi.
   Qolgan matnlar savol hisoblanadi. Yozuv aniqlanadi: lotin, kirill yoki rus.
2. **Klassifikator.** Kalit so'zlar va TF-IDF (belgi n-grammalari) kartani topadi. Ishonch `CLASSIFIER_THRESHOLD`
   (0.35) dan yuqori bo'lsa, javob **faqat kartadan** olinadi. Ixtiyoriy ravishda sentence-transformers embedding'ini yoqish mumkin.
3. **Karta javobi.** Kartadagi tushuntirish, sabablar, qadamlar, hujjatlar, muddatlar, qayerga borish, iqtibos va manba.
4. **RAG.** Karta topilmasa, lex.uz abzaslari bo'yicha qidiriladi va iqtibos bilan javob beriladi.
   Mos abzas bo'lmasa, javob: «tasdiqlangan ma'lumot topilmadi».
5. **LLM faqat qayta ifodalaydi.** LLM kartani sodda tilga o'giradi, lekin yangi fakt qo'shmaydi.
6. **LLM himoyasi.** Javobda kartada yo'q raqam (modda, summa, muddat) yoki havola bo'lsa, LLM javobi rad etiladi
   va kartaning shablon matni yuboriladi (`answer._llm_output_is_safe`).
7. Har javob oxirida manba va ogohlantirish bor: «AI tushuntiradi; rasmiy kuchga ega manba — qonun hujjatining o'zi».

### STT va TTS
- **STT** (`STT_PROVIDER`): `gemini` (Telegram `.ogg` audio `generateContent`'ga yuboriladi, timeout 15 s), `openai`
  (Whisper-mos API), `faster_whisper` (lokal) yoki `none`.
- **TTS** (`TTS_PROVIDER=edge`): `uz-UZ-MadinaNeural` ovozi. Ishga tushganda tekshiriladi, natija keshlanadi.
  Ishlamasa, 10 daqiqada bir qayta tekshiriladi.

### Timeout va fallback (demo hech qachon qulamaydi)
| Qism | Chegara | Ishlamasa |
|---|---|---|
| LLM | `LLM_TIMEOUT` (8 s) | Kartadan shablon javob |
| Gemini modeli | Ishga tushganda ro'yxatdan tekshiriladi | `GEMINI_MODEL` → `GEMINI_FALLBACK_MODEL` → shablon |
| STT | 15 s (Gemini) / `STT_TIMEOUT` | «Ovozli xabar hozircha qo'llab-quvvatlanmaydi» |
| TTS | `TTS_TIMEOUT` (15 s) | Faqat matn |
| Bot → backend | `BACKEND_TIMEOUT` (25 s) | «Kechirasiz, hozir javob bera olmadim» |
| Telegram token yo'q | — | Bot CLI rejimida ishlaydi |

Batafsil arxitektura, shu jumladan haqiqiy OneID va idoralararo integratsiya platformasiga ulanish rejasi:
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## 5. Bilimlar bazasi — `knowledge/`

| Papka | Nima bor |
|---|---|
| `cards/` | 15 ta vaziyat kartasi: trigger so'zlar, sodda tushuntirish, sabablar, qadamlar, hujjatlar, muddatlar, qayerga borish, huquqiy asos, ariza shabloni |
| `lex/excerpts.json` | 63 ta qonun abzasi yozuvi: asl matn (`original_text`), paragrafgacha aniq `lex_url`, `retrieved_at`, sodda matn (`plain_uz`, `plain_ru`) |
| `lex/changes_feed.json` | Qonun o'zgarishlarining **demo** lentasi (`[DEMO]` belgili, haqiqiy o'zgarish emas) |
| `laws/` | 13 ta qonun hujjati pasporti: rasmiy nom, raqam, sana, lex.uz havolasi, sodda tavsif |
| `rights/` | 4 ta huquqiy maqom (`status_*`) va 8 ta toifa (`situation_*`): huquqlar, majburiyatlar, imtiyozlar, hujjatlar, qayerga borish |
| `benefits/` | 9 ta imtiyoz va ularning qoidalari (`rule`): qaysi shart bajarilgan, qaysi biri tekshirilishi kerak |
| `appeal_templates/` | 11 ta ariza va shikoyat shabloni. Har birida qaysi qonun asos ekani yozilgan |
| `factcheck/known_claims.json` | Ma'lum da'volar va ularning hukmi (fakt-tekshiruv uchun) |
| `oneid_demo/persons.json` | 7 ta o'ylab topilgan DEMO ID shaxsi |
| `mock_profiles/` | Eski «MyGov mock» profillari (bot CLI'dagi `/login`) |
| `textbooks/` | Ta'lim bo'limi uchun amaliy qo'llanma bo'laklari |
| `i18n/` | Interfeys matnlari: `uz.json`, `ru.json`. Kirill yozuvi lotindan avtomatik hosil qilinadi |

### lex.uz abzaslari qanday olinadi va tekshiriladi
- Har abzas lex.uz sahifasidan **aynan** ko'chirilgan va paragraf identifikatorigacha aniq havolaga ega.
  63 ta yozuvdan 61 tasida asl matn bor. 2 tasi `TODO_LAWYER` belgili joy egallagich bo'lib, UI'ga chiqmaydi.
- `python scripts/verify_lex_excerpts.py` har `original_text`'ni jonli lex.uz sahifasi bilan solishtiradi.
  lex.uz ochilmasa, hujjat «tekshirib bo'lmadi» deb belgilanadi va yozuv o'zgartirilmaydi.
- `python scripts/verify_card_sources.py` kartalardagi manbalarni tekshiradi.
- Kodda majburiy qoida: abzas faqat rasmiy URL (`lex.uz` yoki `*.gov.uz`), `retrieved_at` va `TODO` bo'lmagan matn
  bilan ko'rsatiladi. Abzasga bog'lanmagan yozuv «Mening huquqlarim»da chiqmaydi (`services/rights.py`).
- lex.uz agressiv skreyp qilinmaydi. Faqat kichik keshlangan namuna ishlatiladi.

### verified va TODO_LAWYER qoidasi
- Barcha kartalar, imtiyozlar va abzaslar hozircha `"verified": false`. UI'da «TEKSHIRILMAGAN (demo)» yoki
  «Huquqshunos tekshirmagan» belgisi turadi. Manba lex.uz bilan solishtirilgan bo'lsa, «📚 Manba tekshirildi: lex.uz, <sana>» belgisi chiqadi.
- Huquqshunos tasdiqlaganda `verified_by` va `verified_at` to'ldiriladi, `verified=true` bo'ladi va «✅ Tekshirilgan manba» belgisi chiqadi.
- Qonun matnida yo'q modda, summa yoki muddat **to'qilmaydi**. Ular o'rnida `TODO_LAWYER` turadi va UI'da
  «huquqshunos tasdiqlashi kutilmoqda» deb ko'rsatiladi.
- Oddiy tildagi matn AI tomonidan soddalashtirilgan (`simplified_by: "ai"`) va doim rasmiy matn yonida ko'rsatiladi.

### Foydalanilgan normativ hujjatlar (lex.uz, 21.11.2026 holatiga)

| Hujjat | Nima uchun | lex.uz |
|---|---|---|
| O'zbekiston Respublikasi Konstitutsiyasi | asosiy huquqlar (murojaat, mehnat, ijtimoiy ta'minot, ta'lim, sud himoyasi) | [6445145](https://lex.uz/docs/6445145) |
| «Jismoniy va yuridik shaxslarning murojaatlari to'g'risida»gi Qonun (O'RQ-378) | murojaat rekvizitlari, muddatlar, tatbiq doirasi | [-2509996](https://lex.uz/docs/-2509996) |
| «Shaxsga doir ma'lumotlar to'g'risida»gi Qonun (O'RQ-547) | shaxsiy ma'lumotlarni himoya qilish | [4396419](https://lex.uz/docs/4396419) |
| «Ta'lim to'g'risida»gi Qonun (O'RQ-637) | talaba huquqlari va majburiyatlari | [-5013007](https://lex.uz/docs/-5013007) |
| VM 31.01.2020 dagi 59-son qarori, 1-ilova | stipendiya turlari va shartlari | [-4725554](https://lex.uz/docs/-4725554) |
| VM 28.01.2026 dagi 32-son qarori, 1-ilova | yotoqxona to'lovini qoplash | [-8022224](https://lex.uz/docs/-8022224) |
| VM 29.01.2026 dagi 35-son qarori, 3-ilova | bolalar nafaqasi | [-8027513](https://lex.uz/docs/-8027513) |
| Mehnat kodeksi | dekret, bola parvarishi ta'tili, homilador ayollar kafolatlari, ish haqi | [-6257288](https://lex.uz/docs/-6257288) |
| Oila kodeksi | aliment, ota-onaning majburiyatlari | [-104720](https://lex.uz/docs/-104720) |
| Soliq kodeksi | ro'yxatdan o'tish, aylanma soliq, QQS, tekshiruvda huquqlar, shikoyat | [-4674902](https://lex.uz/docs/-4674902) |
| «Fuqarolarning davlat pensiya ta'minoti to'g'risida»gi Qonun (938-XII) | pensiya huquqi, yoshi, arizasiz tayinlash | [-112314](https://lex.uz/docs/-112314) |
| Ma'muriy javobgarlik to'g'risidagi kodeks | jarima chegirmasi, to'lash va shikoyat muddati (332¹-modda) | [-97664](https://lex.uz/docs/-97664) |
| «Chet el fuqarolarining va fuqaroligi bo'lmagan shaxslarning huquqiy holati to'g'risida»gi Qonun (O'RQ-692) | chet el fuqarolari va fuqaroligi bo'lmagan shaxslarning huquqlari | [-5443899](https://lex.uz/docs/-5443899) |

---

## 6. Xavfsizlik va maxfiylik

- **DEMO ID (OneID simulyatsiyasi)** — OAuth2'ga o'xshash oqim: `authorize` → login → rozilik → bir martalik kod
  (5 daqiqa) → grant. Huquqim shaxs ma'lumotini har so'rovda grant bo'yicha oladi va bazaga yozmaydi.
  Rozilik bekor qilinganda grant o'chiriladi va bog'lanish uziladi. Modul alohida: o'z jadvallari, sessiyasi va cookie yo'li bor.
- **Parollar:** `scrypt` (n=2¹⁴, r=8, p=1, tasodifiy salt). Tekshirish doimiy vaqtda (`hmac.compare_digest`).
- **Cookie:** `HttpOnly`, `SameSite=Lax`, HTTPS'da `Secure`. Huquqim sessiyasi 7 kun, DEMO ID sessiyasi 30 daqiqa
  (faqat `/oneid-demo` yo'lida). Sessiya va bog'lash tokenlari bazada xesh ko'rinishida saqlanadi.
- **Rate limit:** login 5 daqiqada 8 urinish (har login uchun) va 20 urinish (har IP uchun); ro'yxatdan o'tish soatiga 10 ta (IP);
  Telegram bog'lash 10 daqiqada 10 ta. DEMO ID login'ida ham xuddi shu chegaralar.
- **Telegram Mini App:** `initData` imzosi rasmiy algoritm bo'yicha tekshiriladi
  (HMAC-SHA256, kalit = HMAC("WebAppData", bot token)). Muddati 24 soat.
- **Bot → backend:** `INTERNAL_API_TOKEN` bilan imzolanadi (`X-Internal-Token`). Davlat API'si uchun ixtiyoriy `ADMIN_TOKEN` bor.
- **Nima saqlanmaydi:** PINFL, pasport, F.I.Sh., telefon, **savol matni**. Analitika hodisasida faqat mavzu, hudud
  (ixtiyoriy), til, kanal, vaqt va «foydali»/«ariza» belgisi saqlanadi. SMS'dagi ism va tug'ilgan sana saqlashdan oldin
  olib tashlanadi (`services/privacy.py`). LLM'ga shaxsiy ma'lumot yuborilmaydi.
- **Anonim rejim:** maqom va holat tanlovi saytda brauzerda, botda esa jarayon xotirasida qoladi. Backendga faqat savol
  bilan birga `legal_status` parametri boradi.
- **Rollar:** `verified` (OneID'dan o'tgan), `student` (DEMO ID'dagi kasb bo'yicha), `gov` (faqat whitelist'dan).
  Talaba davlat kabinetiga kira olmaydi (403).
- **Simulyatsiya xavfsizligi:** o'zgarish xabari faqat demo hisoblarga ulangan chatlarga boradi. 30 soniyada 1 marta,
  bitta simulyatsiyada ko'pi bilan 30 xabar.
- **Sirlar** faqat `.env` faylida va repoga tushmaydi. Demo'dagi barcha shaxslar va analitika o'ylab topilgan.

---

## 7. Lokal ishga tushirish

**Talablar:** Python 3.11+, Node.js 18+ va npm. `make` ixtiyoriy.
Kalitlarsiz ham ishlaydi: LLM bo'lmasa javob kartadan shablon bilan beriladi, STT bo'lmasa ovozli xabar qabul qilinmaydi.
Telegram token bo'lmasa, bot CLI rejimida ishlaydi.

```bash
cp .env.example .env                                   # kalitlar bo'sh qolishi mumkin
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt          # Linux/macOS: .venv/bin/pip
cd frontend && npm install && npm run build && cd ..
.venv/Scripts/python scripts/seed_demo_data.py         # dashboard uchun o'ylab topilgan anonim analitika
.venv/Scripts/python -m uvicorn app.main:app --app-dir backend --port 8000
```

- Sayt: http://localhost:8000 · Mini App: http://localhost:8000/miniapp · Dashboard: http://localhost:8000/dashboard ·
  API hujjatlari: http://localhost:8000/docs
- **Bot (Telegram):** `.env` ga `TELEGRAM_BOT_TOKEN` yozing → `.venv/Scripts/python bot/main.py`
- **Bot (tokensiz CLI):** `.venv/Scripts/python bot/cli.py`. Buyruqlar: `/tekshir <matn>`, `/appeal`, `/region <id>`,
  `/profilim`, `/login <profil_id>`, `/ariza <imtiyoz_id>`, `/chiqish`, `/exit`.
- **Frontend dev server:** `cd frontend && npm run dev` (:5173, `/api` so'rovlari :8000 ga yo'naltiriladi)
- **make:** `make install`, `make web`, `make seed`, `make dev`, `make bot`, `make cli`, `make test`, `make smoke`
- **Docker:** `docker compose up --build` (backend :8000 va bot; webhook rejimi uchun :8081)

### `.env` o'zgaruvchilari
To'liq ro'yxat va standart qiymatlar: [`.env.example`](.env.example).

| O'zgaruvchi | Vazifasi |
|---|---|
| `APP_NAME`, `ENV`, `LOG_LEVEL` | Mahsulot nomi, muhit, log darajasi |
| `DATABASE_URL` | Baza manzili (standart: SQLite `data/huquqim.db`; Postgres URL ham ishlaydi) |
| `LLM_PROVIDER` | `anthropic` yoki `gemini` |
| `ANTHROPIC_API_KEY`, `LLM_MODEL`, `LLM_EFFORT` | Anthropic kaliti, modeli va javob tezligi darajasi |
| `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_FALLBACK_MODEL` | Gemini kaliti, asosiy va zaxira modeli |
| `LLM_TIMEOUT`, `LLM_MAX_TOKENS` | LLM so'rovi uchun chegara (soniya) va maksimal hajm |
| `STT_PROVIDER` | `none`, `gemini`, `openai` yoki `faster_whisper` |
| `STT_API_BASE`, `STT_API_KEY`, `STT_MODEL`, `STT_LANGUAGE`, `STT_TIMEOUT` | Whisper-mos API sozlamalari |
| `FASTER_WHISPER_SIZE` | Lokal faster-whisper model o'lchami |
| `TTS_PROVIDER`, `TTS_VOICE_UZ`, `TTS_VOICE_RU`, `TTS_TIMEOUT` | Ovozli javob: provayder, ovozlar, chegara |
| `CLASSIFIER_THRESHOLD` | Kartani tanlash uchun minimal ishonch darajasi |
| `EMBEDDINGS_ENABLED`, `EMBEDDING_MODEL` | Ixtiyoriy sentence-transformers qidiruvi |
| `TELEGRAM_BOT_TOKEN` | Bot tokeni (bo'sh bo'lsa CLI rejimi) |
| `BOT_MODE`, `BOT_WEBHOOK_PATH`, `BOT_WEBHOOK_SECRET`, `BOT_HOST`, `BOT_PORT` | `polling` yoki `webhook` rejimi sozlamalari |
| `BACKEND_URL`, `BACKEND_TIMEOUT` | Bot backendga qaysi manzil orqali va qancha kutib murojaat qiladi |
| `PUBLIC_BASE_URL`, `WEBAPP_URL` | Sayt domeni (webhook va havolalar) va Mini App manzili |
| `CORS_ORIGINS` | Ruxsat etilgan manbalar |
| `ADMIN_TOKEN` | To'ldirilsa, `/api/gov/*` uchun `X-Admin-Token` talab qilinadi |
| `INTERNAL_API_TOKEN` | Bot → backend so'rovlarining imzosi (production'da majburiy) |
| `NOTIFIER_INTERVAL` | Eslatma va xabar yuboruvchi fon jarayonining davri (soniya) |

`config.py` da qo'shimcha sozlamalar ham bor: `GOV_STAFF_SUBS` (davlat xodimlari whitelist'i), `BOT_USERNAME`,
`SIM_COOLDOWN_S`, `SIM_MAX_MESSAGES`.

---

## 8. Testlar

```bash
.venv/Scripts/python -m pytest -q backend/tests bot/tests       # 102 ta test; server, LLM, STT, TTS kerak emas
.venv/Scripts/python scripts/verify_lex_excerpts.py              # abzaslar ↔ jonli lex.uz (internet kerak)
.venv/Scripts/python scripts/smoke_test.py --base <url>          # ishlab turgan serverga demo so'rovlar
.venv/Scripts/python scripts/smoke_accounts.py --base <url>      # 7 ta DEMO ID shaxsi bilan to'liq oqim
.venv/Scripts/python scripts/delete_accounts_by_prefix.py smoke_ --apply   # smoke hisoblarni tozalash
```

Testlar tashqi tarmoqqa chiqmaydi: kalitlar bo'shatiladi, Gemini so'rovlari `httpx.MockTransport` bilan almashtiriladi.

| Fayl | Nimani tekshiradi |
|---|---|
| `test_smoke.py` | Javob pipeline'i: karta, iqtibos, manba, SMS, fakt-tekshiruv |
| `test_ask_topics.py` | Mavzular to'g'ri kartaga tushadi, asl iqtibos bor |
| `test_llm_guard.py` | LLM kartada yo'q raqam yoki havola qo'shsa, javob rad etiladi |
| `test_gemini.py` | Gemini modelini tekshirish, zaxira model, shablonga qaytish, LLM'ga PII ketmasligi |
| `test_stt_gemini.py` | Ovozni matnga aylantirish: so'rov tuzilishi, xato va timeout'da fallback |
| `test_lex_excerpts.py` | Abzaslar rasmiy URL va asl matn bilan |
| `test_rights_categories.py` | 5 toifa, har yozuv abzasga bog'langan, qoidalar dvigateli |
| `test_appeal_templates.py` | Ariza rekvizitlari faqat tatbiq etiladigan qonundan olinadi |
| `test_profiles.py` | Rozilik majburiy, imtiyozlarda «albatta» yo'q, ariza, o'zgarish faqat ta'sir qiladiganga, initData imzosi |
| `test_accounts.py` | Hisob, DEMO ID oqimi, rollar, rate limit, Telegram bog'lash |
| `bot/tests/*` | `/start` oqimi (ikki yo'l, anonim maqom), hisobni botga ulash, CLI profil kirishi, Mini App menyu tugmasi |

---

## 9. Deploy (umumiy tavsif)

- Bitta Linux server. **nginx** HTTPS so'rovlarini qabul qiladi va ichki portdagi FastAPI'ga uzatadi.
  `/dashboard` va `/api/gov/*` nginx basic auth bilan yopilgan.
- **systemd** ikkita xizmatni boshqaradi: `huquqim-web` (uvicorn: API, sayt, Mini App, dashboard) va `huquqim-bot`
  (aiogram, long polling). Xizmatlar alohida tizim foydalanuvchisi nomidan ishlaydi. Himoya sozlamalari:
  `NoNewPrivileges`, `ProtectSystem=strict`, `ProtectHome`, `PrivateTmp`, `MemoryMax`. Yozish faqat ma'lumotlar papkasiga ruxsat etilgan.
- Shablonlar repoda: [`deploy/huquqim-web.service`](deploy/huquqim-web.service), [`deploy/huquqim-bot.service`](deploy/huquqim-bot.service),
  [`deploy/nginx-huquqim.conf`](deploy/nginx-huquqim.conf), [`deploy/constraints.txt`](deploy/constraints.txt) (aniq paket versiyalari).
- Sirlar server muhit faylida saqlanadi, repoga tushmaydi.
- **Har deploydan oldin zaxira olinadi:** kod arxivi, SQLite'ning `.backup` nusxasi, nginx konfiguratsiyasi va muhit fayli.
  Frontend serverda build qilinadi. Kod faqat build muvaffaqiyatli bo'lsa almashtiriladi.
- **Rollback** bitta buyruq bilan bajariladi: xizmatlar to'xtatiladi, zaxiradagi kod (kerak bo'lsa baza va nginx) tiklanadi,
  keyin xizmatlar qayta ishga tushiriladi va `/api/health` tekshiriladi.
- Deploydan keyin tekshiruv: `/api/health` (LLM, STT, TTS, Telegram holati), `smoke_accounts.py`, `verify_lex_excerpts.py`.

---

## 10. Loyiha tuzilmasi

```
backend/                 FastAPI ilovasi
  app/main.py            ishga tushish, kartalarni yuklash, router'lar, statik frontend
  app/config.py          barcha sozlamalar (.env), APP_NAME, 14 hudud
  app/api/               citizen (savol, SMS, fakt, ovoz), account (hisob, kabinet, rollar), gov, profile, lex
  app/services/          classifier, answer, rag, llm, speech, sms_parser, rights, profile, appeal, changes,
                         analytics, outreach, notifier, privacy, security, accounts, cabinet, edu, i18n
  app/oneid_demo/        DEMO ID — OneID simulyatsiyasi (o'z jadvallari, sessiyasi, sahifalari)
  app/models/            SQLAlchemy modellari
  tests/                 pytest
bot/                     aiogram 3 bot: main.py (polling, webhook, CLI), handlers, account_handlers, cli.py, tests/
frontend/                React + Vite + Tailwind: / (sayt, kabinet, anonim), /miniapp, /dashboard
  src/features/          LawView, RightsCategories, AskBox, AppealForm
  src/ui/                umumiy UI komponentlari
knowledge/               bilimlar bazasi (5-bo'lim)
prompts/                 LLM uchun tizim va vazifa promptlari
scripts/                 seed, smoke, lex.uz tekshiruvi, kontent generatorlari, hisoblarni tozalash
deploy/                  systemd, nginx, constraints.txt
docs/ARCHITECTURE.md     arxitektura va OneID integratsiyasi rejasi
brand/                   logo (SVG, PNG), favicon, Telegram avatari
Taqdimot_Huquqim.pdf     taqdimot
DEMO_ACCOUNTS.md         hakamlar uchun demo hisoblar
INFO.md                  qisqa ma'lumot (1 sahifa)
docker-compose.yml, Makefile, requirements.txt, .env.example
```

---

## 11. Demo kirish

Barcha DEMO ID shaxslari, har birida nima ko'rinishi, namunaviy savollar, SMS va feyk post:
**[`DEMO_ACCOUNTS.md`](DEMO_ACCOUNTS.md)**.

---

## 12. Cheklovlar va reja

**Hozirgi demo holati:**
- **DEMO ID** — OneID'ning simulyatsiyasi. Haqiqiy davlat tizimiga ulanmagan, barcha shaxslar o'ylab topilgan.
- Huquqiy mazmun **huquqshunos tasdig'ini kutmoqda**. Barcha yozuvlar `verified: false`, noma'lum joylar `TODO_LAWYER` bilan belgilangan.
- Qonun o'zgarishlari lentasi — **demo** (`[DEMO]` belgili). Dashboard analitikasi o'ylab topilgan ma'lumotlardan tuzilgan.
- Pensiya bo'yicha alohida savol-javob kartasi hali yo'q. Pensiya «Mening huquqlarim»da (Pensioner toifasi) ko'rinadi.
- Rus tilidagi batafsil javob hozircha qisman: sarlavha va asosiy matn tarjima qilingan, qolgani o'zbek tilida.
- Ta'lim moduli (6–8-muammolar) qo'shimcha sifatida faqat talaba rolida ochiq.

**Yo'l xaritasi** (batafsil — [`Taqdimot_Huquqim.pdf`](Taqdimot_Huquqim.pdf)):
- **6 oy:** Adliya vazirligi bilan 1 viloyatda pilot; haqiqiy OneID ulanishi; 100 ta kartani huquqshunos tasdiqlashi; 10 000 foydalanuvchi.
- **1 yil:** 14 hudud; virtual qabulxona bilan ulanish; ta'lim moduli OTM'larda; 50 000 faol foydalanuvchi.
- **3 yil:** 1 mln foydalanuvchi; rus va qoraqalpoq tillari; davlat portallari uchun API.

---

## 13. Jamoa

| | Rol |
|---|---|
| **Rasulberdi Anorov** | Founder, Lead developer, Cybersecurity Research |
| **Jaxona Baxodirova** | Designer |
| **Odina Amonqulova** | Project manager |
