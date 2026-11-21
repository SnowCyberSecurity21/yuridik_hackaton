// Sayt: bosh sahifa, anonim sahifa, kirish/ro'yxat, kabinet. Kabinet ko'rinishi Mini App'da ham ishlatiladi.
import { Suspense, lazy, useCallback, useEffect, useState } from "react";
import { api, localStorageSafe } from "./api.js";
import { APP_NAME } from "./config.js";
import { AnimatePresence, motion } from "motion/react";
import { LogIn, LogOut, Moon, Sun, UserRound } from "lucide-react";
import {
  Alert, Badge, Button, Card, EmptyState, Logo, Sheet, SkeletonCard, SkeletonList, TabPanel, Tabs, TrustBadge,
  toast, useScrolled, useTelegramBackButton, useTelegramMainButton,
} from "./ui/index.js";
import { AppealForm, RightsCategories } from "./features/index.js";

const Dashboard = lazy(() => import("./Dashboard.jsx"));
const Edu = lazy(() => import("./Edu.jsx"));

export function go(path) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

function copy(text) {
  try { navigator.clipboard?.writeText(text); } catch { /* ruxsat yo'q */ }
}
const dmy = (iso) => (iso ? String(iso).slice(0, 10).split("-").reverse().join(".") : "—");
const money = (n) => (n == null ? "—" : `${new Intl.NumberFormat("ru-RU").format(n)} so'm`);

// ---------------------------------------------------------------- umumiy

export function useTheme() {
  const [theme, setTheme] = useState(() => (localStorageSafe("theme") === "light" ? "light" : ""));
  useEffect(() => {
    if (theme) document.documentElement.setAttribute("data-theme", theme);
    else document.documentElement.removeAttribute("data-theme");
    localStorageSafe("theme", theme);
  }, [theme]);
  return [theme, setTheme];
}

export function ThemeToggle() {
  const [theme, setTheme] = useTheme();
  // Standart — qorong'i. Faqat ikki holat: qorong'i ↔ yorug'.
  const light = theme === "light";
  const label = light ? "Yorug' rejim" : "Qorong'i rejim";
  return (
    <button className="btn btn-icon" onClick={() => setTheme(light ? "" : "light")} aria-label={`${label}. Almashtirish`} title={label}>
      {light ? <Sun size={20} strokeWidth={2} /> : <Moon size={20} strokeWidth={2} />}
    </button>
  );
}

export function Header({ me, wide = false }) {
  const scrolled = useScrolled();
  return (
    <header className="site-header" data-scrolled={scrolled}>
      <div className={`mx-auto flex h-[var(--header-h)] items-center gap-2 px-4 ${wide ? "max-w-6xl" : "max-w-3xl"}`}>
        <span className="brand">
          <Logo height={36} href="/" onClick={(e) => { e.preventDefault(); go("/"); }} />
        </span>
        <nav className="ml-auto flex items-center gap-1" aria-label="Asosiy">
          {me?.logged_in
            ? <Button size="sm" icon={UserRound} onClick={() => go("/kabinet")}>Kabinet</Button>
            : <Button size="sm" icon={LogIn} onClick={() => go("/kirish")}>Kirish</Button>}
          <ThemeToggle />
        </nav>
      </div>
    </header>
  );
}

export function Footer({ wide = false }) {
  return (
    <footer className="border-t" style={{ borderColor: "var(--border)" }}>
      <div className={`muted mx-auto flex flex-wrap items-center gap-x-4 gap-y-1 px-4 py-6 text-xs ${wide ? "max-w-6xl" : "max-w-3xl"}`}>
        <Logo height={24} />
        <span>Demo versiya. AI tushuntiradi; rasmiy manba — qonun hujjatining o'zi.</span>
        <a className="underline sm:ml-auto" href="https://lex.uz" target="_blank" rel="noreferrer">Manbalar: lex.uz</a>
      </div>
    </footer>
  );
}

function Err({ error }) {
  if (!error) return null;
  return <Alert tone="danger" className="my-2">{error}</Alert>;
}

function Source({ law, article }) {
  if (!law) return null;
  return (
    <p className="source mt-3">
      <span aria-hidden>📚 </span>
      <a className="law" style={{ color: "inherit" }} href={law.url} target="_blank" rel="noreferrer">«{law.title}»</a>
      {law.number ? `, ${law.number}` : <> <Badge tone="warn">raqami: tekshirilishi kerak</Badge></>}
      {` (${law.date_text})`}{article ? `, ${article}` : ""}
      <span className="muted"> · tekshirildi {dmy(law.retrieved_at)}</span>
    </p>
  );
}

const KIND_ICON = { duty: "📌", info: "ℹ️" };

function RightItem({ i }) {
  return (
    <li className="card p-4 sm:p-5">
      <div className="flex gap-3">
        <span aria-hidden className="mt-0.5">{KIND_ICON[i.kind] || "✅"}</span>
        <div className="min-w-0">
          <div className="font-semibold leading-snug">{i.title}</div>
          <p className="secondary mt-1 text-[0.95rem] leading-relaxed">{i.plain}</p>
          <Source law={i.law} article={i.article} />
        </div>
      </div>
    </li>
  );
}

