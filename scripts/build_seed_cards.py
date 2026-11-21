"""10 ta seed vaziyat kartasini /knowledge/cards ga yozadi.

MUHIM: huquqiy mazmun PLACEHOLDER. Modda raqami, summa, muddat — hech biri to'qilmagan,
ular o'rnida TODO_LAWYER turadi. Jamoa huquqshunosi to'ldirib, "verified": true qiladi.
Ishga tushirish:  python scripts/build_seed_cards.py   (mavjud fayllarni qayta yozmaydi, --force bilan yozadi)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.services.textutil import lat_to_cyr  # noqa: E402

T = "TODO_LAWYER"
LEX = "https://lex.uz/"  # TODO_LAWYER: aniq hujjat havolasi (lex.uz/docs/...)
MYGOV = {"name": "Yagona interaktiv davlat xizmatlari portali (my.gov.uz)", "url": "https://my.gov.uz"}
PM = {"name": "Prezidentning Virtual qabulxonasi (pm.gov.uz)", "url": "https://pm.gov.uz"}
LEXUZ = {"name": "Qonunchilik ma'lumotlari milliy bazasi (lex.uz)", "url": "https://lex.uz"}


def basis(ref_id: str, doc: str) -> dict:
    return {"ref_id": ref_id, "doc": doc, "article": T, "lex_url": LEX}


CARDS = [
    {
        "id": "child_allowance_refused",
        "category": "ijtimoiy_himoya",
        "title_uz": "Bola nafaqasi berilmadi",
        "title_ru": "Отказ в детском пособии",
        "triggers": ["bola nafaqasi", "bolalar nafaqasi", "nafaqa berilmadi", "nafaqa nega berilmadi",
                     "nafaqa rad etildi", "bolamga nafaqa", "18 yoshgacha nafaqa", "бола нафақаси",
                     "нафақа берилмади", "детское пособие", "пособие на ребенка", "отказали в пособии"],
        "plain_explanation_uz": "Bolalik nafaqasi oila daromadi va boshqa mezonlar tekshirilgandan keyin tayinlanadi. "
                                 "Rad etilgan bo'lsa, rad etish sababini yozma ravishda so'rashga va qaror ustidan shikoyat qilishga haqingiz bor.",
        "common_reasons": [f"Oila daromadi belgilangan mezondan oshgan ({T}: aniq mezon)",
                           "Arizadagi yoki reestrdagi ma'lumotlar mos kelmagan",
                           "Hujjatlar to'liq topshirilmagan",
                           f"Boshqa asoslar ({T})"],
        "steps": ["Rad etish sababini yozma ravishda so'rang",
                  "Ma'lumotlaringiz (oila tarkibi, daromad) to'g'ri kiritilganini tekshiring",
                  "Xato bo'lsa — tuzatib qayta ariza bering",
                  "Rozi bo'lmasangiz — yuqori organga yoki sudga shikoyat qiling"],
        "documents": ["Shaxsni tasdiqlovchi hujjat", "Bolaning tug'ilganlik haqida guvohnomasi",
                      f"Daromad haqida ma'lumot ({T}: talab qilinadimi)"],
        "deadlines": [f"Arizani ko'rib chiqish muddati: {T}", f"Shikoyat berish muddati: {T}"],
        "where_to_go": [MYGOV, {"name": "Tuman (shahar) \"Inson\" ijtimoiy xizmatlar markazi", "url": "https://my.gov.uz"}, PM],
        "legal_basis": [basis("REF_CHILD_ALLOWANCE_1", f"{T}: bolalik nafaqasini tayinlash tartibini belgilovchi hujjat")],
        "appeal_template_id": "appeal_social_benefit",
        "appeal_addressee": "Tuman (shahar) \"Inson\" ijtimoiy xizmatlar markazi rahbariga",
        "textbook_refs": ["social_law_ch2_s1"],
    },
    {
        "id": "alimony",
        "category": "oila",
        "title_uz": "Aliment: qanday undiriladi, qarzdor to'lamasa nima qilinadi",
        "title_ru": "Алименты: как взыскать и что делать, если должник не платит",
        "triggers": ["aliment", "alimentni undirish", "aliment to'lamayapti", "aliment qarzi", "bolaga aliment",
                     "sobiq erim aliment", "алимент", "алименты", "не платит алименты"],
        "plain_explanation_uz": "Ota-ona voyaga yetmagan bolasini ta'minlashi shart. Ixtiyoriy to'lanmasa, aliment sud orqali undiriladi, "
                                 "sud qarori esa majburiy ijro organi orqali ijro etiladi.",
        "common_reasons": ["Aliment bo'yicha sud qarori hali yo'q", "Qarzdorning daromadi yashirilgan",
                           "Ijro hujjati ijroga topshirilmagan"],
        "steps": ["Kelishuv bo'lmasa — sudga aliment undirish haqida ariza bering",
                  "Sud qarori yoki ijro hujjatini majburiy ijro organiga topshiring",
                  "To'lanmasa — ijro organidan qarzdorga nisbatan choralar ko'rishni so'rang"],
        "documents": ["Bolaning tug'ilganlik haqida guvohnomasi", "Nikoh yoki ajrim haqidagi hujjat (bo'lsa)",
                      "Sud qarori / ijro hujjati (bo'lsa)"],
        "deadlines": [f"Aliment miqdori va undirish muddatlari: {T}"],
        "where_to_go": [{"name": "Tuman (shahar) sudi (fuqarolik ishlari)", "url": "https://my.sud.uz"},
                        {"name": "Majburiy ijro byurosi hududiy bo'limi", "url": "https://my.gov.uz"}, MYGOV],
        "legal_basis": [basis("REF_ALIMONY_1", "O'zbekiston Respublikasi Oila kodeksi"),
                        basis("REF_ENFORCEMENT_1", "\"Sud hujjatlari va boshqa organlar hujjatlarini ijro etish to'g'risida\"gi Qonun")],
        "appeal_template_id": "appeal_enforcement",
        "appeal_addressee": "Majburiy ijro byurosi hududiy bo'limi boshlig'iga",
        "textbook_refs": ["family_law_ch3_s1"],
    },
    {
        "id": "mib_debt_travel_ban",
        "category": "ijro",
        "title_uz": "MIB qarzi va chet elga chiqish cheklovi",
        "title_ru": "Долг в МИБ и запрет на выезд",
        "triggers": ["mib qarz", "mib qarzim", "majburiy ijro", "chet elga chiqish taqiqlandi", "chiqish cheklovi",
                     "ijro varaqasi", "mib", "мажбурий ижро", "миб", "долг миб", "запрет на выезд"],
        "plain_explanation_uz": "Agar sizga nisbatan ijro ishi ochilgan bo'lsa, qarz to'liq to'lanmaguncha ijro organi cheklov choralarini qo'llashi mumkin. "
                                 "Qarz qaysi hujjat asosida ochilganini bilish va uni tekshirish huquqingiz bor.",
        "common_reasons": ["To'lanmagan jarima, kredit, kommunal yoki aliment qarzi", "Sud buyrug'i yoki qarori ijroga yuborilgan",
                           "Qarz to'langan, lekin tizimda yopilmagan"],
        "steps": ["Qarzingiz va ijro ishi raqamini rasmiy portal orqali tekshiring",
                  "Qaysi hujjat asosida ochilganini aniqlang",
                  "Qarz to'langan bo'lsa — to'lov hujjati bilan yopishni so'rang",
                  "Noto'g'ri deb hisoblasangiz — ijro harakati ustidan shikoyat qiling"],
        "documents": ["Shaxsni tasdiqlovchi hujjat", "To'lov kvitansiyasi (to'langan bo'lsa)", "Ijro ishi raqami"],
        "deadlines": [f"Cheklovni bekor qilish muddati: {T}", f"Ijro harakati ustidan shikoyat muddati: {T}"],
        "where_to_go": [MYGOV, {"name": "Majburiy ijro byurosi hududiy bo'limi", "url": "https://my.gov.uz"}],
        "legal_basis": [basis("REF_ENFORCEMENT_1", "\"Sud hujjatlari va boshqa organlar hujjatlarini ijro etish to'g'risida\"gi Qonun")],
        "appeal_template_id": "appeal_enforcement",
        "appeal_addressee": "Majburiy ijro byurosi hududiy bo'limi boshlig'iga",
        "textbook_refs": ["civil_proc_ch5_s2"],
    },
    {
        "id": "traffic_fine",
        "category": "yol_harakati",
        "title_uz": "Yo'l harakati jarimasi: kamera, inspektor, chegirma va e'tiroz",
        "title_ru": "Штраф ПДД: камера, инспектор, скидка и обжалование",
        "triggers": ["jarima", "yo'l jarimasi", "kamera jarima", "radar", "inspektor jarima", "jarima sms",
                     "jarima chegirma", "50 foiz", "jarimani bekor qilish", "invoys", "жарима", "штраф", "штраф гаи",
                     "камера штраф"],
        "plain_explanation_uz": "Jarima haqida xabar kelganda summasi, chegirmali summasi va chegirma muddati ko'rsatiladi. "
                                 "Chegirma muddatida to'lasangiz kamroq to'laysiz. Qoidabuzarlikka rozi bo'lmasangiz, qarorga e'tiroz bildirishingiz mumkin.",
        "common_reasons": ["Kamera qayd etgan qoidabuzarlik (avtomobil egasiga yuboriladi)",
                           "Inspektor tuzgan bayonnoma",
                           "Avtomobilni boshqa shaxs boshqargan bo'lishi mumkin"],
        "steps": ["SMS'dagi invoys raqami bo'yicha jarimani rasmiy portalda tekshiring",
                  "Rozi bo'lsangiz — chegirma muddatida to'lang",
                  "Rozi bo'lmasangiz — qaror ustidan yuqori organga yoki sudga e'tiroz bildiring",
                  "Kamera fotosuratini (dalilni) ko'rishni so'rang"],
        "documents": ["Jarima qarori yoki invoys raqami", "Haydovchilik guvohnomasi / texpasport", "E'tiroz uchun dalillar (foto, video)"],
        "deadlines": [f"Chegirmali to'lov muddati: SMS'da ko'rsatilgan sana ({T}: qonuniy muddat)",
                      f"E'tiroz bildirish muddati: {T}"],
        "where_to_go": [MYGOV, {"name": "Yo'l harakati xavfsizligi xizmati hududiy bo'limi", "url": "https://my.gov.uz"}],
        "legal_basis": [basis("REF_ADMIN_CODE_TRAFFIC", "O'zbekiston Respublikasining Ma'muriy javobgarlik to'g'risidagi kodeksi")],
        "appeal_template_id": "appeal_fine_dispute",
        "appeal_addressee": "Jarima qarorini chiqargan organning yuqori turuvchi rahbariga",
        "textbook_refs": ["admin_law_ch6_s1"],
    },
    {
        "id": "unpaid_salary",
        "category": "mehnat",
        "title_uz": "Ish haqi berilmayapti / mehnat nizosi",
        "title_ru": "Не выплачивают зарплату / трудовой спор",
        "triggers": ["ish haqi berilmayapti", "maosh bermayapti", "oylik bermayapti", "ish haqi kechikmoqda",
                     "ishdan bo'shatishdi", "mehnat nizosi", "иш ҳақи", "ойлик бермаяпти", "не платят зарплату",
                     "задержка зарплаты", "трудовой спор"],
        "plain_explanation_uz": "Ish beruvchi bajarilgan ish uchun ish haqini o'z vaqtida to'lashi shart. "
                                 "To'lanmasa, avval ish beruvchiga yozma murojaat qiling, so'ng mehnat inspeksiyasi yoki sudga murojaat qilishingiz mumkin.",
        "common_reasons": ["Mehnat shartnomasi rasmiylashtirilmagan", "Korxonada moliyaviy qiyinchilik",
                           "Ishdan bo'shatishda hisob-kitob qilinmagan"],
        "steps": ["Ish beruvchiga yozma talabnoma bering va nusxasini saqlang",
                  "Mehnat shartnomasi, buyruqlar, ish haqi hisob-kitobini to'plang",
                  "Davlat mehnat inspeksiyasiga murojaat qiling",
                  "Hal bo'lmasa — sudga da'vo bering"],
        "documents": ["Mehnat shartnomasi yoki ishga qabul buyrug'i", "Ish haqi hisob-varag'i / bank ko'chirmasi", "Yozma talabnoma nusxasi"],
        "deadlines": [f"Mehnat nizosi bo'yicha sudga murojaat muddati: {T}"],
        "where_to_go": [{"name": "Davlat mehnat inspeksiyasi hududiy bo'limi", "url": "https://my.gov.uz"},
                        {"name": "Tuman (shahar) sudi (fuqarolik ishlari)", "url": "https://my.sud.uz"}, MYGOV],
        "legal_basis": [basis("REF_LABOR_SALARY", "O'zbekiston Respublikasining Mehnat kodeksi")],
        "appeal_template_id": "appeal_labor",
        "appeal_addressee": "Davlat mehnat inspeksiyasi hududiy bo'limi boshlig'iga",
        "textbook_refs": ["labor_law_ch4_s2"],
    },
    {
        "id": "utility_debt_court_order",
        "category": "kommunal",
        "title_uz": "Kommunal qarz va sud buyrug'i",
        "title_ru": "Коммунальный долг и судебный приказ",
        "triggers": ["kommunal qarz", "sud buyrug'i", "gaz qarzi", "svet qarzi", "elektr qarzi", "suv qarzi",
                     "kommunal to'lov", "суд буйруғи", "коммунальный долг", "судебный приказ"],
        "plain_explanation_uz": "Kommunal qarz bo'yicha sud buyrug'i — soddalashtirilgan tartibda, tomonlarni chaqirmasdan chiqariladigan hujjat. "
                                 "Qarz summasiga rozi bo'lmasangiz, belgilangan muddatda e'tiroz bildirib, buyruqni bekor qildirishingiz mumkin.",
        "common_reasons": ["Hisoblagich ko'rsatkichlari noto'g'ri", "To'lov tizimda aks etmagan",
                           "Boshqa abonent qarzi sizga yozilgan"],
        "steps": ["Sud buyrug'i nusxasini oling va qarz summasini tekshiring",
                  "To'lov kvitansiyalaringizni to'plang",
                  "Rozi bo'lmasangiz — buyruqni chiqargan sudga e'tiroz yuboring",
                  "Xizmat ko'rsatuvchi tashkilot bilan hisob-kitobni solishtiring"],
        "documents": ["Sud buyrug'i nusxasi", "To'lov kvitansiyalari", "Hisoblagich ko'rsatkichlari"],
        "deadlines": [f"Sud buyrug'iga e'tiroz bildirish muddati: {T}"],
        "where_to_go": [{"name": "Buyruqni chiqargan sud", "url": "https://my.sud.uz"}, MYGOV],
        "legal_basis": [basis("REF_CIVPROC_COURT_ORDER", "O'zbekiston Respublikasining Fuqarolik protsessual kodeksi")],
        "appeal_template_id": "appeal_court_order_objection",
        "appeal_addressee": "Sud buyrug'ini chiqargan sudga",
        "textbook_refs": ["civil_proc_ch5_s1"],
    },
    {
        "id": "online_loan_fraud",
        "category": "moliya",
        "title_uz": "Firibgarlar nomimga onlayn kredit olgan",
        "title_ru": "Мошенники оформили на меня онлайн-кредит",
        "triggers": ["nomimga kredit", "onlayn kredit firibgar", "men olmagan kredit", "mikroqarz", "kredit olishgan",
                     "firibgarlik kredit", "номимга кредит", "оформили кредит на меня", "мошенники кредит"],
        "plain_explanation_uz": "Agar siz olmagan kredit nomingizga rasmiylashtirilgan bo'lsa, bu firibgarlik belgisi. "
                                 "Darhol bank yoki kredit tashkilotiga yozma xabar bering va huquqni muhofaza qiluvchi organga ariza yozing.",
        "common_reasons": ["SMS kod yoki karta ma'lumotlari begonaga berilgan", "Shaxsiy hujjat nusxasidan foydalanilgan",
                           "Telefon raqami boshqa shaxs qo'lida"],
        "steps": ["Kredit bergan tashkilotga yozma ariza bering (kreditni olmaganingiz haqida)",
                  "Ichki ishlar organiga firibgarlik haqida ariza yozing",
                  "Kredit tarixingizni tekshiring",
                  "Hech kimga SMS kodlarni bermang"],
        "documents": ["Shaxsni tasdiqlovchi hujjat", "Kredit haqidagi xabar/SMS skrinshoti", "Politsiyaga arizaning nusxasi"],
        "deadlines": [f"Bankka xabar berish muddati: {T}"],
        "where_to_go": [{"name": "Ichki ishlar organi (tuman bo'limi)", "url": "https://my.gov.uz"},
                        {"name": "Kredit bergan bank / tashkilot", "url": "https://my.gov.uz"}, MYGOV],
        "legal_basis": [basis("REF_CONSUMER_CREDIT", f"{T}: iste'mol kreditlari / firibgarlikka oid hujjat")],
        "appeal_template_id": "appeal_fraud",
        "appeal_addressee": "Ichki ishlar bo'limi boshlig'iga",
        "textbook_refs": ["civil_law_ch4_s2"],
    },
    {
        "id": "fake_mib_sms",
        "category": "firibgarlik",
        "title_uz": "MIB nomidan soxta SMS (firibgarlik)",
        "title_ru": "Фальшивое SMS от имени МИБ",
        "triggers": ["mib sms havola", "soxta sms", "firibgar sms", "havolaga o'ting qarz", "karta raqamini so'rayapti",
                     "sms kod so'rashdi", "фальшивое смс", "мошенническое смс", "сохта смс"],
        "plain_explanation_uz": "Davlat organi nomidan kelgan SMS'da noma'lum havola, karta raqami yoki SMS kod so'ralsa — bu firibgarlik bo'lishi mumkin. "
                                 "Qarzingizni faqat rasmiy portal orqali tekshiring, havolani ochmang.",
        "common_reasons": ["SMS'da gov.uz bo'lmagan havola", "Shoshilinch to'lashga undash, 'bloklanadi' degan tahdid",
                           "Karta ma'lumotlari yoki kod so'ralmoqda"],
        "steps": ["Havolani ochmang, karta ma'lumotini kiritmang",
                  "Qarzingizni faqat rasmiy portalda tekshiring",
                  "Ma'lumot kiritib qo'ygan bo'lsangiz — darhol bankka qo'ng'iroq qilib kartani bloklang",
                  "Ichki ishlar organiga xabar bering"],
        "documents": ["SMS skrinshoti", "Yuboruvchi raqam"],
        "deadlines": ["Karta ma'lumoti kiritilgan bo'lsa — darhol bankka murojaat qiling"],
        "where_to_go": [MYGOV, {"name": "Ichki ishlar organi (tuman bo'limi)", "url": "https://my.gov.uz"}],
        "legal_basis": [basis("REF_FRAUD_1", f"{T}: firibgarlik uchun javobgarlik belgilovchi hujjat")],
        "appeal_template_id": "appeal_fraud",
        "appeal_addressee": "Ichki ishlar bo'limi boshlig'iga",
        "textbook_refs": ["criminal_law_ch7_s1"],
    },
    {
        "id": "mahalla_noise_waste_fine",
        "category": "obodonlashtirish",
        "title_uz": "Shovqin yoki chiqindi uchun jarima (mahallada)",
        "title_ru": "Штраф за шум или мусор (в махалле)",
        "triggers": ["shovqin jarima", "chiqindi jarima", "axlat jarima", "musor jarima", "tunda shovqin",
                     "obodonlashtirish jarima", "шовқин", "штраф за шум", "штраф за мусор"],
        "plain_explanation_uz": "Jamoat tartibi va obodonlashtirish qoidalarini buzish uchun ma'muriy jarima qo'llanishi mumkin. "
                                 "Jarima faqat rasmiylashtirilgan bayonnoma va qaror asosida qo'llanadi, siz unga e'tiroz bildirishingiz mumkin.",
        "common_reasons": ["Belgilangan vaqtda shovqin", "Chiqindini belgilanmagan joyga tashlash",
                           "Bayonnoma sizning ishtirokingizsiz tuzilgan"],
        "steps": ["Bayonnoma yoki qaror nusxasini so'rang",
                  "Kim, qachon va qanday dalil bilan qayd etganini tekshiring",
                  "Rozi bo'lmasangiz — yuqori organga yoki sudga e'tiroz bildiring"],
        "documents": ["Bayonnoma / qaror nusxasi", "Dalillar (guvohlar, foto)"],
        "deadlines": [f"E'tiroz bildirish muddati: {T}"],
        "where_to_go": [{"name": "Tuman (shahar) hokimligi", "url": "https://my.gov.uz"}, MYGOV],
        "legal_basis": [basis("REF_ADMIN_CODE_PUBLIC_ORDER", "O'zbekiston Respublikasining Ma'muriy javobgarlik to'g'risidagi kodeksi")],
        "appeal_template_id": "appeal_fine_dispute",
        "appeal_addressee": "Jarima qarorini chiqargan organning yuqori turuvchi rahbariga",
        "textbook_refs": ["admin_law_ch6_s2"],
    },
    {
        "id": "consumer_refund",
        "category": "istemolchi",
        "title_uz": "Sifatsiz tovar: qaytarish va pulni olish",
        "title_ru": "Некачественный товар: возврат и деньги",
        "triggers": ["tovarni qaytarish", "pulimni qaytarmayapti", "sifatsiz tovar", "brak tovar", "kafolat",
                     "do'kon qaytarmayapti", "iste'molchi huquqi", "товар қайтариш", "вернуть товар", "возврат денег",
                     "некачественный товар"],
        "plain_explanation_uz": "Sifatsiz tovar sotilgan bo'lsa, iste'molchi uni almashtirish, ta'mirlash yoki pulni qaytarishni talab qilishi mumkin. "
                                 "Avval sotuvchiga yozma talab bering, javob bo'lmasa vakolatli organ yoki sudga murojaat qiling.",
        "common_reasons": ["Chek yoki kafolat taloni yo'q", "Kafolat muddati o'tgan", "Sotuvchi nuqsonni tan olmayapti"],
        "steps": ["Sotuvchiga yozma talabnoma bering (nusxasini saqlang)",
                  "Chek, kafolat taloni va nuqson suratlarini saqlang",
                  "Javob bo'lmasa — iste'molchilar huquqlarini himoya qilish organiga murojaat qiling",
                  "Kerak bo'lsa — sudga da'vo bering"],
        "documents": ["Chek yoki to'lov hujjati", "Kafolat taloni", "Yozma talabnoma nusxasi"],
        "deadlines": [f"Talabni ko'rib chiqish va pulni qaytarish muddati: {T}"],
        "where_to_go": [{"name": f"Iste'molchilar huquqlarini himoya qilish bo'yicha vakolatli organ ({T}: aniq nomi)", "url": "https://my.gov.uz"},
                        MYGOV],
        "legal_basis": [basis("REF_CONSUMER_RIGHTS_1", "\"Iste'molchilarning huquqlarini himoya qilish to'g'risida\"gi Qonun")],
        "appeal_template_id": "appeal_consumer",
        "appeal_addressee": "Do'kon (sotuvchi) rahbariga",
        "textbook_refs": ["civil_law_ch4_s3"],
    },
]


def main(force: bool) -> None:
    out_dir = ROOT / "knowledge" / "cards"
    out_dir.mkdir(parents=True, exist_ok=True)
    for c in CARDS:
        card = {
            "id": c["id"],
            "category": c["category"],
            "title_uz": c["title_uz"],
            "title_cyrl": lat_to_cyr(c["title_uz"]),
            "title_ru": c["title_ru"],
            **{k: v for k, v in c.items() if k not in {"id", "category", "title_uz", "title_ru"}},
            "verified": False,
            "verified_by": None,
            "verified_at": None,
            "_note": "PLACEHOLDER: huquqiy mazmunni huquqshunos tekshirishi va TODO_LAWYER joylarini to'ldirishi shart.",
        }
        path = out_dir / f"{c['id']}.json"
        if path.exists() and not force:
            print("o'tkazildi (mavjud):", path.name)
            continue
        path.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
        print("yozildi:", path.name)


if __name__ == "__main__":
    main(force="--force" in sys.argv)
