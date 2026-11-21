# Huquqim — hakamlar uchun demo hisoblar

Sayt: https://huquqim.zehnprotect.uz · Bot: [@Huquqim_official_bot](https://t.me/Huquqim_official_bot) ·
To'liq hujjat: [`README.md`](README.md)

> ⚠️ **Barcha shaxslar o'ylab topilgan.** DEMO ID — OneID'ning simulyatsiyasi, haqiqiy davlat tizimiga ulanmagan.
> Ism, sana, summa va invoyslar fiktiv. Haqiqiy OneID login va parolingizni kiritmang.
>
> Quyidagi natijalar **21.11.2026 kuni jonli saytda** har bir hisob bilan kirib tekshirilgan.
> Majburiyat muddatlari kirgan kunga nisbatan hisoblanadi (masalan, «6 kundan keyin»).

## Qanday kirish kerak

1. https://huquqim.zehnprotect.uz/kirish → **«Hisob ochish»**: istalgan login va parolni o'ylab toping.
   Bu Huquqim hisobi bo'lib, unga shaxsiy ma'lumot yozilmaydi.
2. **«OneID bilan tasdiqlang»** → DEMO ID sahifasi ochiladi.
3. Pastdagi jadvaldan **DEMO ID login**ini kiriting. Parol hammasi uchun bir xil: **`12345678`**.
4. Rozilik ekranida **«✅ Roziman»** tugmasini bosing → `/kabinet` ochiladi.
5. Boshqa shaxsni ko'rish uchun kabinetda **«Rozilikni bekor qilish»**ni bosing va 2-qadamdan takrorlang.
   Yoki yangi Huquqim hisobi oching.

| DEMO ID login | Parol | Kim | Asosiy ko'rinish |
|---|---|---|---|
| `Malika` | `12345678` | 2 bolali ona | Bolalar nafaqasi va aliment, gaz qarzi |
| `Azizbek` | `12345678` | Yuridik fakultet talabasi | Stipendiya; yotoqxona «mos emas»; Ta'lim bo'limi |
| `Jasur` | `12345678` | MChJ direktori | Aylanma soliq rejimi, soliq tekshiruvi |
| `Karim` | `12345678` | Yolg'iz pensioner | Pensiyani qayta hisoblash, uyda ijtimoiy xizmat |
| `Sardor` | `12345678` | Haydovchi va yakka tadbirkor | Jarima chegirmasi, MIB qarzi, e'tiroz arizasi |
| `Erlan` | `12345678` | Chet el fuqarosi | Maqomga qarab boshqa huquqlar va qonun |
| `Dilnoza` | `12345678` | Tuman adliya bo'limi mutaxassisi | Davlat kabineti |

Kabinetdagi har bir imtiyozda bitta holat ko'rinadi:
- **«Haqli bo'lishingiz mumkin»** — ✓ bajarilgan shartlar va ❔ «tekshirilishi kerak» bo'lgan shartlar bilan.
- **«Mos emas»** — qaysi shart bajarilmagani yoziladi.

Natija hech qachon «albatta olasiz» emas.

---

## Malika — 2 bolali ona