export function RightsView({ status, situations }) {
  if (!status) return null;
  return (
    <div className="space-y-8">
      <section>
        <h3 className="h2"><span aria-hidden>{status.icon}</span> {status.title}</h3>
        <p className="secondary mt-1 measure">{status.intro}</p>
        <h4 className="mt-5 mb-2 text-sm font-semibold">Huquqlar va imtiyozlar</h4>
        <ul className="space-y-2.5">{status.rights.map((i) => <RightItem key={i.id} i={i} />)}</ul>
        {status.duties.length > 0 && (<>
          <h4 className="mt-6 mb-2 text-sm font-semibold">Majburiyatlar</h4>
          <ul className="space-y-2.5">{status.duties.map((i) => <RightItem key={i.id} i={i} />)}</ul>
        </>)}
      </section>
      {(situations || []).map((s) => (
        <section key={s.id}>
          <h3 className="h3 mb-2"><span aria-hidden>{s.icon}</span> {s.title}</h3>
          <ul className="space-y-2.5">{[...s.rights, ...s.duties].map((i) => <RightItem key={i.id} i={i} />)}</ul>
        </section>
      ))}
      <p className="muted text-xs">Sodda izoh — huquqiy xulosa emas. Rasmiy manba — qonun hujjatining o'zi.</p>
    </div>
  );
}

export function LawsList({ laws }) {
  if (!laws?.length) return <EmptyState icon="📚" title="Hozircha qonunlar yo'q">Maqom yoki holatni tanlang — tegishli hujjatlar shu yerda chiqadi.</EmptyState>;
  return (
    <ul className="space-y-2.5">
      {laws.map((l) => (
        <li key={l.id} className="card p-4 sm:p-5">
          <div className="law text-[1.05rem] font-semibold leading-snug" style={{ color: "var(--text-primary)" }}>{l.title}</div>
          <div className="muted mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs">
            {l.number ? <span className="tabnum">{l.number}</span> : <Badge tone="warn">raqami: tekshirilishi kerak</Badge>}
            <span>{l.date_text}</span>
          </div>
          <p className="secondary mt-2 text-[0.95rem] leading-relaxed">{l.plain}</p>
          <div className="source mt-3">📚 <a href={l.url} target="_blank" rel="noreferrer">{l.url.replace("https://", "")}</a> · tekshirildi {dmy(l.retrieved_at)}</div>
        </li>
      ))}
    </ul>
  );
}

// ---------------------------------------------------------------- savol / SMS / feyk

const ASK_MODES = [
  { id: "question", icon: "❓", label: "Savol", ph: "Masalan: Bolamga nafaqa nega berilmadi?", hint: "Vaziyatingizni o'z so'zingiz bilan yozing." },
  { id: "sms", icon: "🧾", label: "SMS tahlili", ph: "Jarima yoki MIB SMS matnini shu yerga joylang", hint: "Ism va tug'ilgan sana avtomatik olib tashlanadi." },
  { id: "factcheck", icon: "🕵️", label: "Feyk tekshiruvi", ph: "Shubhali post matnini joylang", hint: "Manba topilmasa — «Tasdiqlanmagan», taxmin qilinmaydi." },
];

const VERDICT_TONE = { togri: "ok", notogri: "danger", qisman: "warn" };

export function AskPanel({ legalStatus, headers = {}, suggestions = [] }) {
  const [mode, setMode] = useState("question");
  const [text, setText] = useState("");
  const [res, setRes] = useState(null);
  const [busy, setBusy] = useState(false);
  const [appeal, setAppeal] = useState(null);
  const [appealBusy, setAppealBusy] = useState(false);
  const m = ASK_MODES.find((x) => x.id === mode);
  const send = async (q, forceMode) => {
    const body = (typeof q === "string" ? q : text).trim();
    if (!body) return;
    setBusy(true); setRes(null);
    const r = await api.post("/api/ask", { text: body, mode: forceMode || mode, channel: "web", legal_status: legalStatus || null }, { headers });
    setBusy(false); setRes(r);
  };
  const ask = (q) => { setMode("question"); setText(q); send(q, "question"); };
  const disagree = async () => {
    setAppealBusy(true);
    const r = await api.post("/api/appeal", { card_id: res.card_id, event_id: res.event_id || null, lang: "uz" });
    setAppealBusy(false);
    setAppeal(r?.error ? { title: "Ariza", error: r.error } : { title: res.title, ...r });
  };
  return (
    <div className="space-y-4">
      <Tabs ariaLabel="So'rov turi" value={mode} onChange={(id) => { setMode(id); setRes(null); }}
        items={ASK_MODES.map(({ id, icon, label }) => ({ id, icon, label }))} />
      {mode === "question" && suggestions.length > 0 && (
        <div>
          <div className="muted mb-2 text-xs font-semibold">Tayyor savollar</div>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((s) => (
              <button key={s.q} className="chip" disabled={busy} onClick={() => ask(s.q)}>
                <span>{s.q} {s.article ? <span className="muted text-xs">({s.article})</span> : null}</span>
              </button>
            ))}
          </div>
        </div>
      )}
      <div>
        <label className="sr-only" htmlFor="ask">{m.label}</label>
        <textarea id="ask" rows={mode === "question" ? 3 : 5} className="w-full" placeholder={m.ph} value={text}
          onChange={(e) => setText(e.target.value)} maxLength={4000}
          onKeyDown={(e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) send(); }} />
        <div className="mt-1 flex items-center gap-2">
          <span className="muted text-xs">{m.hint}</span>
          <span className="muted tabnum ml-auto text-xs">{text.length > 3000 ? `${text.length}/4000` : ""}</span>
        </div>
      </div>
      <Button variant="primary" size="lg" block loading={busy} disabled={!text.trim()} onClick={() => send()}>
        {busy ? "Tekshirilmoqda…" : mode === "factcheck" ? "Tekshirish" : mode === "sms" ? "Tahlil qilish" : "Javob olish"}
      </Button>
      <AnimatePresence mode="wait" initial={false}>
        {busy && (
          <motion.div key="wait" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <SkeletonCard lines={4} />
          </motion.div>
        )}
        {!busy && res?.error && (
          <motion.div key="err" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <Alert tone="danger">{res.error}</Alert>
          </motion.div>
        )}
        {!busy && res && !res.error && (
          <motion.div key="res" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.23, 1, 0.32, 1] }}>
            <Card padding="md" style={{ boxShadow: "inset 3px 0 0 var(--feruza), var(--shadow-1)" }}>
              {res.verdict && <div className="mb-3"><Badge tone={VERDICT_TONE[res.verdict] || "warn"} className="text-sm">{res.verdict_label || res.verdict}</Badge></div>}
              <div className="measure whitespace-pre-wrap text-[1.0625rem] leading-relaxed">{res.text}</div>
              {res.card_id && (
                <div className="mt-4 flex flex-wrap gap-2 border-t pt-4" style={{ borderColor: "var(--border)" }}>
                  <Button loading={appealBusy} onClick={disagree} icon="❌">Baribir rozi emasman — ariza tuzish</Button>
                </div>
              )}
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
      <AppealSheet appeal={appeal} onClose={() => setAppeal(null)} />
    </div>
  );
}

