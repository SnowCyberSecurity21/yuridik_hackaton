// Bosh sahifa: hero (qonun tili → oddiy til), 2 yo'l, «Qanday ishlaydi» (5 muammo → yechim), savol bloki, dalillar.
import { motion } from "motion/react";
import { APP_NAME } from "./config.js";
import { AskPanel, go } from "./Site.jsx";
import { Badge, Card, CountUp, Reveal, RevealGroup, RevealItem, UnverifiedBadge } from "./ui/index.js";

const ease = [0.23, 1, 0.32, 1];

// Namuna — aniq modda yoki raqam keltirilmaydi (haqiqiy javoblarda manba kartadan olinadi).
const LEGAL = "Nafaqa tayinlash to'g'risidagi ariza zarur hujjatlar ilova qilingan holda vakolatli organga taqdim etiladi hamda oila daromadi belgilangan mezonlarga muvofiqligi aniqlangan taqdirda nafaqa tayinlanadi.";
const PLAIN = [
  "Ariza yozasiz va hujjatlarni ilova qilasiz.",
  "Oila daromadi belgilangan chegaradan oshmasa — nafaqa tayinlanadi.",
  "Rad etilsa — keyingi qadam va tayyor ariza.",
];

function TranslateDemo() {
  return (
    <div className="relative" aria-label="Namuna: qonun matni va uning oddiy tildagi tushuntirishi">
      <motion.div className="card overflow-hidden" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease, delay: 0.1 }}>
        <div className="p-5 sm:p-6" style={{ background: "var(--surface-2)" }}>
          <div className="mb-2 flex items-center gap-2">
            <span className="tiny muted font-semibold">Qonun tili</span>
            <span className="tiny muted">· namuna</span>
          </div>
          <p className="law text-[0.95rem] sm:text-base">{LEGAL}</p>
        </div>
        <div className="relative px-5 pb-5 pt-6 sm:px-6 sm:pb-6">
          <motion.span className="absolute -top-3.5 left-5 sm:left-6"
            initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.4, ease, delay: 0.75 }}>
            <span className="badge badge-info" style={{ boxShadow: "0 0 0 4px var(--surface-1)" }}>↓ Oddiy tilda</span>
          </motion.span>
          <ul className="space-y-2.5">
            {PLAIN.map((line, i) => (
              <motion.li key={line} className="flex gap-3 text-[1.0625rem] font-medium leading-snug"
                initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45, ease, delay: 0.95 + i * 0.16 }}>
                <span className="tabnum muted mt-0.5 text-sm" aria-hidden>{i + 1}</span>
                <span>{i === 1 ? <span className="plain-mark">{line}</span> : line}</span>
              </motion.li>
            ))}
          </ul>
          <motion.div className="mt-5 flex flex-wrap items-center gap-2 border-t pt-4" style={{ borderColor: "var(--border)" }}
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4, delay: 1.55 }}>
            <Badge tone="verified">✅ Manba: lex.uz</Badge>
            <span className="source">Har javobda hujjat, modda va havola</span>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}

function PathCard({ icon, title, text, cta, primary, onClick }) {
  return (
    <button type="button" onClick={onClick}
      className="card card-interactive group flex h-full flex-col p-5"
      style={primary ? { background: "var(--primary)", color: "var(--text-on-primary)", borderColor: "transparent" } : undefined}>
      <span className="text-2xl" aria-hidden>{icon}</span>
      <span className="mt-3 text-lg font-bold leading-snug">{title}</span>
      <span className="mt-1 text-sm leading-relaxed" style={{ opacity: primary ? 0.88 : 1, color: primary ? "inherit" : "var(--text-secondary)" }}>{text}</span>
      <span className="mt-auto pt-4 text-sm font-semibold underline decoration-1 underline-offset-4">{cta}</span>
    </button>
  );
}

const PROBLEMS = [
  { n: 1, problem: "Qonun tili murakkab", solution: "Oddiy til + asl matn", text: "Har javobda sodda tushuntirish, yonida esa qonunning asl matni va lex.uz havolasi." },
  { n: 2, problem: "Yangi qonunlar kech bilinadi", solution: "Shaxsiy o'zgarish xabarlari", text: "Qonun o'zgarsa, faqat sizga taalluqli bo'lsa xabar keladi — nega aynan sizga ekani bilan." },
  { n: 3, problem: "Targ'ibot formati eskirgan", solution: "Kartochka, audio, ulashish", text: "Qisqa kartochka, ovozli javob va qarindoshingizga yuborish uchun bitta tugma." },
  { n: 4, problem: "Chekka hududlarga yetib borish qiyin", solution: "Telegram, ovoz, kirill", text: "Yangi ilova o'rnatish shart emas: Telegram'da ovoz bilan so'rang, kirill yozuvida ham ishlaydi." },
  { n: 5, problem: "Ijtimoiy tarmoqda yolg'on ma'lumot", solution: "Fakt-tekshiruv", text: "Shubhali postni yuboring: To'g'ri, Qisman, Noto'g'ri yoki Tasdiqlanmagan — manbasi bilan." },
];

