"""2026-11-21: «manba topilmadi» ro'yxatini yopish — kartalarni lex.uz'da ochib tekshirilgan amaldagi hujjatlarga ulash.

Faqat manbada aniq ko'rilgan qoidalar yozildi. Summa / miqdor ko'rinmagan joylar TODO_LAWYER bo'lib qoladi.
`source_checked` — manba tekshirildi (UI: «Manba tekshirildi: lex.uz, 21.11.2026»).
`verified` / `verified_by` / `verified_at` — huquqshunos tasdig'i (alohida, qo'lda to'ldiriladi).

Tekshirilgan hujjatlar:
- VM 29.01.2026 dagi 35-son qarori (kuchga kirgan 02.02.2026; oxirgi tahrir 02.10.2026) — https://lex.uz/docs/-8027513
  1-ilova 33-band (rad etish asoslari), 3-ilova (bolalar nafaqasi nizomi: 2, 6, 11, 12, 13-bandlar),
  4-ilova (apellyatsiya kengashlari: 7, 33-bandlar va 2-ilova sxemasi — 30 kun).
  ESLATMA: so'ralgan VM 15.02.2013 dagi 44-son qarori (https://lex.uz/docs/-2134701) lex.uz'da «Hujjat kuchini yo'qotgan 01.04.2021»;
  uning o'rnini bosgan VM 654 (21.10.2021) nizomi ham 02.02.2026 dan VM 35 bilan kuchini yo'qotgan.
- 258-II «Sud hujjatlari va boshqa organlar hujjatlarini ijro etish to'g'risida» (29.08.2001) — https://lex.uz/docs/-26477
  42¹, 43¹ (O'RQ-1134, 20.04.2026 tahririda), 43² (O'RQ-1134 bilan to'ldirilgan), 70, 71-moddalar.
- 221-I «Iste'molchilarning huquqlarini himoya qilish to'g'risida» (26.04.1996) — https://lex.uz/docs/-4704 — 13, 18, 29-moddalar.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "knowledge"
R = "2026-11-21"
VM35 = "https://lex.uz/docs/-8027513"
ENF = "https://lex.uz/docs/-26477"
CONS = "https://lex.uz/docs/-4704"
VM35_DOC = "Vazirlar Mahkamasining 29.01.2026 dagi 35-son qarori"


def src(ref_id, doc, article, url, date, note=None):
    d = {"ref_id": ref_id, "doc": doc, "article": article, "lex_url": url, "doc_date": date,
         "retrieved_at": R, "source_type": "lex.uz", "source_verified": True}
    if note:
        d["note"] = note
    return d


def checked(d: dict) -> dict:
    d["source_checked"] = True
    d["source_checked_at"] = R
    d["source_checked_by"] = "Huquqim jamoasi (lex.uz'da matn bilan solishtirildi)"
    d["verified"] = bool(d.get("verified_by"))  # huquqshunos tasdig'i — faqat verified_by to'ldirilganda
    d.setdefault("verified_by", None)
    d.setdefault("verified_at", None)
    d["_note"] = ("Manba lex.uz'da tekshirildi (21.11.2026). Huquqshunos tasdig'i: verified_by / verified_at maydonlarini to'ldiring. "
                  "TODO_LAWYER — manbada aniq ko'rinmagan summa/miqdor.")
    return d


VM35_BASIS = [
    src("REF_CHILD_ALLOWANCE_1", f"{VM35_DOC}, 3-ilova — Ijtimoiy reyestrga kiritilgan oilalarga bolalar nafaqasi va moddiy yordamni tayinlash va to'lash tartibi to'g'risidagi Nizom",
        "2, 6, 11, 12, 13-bandlar", VM35, "2026-01-29"),
    src("REF_SOCIAL_REGISTRY_1", f"{VM35_DOC}, 1-ilova — Ijtimoiy reyestrni yuritish tartibi to'g'risidagi Nizom", "33-band", VM35, "2026-01-29"),
    src("REF_APPEAL_COUNCIL_1", f"{VM35_DOC}, 4-ilova — Tuman (shahar) hokimliklari huzuridagi apellyatsiya kengashlari to'g'risidagi Nizom",
        "7, 33-bandlar, 2-ilova (sxema)", VM35, "2026-01-29"),
]


def update(path: Path, fn) -> None:
    d = json.loads(path.read_text(encoding="utf-8"))
    fn(d)
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("yangilandi:", path.relative_to(ROOT))


def child_card(d):
    d["plain_explanation_uz"] = (
        "Bolalar nafaqasi Ijtimoiy reyestrga kiritilgan oilalarga tayinlanadi. Shart: oilaning eng kichik yoki yagona bolasi "
        "18 yoshga to'lmagan bo'lishi kerak. Rad etish uchun asos topilmasa, nafaqa ariza ko'rib chiqilgan oydan keyingi oydan "
        "avtomatik tayinlanadi. Rad etilsa — sababini bilish va shikoyat qilish huquqingiz bor.")
    d["common_reasons"] = [
        "Oila a'zosiga to'g'ri keladigan oylik o'rtacha daromad minimal iste'mol xarajatlaridan yuqori",
        "Oilada bittadan ortiq ko'chmas mulk va yer uchastkasi yoki noturar joy bor",
        "Oila a'zolari nomida yoki foydalanuvida 12 yildan yangi soz yengil avtomobil (nogironligi bo'lgan a'zo bo'lsa — 7 yil) yoki 15 yildan yangi yuk mashinasi, texnika bor",
        "Bank depozitida yoki qimmatli qog'ozlarda eng kam ish haqining 5 baravari va undan ko'p mablag' bor",
        "Oila Reyestrga kiritilmagan yoki «kambag'allik chegarasidagi oila» toifasiga kiritilganiga 6 oy to'lgan",
    ]
    d["steps"] = [
        "Rad etish sababini aniqlang (SMS, my.gov.uz yoki «Inson» ijtimoiy xizmatlar markazi)",
        "Sabab xato ma'lumotga asoslangan bo'lsa (masalan, sizga tegishli bo'lmagan mashina) — dalil to'plang",
        "Ma'muriy hujjat kuchga kirgan kundan 30 kun ichida tuman (shahar) hokimligi huzuridagi apellyatsiya kengashiga shikoyat qiling",
        "Kengashga shikoyat ixtiyoriy: yuqori organga yoki to'g'ridan-to'g'ri sudga ham murojaat qilishingiz mumkin",
    ]
    d["documents"] = [
        "Shaxsni tasdiqlovchi hujjat (chet el fuqarosi yoki fuqaroligi bo'lmagan shaxs — O'zbekistonda yashash guvohnomasi)",
        "Ariza — davlat xizmatlari markazida yoki ijtimoiy xodim siz bilan birga to'ldiradi, yoki my.gov.uz / «Ijtimoiy karta» ilovasida o'zingiz",
        "Qo'shimcha hujjatlar ro'yxati: TODO_LAWYER",
    ]
    d["deadlines"] = [
        "Bolalar nafaqasi uchun murojaat — oyda bir marta",
        "Nafaqa — ariza ko'rib chiqilgan oydan keyingi oydan; eng kichik bola 18 yoshga to'lgan oyning oxirigacha to'lanadi",
        "Apellyatsiya kengashiga shikoyat — ma'muriy hujjat kuchga kirgan kundan 30 kun ichida; 15 kun ichida ko'rib chiqiladi; to'lov olinmaydi",
    ]
    d["where_to_go"] = [
        {"name": "Yagona interaktiv davlat xizmatlari portali (my.gov.uz)", "url": "https://my.gov.uz"},
        {"name": "Tuman (shahar) «Inson» ijtimoiy xizmatlar markazi yoki davlat xizmatlari markazi", "url": "https://my.gov.uz"},
        {"name": "Tuman (shahar) hokimligi huzuridagi apellyatsiya kengashi", "url": "https://my.gov.uz"},
    ]
    d["legal_basis"] = [dict(b) for b in VM35_BASIS]
    d["status_notes"] = {"foreign": "Ariza beruvchi O'zbekistonda yashash guvohnomasiga ega chet el fuqarosi yoki fuqaroligi bo'lmagan shaxs ham bo'lishi mumkin (VM 35, 3-ilova, 2-band)."}
    checked(d)


def child_benefit(d):
    d["title_uz"] = "Ijtimoiy reyestrdagi oilalarga bolalar nafaqasi"
    d["summary_uz"] = ("Ijtimoiy reyestrga kiritilgan, eng kichik yoki yagona bolasi 18 yoshga to'lmagan oilaga bolalar nafaqasi "
                       "tayinlanadi. Rad etish asosi bo'lmasa, ariza ko'rib chiqilgan oydan keyingi oydan avtomatik to'lanadi.")
    d["amount"] = "TODO_LAWYER: nafaqa miqdori (VM 35, 3-ilovaga 1-ilova — sxema)"
    d["rule"] = {"all": [
        {"fact": "minor_children", "op": ">=", "value": 1,
         "label_uz": "Eng kichik yoki yagona bola 18 yoshga to'lmagan", "label_ru": "Младший или единственный ребёнок не достиг 18 лет",
         "appeal_uz": "Oilamda 18 yoshga to'lmagan bola bor"},
        {"fact": "low_income_registry", "op": "==", "value": True,
         "label_uz": "Oila Ijtimoiy reyestrga kiritilgan", "label_ru": "Семья включена в Социальный реестр",
         "appeal_uz": "Oilam Ijtimoiy reyestrga kiritilgan"},
        {"todo": "Daromad va mol-mulk ma'lumoti demo profilda yo'q — vakolatli organ idoralararo tekshiradi",
         "label_uz": "Rad etish asoslari yo'qligi: daromad minimal iste'mol xarajatlaridan yuqori emas, ortiqcha ko'chmas mulk, yangi avtomobil, katta depozit yo'q",
         "label_ru": "Нет оснований для отказа (доход, имущество, авто, депозиты)"},
    ]}
    d["documents"] = [
        "Shaxsni tasdiqlovchi hujjat (chet el fuqarosi yoki fuqaroligi bo'lmagan shaxs — yashash guvohnomasi)",
        "Ariza (davlat xizmatlari markazi, «Inson» markazi, ijtimoiy xodim, my.gov.uz yoki «Ijtimoiy karta» ilovasi orqali)",
        "Qo'shimcha hujjatlar ro'yxati: TODO_LAWYER",
    ]
    d["where_to_go"] = [
        {"name": "Yagona interaktiv davlat xizmatlari portali (my.gov.uz)", "url": "https://my.gov.uz"},
        {"name": "Tuman (shahar) «Inson» ijtimoiy xizmatlar markazi", "url": "https://my.gov.uz"},
    ]
    d["legal_basis"] = [dict(b) for b in VM35_BASIS[:2]]
    checked(d)


ENF_TRAVEL = src("REF_ENFORCEMENT_TRAVEL", "«Sud hujjatlari va boshqa organlar hujjatlarini ijro etish to'g'risida»gi Qonun (258-II)",
                 "42¹-modda", ENF, "2001-08-29")
ENF_SIMPLE = src("REF_ENFORCEMENT_SIMPLE", "«Sud hujjatlari va boshqa organlar hujjatlarini ijro etish to'g'risida»gi Qonun (258-II)",
                 "43¹, 43²-moddalar (O'RQ-1134, 20.04.2026 tahririda)", ENF, "2001-08-29")
ENF_ALIMONY = src("REF_ENFORCEMENT_1", "«Sud hujjatlari va boshqa organlar hujjatlarini ijro etish to'g'risida»gi Qonun (258-II)",
                  "70-modda", ENF, "2001-08-29")


def alimony(d):
    d["plain_explanation_uz"] = (
        "Ota-ona voyaga yetmagan bolasini ta'minlashi shart. Aliment ixtiyoriy to'lanmasa, sud orqali undiriladi. "
        "Aliment va aliment qarzini undirish tartibi Oila kodeksida belgilangan; sud qarori Majburiy ijro byurosi orqali ijro etiladi. "
        "Qarzdor sud hujjatini uzrsiz bajarmasa, davlat ijrochisi uning chet elga chiqishini vaqtincha cheklashi mumkin.")
    d["steps"] = [
        "Kelishuv bo'lmasa — sudga aliment undirish haqida ariza bering",
        "Sud qarori yoki ijro hujjatini Majburiy ijro byurosiga topshiring",
        "To'lanmasa — davlat ijrochisidan qarzdorning chet elga chiqishini vaqtincha cheklashni so'rang (undiruvchi arizasi bilan)",
    ]
    d["deadlines"] = ["Aliment miqdori va undirish muddatlari: TODO_LAWYER (Oila kodeksi)"]
    d["legal_basis"] = [b for b in d.get("legal_basis", []) if b.get("ref_id") == "REF_ALIMONY_1"] + [ENF_ALIMONY, ENF_TRAVEL]
    checked(d)


def mib(d):
    d["plain_explanation_uz"] = (
        "Sud hujjati talabi belgilangan muddatda uzrsiz bajarilmasa, davlat ijrochisi qarzdorning O'zbekistondan chiqishini vaqtincha "
        "cheklashi mumkin; qaror katta davlat ijrochisi tomonidan tasdiqlanadi va ustidan shikoyat qilish mumkin. Qarz to'langach, "
        "cheklov olib tashlanganligi haqida keyingi kundan kechiktirmay xabar beriladi. Ma'muriy jarima, soliq, kommunal qarz va "
        "BHMning 5 baravarigacha bo'lgan summalar soddalashtirilgan tartibda undiriladi — bunda chet elga chiqishni cheklash qo'llanilmaydi.")
    d["common_reasons"] = [
        "Sud qarori bo'yicha qarz (kredit, aliment va boshqalar) muddatida to'lanmagan",
        "Qarz to'langan, lekin ijro ishi hali tamomlanmagan",
        "Ijro ishi sizga tegishli emas yoki xato ochilgan",
    ]
    d["steps"] = [
        "Qarzingiz va ijro ishi raqamini my.gov.uz orqali tekshiring",
        "Qarz qaysi hujjat asosida ekanini aniqlang: sud hujjatimi yoki soddalashtirilgan tartibdagi qarz (jarima, soliq, kommunal)mi",
        "To'lagan bo'lsangiz — to'lov hujjati bilan ijro ishini tamomlashni so'rang",
        "Cheklov noto'g'ri deb hisoblasangiz — davlat ijrochisining qarori ustidan shikoyat qiling",
    ]
    d["deadlines"] = [
        "Cheklov olib tashlanganligi haqida xabar — qarz to'langan (ijro ishi tamomlangan) kundan keyingi kundan kechiktirmay",
        "Soddalashtirilgan tartibda ixtiyoriy to'lash — xabarnoma olingan kundan 5 kun",
        "Shikoyat berish muddati: TODO_LAWYER",
    ]
    d["legal_basis"] = [ENF_TRAVEL, ENF_SIMPLE]
    checked(d)


def consumer(d):
    d["plain_explanation_uz"] = (
        "Nuqsonli tovar sotilgan bo'lsa (va bu oldindan aytilmagan bo'lsa), o'zingiz tanlab talab qilasiz: almashtirish, "
        "bepul tuzatish, narxni kamaytirish yoki shartnomani bekor qilib zararni qoplash. Nuqson kafolat muddatida, kafolat bo'lmasa — "
        "6 oy ichida aniqlangan bo'lishi kerak. Sifatli nooziq-ovqat tovarini 10 kun ichida almashtirish (bo'lmasa — pulni qaytarish) mumkin.")
    d["common_reasons"] = [
        "Nuqson kafolat muddati (kafolat bo'lmasa — 6 oy) o'tgandan keyin aniqlangan",
        "Sifatli tovar ishlatilgan, shikastlangan yoki qadog'isiz qaytarilmoqda",
        "Tovar shu sotuvchidan olinganini tasdiqlovchi asos (chek) yo'q",
        "Tovar almashtirilmaydigan tovarlar ro'yxatida (Hukumat qoidalari — TODO_LAWYER)",
    ]
    d["steps"] = [
        "Sotuvchiga yozma talabnoma bering: qaysi talabni tanlaganingizni yozing (nusxasini saqlang)",
        "Chek, kafolat taloni va nuqson suratlarini saqlang",
        "Rad etilsa — sudga da'vo bering: o'zingiz yashaydigan joy, javobgar joylashgan joy yoki zarar yetkazilgan joydagi sudga",
        "Iste'molchi huquqi buzilishi bo'yicha da'volarda davlat boji to'lanmaydi",
    ]
    d["deadlines"] = [
        "Nuqsonli tovar: kafolat yoki yaroqlilik muddati ichida; muddat belgilanmagan bo'lsa — 6 oy; ko'chmas mulk — 2 yil",
        "Sifatli nooziq-ovqat tovarini almashtirish — xarid kunidan 10 kun ichida",
        "Talabni ko'rib chiqish va pulni qaytarish muddati: TODO_LAWYER",
    ]
    d["legal_basis"] = [src("REF_CONSUMER_RIGHTS_1", "«Iste'molchilarning huquqlarini himoya qilish to'g'risida»gi Qonun (221-I)",
                            "13, 18, 29-moddalar", CONS, "1996-04-26")]
    checked(d)


def feed(d):
    for c in d.get("changes", []):
        if c.get("ref_id") == "REF_CHILD_ALLOWANCE_1":
            c["doc"] = f"{VM35_DOC}, 3-ilova (bolalar nafaqasi nizomi)"
            c["article"] = "6-band"
            c["lex_url"] = VM35


if __name__ == "__main__":
    update(ROOT / "cards" / "child_allowance_refused.json", child_card)
    update(ROOT / "benefits" / "benefit_child_allowance.json", child_benefit)
    update(ROOT / "cards" / "alimony.json", alimony)
    update(ROOT / "cards" / "mib_debt_travel_ban.json", mib)
    update(ROOT / "cards" / "consumer_refund.json", consumer)
    update(ROOT / "lex" / "changes_feed.json", feed)
