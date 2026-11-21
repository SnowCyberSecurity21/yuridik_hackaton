# Huquqim — hakamlar uchun qisqa ma'lumot

**LexHackathon 2026 · 2-trek: «Huquqiy targ'ibot va ta'lim»**

Sayt: https://huquqim.zehnprotect.uz · Bot: [@Huquqim_official_bot](https://t.me/Huquqim_official_bot) ·
Taqdimot: [`Taqdimot_Huquqim.pdf`](Taqdimot_Huquqim.pdf)

- To'liq hujjat (imkoniyatlar, arxitektura, bilimlar bazasi, xavfsizlik, ishga tushirish): [`README.md`](README.md)
- Demo hisoblar va har birida nima ko'rinishi: [`DEMO_ACCOUNTS.md`](DEMO_ACCOUNTS.md)

> **Huquqiy mazmun.** Qonun abzaslari lex.uz'dan **aynan** olingan (paragrafgacha havola, `retrieved_at`) va
> `scripts/verify_lex_excerpts.py` bilan jonli lex.uz'ga solishtiriladi. Oddiy tildagi matnni AI soddalashtirgan va u
> rasmiy matn yonida ko'rsatiladi. Huquqshunos tasdig'i kutilmoqda: hamma yozuv `verified: false`, UI'da belgi bor.
> Matnda yo'q summa yoki muddat yozilmaydi, o'rnida `TODO_LAWYER` turadi. Shaxslar va dashboard analitikasi **o'ylab topilgan**.

## Muammo

Fuqaro qonunni faqat muammo boshiga tushganda qidiradi: jarima SMS'i keladi, MIB qarzi chiqadi, nafaqa berilmaydi,
stipendiya kesiladi. Qonun matni murakkab, yuristga esa 8,6% odamgina pul to'lay oladi. Natijada savol rasmiy
murojaatga aylanadi. Murojaatlarning katta qismi esa shunchaki «huquqiy ma'lumot berish» bilan yopiladi
(masalan, Oliy ta'lim vazirligi, 2026-yil I chorak: 65,2%).

## Yechim

Murojaatdan **oldin** oddiy tilda, rasmiy manba bilan tushuntirish. Bitta backend uchta kanalga xizmat qiladi:
Telegram bot (matn va ovoz), Mini App va sayt. Har bir savol davlat uchun anonim signalga aylanadi.

| # | Trek muammosi | Huquqim'dagi javob | Qayerda ko'rish |
|---|---|---|---|
| 1 | Qonun tili murakkab | «Qonunda ↔ Oddiy tilda»: lex.uz abzasi va yonida sodda izoh; 8 qatorgacha javob kartasi | Bot, sayt «Savol bering», kabinet |
| 2 | Yangi qonunlarni kech bilishadi | «Mening huquqlarim»: 5 toifa, shaxsiy imtiyozlar; o'zgarish xabari faqat ta'sir qiladigan fuqaroga | Kabinet → O'zgarishlar; Dashboard → «O'zgarishni simulyatsiya qilish» |
| 3 | Targ'ibot formatlari eskirgan | Kartochka, 🔊 audio; davlat uchun bir bosishda video ssenariy, infografika, Telegram post, test | Dashboard → Top-10 mavzu |
| 4 | Uzoq hududlar | Telegram, ovozli savol, kirill yozuvi, ro'yxatdan o'tmasdan anonim rejim | Bot; sayt `/anonim` |
| 5 | Yolg'on ma'lumot | Fakt-tekshiruv (To'g'ri / Qisman / Noto'g'ri / Tasdiqlanmagan) va jarima SMS'i tahlili | Bot (forward), sayt |
| ➕ | — | Tayyor murojaat: 11 ta shablon, qonundagi rekvizitlar, nusxa yoki PDF | Har moduldan |

Huquqim mavjud xizmatlarni to'ldiradi: LexAI umumiy savol-javob beradi, lex.uz bildirishnomasi xom matn havolasini
yuboradi, Road24, Payme va MIB to'lov qabul qiladi, lekin e'tiroz yo'lini tushuntirmaydi.

Arxitektura va javob pipeline'i: [README → 4](README.md#4-arxitektura). Foydalanilgan qonunlar:
[README → 5](README.md#5-bilimlar-bazasi--knowledge). Xavfsizlik va maxfiylik:
[README → 6](README.md#6-xavfsizlik-va-maxfiylik).

## 2 daqiqalik demo

1. **Bot:** ovozli savol «Bolamga nafaqa nega berilmadi?» → oddiy javob, qonundan iqtibos, 🔊 audio va manba →
   «❌ Baribir rozi emasman» → tayyor ariza.
2. **Bot:** jarima SMS'ini joylash → summa, 50% chegirma va muddati, organ, e'tiroz muddati (10 kun), MJtK 332¹-moddadan iqtibos.
3. **Bot:** feyk postni forward qilish («1-yanvardan hamma mashinaga yangi soliq») → «❌ Noto'g'ri» va manba.
4. **Sayt:** `/kirish` → DEMO ID `Malika` → kabinet: bolalar nafaqasi «Haqli bo'lishingiz mumkin» → «Ariza» → PDF.
5. **Davlat kabineti** (DEMO ID `Dilnoza`) yoki `/dashboard`: 14 hudud xaritasi, Top-10 mavzu → «Targ'ibot kontenti»;
   «O'zgarishni simulyatsiya qilish» → xabar faqat taalluqli shaxslarga.

Kirish ma'lumotlari: [`DEMO_ACCOUNTS.md`](DEMO_ACCOUNTS.md).

## Jamoa

Rasulberdi Anorov — Founder, Lead developer, Cybersecurity Research · Jaxona Baxodirova — Designer ·
Odina Amonqulova — Project manager