function HowItWorks() {
  return (
    <section aria-labelledby="how" className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)] lg:gap-10">
      <Reveal className="lg:sticky lg:top-24 lg:self-start">
        <h2 id="how" className="h1">Qanday ishlaydi</h2>
        <p className="secondary mt-2 measure">Huquqiy targ'ibot trekining beshta muammosi va {APP_NAME} ularning har biriga qanday javob beradi.</p>
      </Reveal>
      <RevealGroup as="ol" className="card divide-y overflow-hidden p-0">
        {PROBLEMS.map((p) => (
          <RevealItem as="li" key={p.n} className="grid gap-1 p-5 sm:grid-cols-[11rem_minmax(0,1fr)] sm:gap-6" style={{ borderColor: "var(--border)" }}>
            <div>
              <div className="tiny muted tabnum font-semibold">{p.n}-muammo</div>
              <div className="secondary mt-0.5 text-sm leading-snug">{p.problem}</div>
            </div>
            <div>
              <div className="font-semibold leading-snug">{p.solution}</div>
              <p className="secondary mt-1 text-sm leading-relaxed">{p.text}</p>
            </div>
          </RevealItem>
        ))}
      </RevealGroup>
    </section>
  );
}

const STATS = [
  { value: 557254, label: "murojaat Xalq qabulxonalariga 2026-yilda", source: "Prezident Xalq qabulxonasi" },
  { value: 48778, label: "murojaat bolalar nafaqasi bo'yicha, o'tgan yilga nisbatan +38%", source: "Prezident Xalq qabulxonasi" },
  { value: 65.2, label: "% murojaat shunchaki «huquqiy ma'lumot berish» bilan yopilgan", source: "Oliy ta'lim vazirligi, 2026 I chorak", pct: true },
];

function Evidence() {
  return (
    <section aria-labelledby="why" className="space-y-5">
      <Reveal>
        <h2 id="why" className="h1">Nega murojaatdan oldin</h2>
        <p className="secondary mt-2 measure">Ko'p murojaatlarga javob — oddiy tushuntirish. Uni fuqaro navbatsiz, darhol olishi mumkin.</p>
      </Reveal>
      <RevealGroup className="grid gap-px overflow-hidden rounded-[var(--radius-lg)] border sm:grid-cols-3" style={{ borderColor: "var(--border)", background: "var(--border)" }}>
        {STATS.map((s) => (
          <RevealItem key={s.label} className="p-5" style={{ background: "var(--surface-1)" }}>
            <div className="text-[2rem] font-bold leading-none tracking-tight sm:text-[2.4rem]">
              <CountUp value={s.value} format={s.pct ? (n) => String(n).replace(".", ",") : undefined} />{s.pct && "%"}
            </div>
            <p className="secondary mt-2 text-sm leading-snug">{s.pct ? s.label.replace(/^% /, "") : s.label}</p>
            <p className="muted mt-2 text-xs">{s.source}</p>
          </RevealItem>
        ))}
      </RevealGroup>
    </section>
  );
}

export default function Home({ me }) {
  const toCabinet = () => go(me?.logged_in ? "/kabinet" : "/kirish?next=oneid");
  return (
    <div className="space-y-16 sm:space-y-24">
      <section className="grid grid-cols-1 items-center gap-10 pt-4 sm:pt-10 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,1fr)] lg:gap-14">
        <div>
          <motion.h1 className="display" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.55, ease }}>
            Huquqingizni murojaatdan oldin, oddiy tilda biling.
          </motion.h1>
          <motion.p className="lead mt-4" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.55, ease, delay: 0.08 }}>
            {APP_NAME} vaziyatingizni sodda tushuntiradi, har javobga rasmiy manba qo'yadi va kerak bo'lsa tayyor ariza beradi.
          </motion.p>
          <motion.div className="mt-7 grid gap-3 sm:grid-cols-2" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.55, ease, delay: 0.16 }}>
            <PathCard primary icon="🪪" title="OneID bilan kirish" cta={me?.logged_in ? "Kabinetga o'tish" : "Hisob ochish"}
              text="Imtiyozlaringiz, jarima va qarz muddatlari, sizga ta'sir qiluvchi o'zgarishlar va bir bosishda ariza." onClick={toCabinet} />
            <PathCard icon="👤" title="Anonim foydalanish" cta="Ro'yxatsiz boshlash"
              text="Savol, SMS tahlili va feyk tekshiruvi. Ism, telefon yoki PINFL so'ralmaydi." onClick={() => go("/anonim")} />
          </motion.div>
          <p className="muted mt-5 text-sm">
            Telegram'da ham: <a className="link" href="https://t.me/Huquqim_official_bot" target="_blank" rel="noreferrer">@Huquqim_official_bot</a> — matn yoki ovoz bilan.
          </p>
        </div>
        <TranslateDemo />
      </section>

      <HowItWorks />

      <section id="savol" aria-labelledby="ask-h" className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)] lg:gap-10">
        <Reveal>
          <h2 id="ask-h" className="h1">Savol bering</h2>
          <p className="secondary mt-2 measure">Vaziyatingizni o'z so'zingiz bilan yozing, jarima SMS'ini yoki shubhali postni joylang. Ro'yxatdan o'tish shart emas.</p>
        </Reveal>
        <Reveal delay={0.05}>
          <Card padding="lg"><AskPanel /></Card>
        </Reveal>
      </section>

      <Evidence />

      <Reveal as="section" className="flex flex-wrap items-center gap-3">
        <UnverifiedBadge>DEMO</UnverifiedBadge>
        <p className="muted measure text-sm">Huquqiy mazmun huquqshunos tomonidan to'liq tekshirilmagan. OneID — simulyatsiya (DEMO ID), barcha shaxslar o'ylab topilgan. AI tushuntiradi; rasmiy manba — qonun hujjatining o'zi.</p>
      </Reveal>
    </div>
  );
}