// ---------------------------------------------------------------- imtiyoz, majburiyat, ariza

/** Murojaat shakli (features/AppealForm) — Sheet ichida. open: { cardId?, title? } | null */
export function AppealFormSheet({ open, onClose }) {
  return (
    <Sheet open={!!open} onClose={onClose} title={open?.title ? `📝 ${open.title}` : "📝 Murojaat tayyorlash"}
      description="Rekvizitlarni to'ldiring — tayyor matnni nusxalang yoki PDF qiling.">
      {open && <AppealForm cardId={open.cardId || undefined} onDone={(r) => { if (!r?.error) toast("Murojaat matni tayyor", { tone: "ok" }); }} />}
    </Sheet>
  );
}
export const appealFromItem = (item) => ({ cardId: item?.card_id || item?.card || item?.appeal_card_id || null, title: item?.title });


export function AppealSheet({ appeal, onClose }) {
  const [copied, setCopied] = useState(false);
  useEffect(() => { setCopied(false); }, [appeal]);
  const doCopy = () => { copy(appeal.text); setCopied(true); toast("Ariza matni nusxalandi", { tone: "ok" }); };
  useTelegramMainButton({ text: "📋 Nusxa olish", onClick: doCopy, active: !!appeal && !appeal.error });
  return (
    <Sheet open={!!appeal} onClose={onClose} title={appeal ? `📝 ${appeal.title}` : ""} description={appeal?.hint}
      footer={appeal && !appeal.error ? (
        <>
          <Button variant="primary" onClick={doCopy} icon={copied ? "✅" : "📋"}>{copied ? "Nusxa olindi" : "Nusxa olish"}</Button>
          {(appeal.submit_channels || []).map((c) => <Button key={c.url + c.name} as="a" href={c.url} target="_blank" rel="noreferrer" icon="↗">{c.name}</Button>)}
        </>
      ) : null}>
      {appeal?.error ? <Alert tone="danger">{appeal.error}</Alert> : appeal && (
        <>
          {appeal.to_check?.length > 0 && (
            <Alert tone="warn" title="Tekshirilishi kerak" className="mb-3">{appeal.to_check.join("; ")}</Alert>
          )}
          <div className="card card-inset p-4 sm:p-5">
            <pre className="law whitespace-pre-wrap text-[0.95rem]" style={{ color: "var(--text-primary)", margin: 0 }}>{appeal.text}</pre>
          </div>
        </>
      )}
    </Sheet>
  );
}

function Benefit({ b, onAppeal, busy }) {
  return (
    <article className="card p-4 sm:p-5">
      <div className="flex items-start gap-3">
        <span className="grid h-11 w-11 flex-none place-items-center rounded-[var(--radius-md)] text-2xl" style={{ background: "var(--primary-soft)" }} aria-hidden>{b.icon}</span>
        <div className="min-w-0 flex-1">
          <h3 className="h3">{b.title}</h3>
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            <Badge tone="ok">✓ {b.status_text}</Badge>
            {b.verified ? <Badge tone="verified">✅ Huquqshunos tasdiqlagan</Badge>
              : b.source_checked ? <Badge tone="source">{b.badge}</Badge>
              : <Badge tone="unverified">TEKSHIRILMAGAN (demo)</Badge>}
          </div>
        </div>
      </div>
      <p className="secondary mt-3 text-[0.95rem] leading-relaxed">{b.summary}</p>
      {b.status_note && <Alert tone="warn" className="mt-3">{b.status_note}</Alert>}
      {(b.met.length > 0 || b.to_check.length > 0) && (
        <ul className="mt-3 space-y-1.5 text-sm">
          {b.met.map((m) => (
            <li key={m} className="flex gap-2"><span aria-hidden style={{ color: "var(--ok-ink)" }}>✓</span><span>{m}</span></li>
          ))}
          {b.to_check.map((m) => (
            <li key={m} className="flex gap-2"><span aria-hidden className="muted">❔</span><span className="secondary">{m} <span className="muted">— tekshirilishi kerak</span></span></li>
          ))}
        </ul>
      )}
      <div className="source law mt-3">{b.source_line}</div>
      <Button variant="primary" block className="mt-4" loading={busy} icon="📝" onClick={() => onAppeal(b)}>
        {busy ? "Tayyorlanmoqda…" : `${b.appeal_label} — tayyor ariza`}
      </Button>
    </article>
  );
}

