// features/ — huquqiy kontent komponentlari (2-oyna). 1-oyna shu fayl orqali sahifalarga ulaydi.
// Hammasi src/ui komponentlari va index.css tokenlaridan foydalanadi; API — ./api.js (timeout + {error}).
//
// ─────────────────────────────────────────────────────────────────────────────────────────────
// LawView                — qonun abzasi: «Qonunda» (lex.uz'dan aynan, serif) ↔ «Oddiy tilda» (AI, marker).
//   Qayerga:  kabinet («Mening huquqlarim» yozuvi ochilganda), /anonim javob kartasi, Mini App karta sahifasi.
//   Props:    excerpts?: Excerpt[]  — tayyor ro'yxat (masalan, /api/ask javobidagi `quotes`, toifa yozuvidagi `excerpts`)
//             ids?: string[] | category?: string | item?: string — berilsa o'zi /api/lex/excerpts dan yuklaydi
//             compact?: boolean (karta ichida), lang?: "uz"|"ru", limit?: number, emptyText?: string
//   Misol:    <LawView ids={["ex_stip_grades"]} />   <LawView excerpts={answer.quotes} compact />
//
// RightsCategories       — «Mening huquqlarim»: Talaba · Bolali ona · Yuridik shaxs/tadbirkor · Pensioner · Haydovchi.
//   Qayerga:  /anonim «Huquqlarim» bo'limi (hammasi); /kabinet — `only={cabinet.situations.map(s => s.id)}`.
//   Props:    initial?: string, only?: string[], onAppeal?: (item) => void (imtiyozda «Ariza tayyorlash»), lang?
//
// AskBox                 — «Savol bering»: savol → manbali javob + asl iqtibos + oddiy til (LawView ichida).
//   Qayerga:  bosh sahifa / anonim sahifa «Savol bering» bloki.
//   Props:    legalStatus?: string, region?: string, placeholder?: string,
//             onAppeal?: (cardId: string) => void — «Ariza tayyorlash» tugmasi (masalan AppealForm Sheet'ini ochish)
//
// AppealForm             — murojaat: rekvizitlar (Murojaatlar to'g'risidagi Qonun, 6-modda) → tayyor matn → nusxa / PDF.
//   Qayerga:  Sheet/Modal ichida (AskBox yoki RightsCategories dan), yoki alohida «Ariza» sahifasi.
//   Props:    cardId?: string (berilmasa — mavzu tanlanadi), defaults?: {applicant_name, address, contact, region, situation},
//             onDone?: (result) => void
//
// howItWorks             — «Qanday ishlaydi» matni (bosh sahifa uchun): { title, lead, steps[], trust[] }.
// featuresApi            — API klienti (categories, category, excerpts, ask, appealTemplates, appeal, cards).
// ─────────────────────────────────────────────────────────────────────────────────────────────

export { default as LawView, LawExcerpt } from "./LawView.jsx";
export { default as RightsCategories } from "./RightsCategories.jsx";
export { default as AskBox } from "./AskBox.jsx";
export { featuresApi } from "./api.js";
