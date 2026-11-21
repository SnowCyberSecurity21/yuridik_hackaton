"""Bilimlar bazasining qolgan seed fayllarini yozadi:
murojaat shablonlari, fact-check claim'lari, lex namunalari, o'zgarishlar lentasi (mock), darslik bo'laklari.
Huquqiy mazmun — PLACEHOLDER (TODO_LAWYER). Ishga tushirish: python scripts/build_seed_knowledge.py [--force]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

K = Path(__file__).resolve().parents[1] / "knowledge"
T = "TODO_LAWYER"
FORCE = "--force" in sys.argv


def w(rel: str, obj) -> None:
    p = K / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() and not FORCE:
        print("o'tkazildi (mavjud):", rel)
        return
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    print("yozildi:", rel)


# ---- Murojaat shablonlari -------------------------------------------------
BODY = (
    "{addressee}\n"
    "{region} hududida yashovchi fuqaro {applicant_name}dan\n"
    "Manzil: {address}\n"
    "Aloqa: {contact}\n\n"
    "{doc_type}\n\n"
    "{intro}\n\n"
    "Vaziyat: {situation}\n\n"
    "Huquqiy asos: {legal_basis}\n\n"
    "Yuqoridagilarni inobatga olib, {request}\n\n"
    "Ilova: {attachments}\n\n"
    "Sana: {date}                Imzo: ____________\n"
)
TEMPLATES = {
    "appeal_social_benefit": ("ARIZA (SHIKOYAT)",
                              "Men bolamga nafaqa tayinlash uchun murojaat qilgan edim, biroq nafaqa tayinlanmadi.",
                              "rad etish sababini yozma ravishda tushuntirishingizni va qarorni qayta ko'rib chiqishingizni so'rayman."),
    "appeal_enforcement": ("ARIZA", "Men ijro ishi bo'yicha quyidagi masalada murojaat qilmoqdaman.",
                           "ijro ishi holati haqida yozma ma'lumot berishingizni va qonuniy choralar ko'rishingizni so'rayman."),
    "appeal_fine_dispute": ("SHIKOYAT (E'TIROZ)", "Menga nisbatan qo'llangan jarima qaroriga rozi emasman.",
                            "jarima qarorini qayta ko'rib chiqishingizni va dalillarni taqdim etishingizni so'rayman."),
    "appeal_labor": ("ARIZA", "Ish beruvchim tomonidan mehnat huquqlarim buzilmoqda.",
                     "ish beruvchiga nisbatan tekshiruv o'tkazishingizni va ish haqimni to'lash choralarini ko'rishingizni so'rayman."),
    "appeal_court_order_objection": ("SUD BUYRUG'IGA E'TIROZ", "Menga nisbatan chiqarilgan sud buyrug'iga rozi emasman.",
                                     "sud buyrug'ini bekor qilishingizni so'rayman."),
    "appeal_fraud": ("ARIZA", "Nomimdan firibgarlik harakatlari sodir etilgan.",
                     "firibgarlik holati yuzasidan tekshiruv o'tkazishingizni so'rayman."),
    "appeal_consumer": ("TALABNOMA", "Sizning do'koningizdan sotib olingan tovar sifatsiz chiqdi.",
                        "tovarni almashtirishingizni yoki to'langan pulni qaytarishingizni talab qilaman."),
}
for tid, (doc_type, intro, req) in TEMPLATES.items():
    w(f"appeal_templates/{tid}.json", {
        "id": tid, "doc_type": doc_type, "intro": intro, "request": req, "body": BODY,
        "checklist": ["Adresat (qaysi organ/rahbarga) to'g'ri ko'rsatilgan", "Ariza beruvchining F.I.Sh. va manzili",
                      "Vaziyat qisqa va aniq bayon qilingan", "Huquqiy asos ko'rsatilgan", "Aniq talab",
                      "Ilovalar ro'yxati", "Sana va imzo"],
        "submit_channels": [{"name": "my.gov.uz", "url": "https://my.gov.uz"},
                            {"name": "Virtual qabulxona (pm.gov.uz)", "url": "https://pm.gov.uz"}],
        "verified": False,
    })

# ---- Fact-check: namunaviy claim'lar ---------------------------------------
w("factcheck/known_claims.json", {
    "_note": "DEMO claim'lar. Hukm va manbani huquqshunos tasdiqlashi shart (verified=false).",
    "claims": [
        {"id": "claim_car_new_tax_jan1",
         "claim_uz": "1-yanvardan hamma mashinaga yangi soliq joriy qilinadi",
         "triggers": ["1-yanvardan hamma mashinaga yangi soliq", "hamma mashinaga yangi soliq", "hamma mashinaga soliq",
                      "barcha avtomobillarga yangi soliq", "mashina egalari yangi soliq to'laydi",
                      "все машины новый налог", "ҳамма машинага солиқ"],
         "verdict": "notogri",
         "explanation_uz": "Barcha avtomobillarga 1-yanvardan yangi soliq joriy etilgani haqidagi da'vo rasmiy hujjat bilan tasdiqlanmagan. "
                           "Soliqlar Soliq kodeksi va rasmiy e'lon qilingan hujjatlar bilan belgilanadi — postdagi da'vo manbasiz.",
         "legal_basis": [{"ref_id": "REF_TAX_CODE_1", "doc": "O'zbekiston Respublikasining Soliq kodeksi", "article": T, "lex_url": "https://lex.uz/"}],
         "topic_id": None, "verified": False},
        {"id": "claim_alimony_stops_at_16",
         "claim_uz": "Aliment bola 16 yoshga to'lganda to'xtaydi",
         "triggers": ["aliment 16 yoshda to'xtaydi", "16 yoshdan keyin aliment yo'q", "aliment 16 yoshgacha"],
         "verdict": "tasdiqlanmagan",
         "explanation_uz": f"Aliment to'lash yoshi va muddati qonunda belgilangan ({T}). Huquqshunos tasdiqlamaguncha bu da'voga baho berilmaydi.",
         "legal_basis": [{"ref_id": "REF_ALIMONY_1", "doc": "O'zbekiston Respublikasi Oila kodeksi", "article": T, "lex_url": "https://lex.uz/"}],
         "topic_id": "alimony", "verified": False},
        {"id": "claim_mib_sms_link_pay",
         "claim_uz": "MIB qarzingizni shu havola orqali 24 soatda to'lamasangiz kartangiz bloklanadi",
         "triggers": ["kartangiz bloklanadi", "24 soat ichida to'lang havola", "mib havola orqali to'lang"],
         "verdict": "notogri",
         "explanation_uz": "Davlat organlari to'lovni noma'lum havola orqali talab qilmaydi. Bu firibgarlik belgisi — qarzni faqat rasmiy portalda tekshiring.",
         "legal_basis": [{"ref_id": "REF_FRAUD_1", "doc": f"{T}: firibgarlik uchun javobgarlik belgilovchi hujjat", "article": T, "lex_url": "https://lex.uz/"}],
         "topic_id": "fake_mib_sms", "verified": False},
        {"id": "claim_fine_discount_70",
         "claim_uz": "Endi barcha jarimalarga 70 foiz chegirma beriladi",
         "triggers": ["jarimalarga 70 foiz chegirma", "70% chegirma jarima", "barcha jarimalarga chegirma"],
         "verdict": "qisman",
         "explanation_uz": f"Ayrim jarimalar muddatida to'lansa chegirma qo'llanadi (SMS'da ko'rsatiladi), biroq 'barcha jarimalarga 70 foiz' degan da'vo tasdiqlanmagan ({T}: amaldagi chegirma tartibi).",
         "legal_basis": [{"ref_id": "REF_ADMIN_CODE_TRAFFIC", "doc": "O'zbekiston Respublikasining Ma'muriy javobgarlik to'g'risidagi kodeksi", "article": T, "lex_url": "https://lex.uz/"}],
         "topic_id": "traffic_fine", "verified": False},
    ]})

# ---- Lex.uz kesh namunalari (RAG) -----------------------------------------
w("lex/excerpts.json", {
    "_note": "Bu yerga lex.uz'dan qo'lda olingan ANIQ parchalar qo'yiladi. Matni TODO_LAWYER bilan boshlanadigan yozuvlar RAG'da e'tiborga olinmaydi.",
    "excerpts": [
        {"id": "ex_appeals_law_1", "ref_id": "REF_APPEALS_LAW_1",
         "doc": "\"Jismoniy va yuridik shaxslarning murojaatlari to'g'risida\"gi Qonun", "article": T, "lex_url": "https://lex.uz/",
         "text": f"{T}: murojaatlarni ko'rib chiqish muddatlari haqidagi modda matni"},
        {"id": "ex_labor_salary_1", "ref_id": "REF_LABOR_SALARY",
         "doc": "O'zbekiston Respublikasining Mehnat kodeksi", "article": T, "lex_url": "https://lex.uz/",
         "text": f"{T}: ish haqini to'lash muddatlari haqidagi modda matni"},
    ]})

# ---- O'zgarishlar lentasi (mock) -------------------------------------------
w("lex/changes_feed.json", {
    "_note": "MOCK lenta. Matnlar [DEMO] — haqiqiy o'zgarish emas. Haqiqiysi bilan huquqshunos almashtiradi.",
    "changes": [
        {"id": "chg_demo_child_allowance", "ref_id": "REF_CHILD_ALLOWANCE_1",
         "doc": f"{T}: bolalik nafaqasini tayinlash tartibini belgilovchi hujjat", "article": T, "date": "2026-11-21",
         "summary_uz": "[DEMO] Bolalik nafaqasi uchun ariza berish tartibi o'zgardi: ariza endi faqat onlayn qabul qilinadi.",
         "old_text": "[DEMO] Ariza tuman ijtimoiy xizmatlar markaziga qog'oz shaklida yoki onlayn topshiriladi.",
         "new_text": "[DEMO] Ariza faqat my.gov.uz orqali onlayn topshiriladi; markaz xodimi arizani to'ldirishda yordam beradi."},
        {"id": "chg_demo_labor_salary", "ref_id": "REF_LABOR_SALARY",
         "doc": "O'zbekiston Respublikasining Mehnat kodeksi", "article": T, "date": "2026-11-22",
         "summary_uz": "[DEMO] Ish haqi kechiktirilganda xodimni xabardor qilish tartibi o'zgardi.",
         "old_text": "[DEMO] Ish beruvchi ish haqi kechikishi haqida xodimni og'zaki xabardor qiladi.",
         "new_text": "[DEMO] Ish beruvchi ish haqi kechikishi haqida xodimni yozma ravishda xabardor qilishi shart."},
    ]})

# ---- Darslik bo'laklari ----------------------------------------------------
w("textbooks/practical_manual.json", {
    "id": "practical_manual", "title": "Amaliy huquq: fuqarolar murojaatlari (o'quv qo'llanma, DEMO)",
    "_note": "DEMO o'quv matni. Modda raqamlari yo'q — ref_id orqali bog'langan.",
    "chunks": [
        {"id": "social_law_ch2_s1", "title": "2.1. Bolalik nafaqasini tayinlash tartibi",
         "text": "Bolalik nafaqasi oila daromadi va boshqa mezonlar asosida tayinlanadi. "
                 "[DEMO] Ariza tuman ijtimoiy xizmatlar markaziga qog'oz shaklida yoki onlayn topshiriladi. "
                 "Talaba fuqaroga rad etish sababini yozma so'rash huquqini tushuntira olishi kerak.",
         "refs": ["REF_CHILD_ALLOWANCE_1"]},
        {"id": "labor_law_ch4_s2", "title": "4.2. Ish haqini to'lash va kechiktirish",
         "text": "Ish beruvchi bajarilgan ish uchun ish haqini o'z vaqtida to'lashi shart. "
                 "[DEMO] Ish beruvchi ish haqi kechikishi haqida xodimni og'zaki xabardor qiladi. "
                 "Nizolar mehnat inspeksiyasi yoki sud orqali hal qilinadi.",
         "refs": ["REF_LABOR_SALARY"]},
        {"id": "family_law_ch3_s1", "title": "3.1. Aliment majburiyatlari",
         "text": "Ota-ona voyaga yetmagan bolasini ta'minlashi shart. Ixtiyoriy to'lanmasa, aliment sud orqali undiriladi.",
         "refs": ["REF_ALIMONY_1", "REF_ENFORCEMENT_1"]},
        {"id": "admin_law_ch6_s1", "title": "6.1. Yo'l harakati sohasidagi ma'muriy jarimalar",
         "text": "Jarima qarori ustidan e'tiroz bildirish mumkin. Kamera qayd etgan qoidabuzarlik avtomobil egasiga yuboriladi.",
         "refs": ["REF_ADMIN_CODE_TRAFFIC"]},
    ]})