function Obligation({ o, onRemind, note }) {
  const disc = o.discount_deadline != null;
  const left = disc ? o.discount_days_left : o.days_left;
  const tone = left == null ? "info" : left <= 7 ? "danger" : left <= 14 ? "warn" : "info";
  return (
    <article className="card p-4 sm:p-5" style={left != null && left <= 7 ? { boxShadow: "inset 3px 0 0 var(--danger), var(--shadow-1)" } : undefined}>
      <div className="flex items-start gap-3">
        <div className="min-w-0 flex-1">
          <h3 className="h3">{o.title}</h3>
          <div className="muted mt-0.5 text-xs">{o.issuer}{o.invoice ? ` · invoys ${o.invoice}` : ""}</div>
        </div>
        <div className="tabnum text-right text-lg font-bold leading-tight">{o.amount_text}</div>
      </div>
      {disc && (
        <div className="mt-3 rounded-[var(--radius-md)] p-3 text-sm" style={{ background: "var(--ok-bg)", color: "var(--ok-ink)" }}>
          💸 Chegirma bilan <b className="tabnum">{money(o.discount_amount)}</b> ({o.discount_pct}%) — <b className="tabnum">{dmy(o.discount_deadline)}</b> gacha
        </div>
      )}
      {!disc && o.deadline && <div className="mt-3 text-sm">📅 Muddat: <b className="tabnum">{dmy(o.deadline)}</b></div>}
      {o.warning && <Alert tone="warn" className="mt-3">{o.warning}</Alert>}
      <div className="mt-3 flex flex-wrap items-center gap-2">
        {left != null && <Badge tone={tone} className="tabnum">⏳ {left} kun qoldi</Badge>}
        {o.reminder_date && <Button size="sm" icon="⏰" onClick={() => onRemind(o)}>{dmy(o.reminder_date)} kuni eslatish</Button>}
      </div>
      {note && <div className="muted mt-2 text-xs" role="status">{note}</div>}
    </article>
  );
}

// ---------------------------------------------------------------- anonim

function useRightsMeta() {
  const [meta, setMeta] = useState(null);
  useEffect(() => { api.get("/api/rights/meta").then((r) => !r?.error && setMeta(r)); }, []);
  return meta;
}

export function AnonView({ headers = {}, compact = false }) {
  const meta = useRightsMeta();
  // Tanlov faqat shu brauzerda (localStorage), serverga saqlanmaydi
  const [status, setStatus] = useState(() => localStorageSafe("anonStatus") || "");
  const [sits, setSits] = useState(() => (localStorageSafe("anonSituations") || "").split(",").filter(Boolean));
  const [tab, setTab] = useState("rights");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [formOpen, setFormOpen] = useState(null);
  useEffect(() => { localStorageSafe("anonStatus", status); localStorageSafe("anonSituations", sits.join(",")); }, [status, sits]);
  useEffect(() => {
    if (!status) return;
    setLoading(true);
    api.get(`/api/rights?status=${encodeURIComponent(status)}&situations=${encodeURIComponent(sits.join(","))}`)
      .then((r) => { if (!r?.error) setData(r); setLoading(false); });
  }, [status, sits]);
  const toggle = (id) => setSits((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]));
  const tabs = [
    { id: "mine", icon: "🧩", label: "Mening huquqlarim" },
    { id: "rights", icon: "⚖️", label: "Umumiy huquqlar" },
    { id: "laws", icon: "📚", label: "Siz uchun qonunlar", count: data?.laws?.length || undefined },
    { id: "ask", icon: "❓", label: "Savol · SMS · Feyk" },
  ];

  return (
    <div className="space-y-6">
      {!compact && (
        <div className="pt-2 sm:pt-4">
          <h1 className="h1">Anonim rejim</h1>
          <p className="secondary mt-2 measure">Ro'yxatsiz ishlaydi. Shaxsiy ma'lumot so'ralmaydi va saqlanmaydi — tanlovingiz faqat shu qurilmada qoladi.</p>
        </div>
      )}
      <Card padding="md">
        <fieldset>
          <legend className="font-semibold">Huquqiy maqomingiz <span className="muted text-sm font-normal">(ixtiyoriy)</span></legend>
          <div className="mt-2.5 flex flex-wrap gap-2">
            {!meta && [1, 2, 3, 4].map((i) => <span key={i} className="skeleton inline-block h-10 w-32 rounded-full" />)}
            {(meta?.statuses || []).map((s) => <button key={s.id} className="chip" aria-pressed={status === s.id} onClick={() => setStatus(s.id)}><span aria-hidden>{s.icon}</span> {s.title}</button>)}
          </div>
        </fieldset>
        <fieldset className="mt-5">
          <legend className="font-semibold">Holatingiz <span className="muted text-sm font-normal">(bir nechtasini tanlash mumkin)</span></legend>
          <div className="mt-2.5 flex flex-wrap gap-2">
            {(meta?.situations || []).map((s) => <button key={s.id} className="chip" aria-pressed={sits.includes(s.id)} onClick={() => toggle(s.id)}><span aria-hidden>{s.icon}</span> {s.title}</button>)}
          </div>
        </fieldset>
      </Card>
      <Tabs ariaLabel="Anonim bo'limlar" value={tab} onChange={setTab} items={tabs} />
      <TabPanel id={tab} key={tab}>
        {tab === "ask" && <Card padding="lg"><AskPanel legalStatus={status} headers={headers} suggestions={data?.status?.suggested_questions || []} /></Card>}
        {tab === "mine" && <RightsCategories initial={sits[0]} onAppeal={(it) => setFormOpen(appealFromItem(it))} />}
        {tab !== "ask" && tab !== "mine" && !status && (
          <EmptyState icon="🧭" title="Avval maqomni tanlang">
            Yuqoridan maqomingizni belgilang (yoki «Bilmayman») — huquqlar va tegishli qonunlar shu yerda chiqadi.
          </EmptyState>
        )}
        {tab !== "ask" && tab !== "mine" && status && (loading && !data ? <SkeletonList count={3} /> : (
          <div style={{ opacity: loading ? 0.6 : 1, transition: "opacity var(--dur-base) ease" }}>
            {tab === "rights" && data && <RightsView status={data.status} situations={data.situations} />}
            {tab === "laws" && data && <LawsList laws={data.laws} />}
          </div>
        ))}
      </TabPanel>
      <AppealFormSheet open={formOpen} onClose={() => setFormOpen(null)} />
    </div>
  );
}