| | |
|---|---|
| **Kim** | Malika Sobirova (DEMO), 1994-yilda tug'ilgan, Samarqand. Ajrashgan, oilada 3 kishi, bolalari 6 va 3 yoshda. Vaqtincha ishsiz, kam ta'minlanganlar reestrida. O'zbekiston fuqarosi |
| **Toifalar** | Ota-ona · Bolali ona |
| **Imtiyozlar** | ✅ **Ijtimoiy reyestrdagi oilalarga bolalar nafaqasi** — «Haqli bo'lishingiz mumkin». ✓ eng kichik bola 18 yoshga to'lmagan; ✓ oila Ijtimoiy reyestrda. ❔ rad etish asoslari yo'qligi (daromad, ko'chmas mulk, avtomobil, depozit) tekshirilishi kerak |
| | ✅ **Bolalar uchun aliment undirish huquqi** — «Haqli bo'lishingiz mumkin». ✓ voyaga yetmagan bola bor; ✓ bolalarni yolg'iz tarbiyalaydi. ❔ aliment bo'yicha kelishuv yoki sud qarori bor-yo'qligi |
| | ❌ Mos emas: pensiyani qayta hisoblash, yolg'iz keksalarga xizmat, jarima chegirmasi, bola parvarishi ta'tili (mehnat shartnomasi yo'q, 2 yoshgacha bola yo'q) |
| **Huquqlar** | Fuqaro sifatida: murojaat, mehnat, ijtimoiy ta'minot, ta'lim, sud himoyasi. Bolali ona sifatida: bolalar nafaqasi, homiladorlik va tug'ish ta'tili, bola parvarishi ta'tili, aliment, homiladorlik yoki bola sababli ishdan bo'shatish taqiqi |
| **Majburiyatlar** | Ota-onaning majburiyati, bolani voyaga yetguncha boqish. Muddatli: **gaz qarzi 186 000 so'm, muddati 15 kundan keyin** (⏰ eslatma qo'yish mumkin) |
| **Hujjatlar** | Nafaqa uchun: shaxsni tasdiqlovchi hujjat va ariza (davlat xizmatlari markazi, «Inson» markazi, my.gov.uz yoki «Ijtimoiy karta» orqali). Aliment uchun: bolalarning tug'ilganlik haqidagi guvohnomasi, nikohdan ajratish haqidagi hujjat |
| **Ariza** | Nafaqa → **ARIZA**, «Tuman (shahar) "Inson" ijtimoiy xizmatlar markazi rahbariga». Asos: VM 35-son qarori, 3-ilova. Aliment → **ARIZA**, yashash joyidagi vakolatli sudga |
| **Namunaviy savollar** | «Bolamga nafaqa nega berilmadi?» · «Sobiq erim aliment to'lamayapti, nima qilay?» · «Gaz qarzi uchun sud buyrug'i keldi» |
| **Kutiladigan natija** | Har bir savol o'z kartasiga tushadi: `child_allowance_refused`, `alimony`, `utility_debt_court_order`. Javobda qonundan iqtibos, sodda izoh, hujjatlar va manba bo'ladi |

## Azizbek — talaba

