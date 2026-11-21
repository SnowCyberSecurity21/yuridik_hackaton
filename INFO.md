# Huquqim — hakamlar uchun qisqa ma'lumot

**LexHackathon 2026 · 2-trek: «Huquqiy targ'ibot va ta'lim»**

> Barcha huquqiy mazmun hozircha **demo** (`verified: false`, UI'da «TEKSHIRILMAGAN (demo)» belgisi).
> Shaxslar, profillar va dashboard analitikasi — **o'ylab topilgan**, haqiqiy fuqaro ma'lumoti yo'q.

## 1. Muammo → yechim

**Muammo.** Fuqaro qonunni faqat muammo boshiga tushganda qidiradi: jarima SMS keladi, MIB qarzi chiqadi, nafaqa berilmaydi.
Qonun matni murakkab, yuristga 8.6% odamgina pul to'lay oladi. Natijada savol rasmiy murojaatga aylanadi.
Murojaatlarning katta qismi esa "huquqiy ma'lumot berish" bilan yopiladi (masalan, Oliy ta'lim vazirligi, 2026 I chorak: 65.2%).

**Yechim.** Murojaatdan **oldin** oddiy tilda, rasmiy manba bilan tushuntirish:
- Telegram bot (matn + ovoz), Mini App va web sayt — bitta backend.
- Har javob **tekshirilgan vaziyat kartasi**dan olinadi va Lex.uz havolasi bilan chiqadi. Manba topilmasa — "tasdiqlangan ma'lumot topilmadi", taxmin qilinmaydi.
- «Mening huquqlarim»: DEMO ID (OneID simulyatsiyasi) orqali kirgan fuqaro qaysi imtiyozlarga **haqli bo'lishi mumkin**, qaysi muddatli majburiyatlari bor va qaysi qonun o'zgarishi aynan unga ta'sir qilishini ko'radi. Har imtiyozdan bir bosishda tayyor ariza.
- Har savol davlat uchun **anonim signal**ga aylanadi: hududlar bo'yicha "huquqiy tushunmovchilik xaritasi" va bir bosishda targ'ibot kontenti.

Mavjud yechimlarni **to'ldiradi**, takrorlamaydi: LexAI — umumiy savol-javob; Lex.uz bildirishnomalari — xom matn havolasi;
Road24/Payme/MIB — to'lov, lekin huquq va e'tiroz yo'lini tushuntirmaydi.

## 2. Trekning 5 ta muammosi xaritasi

Mentor qarori bilan MVP fuqaro va davlat tomoniga qaratildi (1–5-muammolar). Ta'lim moduli (6–8) kodi saqlangan, demo menyusida yo'q.

| # | Muammo | Huquqim'dagi javob | Qayerda ko'rish |
|---|---|---|---|
| 1 | Qonun tili murakkab | Vaziyat kartasi → ≤8 qator oddiy tilda: nima deydi, sizga nima tegishli, hujjatlar, muddat, qayerga borish + manba | Bot: istalgan savol; sayt `/anonim` |
| 2 | Yangi qonunlarni kech bilishadi | O'zgarishlar zanjiri: yangi o'zgarish **faqat ta'sir qiladigan** profillarga shaxsiy xabar ("Nega sizga: …") | Dashboard → «⚡ O'zgarishni simulyatsiya qilish» |
| 3 | Targ'ibot formatlari eskirgan | Mavzu bo'yicha bir bosishda: 30 soniyalik video ssenariy, infografika matni, Telegram post, 3 savollik test | Dashboard → top mavzular → «✨ Targ'ibot kontenti» |
| 4 | Chekka hududlar, raqamli ko'nikma past | Telegram (yangi ilova shart emas), ovozli savol va 🔊 ovozli javob, kirill yozuvi, forward qilinadigan qisqa kartalar; jarima SMS'ini joylash → tahlil | Bot |
| 5 | Ijtimoiy tarmoqda noto'g'ri ma'lumot | Fakt-tekshiruv: forward qilingan post → To'g'ri / Qisman / Noto'g'ri / Tasdiqlanmagan + aniq manba; dashboard'da "tarqalayotgan feyklar" signali | Bot (forward), Dashboard → signallar |

## 3. Arxitektura

```
 Fuqaro ──► Telegram bot (aiogram 3) ─┐
 Fuqaro ──► Mini App / sayt (React) ──┼──► FastAPI backend ──► SQLite (anonim analitika, rozilik, obuna)
 Davlat ──► /dashboard (React) ───────┘        │
                                               ├─ klassifikator (trigger + TF-IDF) → vaziyat kartasi → javob + manba
                                               ├─ LLM (Anthropic / Gemini) — faqat qayta ifodalaydi, fakt qo'shmaydi
                                               ├─ SMS tahlili (regex, PII olib tashlanadi), fakt-tekshiruv
                                               ├─ imtiyozlar qoidalar dvigateli (knowledge/benefits, rights, laws)
                                               ├─ o'zgarishlar zanjiri (changes_feed → profil nishoni → alert)
                                               ├─ STT / TTS (edge-tts, o'zbek ovozlari)
                                               └─ DEMO ID moduli (/oneid-demo) — OneID simulyatsiyasi
```

- **Xavfsizlik:** har tashqi chaqiruvda timeout + fallback (kalitlarsiz ham ishlaydi). LLM javobida kartada yo'q raqam yoki havola chiqsa — javob rad etiladi.
- **Shaxsiy ma'lumot:** analitikada savol matni, PINFL, pasport, F.I.Sh., telefon saqlanmaydi. Profil ma'lumotlari DB'ga yozilmaydi, faqat rozilik va bog'lanish.
- Batafsil: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## 4. Demo loginlar (DEMO ID — barcha shaxslar o'ylab topilgan)

Sayt: «OneID bilan tasdiqlash» → DEMO ID sahifasi. **Parol hammasi uchun: `12345678`**

| Login | Kim | Nimani ko'rsatadi |
|---|---|---|
| `Malika` | 2 bolali ona, kam ta'minlanganlar reestrida | Bolalar nafaqasi, aliment, tayyor ariza; o'zgarish xabari keladi |
| `Karim` | Yolg'iz pensioner | Pensionerlar imtiyozlari |
| `Sardor` | Haydovchi, yakka tadbirkor | Jarima (50% chegirma muddati), MIB qarzi, eslatma |
| `Erlan` | Chet el fuqarosi, doimiy yashaydi | Huquqiy maqomga qarab boshqacha huquqlar |
| `Azizbek` | Yuridik fakultet talabasi | Ta'lim roli |
| `Dilnoza` | Tuman adliya bo'limi mutaxassisi | Davlat kabineti (analitika, kontent, simulyatsiya) |

- **Anonim rejim:** `/anonim` — kirishsiz savol, SMS tahlili, fakt-tekshiruv.
- **Dashboard** (`/dashboard`) serverda basic auth ortida. Login/parol hakamlarga alohida beriladi.

## 5. 2 daqiqalik demo

1. Bot: ovozli savol "Bolamga nafaqa nega berilmadi?" → oddiy javob + 🔊 audio + manba → «Baribir rozi emasman» → tayyor ariza.
2. Jarima SMS'ini joylash → summa, 50% chegirma muddati, organ, qanday e'tiroz qilish.
3. Feyk postni forward qilish ("1-yanvardan hamma mashinaga yangi soliq") → «Noto'g'ri» + manba.
4. Dashboard: hududlar va top mavzular → «✨ Targ'ibot kontenti» → ssenariy, post, test.
5. «⚡ O'zgarishni simulyatsiya qilish» → xabar faqat o'zgarish taalluqli bo'lgan demo shaxslarga boradi, qolganlarga bormaydi.