// ---------------------------------------------------------------- kirish / ro'yxat

export function AuthPage({ onAuthed }) {
  const params = new URLSearchParams(window.location.search);
  const next = params.get("next");
  const [mode, setMode] = useState("register");
  const [username, setU] = useState("");
  const [password, setP] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const submit = async (e) => {
    e.preventDefault();
    setBusy(true); setError(null);
    const r = await api.post(`/api/auth/${mode}`, { username, password });
    setBusy(false);
    if (r?.error) { setError(r.error); return; }
    onAuthed(r);
    if (next === "oneid" && !r.verified) window.location.href = "/api/oneid/start";
    else go("/kabinet");
  };
  const steps = [
    ["Hisob oching", `${APP_NAME} hisobi: faqat login va parol. Ism, PINFL yoki telefon so'ralmaydi.`],
    ["OneID bilan tasdiqlang", "DEMO ID sahifasida rozilik berasiz. Ma'lumot faqat kerak bo'lganda so'raladi."],
    ["Kabinetingiz tayyor", "Imtiyozlar, muddatli majburiyatlar va sizga taalluqli o'zgarishlar."],
  ];
  return (
    <div className="grid grid-cols-1 gap-8 pt-2 sm:pt-6 md:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)] md:gap-10">
      <div className="md:pt-2">
        <h1 className="h1">{mode === "register" ? "Hisob ochish" : "Hisobga kirish"}</h1>
        <p className="secondary mt-2">Shaxsiy imtiyozlar va muddatlarni ko'rish uchun uch qadam.</p>
        <ol className="mt-6 space-y-4">
          {steps.map(([t, d], i) => (
            <li key={t} className="flex gap-3">
              <span className="tabnum grid h-7 w-7 flex-none place-items-center rounded-full text-sm font-semibold"
                style={i === 0 ? { background: "var(--primary)", color: "var(--text-on-primary)" } : { background: "var(--surface-2)", color: "var(--text-secondary)" }}>{i + 1}</span>
              <div>
                <div className="font-semibold leading-snug">{t}</div>
                <p className="secondary mt-0.5 text-sm">{d}</p>
              </div>
            </li>
          ))}
        </ol>
      </div>
      <div>
        <Card padding="lg">
          <Tabs ariaLabel="Kirish turi" value={mode} onChange={(id) => { setMode(id); setError(null); }}
            items={[{ id: "register", label: "Ro'yxatdan o'tish" }, { id: "login", label: "Kirish" }]} />
          <form className="mt-5 space-y-4" onSubmit={submit} noValidate={false}>
            <div>
              <label className="mb-1.5 block text-sm font-medium" htmlFor="u">Login</label>
              <input id="u" className="w-full" autoComplete="username" autoCapitalize="none" spellCheck={false}
                value={username} onChange={(e) => setU(e.target.value)} required minLength={3} maxLength={30} placeholder="masalan: malika94" />
            </div>
            <div>
              <div className="mb-1.5 flex items-center">
                <label className="text-sm font-medium" htmlFor="p">Parol</label>
                <button type="button" className="btn btn-ghost btn-sm ml-auto -mr-2" onClick={() => setShowPw((v) => !v)}
                  aria-pressed={showPw} aria-controls="p">{showPw ? "Yashirish" : "Ko'rsatish"}</button>
              </div>
              <input id="p" className="w-full" type={showPw ? "text" : "password"} autoComplete={mode === "register" ? "new-password" : "current-password"}
                value={password} onChange={(e) => setP(e.target.value)} required minLength={8} maxLength={128} placeholder="kamida 8 belgi" />
            </div>
            <AnimatePresence initial={false}>
              {error && (
                <motion.div initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                  <Alert tone="danger">{error}</Alert>
                </motion.div>
              )}
            </AnimatePresence>
            <Button type="submit" variant="primary" size="lg" block loading={busy}>
              {mode === "register" ? "Hisob ochish" : "Kirish"}
            </Button>
          </form>
        </Card>
        <p className="muted mt-3 text-xs">Parol xeshlangan holda saqlanadi. Hisobda F.I.Sh., PINFL yoki telefon saqlanmaydi.</p>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------- kabinet

function TelegramPanel({ linked, onChange }) {
  const [link, setLink] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const make = async () => {
    setBusy(true);
    const r = await api.post("/api/me/telegram/link", {});
    setBusy(false);
    if (r?.error) setError(r.error); else setLink(r);
  };
  const unlink = async () => { setBusy(true); await api.post("/api/me/telegram/unlink", {}); setBusy(false); setLink(null); toast("Telegram uzildi"); onChange?.(); };
  return (
    <Card>
      <h3 className="h3">📲 Telegram bot</h3>
      {linked ? (
        <>
          <p className="secondary mt-1 text-sm">Hisobingiz @Huquqim_official_bot'ga ulangan: eslatma va o'zgarishlar botga keladi.</p>
          <Button className="mt-4" loading={busy} onClick={unlink}>Uzish</Button>
        </>
      ) : (
        <>
          <p className="secondary mt-1 text-sm">Bir martalik havola 10 daqiqa amal qiladi. Botda «Start» ni bosing.</p>
          {link ? (
            <Button as="a" variant="primary" block className="mt-4" href={link.url} target="_blank" rel="noreferrer" icon="↗">Telegram'da ochish va ulash</Button>
          ) : (
            <Button variant="primary" block className="mt-4" loading={busy} onClick={make}>Telegram'ni ulash</Button>
          )}
          {link && <Button variant="ghost" block className="mt-2" onClick={() => onChange?.()}>Uladim — yangilash</Button>}
        </>
      )}
      <Err error={error} />
    </Card>
  );
}

function ConsentPanel({ me, onRevoked }) {
  const [busy, setBusy] = useState(false);
  const [ask, setAsk] = useState(false);
  const revoke = async () => {
    setBusy(true);
    await api.post("/api/oneid/revoke", {});
    setBusy(false);
    setAsk(false);
    toast("Rozilik bekor qilindi");
    onRevoked();
  };
  return (
    <Card>
      <h3 className="h3">🔐 Rozilik (OneID — DEMO)</h3>
      <p className="secondary mt-1 text-sm">Berilgan: <span className="tabnum">{dmy(me?.consent_at)}</span>. {APP_NAME} quyidagilarni kerak bo'lganda so'raydi va bazada saqlamaydi:</p>
      <ul className="secondary mt-2 list-disc space-y-0.5 pl-5 text-sm">{(me?.consent_scope || []).map((s) => <li key={s}>{s}</li>)}</ul>
      <Button className="mt-4" onClick={() => setAsk(true)}>Rozilikni bekor qilish</Button>
      <Sheet open={ask} onClose={() => setAsk(false)} title="Rozilikni bekor qilasizmi?"
        description="OneID (demo) bilan bog'lanish uziladi. Shaxsiy bo'limlar yopiladi, keyin qayta tasdiqlash mumkin."
        footer={<>
          <Button variant="danger" loading={busy} onClick={revoke}>Ha, bekor qilish</Button>
          <Button variant="ghost" onClick={() => setAsk(false)}>Qoldirish</Button>
        </>}>
        <p className="secondary text-sm">Saqlangan rozilik yozuvi va profil bog'lanishi o'chiriladi.</p>
      </Sheet>
    </Card>
  );
}

const SECTIONS = [
  ["benefits", "Imtiyozlarim", "🎁"], ["rights", "Huquqlarim", "⚖️"], ["obligations", "Majburiyatlar", "📅"],
  ["laws", "Qonunlar", "📚"], ["changes", "O'zgarishlar", "🔔"], ["ask", "Savol · SMS · Feyk", "❓"], ["account", "Hisob", "⚙️"],
];

function CabinetSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-[17rem_minmax(0,1fr)]" role="status" aria-label="Yuklanmoqda">
      <div className="space-y-3"><SkeletonCard lines={2} /></div>
      <SkeletonList count={3} />
    </div>
  );
}