| | |
|---|---|
| **Kim** | Azizbek Rustamov (DEMO), 20 yosh, Toshkent shahri. Yuridik fakultet, 3-kurs, davlat OTM, kunduzgi, davlat granti, yotoqxonada yashaydi. Oila Ijtimoiy reyestrda emas |
| **Toifa / rol** | Talaba · **Ta'lim bo'limi ochiq** (`student` roli). Davlat kabineti yopiq (403) |
| **Imtiyozlar** | ✅ **Talaba stipendiyasi** — «Haqli bo'lishingiz mumkin». ✓ OTM talabasi, kunduzgi, davlat OTM, grant. ❔ oldingi semestrda «qoniqarli» baholar 30% dan kam ekani |
| | ❌ **Yotoqxona to'lovini davlat qoplashi — mos emas.** Sababi: oila Ijtimoiy reyestrga kiritilmagan |
| | ❌ Mos emas: bolalar nafaqasi, aliment, pensiya, keksalarga xizmat, jarima chegirmasi |
| **Huquqlar** | Oylik stipendiya va uning oshirilgan turlari (a'lochilar, kontrakt, qizlar, nogironligi bo'lgan, yetim talabalar), bir martalik moddiy yordam, imtiyozli ta'lim krediti, akademik ta'til, o'qishni tiklash va ko'chirish, OTM obyektlaridan bepul foydalanish, o'qishga aloqasi yo'q ishga jalb qilish taqiqi |
| **Majburiyatlar** | Talabaning majburiyatlari («Ta'lim to'g'risida»gi Qonun). Muddatli majburiyat yo'q |
| **Hujjatlar** | Stipendiya uchun alohida hujjat shart emas: komissiya xulosasi va rektor buyrug'i bilan tayinlanadi. Tayinlanmasa, rektor nomiga yozma ariza beriladi |
| **Ariza** | Stipendiya → **ARIZA**, «Oliy ta'lim muassasasi rektoriga» (shablon `appeal_stipend`) |
| **Namunaviy savollar** | «Stipendiya nega berilmadi?» · «Yotoqxona to'lovini davlat qoplaydimi?» · «Ish beruvchi 3 oydan beri oylik bermayapti» |
| **Kutiladigan natija** | `student_stipend`, `student_dormitory`, `unpaid_salary` kartalari. Kabinetda «Ta'lim» bo'limi ham bor |

## Jasur — yuridik shaxs rahbari

| | |
|---|---|
| **Kim** | Jasur Qodirov (DEMO), 1985-yilda tug'ilgan, Buxoro. «Demo Savdo» MChJ direktori, yillik daromadi 750 mln so'm, aylanma soliq rejimida. Uylangan, 2 farzandi bor, haydovchilik guvohnomasi bor |
| **Toifalar** | Yuridik shaxs / tadbirkor · Ota-ona · Haydovchi |
| **Imtiyozlar** | ✅ **Aylanmadan olinadigan soliq rejimi** — «Haqli bo'lishingiz mumkin». ✓ yuridik shaxs yoki YaTT; ✓ yillik daromad 1 mlrd so'mdan oshmaydi. ❔ Soliq kodeksi 461-moddasidagi istisnolarga tushmasligi |
| | ❌ Mos emas: bolalar nafaqasi (reyestrda emas), aliment, pensiya, keksalarga xizmat, jarima chegirmasi |
| **Huquqlar** | Ro'yxatdan o'tganda soliq hisobiga avtomatik qo'yish, aylanma soliq, QQS kimga tatbiq etiladi, «AAA» reytingdagilarda tekshiruv yo'q, kameral tekshiruvda kirish va hujjat talab qilish mumkin emas, sayyor tekshiruv faqat buyruq bilan va 10 kundan oshmaydi, tekshiruv natijasi ustidan shikoyat 1 oy ichida. Haydovchi sifatida: jarimani chegirma bilan to'lash, 10 kun ichida shikoyat |
| **Majburiyatlar** | Soliq to'lovchining majburiyatlari, soliq to'lash, bolani boqish, YHQ jarimasini muddatida to'lash |
| **Hujjatlar** | Davlat ro'yxatidan o'tganlik guvohnomasi. Shikoyat uchun tekshiruv dalolatnomasi va qaror |
| **Ariza** | Soliq rejimi → **ARIZA**, «Hududiy soliq organi rahbariga». Asos: Soliq kodeksi, 461-modda |
| **Namunaviy savollar** | «Soliq tekshiruvi keldi, nima qilay?» · «Aylanma soliq yoki QQS, qaysi biri menga to'g'ri keladi?» · «Sifatsiz telefon sotib oldim, do'kon pulimni qaytarmayapti» |
| **Kutiladigan natija** | `business_tax_audit` (shikoyat shabloni `appeal_tax_audit_complaint`, ariza beruvchi — yuridik shaxs), `business_tax_regime`, `consumer_refund` |

## Karim — yolg'iz pensioner

| | |
|---|---|
| **Kim** | Karim Toshmatov (DEMO), 1956-yilda tug'ilgan, Toshkent viloyati. Beva, yolg'iz yashaydi, voyaga yetgan 2 farzandi bor. Pensiyada |
| **Toifa** | Pensioner |
| **Imtiyozlar** | ✅ **Pensiyani tekshirish va qayta hisoblashni so'rash** — «Haqli bo'lishingiz mumkin». ✓ pensiya oladi. ❔ hisobga olinmagan ish staji yoki daromad bor-yo'qligi |
| | ✅ **Yolg'iz keksalarga ijtimoiy xizmat (uyda yordam)** — «Haqli bo'lishingiz mumkin». ✓ pensiya yoshida; ✓ yolg'iz yashaydi. ❔ parvarishga muhtojlik darajasi |
| | ❌ Mos emas: bolalar nafaqasi, aliment, jarima chegirmasi |
| **Huquqlar** | Yoshga doir pensiya (arizasiz tayinlanadi), davlat pensiyasi turlari, pensiya olish huquqi, qariganda ijtimoiy ta'minot, istalgan vaqtda pensiya so'rab murojaat qilish |
| **Majburiyatlar** | Muddatli majburiyat yo'q |
| **Hujjatlar** | Qayta hisoblash uchun: ariza, mehnat daftarchasi yoki ish stajini tasdiqlovchi hujjatlar. Uyda yordam uchun: ariza |
| **Ariza** | Qayta hisoblash → **ARIZA**, pensiya tayinlovchi organning tuman (shahar) bo'limiga. Uyda yordam → **ARIZA**, «Tuman (shahar) "Inson" ijtimoiy xizmatlar markazi rahbariga» |
| **Namunaviy savollar** | «MIB nomidan havolali SMS keldi, bu rostmi?» · «Nomimga men olmagan onlayn kredit rasmiylashtirilgan» · «Gaz qarzi uchun sud buyrug'i keldi» |
| **Kutiladigan natija** | `fake_mib_sms`, `online_loan_fraud`, `utility_debt_court_order`. Pensiya bo'yicha alohida savol-javob kartasi hali yo'q: «Pensiyamni qayta hisoblatsa bo'ladimi?» degan savolga javob «tasdiqlangan ma'lumot topilmadi» bo'ladi. Pensiya ma'lumoti kabinetda ko'rinadi |

## Sardor — haydovchi va yakka tadbirkor

| | |
|---|---|
| **Kim** | Sardor Alimov (DEMO), 1998-yilda tug'ilgan, Toshkent shahri. Yakka tadbirkor (yuk tashish), uylangan, 2 yoshli farzandi bor, haydovchilik guvohnomasi 2017-yildan |
| **Toifalar** | Haydovchi · Yuridik shaxs / tadbirkor · Ota-ona |
| **Imtiyozlar** | ✅ **Jarimani chegirma bilan to'lash yoki e'tiroz bildirish** — «Haqli bo'lishingiz mumkin». ✓ chegirma muddati o'tmagan jarimasi bor. ❔ chegirma shu qoidabuzarlik turiga tatbiq etilishi |
| | ✅ **Aylanmadan olinadigan soliq rejimi** — «Haqli bo'lishingiz mumkin». ✓ YaTT. ❔ yillik daromad 1 mlrd so'mdan oshmasligi va 461-moddadagi istisnolar |
| | ❌ Mos emas: bolalar nafaqasi (reyestrda emas), aliment, pensiya, keksalarga xizmat |
| **Huquqlar** | Jarimani chegirma bilan to'lash, jarima ustidan 10 kun ichida shikoyat qilish, jarimalar qayerda yozilgani; tadbirkor sifatidagi soliq huquqlari |
| **Majburiyatlar** | **Yo'l harakati jarimasi (kamera): 44 000 so'm. Chegirma bilan 22 000 so'm (50%), chegirma muddati 6 kundan keyin tugaydi, to'liq muddat 30 kun** (invoys DEMO-0000000001). **MIB qarzi: 1 250 000 so'm**, ogohlantirish: qarz uzilmasa, chet elga chiqish cheklanishi mumkin |
| **Hujjatlar** | Jarima qarori yoki invoys raqami; rozi bo'lmasa e'tiroz uchun dalillar (foto, video) |
| **Ariza** | Jarima → **SHIKOYAT (E'TIROZ)**, jarima qarorini chiqargan organning yuqori turuvchi organiga yoki sudga. Asos: MJtK. Soliq rejimi → **ARIZA**, «Hududiy soliq organi rahbariga» |
| **Namunaviy savollar** | «Jarimani chegirma bilan qachongacha to'lash mumkin?» · «MIB qarzim bor, chet elga chiqa olamanmi?» · «Mahallada chiqindi uchun jarima yozishdi» |
| **Kutiladigan natija** | `traffic_fine`, `mib_debt_travel_ban`, `mahalla_noise_waste_fine` |

## Erlan — chet el fuqarosi

| | |
|---|---|
| **Kim** | Erlan Nurlanov (DEMO), 1987-yilda tug'ilgan, Toshkent shahri. Chet el fuqarosi, O'zbekistonda doimiy yashaydi (chet el fuqarosining ID-kartasi). Xususiy kompaniyada muhandis, uylangan, 7 yoshli farzandi bor |
| **Maqom / toifalar** | **Chet el fuqarosi** (vaqtincha yoki doimiy yashovchi) · Yollanib ishlovchi · Ota-ona · Haydovchi |
| **Imtiyozlar** | Hozircha mos imtiyoz topilmadi. ❌ bolalar nafaqasi (reyestrda emas), aliment, pensiya, keksalarga xizmat, jarima chegirmasi |
| **Huquqlar** | Maqomga qarab boshqa ro'yxat chiqadi: huquq va erkinliklar kafolati, mehnat huquqlari, pensiya (doimiy yashovchilar uchun), sog'liqni saqlash, ta'lim olish, davlat organlariga murojaat, ID-karta (doimiy yashovchilar). Qonunlar ro'yxatida birinchi bo'lib O'RQ-692 turadi |
| **Majburiyatlar** | Bolani boqish, YHQ jarimasini muddatida to'lash. Muddatli majburiyat yo'q |
| **Ariza** | Imtiyoz yo'qligi sababli tayyor imtiyoz arizasi chiqmaydi. Savol javobidagi «Baribir rozi emasman» tugmasi orqali ariza tuzish mumkin |
| **Namunaviy savollar** | «Chet el fuqarosi O'zbekistonda ishlashi mumkinmi?» · «Chet el fuqarosi davlat organiga murojaat qila oladimi?» · «Bolamga nafaqa nega berilmadi?» |
| **Kutiladigan natija** | Birinchi ikki savolga lex.uz abzaslari bo'yicha (RAG) O'RQ-692 dan iqtibos bilan javob beriladi. Uchinchi savolga `child_allowance_refused` kartasi chiqadi. Unga «ℹ️ Siz chet el fuqarosisiz: bu masalada qoida siz uchun boshqacha bo'lishi mumkin…» eslatmasi (O'RQ-692, VM 35) qo'shiladi |

## Dilnoza — davlat xodimi

| | |
|---|---|
| **Kim** | Dilnoza Yusupova (DEMO), 1990-yilda tug'ilgan, Farg'ona. Tuman adliya bo'limi bosh mutaxassisi, turmush qurgan, farzandlari 9 va 5 yoshda |
| **Toifa / rol** | Davlat xizmatchisi · Yollanib ishlovchi · Ota-ona · Bolali ona · **`gov` roli** (whitelist orqali, OneID'dan emas) |
| **Imtiyozlar** | Hozircha mos imtiyoz topilmadi. ❌ bolalar nafaqasi (reyestrda emas), aliment, pensiya, keksalarga xizmat, jarima chegirmasi, bola parvarishi ta'tili (2 yoshgacha bola yo'q) |
| **Huquqlar va majburiyatlar** | Davlat xizmatchisi sifatida: murojaatlar bilan ishlash, murojaatlarni muddatida ko'rib chiqish, shaxsiy ma'lumotlarni himoya qilish. Ona sifatida: nafaqa, dekret va ishda kafolatlar |
| **Davlat kabineti** | Kabinetda «Davlat kabineti» bo'limi: analitika, Top-10 mavzu, 14 hudud, targ'ibot kontenti, «O'zgarishni simulyatsiya qilish» (pastdagi [Dashboard](#dashboard) bo'limiga qarang) |
| **Namunaviy savollar** | «Dekret ta'tili necha kun?» · «Bolamga nafaqa nega berilmadi?» · «Ish beruvchi 3 oydan beri oylik bermayapti» |
| **Kutiladigan natija** | `maternity_childcare`, `child_allowance_refused`, `unpaid_salary` |

