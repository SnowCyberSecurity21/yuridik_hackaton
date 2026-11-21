# Huquqim — hakamlar uchun qisqa ma'lumot

**LexHackathon 2026 · 2-trek: «Huquqiy targ'ibot va ta'lim»**

> **Huquqiy mazmun:** 63 ta qonun abzasi lex.uz'dan **aynan** olingan (`original_text`, `lex_url` paragrafgacha, `retrieved_at`)
> va `scripts/verify_lex_excerpts.py` bilan jonli lex.uz'ga solishtirilgan. Oddiy tildagi matn — AI soddalashtirgan,
> rasmiy matn yonida ko'rsatiladi. Huquqshunos tasdig'i kutilmoqda: hamma yozuv `verified: false`, UI'da belgi bor.
> Matnda yo'q summa/muddat yozilmaydi — `TODO_LAWYER` (UI'da «huquqshunos tasdiqlashi kutilmoqda»).
> Shaxslar, profillar va dashboard analitikasi — **o'ylab topilgan**, haqiqiy fuqaro ma'lumoti yo'q.

## 1. Muammo → yechim

**Muammo.** Fuqaro qonunni faqat muammo boshiga tushganda qidiradi: jarima SMS keladi, MIB qarzi chiqadi, nafaqa berilmaydi,
stipendiya kesiladi, soliq tekshiruvi keladi. Qonun matni murakkab, yuristga 8.6% odamgina pul to'lay oladi.
Natijada savol rasmiy murojaatga aylanadi, murojaatlarning katta qismi esa "huquqiy ma'lumot berish" bilan yopiladi
(masalan, Oliy ta'lim vazirligi, 2026 I chorak: 65.2%).

**Yechim.** Murojaatdan **oldin** oddiy tilda, rasmiy manba bilan tushuntirish:
- Telegram bot (matn + ovoz), Mini App va web sayt — bitta backend.
- **«Qonunda» ↔ «Oddiy tilda»**: har javobda lex.uz'dan asl iqtibos va uning yonida sodda izoh («AI soddalashtirdi — rasmiy matn yonida»).
- **«Mening huquqlarim»** — 5 toifa: Talaba · Bolali ona · Yuridik shaxs / tadbirkor · Pensioner · Haydovchi.
  Har toifada imtiyozlar, huquqlar, majburiyatlar, kerakli hujjatlar, qayerga borish (rasmiy portal) va yangiliklar.
- DEMO ID (OneID simulyatsiyasi) orqali kirgan fuqaro qaysi imtiyozlarga **haqli bo'lishi mumkin**ligini va qaysi shartlar
  tekshirilishi kerakligini ko'radi. Natija hech qachon «albatta olasiz» emas.
- **Murojaat generatori**: rekvizitlar aynan tatbiq etiladigan qonundan (Murojaatlar to'g'risidagi Qonun, Soliq kodeksi,
  MJtK — har shablonda qaysi qonun ekani yozilgan), nusxa olish va PDF.
- Har savol davlat uchun **anonim signal**: hududlar bo'yicha "huquqiy tushunmovchilik xaritasi" va bir bosishda targ'ibot kontenti.

Mavjud yechimlarni **to'ldiradi**, takrorlamaydi: LexAI — umumiy savol-javob; Lex.uz bildirishnomalari — xom matn havolasi;
Road24/Payme/MIB — to'lov, lekin huquq va e'tiroz yo'lini tushuntirmaydi.

## 2. Trekning 5 ta muammosi xaritasi

Mentor qarori bilan MVP fuqaro va davlat tomoniga qaratildi (1–5-muammolar). Ta'lim moduli (6–8) kodi saqlangan, talaba rolida ochiq.

| # | Muammo | Huquqim'dagi javob | Qayerda ko'rish |
|---|---|---|---|
| 1 | Qonun tili murakkab | Yonma-yon **«Qonunda» (lex.uz'dan aynan) ↔ «Oddiy tilda»**; vaziyat kartasi ≤ 8 qator: nima deydi, sizga nima tegishli, hujjatlar, muddat, qayerga + iqtibos va manba | Bot: istalgan savol; sayt «Savol bering», «Mening huquqlarim» |
| 2 | Yangi qonunlarni kech bilishadi | Toifa yangiliklari (lex.uz'dagi sana bilan, masalan: 2027-yil 1-yanvardan stipendiya faqat ijtimoiy karta orqali); o'zgarishlar zanjiri **faqat ta'sir qiladigan** profillarga shaxsiy xabar | Toifa → «Yangiliklar»; Dashboard → «⚡ O'zgarishni simulyatsiya qilish» |
| 3 | Targ'ibot formatlari eskirgan | Mavzu bo'yicha bir bosishda: 30 soniyalik video ssenariy, infografika matni, Telegram post, 3 savollik test | Dashboard → top mavzular → «✨ Targ'ibot kontenti» |
| 4 | Chekka hududlar, raqamli ko'nikma past | Telegram (yangi ilova shart emas), ovozli savol va 🔊 javob, kirill yozuvi, forward qilinadigan qisqa kartalar, jarima SMS'ini joylash → tahlil; tayyor ariza PDF | Bot; sayt |
| 5 | Ijtimoiy tarmoqda noto'g'ri ma'lumot | Fakt-tekshiruv: To'g'ri / Qisman / Noto'g'ri / Tasdiqlanmagan + aniq manba; dashboard'da "tarqalayotgan feyklar" | Bot (forward), Dashboard → signallar |

## 3. Arxitektura

```
 Fuqaro ──► Telegram bot (aiogram 3) ─┐
 Fuqaro ──► Mini App / sayt (React) ──┼──► FastAPI backend ──► SQLite (anonim analitika, rozilik, obuna)
 Davlat ──► /dashboard (React) ───────┘        │
                                               ├─ klassifikator (trigger + TF-IDF) → vaziyat kartasi → javob + iqtibos + manba
                                               ├─ qonun abzaslari (knowledge/lex/excerpts.json): asl matn + oddiy til
                                               │     └─ scripts/verify_lex_excerpts.py — jonli lex.uz bilan solishtirish
                                               ├─ «Mening huquqlarim»: 5 toifa (knowledge/rights) + qoidalar dvigateli (knowledge/benefits)
                                               ├─ murojaat shablonlari: qonundagi rekvizitlar (knowledge/appeal_templates)
                                               ├─ LLM (Anthropic / Gemini) — faqat qayta ifodalaydi, fakt qo'shmaydi
                                               ├─ SMS tahlili (regex, PII olib tashlanadi), fakt-tekshiruv
                                               ├─ o'zgarishlar zanjiri (changes_feed → profil nishoni → alert)
                                               ├─ STT / TTS (edge-tts, o'zbek ovozlari)
                                               └─ DEMO ID moduli (/oneid-demo) — OneID simulyatsiyasi
```

- **Manba qoidasi (kodda):** abzas faqat rasmiy URL (`lex.uz` yoki `*.gov.uz`), `retrieved_at` va TODO bo'lmagan asl matn bilan ko'rsatiladi.
  Abzasga bog'lanmagan yozuv «Mening huquqlarim» toifasida chiqmaydi. LLM javobida kartada yo'q raqam yoki havola bo'lsa — rad etiladi.
- **Shaxsiy ma'lumot:** analitikada savol matni, PINFL, pasport, F.I.Sh., telefon saqlanmaydi. Profil va ariza maydonlari DB'ga yozilmaydi.
- **Xavfsizlik:** har tashqi chaqiruvda timeout + fallback (kalitlarsiz ham ishlaydi).
- Batafsil: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

### Foydalanilgan qonun hujjatlari (lex.uz, 21.11.2026)

| Hujjat | Nima uchun | lex.uz |
|---|---|---|
| «Ta'lim to'g'risida»gi Qonun (O'RQ-637) | talaba huquqlari, majburiyatlari, ijtimoiy himoya (47, 48, 52-m.) | [-5013007](https://lex.uz/docs/-5013007) |
| VM 31.01.2020 dagi 59-son qarori, 1-ilova | stipendiya turlari va shartlari | [-4725554](https://lex.uz/docs/-4725554) |
| VM 28.01.2026 dagi 32-son qarori, 1-ilova | yotoqxona to'lovini qoplash | [-8022224](https://lex.uz/docs/-8022224) |
| VM 29.01.2026 dagi 35-son qarori, 3-ilova | bolalar nafaqasi | [-8027513](https://lex.uz/docs/-8027513) |
| Mehnat kodeksi | dekret, bola parvarishi, homilador ayollar kafolatlari (392, 404, 405, 408-m.) | [-6257288](https://lex.uz/docs/-6257288) |
| Oila kodeksi | aliment (96, 99, 112, 116-m.) | [-104720](https://lex.uz/docs/-104720) |
| Soliq kodeksi | ro'yxat, aylanma soliq, QQS, tekshiruvda huquqlar, shikoyat (21, 22, 126, 137–139, 232, 233, 237, 461-m.) | [-4674902](https://lex.uz/docs/-4674902) |
| «Fuqarolarning davlat pensiya ta'minoti to'g'risida»gi Qonun | pensiya huquqi, yoshi, proaktiv tayinlash | [-112314](https://lex.uz/docs/-112314) |
| Ma'muriy javobgarlik to'g'risidagi kodeks | jarima chegirmasi, to'lash va shikoyat muddati (316, 332, 332¹-m.) | [-97664](https://lex.uz/docs/-97664) |
| «Jismoniy va yuridik shaxslarning murojaatlari to'g'risida»gi Qonun (O'RQ-378) | murojaat rekvizitlari, muddatlar, tatbiq doirasi (2, 5, 6, 16, 17, 19-m.) | [-2509996](https://lex.uz/docs/-2509996) |

## 4. Demo loginlar (DEMO ID — barcha shaxslar o'ylab topilgan)

Sayt: «OneID bilan tasdiqlash» → DEMO ID sahifasi. **Parol hammasi uchun: `12345678`**

| Login | Kim | Nimani ko'rsatadi |
|---|---|---|
| `Azizbek` | Yuridik fakultet talabasi (davlat OTM, kunduzgi, grant, yotoqxonada) | Ta'lim bo'limi + talaba imtiyozlari: stipendiya «haqli bo'lishingiz mumkin», yotoqxona qoplanishi — «mos emas» (oila reyestrda emas) |
| `Malika` | 2 bolali ona, kam ta'minlanganlar reestrida | Bolalar nafaqasi, aliment, «Bolali ona» toifasi, tayyor ariza; o'zgarish xabari keladi |
| `Jasur` | Yuridik shaxs rahbari (MChJ direktori) | «Yuridik shaxs / tadbirkor»: aylanma soliq rejimi, soliq tekshiruvida huquqlar, shikoyat shabloni (yuridik shaxs rekvizitlari) |
| `Karim` | Yolg'iz pensioner | Pensioner toifasi, pensiya huquqlari |
| `Sardor` | Haydovchi, yakka tadbirkor | Jarima (50% / 70% chegirma muddati — MJtK 332¹), MIB qarzi, eslatma |
| `Erlan` | Chet el fuqarosi, doimiy yashaydi | Huquqiy maqomga qarab boshqacha huquqlar |
| `Dilnoza` | Tuman adliya bo'limi mutaxassisi | Davlat kabineti (analitika, kontent, simulyatsiya) |

- **Anonim rejim:** `/anonim` — kirishsiz savol, «Mening huquqlarim» toifalari, SMS tahlili, fakt-tekshiruv.
- **Dashboard** (`/dashboard`) serverda basic auth ortida. Login/parol hakamlarga alohida beriladi.

## 5. 2 daqiqalik demo

1. Bot: ovozli savol "Bolamga nafaqa nega berilmadi?" → oddiy javob + **qonundan iqtibos** + 🔊 audio + manba → «Baribir rozi emasman» → tayyor ariza.
2. Jarima SMS'ini joylash → summa, 50% chegirma muddati, organ, e'tiroz muddati (10 kun) + MJtK 332¹-modda iqtibosi.
3. Sayt «Savol bering»: "Stipendiya nega berilmadi?" → «Qonunda» ↔ «Oddiy tilda» → «Ariza tayyorlash» → rektorga ariza, PDF.
4. Feyk postni forward qilish ("1-yanvardan hamma mashinaga yangi soliq") → «Noto'g'ri» + manba.
5. Dashboard: hududlar va top mavzular → «✨ Targ'ibot kontenti»; «⚡ O'zgarishni simulyatsiya qilish» → xabar faqat taalluqli shaxslarga.