function ProfileCard({ p, v }) {
  return (
    <Card padding="md">
      <div className="flex items-center gap-3">
        <span className="grid h-12 w-12 flex-none place-items-center rounded-full text-3xl" style={{ background: "var(--surface-2)" }} aria-hidden>{p.icon}</span>
        <div className="min-w-0">
          <div className="text-lg font-bold leading-tight">Salom, {p.first_name}!</div>
          <div className="secondary truncate text-sm">{p.persona}</div>
        </div>
      </div>
      <div className="mt-3 flex flex-wrap gap-1.5">
        <Badge tone="verified">✅ DEMO ID</Badge>
        <Badge tone="info">{p.status_title}</Badge>
        {v.situations.map((s) => <Badge key={s.id} tone="info">{s.icon} {s.title}</Badge>)}
        {v.roles.includes("gov") && <Badge tone="warn">🏛️ Davlat xodimi</Badge>}
      </div>
      <p className="muted mt-3 text-xs leading-relaxed">{p.full_name} · {p.document} · {p.region_name}<br />{v.source}</p>
    </Card>
  );
}

export function CabinetView({ me, headers = {}, onReload, inMiniApp = false }) {
  const [v, setV] = useState(null);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState(() => new URLSearchParams(window.location.search).get("tab") || "benefits");
  const [appeal, setAppeal] = useState(null);
  const [busyId, setBusyId] = useState(null);
  const [notes, setNotes] = useState({});
  const [reloading, setReloading] = useState(false);
  const [formOpen, setFormOpen] = useState(null);
  const load = useCallback(async () => {
    const r = await api.get("/api/me/cabinet", { headers });
    if (r?.error) setError(r.error); else setV(r);
  }, [headers]);
  useEffect(() => { load(); }, [load]);
  useTelegramBackButton(inMiniApp && !!v && tab !== "benefits", () => setTab("benefits"));

  if (error) return <Err error={error} />;
  if (!v) return inMiniApp ? <SkeletonList count={3} /> : <CabinetSkeleton />;
  const p = v.person;
  const sections = [...SECTIONS];
  if (!inMiniApp && v.roles.includes("student")) sections.push(["edu", "Ta'lim", "🎓"]);
  if (!inMiniApp && v.roles.includes("gov")) sections.push(["gov", "Davlat kabineti", "🏛️"]);
  if (inMiniApp) sections.splice(sections.findIndex((s) => s[0] === "account"), 1);
  const counts = { benefits: v.benefits.length, obligations: v.obligations.length, laws: v.laws.length, changes: v.changes.length };
  const items = sections.map(([id, label, icon]) => ({ id, label, icon, count: counts[id] || undefined }));
  const current = sections.find((s) => s[0] === tab) || sections[0];

  const makeAppeal = async (b) => {
    setBusyId(b.id);
    const r = await api.post("/api/me/appeal", { benefit_id: b.id }, { headers });
    setBusyId(null);
    setAppeal(r?.error ? { title: b.title, error: r.error } : r);
  };
  const remind = async (o) => {
    const r = await api.post("/api/me/remind", { obligation_id: o.id }, { headers });
    setNotes((n) => ({ ...n, [o.id]: r?.error ? `⚠️ ${r.error}` : r.text }));
    if (!r?.error) toast("Eslatma qo'yildi", { tone: "ok", icon: "⏰" });
  };
  const refresh = async () => { setReloading(true); await load(); setReloading(false); };

  const panel = (
    <TabPanel id={current[0]} key={current[0]}>
      {tab === "benefits" && (
        <section className="space-y-3">
          <div className="flex items-baseline gap-2">
            <h2 className="h2">Haqli bo'lishingiz mumkin</h2>
            <span className="muted tabnum">{v.benefits.length}</span>
          </div>
          {v.benefits.length === 0 && <EmptyState icon="🎁" title="Hozircha mos imtiyoz topilmadi">Holatingiz o'zgarsa yoki yangi imtiyoz qo'shilsa, shu yerda ko'rinadi.</EmptyState>}
          {v.benefits.map((b) => <Benefit key={b.id} b={b} onAppeal={makeAppeal} busy={busyId === b.id} />)}
          {v.not_eligible.length > 0 && (
            <details className="card card-inset p-4 text-sm">
              <summary className="secondary font-medium">Mos kelmagan imtiyozlar ({v.not_eligible.length})</summary>
              <ul className="secondary mt-2 space-y-1">{v.not_eligible.map((n) => <li key={n.id}>{n.title}: <span className="muted">{n.failed.join("; ")}</span></li>)}</ul>
            </details>
          )}
          <p className="muted text-xs">«Haqli bo'lishingiz mumkin» — yakuniy qarorni vakolatli organ qabul qiladi. {v.disclaimer}</p>
        </section>
      )}
      {tab === "rights" && (
        <div className="space-y-8">
          {v.situations.length > 0 && (
            <section className="space-y-3">
              <h2 className="h2">Mening huquqlarim</h2>
              <RightsCategories only={v.situations.map((s) => s.id)} onAppeal={(it) => setFormOpen(appealFromItem(it))} />
            </section>
          )}
          <RightsView status={v.rights.status} situations={v.rights.situations} />
        </div>
      )}
      {tab === "obligations" && (
        <section className="space-y-3">
          <h2 className="h2">Muddatli majburiyatlar</h2>
          {v.obligations.length === 0 && <EmptyState icon="✅" title="Muddatli majburiyat yo'q">Jarima yoki qarz paydo bo'lsa, muddati va chegirmasi bilan shu yerda ko'rasiz.</EmptyState>}
          {v.obligations.map((o) => <Obligation key={o.id} o={o} onRemind={remind} note={notes[o.id]} />)}
          {v.rights.status?.duties?.length > 0 && (<>
            <h3 className="h3 pt-4">Maqomingiz bo'yicha umumiy majburiyatlar</h3>
            <ul className="space-y-2.5">{v.rights.status.duties.map((i) => <RightItem key={i.id} i={i} />)}</ul>
          </>)}
        </section>
      )}
      {tab === "laws" && <section className="space-y-3"><h2 className="h2">Siz uchun qonunlar</h2><LawsList laws={v.laws} /></section>}
      {tab === "changes" && (
        <section className="space-y-3">
          <div className="flex items-center gap-2">
            <h2 className="h2">Sizga taalluqli o'zgarishlar</h2>
            <Button size="sm" variant="ghost" className="ml-auto" loading={reloading} onClick={refresh} icon="🔄">Yangilash</Button>
          </div>
          {v.changes.length === 0 ? (
            <EmptyState icon="🔔" title="Hozircha o'zgarish yo'q">Sizga taalluqli qonun o'zgarsa, shu yerda va Telegram'da xabar olasiz — nega aynan sizga ekani bilan.</EmptyState>
          ) : (
            <ol className="relative space-y-3 border-l pl-5" style={{ borderColor: "var(--border-strong)" }}>
              {v.changes.map((c) => (
                <li key={c.id} className="relative">
                  <span className="absolute top-5 -left-[1.6rem] h-2.5 w-2.5 rounded-full" style={{ background: "var(--primary)", boxShadow: "0 0 0 3px var(--bg)" }} aria-hidden />
                  <Card padding="md">
                    <div className="muted tabnum text-xs">{dmy(c.date)}</div>
                    <div className="mt-0.5 font-semibold leading-snug">{c.summary}</div>
                    <div className="secondary mt-1 text-sm">{c.reason}</div>
                  </Card>
                </li>
              ))}
            </ol>
          )}
        </section>
      )}
      {tab === "ask" && <Card padding="lg"><AskPanel legalStatus={p.status} headers={headers} suggestions={v.rights.status?.suggested_questions || []} /></Card>}
      {tab === "account" && (
        <section className="grid grid-cols-1 gap-3 md:grid-cols-2">
          <TelegramPanel linked={v.telegram_linked} onChange={load} />
          <ConsentPanel me={me} onRevoked={() => { onReload?.(); go("/kabinet"); }} />
        </section>
      )}
      {tab === "edu" && <Suspense fallback={<SkeletonList count={2} />}><Edu /></Suspense>}
      {tab === "gov" && (
        <Suspense fallback={<SkeletonList count={3} />}>
          <Alert tone="warn" className="mb-4">Simulyatsiya xabarlari FAQAT demo hisoblar va ularga ulangan Telegram chatlarga yuboriladi (cheklov bilan). Real foydalanuvchilarga ommaviy xabar yuborilmaydi.</Alert>
          <Dashboard apiBase="/api/cabinet/gov" />
        </Suspense>
      )}
    </TabPanel>
  );

  if (inMiniApp) {
    return (
      <div className="space-y-4">
        <ProfileCard p={p} v={v} />
        <div className="sticky top-0 z-10 -mx-4 px-4 py-2" style={{ background: "var(--bg)" }}>
          <Tabs ariaLabel="Kabinet bo'limlari" value={current[0]} onChange={setTab} items={items} />
        </div>
        {panel}
        <AppealSheet appeal={appeal} onClose={() => setAppeal(null)} />
        <AppealFormSheet open={formOpen} onClose={() => setFormOpen(null)} />
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-[17rem_minmax(0,1fr)] lg:gap-8">
      <aside className="space-y-4 lg:sticky lg:top-[calc(var(--header-h)+1rem)] lg:self-start">
        <ProfileCard p={p} v={v} />
        <nav aria-label="Kabinet bo'limlari" className="hidden lg:block">
          <Tabs orientation="vertical" ariaLabel="Kabinet bo'limlari" value={current[0]} onChange={setTab} items={items} idPrefix="cab-v" />
        </nav>
      </aside>
      <div className="min-w-0 space-y-4">
        <div className="sticky top-[calc(var(--header-h)-var(--header-collapse))] z-10 -mx-4 px-4 py-2 lg:hidden" style={{ background: "var(--bg)" }}>
          <Tabs ariaLabel="Kabinet bo'limlari" value={current[0]} onChange={setTab} items={items} idPrefix="cab-h" />
        </div>
        {panel}
      </div>
      <AppealSheet appeal={appeal} onClose={() => setAppeal(null)} />
      <AppealFormSheet open={formOpen} onClose={() => setFormOpen(null)} />
    </div>
  );
}

export function CabinetPage({ me, onReload }) {
  const flag = new URLSearchParams(window.location.search).get("oneid");
  useEffect(() => { if (me && !me.logged_in) go("/kirish"); }, [me]);
  useEffect(() => {
    if (flag === "ok") toast("OneID (demo) orqali tasdiqlandi", { tone: "ok" });
  }, [flag]);
  if (!me) return <CabinetSkeleton />;
  if (!me.logged_in) return null;
  const logout = async () => { await api.post("/api/auth/logout", {}); onReload(); go("/"); };
  return (
    <div className="space-y-6">
      {flag === "denied" && <Alert tone="warn">Rozilik berilmadi — hisob tasdiqlanmadi.</Alert>}
      {flag === "error" && <Alert tone="danger">Tasdiqlashda xato. Qayta urinib ko'ring.</Alert>}
      {me.verified ? <CabinetView me={me} onReload={onReload} /> : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.3fr)]">
          <Card padding="lg" className="lg:self-start">
            <div className="muted text-sm">Hisob: <b style={{ color: "var(--text-primary)" }}>{me.username}</b></div>
            <h1 className="h1 mt-2">Bir qadam qoldi: OneID bilan tasdiqlang</h1>
            <p className="secondary mt-2">Imtiyozlar, muddatli majburiyatlar va siz uchun qonunlar faqat tasdiqlangan hisobda ochiladi.</p>
            <Button as="a" variant="primary" size="lg" block className="mt-5" href="/api/oneid/start" icon="🪪">OneID orqali tasdiqlash (DEMO)</Button>
            <p className="muted mt-3 text-xs">Siz alohida DEMO ID sahifasiga o'tasiz. U yerda haqiqiy OneID login va parolingizni kiritmang.</p>
          </Card>
          <div>
            <h2 className="h2 mb-3">Hozircha anonim imkoniyatlar</h2>
            <AnonView compact />
          </div>
        </div>
      )}
      <div className="flex">
        <Button variant="ghost" onClick={logout} icon={LogOut}>Hisobdan chiqish</Button>
      </div>
    </div>
  );
}
