// «Qanday ishlaydi» — bosh sahifa bloki uchun matn (1-oyna ulaydi). Ketma-ketlik haqiqiy: savoldan murojaatgacha.
// steps — tartibli qadamlar (raqamlash o'rinli), trust — ishonch kafolatlari (tartibsiz ro'yxat).

export const howItWorks = {
  title: "Qanday ishlaydi",
  lead: "Muammo boshingizga tushganda — murojaat yozishdan oldin — huquqingizni oddiy tilda, qonun matni bilan birga bilib oling.",
  steps: [
    {
      id: "ask",
      title: "Vaziyatingizni yozing yoki ayting",
      text: "Telegram botga, saytga yoki Mini App'ga oddiy so'z bilan: «Stipendiya nega berilmadi?». Ovozli xabar va jarima SMS'i ham bo'ladi.",
    },
    {
      id: "law",
      title: "Qonunni ikki tilda ko'ring",
      text: "Chapda — lex.uz'dagi asl matn, o'ng tomonda — oddiy tildagi izoh. Har javobda modda va havola bor.",
    },
    {
      id: "rights",
      title: "Haqingizni tekshiring",
      text: "«Mening huquqlarim»da talaba, bolali ona, tadbirkor, pensioner va haydovchi uchun imtiyozlar, hujjatlar va qayerga borish. Natija — «haqli bo'lishingiz mumkin» va tekshiriladigan shartlar.",
    },
    {
      id: "appeal",
      title: "Kerak bo'lsa — tayyor ariza",
      text: "Rekvizitlar qonundan olinadi: to'g'ri adresat, huquqiy asos, ko'rib chiqish muddati. Nusxa oling yoki PDF qilib saqlang.",
    },
  ],
  trust: [
    { id: "source", title: "Faqat rasmiy manba", text: "Qonun matni lex.uz'dan aynan olinadi va avtomatik solishtiriladi. Manba topilmasa — «tasdiqlangan ma'lumot topilmadi»." },
    { id: "ai", title: "AI faqat soddalashtiradi", text: "Oddiy tildagi matn rasmiy matn yonida turadi. Yangi modda, summa yoki muddat qo'shilmaydi." },
    { id: "privacy", title: "Ma'lumotingiz saqlanmaydi", text: "Savol matni, ism, PINFL va telefon saqlanmaydi. Ariza maydonlari faqat matnga qo'yiladi." },
  ],
};

export default howItWorks;
