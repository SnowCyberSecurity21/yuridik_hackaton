"""knowledge/laws va knowledge/rights fayllarini yaratadi.

Har bir yozuv lex.uz'dagi hujjat sahifasini 2026-11-21 da ochib tekshirilgan (sarlavha, sana, raqam, modda matni).
Raqami sahifada aniq ko'rinmagan hujjatlarda `number` = "TODO_LAWYER" (UI: «Tekshirilishi kerak»).
`excerpt` — lex.uz'dagi modda matnidan qisqa ko'chirma (kirillda) — huquqshunos tekshirishi uchun.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "knowledge"
R = "2026-11-21"
LEX = "lex.uz"

LAWS = [
    dict(id="constitution", title_uz="O'zbekiston Respublikasi Konstitutsiyasi", title_official="Ўзбекистон Республикаси Конституцияси",
         number="—", number_note="2023-yil 30-aprel referendumida qabul qilingan (raqamsiz)", date="2023-04-30",
         url="https://lex.uz/docs/6445145",
         plain_uz="Davlatning asosiy qonuni. Har kimning huquq va erkinliklari, fuqarolarning burchlari, chet el fuqarolari va fuqaroligi bo'lmagan shaxslarning holati shu yerda belgilangan.",
         statuses=["uz_citizen", "foreign", "stateless", "unknown"], situations=[]),
    dict(id="foreign_status_law", title_uz="O'zbekiston Respublikasida chet el fuqarolarining va fuqaroligi bo'lmagan shaxslarning huquqiy holati to'g'risida",
         title_official="Ўзбекистон Республикасида чет эл фуқароларининг ва фуқаролиги бўлмаган шахсларнинг ҳуқуқий ҳолати тўғрисида",
         number="O'RQ-692", date="2021-06-04", url="https://lex.uz/docs/5443899",
         plain_uz="Chet el fuqarolari va fuqaroligi bo'lmagan shaxslar O'zbekistonda qanday huquq va majburiyatlarga ega ekanini belgilaydi: mehnat, pensiya, sog'liqni saqlash, ta'lim, murojaat, soliq.",
         statuses=["foreign", "stateless", "unknown"], situations=[]),
    dict(id="appeals_law", title_uz="Jismoniy va yuridik shaxslarning murojaatlari to'g'risida",
         title_official="Жисмоний ва юридик шахсларнинг мурожаатлари тўғрисида", number="O'RQ-378", date="2014-12-03",
         url="https://lex.uz/docs/2509996",
         plain_uz="Davlat organlariga ariza, taklif va shikoyat berish tartibi: murojaatni qanday yozish, qayerga yuborish va qanday ko'rib chiqilishi.",
         statuses=["uz_citizen", "foreign", "stateless", "unknown"], situations=["civil_servant"]),
    dict(id="labor_code", title_uz="O'zbekiston Respublikasining Mehnat kodeksi", title_official="Ўзбекистон Республикасининг Меҳнат кодекси",
         number="TODO_LAWYER", date="2022-10-28", url="https://lex.uz/docs/6257288",
         plain_uz="Ishga qabul qilish, ish haqi, ish vaqti, ta'til va mehnat nizolari qoidalari.",
         statuses=[], situations=["worker", "student", "civil_servant"]),
    dict(id="admin_code", title_uz="O'zbekiston Respublikasining Ma'muriy javobgarlik to'g'risidagi kodeksi",
         title_official="Ўзбекистон Республикасининг Маъмурий жавобгарлик тўғрисидаги кодекси", number="TODO_LAWYER", date="1994-09-22",
         url="https://lex.uz/docs/97664",
         plain_uz="Jarimalar va boshqa ma'muriy jazolar, ularni qo'llash va ustidan shikoyat qilish tartibi (yo'l harakati jarimalari ham shu yerda).",
         statuses=[], situations=["driver"]),
    dict(id="family_code", title_uz="O'zbekiston Respublikasining Oila kodeksi", title_official="Ўзбекистон Республикасининг Оила кодекси",
         number="TODO_LAWYER", date="1998-04-30", url="https://lex.uz/docs/104720",
         plain_uz="Nikoh, ajrashish, ota-ona va bolalarning huquq va majburiyatlari, aliment.",
         statuses=[], situations=["parent"]),
    dict(id="pension_law", title_uz="Fuqarolarning davlat pensiya ta'minoti to'g'risida", title_official="Фуқароларнинг давлат пенсия таъминоти тўғрисида",
         number="938-XII", date="1993-09-03", url="https://lex.uz/docs/112314",
         plain_uz="Pensiya turlari, pensiya tayinlash va unga murojaat qilish tartibi.",
         statuses=[], situations=["pensioner"]),
    dict(id="education_law", title_uz="Ta'lim to'g'risida", title_official="Таълим тўғрисида", number="O'RQ-637", date="2020-09-23",
         url="https://lex.uz/docs/5013007",
         plain_uz="Ta'lim tizimi, ta'lim oluvchilarning huquq va majburiyatlari.",
         statuses=[], situations=["student"]),
    dict(id="personal_data_law", title_uz="Shaxsga doir ma'lumotlar to'g'risida", title_official="Шахсга доир маълумотлар тўғрисида",
         number="O'RQ-547", date="2019-07-02", url="https://lex.uz/docs/4396419",
         plain_uz="Shaxsiy ma'lumotlaringizni kim, qanday asosda va roziligingiz bilan qayta ishlashi mumkinligi.",
         statuses=["uz_citizen", "foreign", "stateless", "unknown"], situations=["civil_servant"]),
    dict(id="tax_code", title_uz="O'zbekiston Respublikasining Soliq kodeksi", title_official="Ўзбекистон Республикасининг Солиқ кодекси",
         number="TODO_LAWYER", date="2019-12-30", url="https://lex.uz/docs/4674902",
         plain_uz="Soliqlar va yig'imlar, ularni to'lash tartibi (yakka tadbirkorlar uchun ham).",
         statuses=[], situations=["entrepreneur"]),
]


def item(id, kind, title, plain, law, article, excerpt):
    return dict(id=id, kind=kind, title_uz=title, plain_uz=plain, law_id=law, article=article, excerpt=excerpt)


STATUSES = {
    "uz_citizen": dict(
        title_uz="O'zbekiston fuqarosi", icon="🏠",
        intro_uz="Konstitutsiyadagi huquq va erkinliklar to'liq hajmda sizga tegishli. Quyida eng ko'p kerak bo'ladiganlari.",
        answer_note_uz=None,
        items=[
            item("c_appeal", "right", "Davlat organlariga murojaat qilish", "Ariza, taklif va shikoyat bilan davlat organlariga, mansabdor shaxslarga murojaat qilishingiz mumkin. Ular qonunda belgilangan tartib va muddatda ko'rib chiqilishi shart.", "constitution", "40-modda", "Ҳар ким ... давлат органларига ... аризалар, таклифлар ва шикоятлар билан мурожаат қилиш ҳуқуқига эга."),
            item("c_labor", "right", "Munosib mehnat va adolatli ish haqi", "Kasbni erkin tanlash, xavfsiz sharoitda ishlash va eng kam miqdordan kam bo'lmagan adolatli haq olish huquqi.", "constitution", "42-modda", "Ҳар ким муносиб меҳнат қилиш, касб ва фаолият турини эркин танлаш ... ҳуқуқига эга."),
            item("c_social", "right", "Ijtimoiy ta'minot", "Qariganda, mehnat qobiliyatini yo'qotganda, ishsizlikda, boquvchisini yo'qotganda ijtimoiy ta'minot huquqi.", "constitution", "46-modda", "Ҳар ким қариганда, меҳнат қобилиятини йўқотганда, ишсизликда ... ижтимоий таъминот ҳуқуқига эга."),
            item("c_edu", "right", "Ta'lim olish", "Har kim ta'lim olish huquqiga ega.", "constitution", "50-modda", "Ҳар ким таълим олиш ҳуқуқига эга."),
            item("c_court", "right", "Huquqlarni sud orqali himoya qilish", "Davlat organlari va mansabdor shaxslarning noqonuniy qarori yoki harakati ustidan sudga shikoyat qilishingiz mumkin.", "constitution", "55-modda", "Ҳар кимга ўз ҳуқуқ ва эркинликларини суд орқали ҳимоя қилиш ... ҳуқуқи кафолатланади."),
            item("c_d_law", "duty", "Konstitutsiya va qonunlarga rioya qilish", "Qonunlarga rioya qilish, boshqalarning huquqi, sha'ni va qadr-qimmatini hurmat qilish.", "constitution", "60-modda", "Фуқаролар Конституция ва қонунларга риоя этишга ... мажбурдирлар."),
            item("c_d_tax", "duty", "Soliq va yig'imlarni to'lash", "Qonun bilan belgilangan soliqlar va yig'imlarni to'lash shart.", "constitution", "63-modda", "Фуқаролар қонун билан белгиланган солиқлар ва йиғимларни тўлаши шарт."),
            item("c_d_defense", "duty", "Vatanni himoya qilish", "Qonunda belgilangan tartibda harbiy yoki muqobil xizmatni o'tash.", "constitution", "64-modda", "Ўзбекистон Республикасини ҳимоя қилиш Ўзбекистон Республикаси ҳар бир фуқаросининг бурчидир."),
        ]),
    "foreign": dict(
        title_uz="Chet el fuqarosi (vaqtincha yoki doimiy yashovchi)", icon="🌍",
        intro_uz="Huquqlaringiz Konstitutsiya, O'RQ-692 qonuni va xalqaro shartnomalar bilan belgilanadi. Ba'zi huquqlar O'zbekistonda DOIMIY yashashingizga bog'liq.",
        answer_note_uz="ℹ️ Siz chet el fuqarosisiz: bu masalada qoida siz uchun boshqacha bo'lishi mumkin. Masalan, pensiya fuqarolar bilan teng huquqda faqat O'zbekistonda doimiy yashovchilarga beriladi (O'RQ-692, 16-modda). Ariza berishdan oldin tegishli organdan tekshiring.",
        items=[
            item("f_const", "right", "Huquq va erkinliklaringiz kafolatlangan", "Huquq va erkinliklaringiz xalqaro huquq normalariga muvofiq ta'minlanadi.", "constitution", "24-modda", "Ўзбекистон Республикаси ҳудудидаги чет эл фуқароларининг ва фуқаролиги бўлмаган шахсларнинг ҳуқуқ ва эркинликлари халқаро ҳуқуқ нормаларига мувофиқ таъминланади."),
            item("f_labor", "right", "Mehnat huquqlari", "Ishlayotgan bo'lsangiz, mehnat qonunchiligidagi huquqlar sizga ham tegishli. Ba'zi lavozimlar faqat O'zbekiston fuqarolari uchun.", "foreign_status_law", "15-modda", "... меҳнат тўғрисидаги қонунчилигига мувофиқ ҳуқуқлардан фойдаланади ҳамда уларнинг зиммасида мажбуриятлар бўлади."),
            item("f_pension", "right", "Pensiya (doimiy yashovchilar uchun)", "O'zbekistonda doimiy yashasangiz — fuqarolar bilan teng huquqda pensiya olishingiz mumkin. Vaqtincha yashovchilar uchun bu qoida yozilmagan — tekshiring.", "foreign_status_law", "16-modda", "... доимий яшайдиган чет эл фуқаролари ва фуқаролиги бўлмаган шахслар ... фуқаролари билан тенг равишда пенсия олиш ҳуқуқига эга."),
            item("f_health", "right", "Sog'liqni saqlash", "Boshqa davlatda doimiy yashab, O'zbekistonda vaqtincha bo'lsangiz — tibbiy yordam xalqaro shartnomalarga muvofiq kafolatlanadi.", "foreign_status_law", "17-modda", "... соғлиқни сақлашга бўлган ҳуқуқи Ўзбекистон Республикасининг халқаро шартномаларига мувофиқ кафолатланади."),
            item("f_edu", "right", "Ta'lim olish", "Xalqaro shartnomalar va qonunchilikka muvofiq O'zbekistonda o'qishingiz mumkin.", "foreign_status_law", "18-modda", "... Ўзбекистон Республикасида таълим олишга ҳақлидир."),
            item("f_appeal", "right", "Davlat organlariga murojaat", "Ariza, taklif va shikoyat bilan murojaat qilishingiz mumkin — «Murojaatlar to'g'risida»gi qonunda belgilangan tartibda.", "foreign_status_law", "22-modda", "Чет эл фуқаролари ва фуқаролиги бўлмаган шахслар ... аризалар, таклифлар ва шикоятлар билан мурожаат қилиш ҳуқуқига эга."),
            item("f_idcard", "info", "ID-karta (doimiy yashovchilar)", "O'zbekistonda doimiy yashovchi chet el fuqarolariga identifikatsiyalovchi ID-karta beriladi.", "foreign_status_law", "9-modda", "Идентификацияловчи карта: Ўзбекистон Республикаси ҳудудида доимий яшайдиган чет эл фуқароларига ..."),
            item("f_d_law", "duty", "Qonunlarga rioya qilish", "Konstitutsiya va qonunlarga rioya qilish, boshqalarning huquq va qadr-qimmatini hurmat qilish.", "foreign_status_law", "25-modda", "... Ўзбекистон Республикасининг Конституциясига, қонунларига ва бошқа норматив-ҳуқуқий ҳужжатларига риоя этиши"),
            item("f_d_tax", "duty", "Soliq to'lash", "Soliq kodeksida belgilangan soliq va yig'imlarni to'laysiz; qonundagi soliq imtiyozlaridan foydalanishingiz mumkin.", "foreign_status_law", "27-modda", "... Солиқ кодексида белгиланган солиқларни ва унда назарда тутилган йиғимларни ... тўлайди."),
        ]),
    "stateless": dict(
        title_uz="Fuqaroligi bo'lmagan shaxs", icon="🕊️",
        intro_uz="Hech bir davlat fuqaroligini tasdiqlovchi dalilingiz bo'lmasa, siz fuqaroligi bo'lmagan shaxssiz. O'zbekistonda DOIMIY yashasangiz, ko'p huquqlarda fuqarolar bilan tengsiz.",
        answer_note_uz="ℹ️ Siz fuqaroligi bo'lmagan shaxssiz: bu masalada qoida siz uchun boshqacha bo'lishi mumkin. Doimiy yashasangiz pensiya, sog'liqni saqlash va ta'limda fuqarolar bilan tengsiz (O'RQ-692, 16–18-moddalar). Ariza berishdan oldin tegishli organdan tekshiring.",
        items=[
            item("s_def", "info", "Kim fuqaroligi bo'lmagan shaxs", "O'zbekiston fuqarosi bo'lmagan va boshqa davlat fuqaroligiga mansubligiga dalili yo'q shaxs.", "foreign_status_law", "3-modda", "фуқаролиги бўлмаган шахс — Ўзбекистон Республикасининг фуқароси бўлмаган ва ўзининг чет давлат фуқаролигига мансублигига доир далилга эга бўлмаган шахс"),
            item("s_const", "right", "Huquq va erkinliklaringiz kafolatlangan", "Huquq va erkinliklaringiz xalqaro huquq normalariga muvofiq ta'minlanadi.", "constitution", "24-modda", "... фуқаролиги бўлмаган шахсларнинг ҳуқуқ ва эркинликлари халқаро ҳуқуқ нормаларига мувофиқ таъминланади."),
            item("s_pension", "right", "Pensiya (doimiy yashovchilar)", "Doimiy yashasangiz — fuqarolar bilan teng huquqda pensiya.", "foreign_status_law", "16-modda", "... доимий яшайдиган ... фуқаролиги бўлмаган шахслар ... фуқаролари билан тенг равишда пенсия олиш ҳуқуқига эга."),
            item("s_health", "right", "Sog'liqni saqlash (doimiy yashovchilar)", "Doimiy yashasangiz — sog'liqni saqlashda fuqarolar bilan tengsiz.", "foreign_status_law", "17-modda", "Ўзбекистон Республикасида доимий яшайдиган фуқаролиги бўлмаган шахслар соғлиқни сақлашга бўлган ҳуқуқдан ... фуқаролари билан тенг равишда фойдаланади."),
            item("s_edu", "right", "Ta'lim (doimiy yashovchilar)", "Doimiy yashasangiz — ta'lim olishda fuqarolar bilan teng huquqqa egasiz.", "foreign_status_law", "18-modda", "Ўзбекистон Республикасида доимий яшайдиган фуқаролиги бўлмаган шахслар таълим олишда ... фуқаролари билан тенг ҳуқуқларга эга."),
            item("s_appeal", "right", "Davlat organlariga murojaat", "Ariza, taklif va shikoyat bilan murojaat qilishingiz mumkin.", "foreign_status_law", "22-modda", "... фуқаролиги бўлмаган шахслар ... аризалар, таклифлар ва шикоятлар билан мурожаат қилиш ҳуқуқига эга."),
            item("s_d_law", "duty", "Qonunlarga rioya qilish", "Konstitutsiya va qonunlarga rioya qilish.", "foreign_status_law", "25-modda", "... Конституциясига, қонунларига ва бошқа норматив-ҳуқуқий ҳужжатларига риоя этиши"),
            item("s_d_tax", "duty", "Soliq to'lash", "Soliq kodeksida belgilangan soliq va yig'imlarni to'laysiz.", "foreign_status_law", "27-modda", "... Солиқ кодексида белгиланган солиқларни ... тўлайди."),
        ]),
    "unknown": dict(
        title_uz="Bilmayman", icon="❔",
        intro_uz="Maqomingizni bilmasangiz ham, quyidagi huquqlar «har kim»ga tegishli. Maqomni aniqlash uchun ta'riflarni o'qing yoki migratsiya organiga murojaat qiling.",
        answer_note_uz="ℹ️ Maqomingiz (fuqarolik) aniq emas: ba'zi imtiyoz va nafaqalar faqat O'zbekiston fuqarolari yoki doimiy yashovchilar uchun bo'lishi mumkin. Ariza berishdan oldin tekshiring.",
        items=[
            item("u_def", "info", "Maqomni aniqlash: ta'riflar", "Chet el fuqarosi — boshqa davlat fuqaroligiga dalili bor shaxs; fuqaroligi bo'lmagan shaxs — hech bir davlat fuqaroligiga dalili yo'q shaxs.", "foreign_status_law", "3-modda", "чет эл фуқароси — Ўзбекистон Республикасининг фуқаролигига эга бўлмаган, бошқа давлат фуқаролигига ... мансублигига доир далилга эга бўлган шахс"),
            item("u_appeal", "right", "Murojaat qilish (har kim)", "Ariza, taklif va shikoyat bilan davlat organlariga murojaat qilish huquqi har kimga tegishli.", "constitution", "40-modda", "Ҳар ким ... аризалар, таклифлар ва шикоятлар билан мурожаат қилиш ҳуқуқига эга."),
            item("u_court", "right", "Sud orqali himoya (har kim)", "Noqonuniy qaror yoki harakat ustidan sudga shikoyat qilish huquqi har kimga kafolatlangan.", "constitution", "55-modda", "Ҳар кимга ўз ҳуқуқ ва эркинликларини суд орқали ҳимоя қилиш ... ҳуқуқи кафолатланади."),
            item("u_social", "right", "Ijtimoiy ta'minot (har kim)", "Qariganda, ishsizlikda, boquvchisini yo'qotganda ijtimoiy ta'minot huquqi — qonunda belgilangan tartibda.", "constitution", "46-modda", "Ҳар ким қариганда ... ижтимоий таъминот ҳуқуқига эга."),
        ]),
}

SITUATIONS = {
    "student": dict(title_uz="Talaba", icon="🎓", items=[
        item("st_edu", "right", "Ta'lim olish huquqi", "Har kim ta'lim olish huquqiga ega; davlat uzluksiz ta'lim tizimini ta'minlaydi.", "constitution", "50-modda", "Ҳар ким таълим олиш ҳуқуқига эга."),
        item("st_law", "info", "Ta'lim oluvchining huquq va majburiyatlari", "Talabaning huquq va majburiyatlari «Ta'lim to'g'risida»gi qonunda.", "education_law", "", ""),
        item("st_labor", "right", "O'qish bilan birga ishlash", "Ishlasangiz — mehnat huquqlaringiz Mehnat kodeksi bilan himoyalanadi.", "labor_code", "", "")]),
    "parent": dict(title_uz="Ota-ona", icon="👨‍👩‍👧", items=[
        item("pa_duty", "duty", "Bolani voyaga yetgunicha boqish", "Ota-onalar farzandlarini voyaga yetgunicha boqishi, tarbiyasi va ta'limi haqida g'amxo'rlik qilishi shart.", "constitution", "77-modda", "Ота-оналар ва уларнинг ўрнини босувчи шахслар ўз фарзандларини вояга етгунига қадар боқиши ..."),
        item("pa_equal", "right", "Bolalar qonun oldida teng", "Farzandlar ota-onasining nasl-nasabi va fuqarolik holatidan qat'i nazar teng.", "constitution", "78-modda", "Фарзандлар ота-онасининг насл-насаби ва фуқаролик ҳолатидан қатъи назар, қонун олдида тенгдирлар."),
        item("pa_family", "info", "Aliment va oilaviy huquqlar", "Aliment, ajrashish va bolalar bilan bog'liq qoidalar Oila kodeksida.", "family_code", "", "")]),
    "pensioner": dict(title_uz="Pensioner", icon="👴", items=[
        item("pe_social", "right", "Qariganda ijtimoiy ta'minot", "Qariganda ijtimoiy ta'minot huquqi Konstitutsiyada kafolatlangan.", "constitution", "46-modda", "Ҳар ким қариганда ... ижтимоий таъминот ҳуқуқига эга."),
        item("pe_apply", "right", "Pensiya so'rab istalgan vaqtda murojaat", "Pensiya huquqi paydo bo'lgandan keyin istalgan vaqtda pensiya tayinlashni so'rab murojaat qilish mumkin. Yoshga doir pensiyalar murojaatsiz (proaktiv) ham tayinlanishi mumkin.", "pension_law", "3-modda", "Фуқаролар пенсия олиш ҳуқуқи пайдо бўлганидан сўнг исталган пайтда пенсия тайинлашни сўраб мурожаат этишлари мумкин.")]),
    "driver": dict(title_uz="Haydovchi", icon="🚗", items=[
        item("dr_admin", "info", "Jarimalar qayerda yozilgan", "Yo'l harakati qoidabuzarligi uchun jarimalar va ularga shikoyat qilish tartibi Ma'muriy javobgarlik to'g'risidagi kodeksda.", "admin_code", "", ""),
        item("dr_court", "right", "Jarima ustidan shikoyat", "Noqonuniy deb hisoblagan qaror ustidan sudga shikoyat qilishingiz mumkin.", "constitution", "55-modda", "... қонунга хилоф қарорлари, ҳаракатлари ва ҳаракатсизлиги устидан судга шикоят қилиш ҳуқуқи кафолатланади.")]),
    "entrepreneur": dict(title_uz="Tadbirkor", icon="💼", items=[
        item("en_tax", "duty", "Soliq to'lash", "Qonun bilan belgilangan soliq va yig'imlarni to'lash shart.", "constitution", "63-modda", "Фуқаролар қонун билан белгиланган солиқлар ва йиғимларни тўлаши шарт."),
        item("en_code", "info", "Soliq kodeksi", "Yakka tadbirkor soliqlari va hisobot tartibi Soliq kodeksida.", "tax_code", "", ""),
        item("en_prop", "right", "Mulkdor bo'lish", "Har bir shaxs mulkdor bo'lishga haqli.", "constitution", "41-modda", "Ҳар бир шахс мулкдор бўлишга ҳақли.")]),
    "worker": dict(title_uz="Yollanib ishlovchi", icon="🛠️", items=[
        item("wo_labor", "right", "Adolatli ish haqi", "Eng kam miqdordan kam bo'lmagan adolatli haq olish huquqi.", "constitution", "42-modda", "... меҳнатга ҳақ тўлашнинг белгиланган энг кам миқдоридан кам бўлмаган тарзда адолатли ҳақ олиш ..."),
        item("wo_code", "info", "Mehnat kodeksi", "Ish haqi, ta'til, ishdan bo'shatish qoidalari.", "labor_code", "", "")]),
    "civil_servant": dict(title_uz="Davlat xizmatchisi", icon="🏛️", items=[
        item("cs_appeal", "duty", "Murojaatlarni muddatida ko'rib chiqish", "Ariza, taklif va shikoyatlar qonunda belgilangan tartibda va muddatlarda ko'rib chiqilishi shart.", "constitution", "40-modda", "Аризалар, таклифлар ва шикоятлар қонунда белгиланган тартибда ва муддатларда кўриб чиқилиши шарт."),
        item("cs_law", "info", "Murojaatlar bilan ishlash", "Murojaatlarni qabul qilish va ko'rib chiqish tartibi.", "appeals_law", "", ""),
        item("cs_pd", "duty", "Shaxsiy ma'lumotlarni himoya qilish", "Fuqarolarning shaxsiy ma'lumotlarini faqat qonun asosida qayta ishlash.", "personal_data_law", "", "")]),
}


def main():
    (ROOT / "laws").mkdir(exist_ok=True)
    (ROOT / "rights").mkdir(exist_ok=True)
    for L in LAWS:
        L.update(retrieved_at=R, source_type=LEX, source_verified=True)
        (ROOT / "laws" / f"{L['id']}.json").write_text(json.dumps(L, ensure_ascii=False, indent=2), encoding="utf-8")
    law_ids = {L["id"] for L in LAWS}
    for kind, group in (("status", STATUSES), ("situation", SITUATIONS)):
        for sid, s in group.items():
            for it in s["items"]:
                assert it["law_id"] in law_ids, it
            (ROOT / "rights" / f"{kind}_{sid}.json").write_text(
                json.dumps({"id": sid, "type": kind, **s}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("ok", len(LAWS), len(STATUSES), len(SITUATIONS))


if __name__ == "__main__":
    main()
