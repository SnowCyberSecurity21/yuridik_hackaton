// Bosh sahifa: hero (telefon maketida bot suhbati), 2 yo'l, lenta, «Qanday ishlaydi», savol bloki, dalillar.
import { useEffect, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import {
  ArrowRight, BellRing, FileText, IdCard, Lock, Mic, RotateCcw, ScanSearch, ShieldCheck, Smartphone, UserRound,
} from "lucide-react";
import { APP_NAME } from "./config.js";
import { AppealFormSheet, go } from "./Site.jsx";
import { AskBox } from "./features/index.js";
import { Card, CountUp, UnverifiedBadge } from "./ui/index.js";

const ease = [0.2, 0.7, 0.2, 1];

/* ------------------------------------------------------------------ telefon maketi */
// Namuna — aniq modda, summa yoki muddat keltirilmaydi.
function PhoneDemo() {
  const reduce = useReducedMotion();
  const [step, setStep] = useState(reduce ? 2 : 0);
  const [run, setRun] = useState(0);
  useEffect(() => {
    if (reduce) { setStep(2); return undefined; }
    setStep(0);
    const t1 = setTimeout(() => setStep(1), 900);
    const t2 = setTimeout(() => setStep(2), 2300);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, [run, reduce]);
  const pop = { initial: { opacity: 0, y: 10, scale: 0.97 }, animate: { opacity: 1, y: 0, scale: 1 }, transition: { duration: 0.35, ease } };

  return (
    <div className="relative mx-auto w-full max-w-[360px] py-6">
      <div className="float-chip" style={{ top: "14%", left: "-6%" }}><ShieldCheck /> Manba: lex.uz</div>
      <div className="float-chip" style={{ top: "46%", right: "-8%", animationDelay: "-2s" }}><Mic /> Ovoz bilan</div>
      <div className="float-chip" style={{ bottom: "12%", left: "-4%", animationDelay: "-4s" }}><FileText /> Tayyor ariza</div>
      <div className="phone" aria-label="Namuna: Telegram botdagi suhbat">
        <div className="phone-screen">
          <div className="phone-bar">
            <img src="/icon-192.png" width="32" height="32" alt="" className="rounded-full" />
            <div className="min-w-0">
              <div className="text-sm font-semibold leading-tight">{APP_NAME}</div>
              <div className="text-[11px] leading-tight" style={{ color: "#8c95a8" }}>{step === 1 ? "yozmoqda…" : "bot"}</div>
            </div>
          </div>
          <div className="phone-chat">
            <motion.div className="bubble bubble-me" {...pop}>Bolamga nafaqa nega berilmadi?</motion.div>
            <AnimatePresence mode="wait">
              {step === 1 && (
                <motion.div key="typing" className="bubble bubble-bot typing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <i /><i /><i />
                </motion.div>
              )}
              {step === 2 && (
                <motion.div key="answer" className="bubble bubble-bot" style={{ maxWidth: "94%", padding: 12 }} {...pop}>
                  <div className="text-[11px] font-semibold" style={{ color: "#8c95a8" }}>Qonunda</div>
                  <p className="law mt-1 text-[12px]" style={{ color: "#b8c0cf", lineHeight: 1.45 }}>
                    Ariza zarur hujjatlar ilova qilingan holda vakolatli organga taqdim etiladi…
                  </p>
                  <div className="my-2 h-px" style={{ background: "rgb(255 255 255 / .08)" }} />
                  <div className="text-[11px] font-semibold" style={{ color: "#ffa552" }}>Oddiy tilda</div>
                  <p className="mt-1 text-[13px] font-medium leading-snug">
                    Ariza yozasiz, hujjatlarni ilova qilasiz. <span className="plain-mark">Rad etilsa — keyingi qadam va tayyor ariza.</span>
                  </p>
                  <div className="mt-2.5 inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-semibold" style={{ background: "rgb(34 230 206 / .12)", color: "#22e6ce" }}>
                    <ShieldCheck size={13} strokeWidth={2.2} /> Manba: lex.uz
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            {step === 2 && (
              <motion.div className="mt-auto grid grid-cols-2 gap-1.5" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
                {["Audio", "Manba", "Tushundim", "Rozi emasman"].map((b) => (
                  <span key={b} className="rounded-lg py-1.5 text-center text-[11.5px]" style={{ background: "#232e42", color: "#d5dbe6" }}>{b}</span>
                ))}
              </motion.div>
            )}
          </div>
        </div>
      </div>
      <div className="mt-4 flex justify-center">
        <button type="button" className="btn btn-sm btn-ghost" onClick={() => setRun((r) => r + 1)}>
          <RotateCcw size={16} strokeWidth={2} /> Qayta ko'rsatish
        </button>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ kartochka-tugma */
function Tap({ icon: I, title, text, cta, primary, onClick }) {
  return (
    <button type="button" onClick={onClick} className={`tap ${primary ? "tap-primary" : ""}`}>
      <span className="ico"><I strokeWidth={2} /></span>
      <span className="mt-5 text-xl font-bold leading-snug">{title}</span>
      <span className="secondary mt-2 text-[0.95rem] leading-relaxed">{text}</span>
      <span className="mt-auto inline-flex items-center gap-2 pt-6 text-sm font-semibold">{cta} <ArrowRight className="tap-arrow" size={18} strokeWidth={2} /></span>
    </button>
  );
}

const STRIP = [
  [ShieldCheck, "Manba: lex.uz"], [Mic, "Ovoz bilan"], [FileText, "Tayyor ariza"], [Lock, "Ma'lumot saqlanmaydi"],
];

const PROBLEMS = [
  { n: 1, icon: FileText, problem: "Qonun tili murakkab", solution: "Oddiy til + asl matn", text: "Har javobda sodda tushuntirish, yonida qonunning asl matni va lex.uz havolasi.", to: "/anonim" },
  { n: 2, icon: BellRing, problem: "Yangi qonunlar kech bilinadi", solution: "Shaxsiy o'zgarish xabarlari", text: "Qonun o'zgarsa, faqat sizga taalluqli bo'lsa xabar keladi — nega aynan sizga ekani bilan.", to: "/kirish?next=oneid" },
  { n: 3, icon: Smartphone, problem: "Targ'ibot formati eskirgan", solution: "Kartochka, audio, ulashish", text: "Qisqa kartochka, ovozli javob va qarindoshingizga yuborish uchun bitta tugma.", to: "#savol" },
  { n: 4, icon: Mic, problem: "Chekka hududlarga yetib borish qiyin", solution: "Telegram, ovoz, kirill", text: "Yangi ilova shart emas: Telegram'da ovoz bilan so'rang, kirill yozuvida ham ishlaydi.", to: "https://t.me/Huquqim_official_bot" },
  { n: 5, icon: ScanSearch, problem: "Ijtimoiy tarmoqda yolg'on ma'lumot", solution: "Fakt-tekshiruv", text: "Shubhali postni yuboring: To'g'ri, Qisman, Noto'g'ri yoki Tasdiqlanmagan — manbasi bilan.", to: "/anonim" },
];

const STATS = [
  { value: 557254, label: "murojaat Xalq qabulxonalariga 2026-yilda", source: "Prezident Xalq qabulxonasi" },
  { value: 48778, label: "murojaat bolalar nafaqasi bo'yicha, o'tgan yilga nisbatan +38%", source: "Prezident Xalq qabulxonasi" },
  { value: 65.2, label: "murojaat shunchaki «huquqiy ma'lumot berish» bilan yopilgan", source: "Oliy ta'lim vazirligi, 2026 I chorak", pct: true },
];

function nav(to) {
  return (e) => {
    if (to.startsWith("http")) return;
    e.preventDefault();
    if (to.startsWith("#")) document.querySelector(to)?.scrollIntoView({ behavior: "smooth", block: "start" });
    else go(to);
  };
}

export default function Home({ me }) {
  const toCabinet = () => go(me?.logged_in ? "/kabinet" : "/kirish?next=oneid");
  const [formOpen, setFormOpen] = useState(null);
  const lines = ["Huquqingizni", "oddiy tilda", "biling"];
  return (
    <div className="space-y-20 sm:space-y-28">
      <section className="grid grid-cols-1 items-center gap-10 pt-6 sm:pt-12 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)] lg:gap-12">
        <div>
          <motion.span className="status-pill" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, ease }}>
            <span className="pulse-dot" aria-hidden /> Jonli demo · LexHackathon 2026
          </motion.span>
          <h1 className="hero-title mt-6">
            {lines.map((l, i) => (
              <motion.span key={l} className={`block l${i + 1}`} initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, ease, delay: 0.08 + i * 0.09 }}>{l}</motion.span>
            ))}
          </h1>
          <motion.p className="lead mt-6" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, ease, delay: 0.4 }}>
            Murojaatdan oldin vaziyatingizni sodda tushuntiramiz, har javobga rasmiy manba qo'yamiz va kerak bo'lsa tayyor ariza beramiz.
          </motion.p>
          <motion.div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, ease, delay: 0.5 }}>
            <Tap primary icon={IdCard} title="OneID bilan kirish" cta={me?.logged_in ? "Kabinetga o'tish" : "Hisob ochish"}
              text="Imtiyozlaringiz, jarima va qarz muddatlari, sizga taalluqli o'zgarishlar va bir bosishda ariza." onClick={toCabinet} />
            <Tap icon={UserRound} title="Anonim foydalanish" cta="Ro'yxatsiz boshlash"
              text="Savol, SMS tahlili va feyk tekshiruvi. Ism, telefon yoki PINFL so'ralmaydi." onClick={() => go("/anonim")} />
          </motion.div>
        </div>
        <motion.div className="overflow-x-clip lg:overflow-visible" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, ease, delay: 0.2 }}>
          <PhoneDemo />
        </motion.div>
      </section>

      <div className="strip">
        {STRIP.map(([I, t]) => (
          <div key={t}><span className="ico ico-sm"><I strokeWidth={2} /></span>{t}</div>
        ))}
      </div>

      <section aria-labelledby="how">
        <div className="reveal max-w-2xl">
          <h2 id="how" className="h1">Qanday ishlaydi</h2>
          <p className="secondary mt-3">Huquqiy targ'ibot trekining beshta muammosi va {APP_NAME} ularning har biriga qanday javob beradi.</p>
        </div>
        <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {PROBLEMS.map((p, i) => (
            <a key={p.n} href={p.to} onClick={nav(p.to)} target={p.to.startsWith("http") ? "_blank" : undefined} rel="noreferrer"
              className="tap reveal" style={{ "--d": `${i * 60}ms` }}>
              <span className="flex items-center gap-3">
                <span className="ico"><p.icon strokeWidth={2} /></span>
                <span className="muted text-sm font-semibold">{p.n}-muammo · {p.problem}</span>
              </span>
              <span className="mt-5 text-lg font-bold leading-snug">{p.solution}</span>
              <span className="secondary mt-2 text-[0.95rem] leading-relaxed">{p.text}</span>
              <span className="mt-auto pt-5"><ArrowRight className="tap-arrow" size={20} strokeWidth={2} style={{ color: "var(--primary-ink)" }} /></span>
            </a>
          ))}
        </div>
      </section>

      <section id="savol" aria-labelledby="ask-h" className="grid grid-cols-1 gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)] lg:gap-12">
        <div className="reveal">
          <h2 id="ask-h" className="h1">Savol bering</h2>
          <p className="secondary mt-3">Vaziyatingizni o'z so'zingiz bilan yozing. Ro'yxatdan o'tish shart emas.</p>
          <p className="muted mt-3 text-sm">Jarima SMS'i yoki shubhali post? <a className="link" href="/anonim" onClick={nav("/anonim")}>Anonim rejimda tekshiring</a>.</p>
        </div>
        <Card padding="lg" className="reveal" style={{ borderRadius: "var(--radius-xl)", backgroundImage: "var(--card-sheen)" }}>
          <AskBox onAppeal={(cardId) => setFormOpen({ cardId })} />
        </Card>
      </section>

      <section aria-labelledby="why">
        <div className="reveal max-w-2xl">
          <h2 id="why" className="h1">Nega murojaatdan oldin</h2>
          <p className="secondary mt-3">Ko'p murojaatlarga javob — oddiy tushuntirish. Uni fuqaro navbatsiz, darhol olishi mumkin.</p>
        </div>
        <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
          {STATS.map((s, i) => (
            <div key={s.label} className="card reveal p-6" style={{ "--d": `${i * 60}ms`, borderRadius: "var(--radius-xl)", backgroundImage: "var(--card-sheen)" }}>
              <div className="text-[2.4rem] font-extrabold leading-none tracking-tight">
                <CountUp value={s.value} format={s.pct ? (n) => String(n).replace(".", ",") : undefined} />{s.pct && <span style={{ color: "var(--primary)" }}>%</span>}
              </div>
              <p className="secondary mt-3 text-sm leading-snug">{s.label}</p>
              <p className="muted mt-3 text-xs">{s.source}</p>
            </div>
          ))}
        </div>
      </section>

      <AppealFormSheet open={formOpen} onClose={() => setFormOpen(null)} />

      <section className="reveal flex flex-wrap items-center gap-3">
        <UnverifiedBadge>DEMO</UnverifiedBadge>
        <p className="muted measure text-sm">Huquqiy mazmun huquqshunos tomonidan to'liq tekshirilmagan. OneID — simulyatsiya (DEMO ID), barcha shaxslar o'ylab topilgan. AI tushuntiradi; rasmiy manba — qonun hujjatining o'zi.</p>
      </section>
    </div>
  );
}