---

## Anonim rejim

1. https://huquqim.zehnprotect.uz/anonim
2. Huquqiy maqomni tanlang: O'zbekiston fuqarosi · Chet el fuqarosi · Fuqaroligi bo'lmagan shaxs · Bilmayman.
3. Ixtiyoriy ravishda holatni tanlang (bir nechtasini tanlash mumkin): Talaba, Bolali ona, Ota-ona, Tadbirkor, Pensioner, Haydovchi.
4. Umumiy huquqlar va qonunlar chiqadi. Pastdagi «Savol · SMS · Feyk» blokida savol bering.

Namunaviy savollar (har biri jonli saytda o'z kartasiga tushadi):
- «Bolamga nafaqa nega berilmadi?» → `child_allowance_refused`
- «Боламга нафақа нега берилмади?» → shu karta, javob kirill yozuvida
- «Почему не дали детское пособие?» → shu karta, sarlavha va asosiy matn rus tilida
- «Stipendiya nega berilmadi?» → `student_stipend`
- «Jarimani chegirma bilan qachongacha to'lash mumkin?» → `traffic_fine`
- «Nomimga men olmagan onlayn kredit rasmiylashtirilgan» → `online_loan_fraud`

15 mavzuning to'liq ro'yxati: [README → 3.5](README.md#35-savol-bering).

---

## Telegram bot

[@Huquqim_official_bot](https://t.me/Huquqim_official_bot)

1. `/start` → **«👤 Anonim davom etish»** → maqom → holat (ixtiyoriy) → «➡️ Tayyor».
   Shaxsiy menyu uchun: saytda kabinet → **«Telegram'ni ulash»** → botda ulanadi (havola 10 daqiqa amal qiladi).
2. **Matnli savol:** «Bolamga nafaqa nega berilmadi?»
3. **Ovozli savol:** shu savolni ovoz bilan ayting. Bot avval «🎙 Eshitdim: «…»» deb yozadi, keyin javob beradi.
4. Javob ostida: 🔊 Audio · 📄 Manba · ✅ Tushundim · ❌ Baribir rozi emasman (tayyor ariza) · 📤 Ulashish.
5. **SMS tahlili.** Quyidagi o'ylab topilgan SMS'ni yuboring:

   ```
   Aliyev Bobur Karimovich, 12.03.1990. Invoys 2611210000123. To'lov 18.11.2026dan. JARIMA 375 000.00 so'm, 28.11.2026gacha 187 500.00 so'm(50%). Organ YHXB / TOSHKENT SH.
   ```

   Kutiladigan natija: ism va tug'ilgan sana olib tashlanadi. Javobda: jarima 375 000 so'm, chegirmali summa
   187 500 so'm (50%), muddati 28.11.2026 (qolgan kunlar soni bilan), organ YHXB / TOSHKENT SH, invoys raqami.
   Keyin nima qilish kerakligi, e'tiroz yo'li (10 kun ichida) va MJtK 332¹-moddadan iqtibos keladi.
6. **Fakt-tekshiruv.** Postni forward qiling yoki `/tekshir` buyrug'idan keyin yuboring:

   ```
   1-yanvardan hamma mashinaga yangi soliq joriy qilinadi, tarqating!
   ```

   Kutiladigan natija: **«❌ Noto'g'ri»**. Da'vo rasmiy hujjat bilan tasdiqlanmagan, manba sifatida Soliq kodeksi ko'rsatiladi.
   Bu yozuv hali huquqshunos tasdig'idan o'tmagan, shuning uchun «TEKSHIRILMAGAN (demo)» belgisi bor.

Xuddi shu SMS va post saytdagi «SMS tahlili» va «Feyk tekshiruvi» bo'limlarida ham ishlaydi.

---

## Dashboard

Davlat analitikasi ikki yo'l bilan ochiladi:
- **DEMO ID `Dilnoza`** bilan kirish → kabinetdagi «Davlat kabineti» bo'limi.
- **https://huquqim.zehnprotect.uz/dashboard** — server tomonida basic auth bilan yopilgan.
  **Login va parol hakamlarga alohida beriladi.**

Ko'rinadigan narsalar (ma'lumotlar o'ylab topilgan):
- Jami savollar, haftalik o'zgarish, «Konsultatsiya murojaati oldi olindi», tayyor murojaatlar, foydali deb baholanganlar ulushi.
- **«Huquqiy tushunmovchilik xaritasi — 14 hudud»**, 28 kunlik trend, **Top-10 mavzu**. Qatorni bossangiz, xarita va trend shu mavzu bo'yicha filtrlanadi.
- **Signallar:** 🚨 tarqalayotgan feyk da'volar va 🧩 eng ko'p tushunilmayotgan mavzular (→ «✏️ Soddalashtirish»).
- **Targ'ibot kontenti:** 🎬 30 soniyalik video ssenariy, 🖼 infografika matni, 📣 Telegram post, ❓ 3 savollik test.
- **«O'zgarishni simulyatsiya qilish»:** qaysi DEMO ID shaxsiga 🔔 xabar borishi va qaysilariga 🔕 «taalluqli emas»ligi ko'rinadi.
  Bog'liq kartalar «qayta tekshiruvga» belgilanadi. **«Demo'ni tiklash»** tugmasi natijani qaytaradi.
