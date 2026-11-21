// Sayt: bosh sahifa, anonim sahifa, kirish/ro'yxat, kabinet. Kabinet ko'rinishi Mini App'da ham ishlatiladi.
import { Suspense, lazy, useCallback, useEffect, useState } from "react";
import { api, localStorageSafe } from "./api.js";
import { APP_NAME } from "./config.js";

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
  const [theme, setTheme] = useState(() => localStorageSafe("theme") || "");
  useEffect(() => {
    if (theme) document.documentElement.setAttribute("data-theme", theme);
    else document.documentElement.removeAttribute("data-theme");
    localStorageSafe("theme", theme);
  }, [theme]);
  return [theme, setTheme];
}

export function ThemeToggle() {
  const [theme, setTheme] = useTheme();
  const next = theme === "" ? "light" : theme === "light" ? "dark" : "";
  const label = theme === "" ? "🖥️ Tizim" : theme === "light" ? "☀️ Yorug'" : "🌙 Qorong'i";
  return <button className="btn btn-ghost px-3" onClick={() => setTheme(next)} aria-label={`Mavzu: ${label}. Almashtirish`}>{label}</button>;
}

export function Header({ me }) {
  return (
    <header className="sticky top-0 z-20 border-b" style={{ background: "var(--bg)", borderColor: "var(--border)" }}>
      <div className="mx-auto flex max-w-3xl items-center gap-2 px-4 py-2">
        <a href="/" onClick={(e) => { e.preventDefault(); go("/"); }} className="flex items-center gap-2 no-underline">
          <span className="hero-mark" style={{ width: 32, height: 32, fontSize: 14 }}>H</span>
          <span className="text-lg font-bold">{APP_NAME}</span>
        </a>
        <div className="ml-auto flex items-center gap-1">
          {me?.logged_in
            ? <button className="btn btn-ghost px-3" onClick={() => go("/kabinet")}>{me.icon || "👤"} Kabinet</button>
            : <button className="btn btn-ghost px-3" onClick={() => go("/kirish")}>Kirish</button>}
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}

function Err({ error }) {
  if (!error) return null;
  return <div className="badge badge-crit my-2" style={{ whiteSpace: "normal" }} role="alert">⚠️ {error}</div>;
}

function Source({ law, article }) {
  if (!law) return null;
  return (
    <div className="source mt-1">
      📚 Manba: <a href={law.url} target="_blank" rel="noreferrer">«{law.title}»</a>
      {law.number ? `, ${law.number}` : <> <span className="badge badge-warn">raqami: tekshirilishi kerak</span></>}
      {` (${law.date_text})`}{article ? `, ${article}` : ""} · tekshirildi {dmy(law.retrieved_at)}
    </div>
  );
}

// ---------------------------------------------------------------- huquqlar va qonunlar

function RightItem({ i }) {
  return (
    <li className="card p-4">
      <div className="font-semibold leading-snug">{i.kind === "duty" ? "📌" : i.kind === "info" ? "ℹ️" : "✅"} {i.title}</div>
      <p className="secondary mt-1 text-sm">{i.plain}</p>
      <Source law={i.law} article={i.article} />
    </li>
  );
}

export function RightsView({ status, situations }) {
  if (!status) return null;
  return (
    <div className="space-y-5">
      <section>
        <h3 className="text-lg font-bold">{status.icon} {status.title}</h3>
        <p className="secondary mt-1 text-sm">{status.intro}</p>
        <h4 className="mt-3 mb-2 font-semibold">Huquqlar va imtiyozlar</h4>
        <ul className="space-y-2">{status.rights.map((i) => <RightItem key={i.id} i={i} />)}</ul>
        {status.duties.length > 0 && (<>
          <h4 className="mt-4 mb-2 font-semibold">Majburiyatlar</h4>
          <ul className="space-y-2">{status.duties.map((i) => <RightItem key={i.id} i={i} />)}</ul>
        </>)}
      </section>
      {(situations || []).map((s) => (
        <section key={s.id}>
          <h3 className="mb-2 font-bold">{s.icon} {s.title}</h3>
          <ul className="space-y-2">{[...s.rights, ...s.duties].map((i) => <RightItem key={i.id} i={i} />)}</ul>
        </section>
      ))}
      <p className="muted text-xs">Sodda izoh — huquqiy xulosa emas. Rasmiy manba — qonun hujjatining o'zi.</p>
    </div>
  );
}

export function LawsList({ laws }) {
  return (
    <ul className="space-y-2">
      {(laws || []).map((l) => (
        <li key={l.id} className="card p-4">
          <div className="font-semibold leading-snug">{l.title}</div>
          <div className="muted mt-0.5 text-xs">
            {l.number ? l.number : <span className="badge badge-warn">raqami: tekshirilishi kerak</span>} · {l.date_text}
          </div>
          <p className="secondary mt-1 text-sm">{l.plain}</p>
          <div className="source mt-1">📚 Manba: <a href={l.url} target="_blank" rel="noreferrer">{l.url.replace("https://", "")}</a> · tekshirildi {dmy(l.retrieved_at)}</div>
        </li>
      ))}
    </ul>
  );
}

// ---------------------------------------------------------------- savol / SMS / feyk

const ASK_MODES = [
  { id: "question", label: "❓ Savol", ph: "Masalan: Bolamga nafaqa nega berilmadi?" },
  { id: "sms", label: "🧾 SMS", ph: "Jarima yoki MIB SMS matnini shu yerga joylang" },
  { id: "factcheck", label: "🕵️ Feyk tekshiruvi", ph: "Shubhali post matnini joylang" },
];

export function AskPanel({ legalStatus, headers = {}, suggestions = [] }) {
  const [mode, setMode] = useState("question");
  const [text, setText] = useState("");
  const [res, setRes] = useState(null);
  const [busy, setBusy] = useState(false);
  const [appeal, setAppeal] = useState(null);
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
    const r = await api.post("/api/appeal", { card_id: res.card_id, event_id: res.event_id || null, lang: "uz" });
    setAppeal(r?.error ? { title: "Ariza", error: r.error } : { title: res.title, ...r });
  };
  return (
    <div className="space-y-3">
      <div className="tabs" role="tablist">
        {ASK_MODES.map((x) => <button key={x.id} role="tab" aria-selected={mode === x.id} className="tab" onClick={() => { setMode(x.id); setRes(null); }}>{x.label}</button>)}
      </div>
      {mode === "question" && suggestions.length > 0 && (
        <div>
          <div className="muted mb-1 text-xs font-semibold">Tayyor savollar (manba: O'RQ-692)</div>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((s) => <button key={s.q} className="chip text-left" disabled={busy} onClick={() => ask(s.q)}><span>💬 {s.q} {s.article ? <span className="muted text-xs">({s.article})</span> : null}</span></button>)}
          </div>
        </div>
      )}
      <label className="sr-only" htmlFor="ask">{m.label}</label>
      <textarea id="ask" rows={mode === "question" ? 3 : 5} className="w-full" placeholder={m.ph} value={text} onChange={(e) => setText(e.target.value)} maxLength={4000} />
      <button className="btn btn-primary w-full" disabled={busy || !text.trim()} onClick={() => send()}>{busy ? "Tekshirilmoqda…" : "Yuborish"}</button>
      <Err error={res?.error} />
      {res && !res.error && (
        <div className="card p-4">
          {res.verdict && <div className="mb-2"><span className={`badge ${res.verdict === "togri" ? "badge-ok" : res.verdict === "notogri" ? "badge-crit" : "badge-warn"}`}>{res.verdict_label || res.verdict}</span></div>}
          <div className="whitespace-pre-wrap text-[15px] leading-relaxed">{res.text}</div>
          {res.card_id && (
            <div className="mt-3 flex flex-wrap gap-2">
              <button className="btn" onClick={disagree}>❌ Baribir rozi emasman → ariza</button>
            </div>
          )}
        </div>
      )}
      <AppealSheet appeal={appeal} onClose={() => setAppeal(null)} />
    </div>
  );
}

// ---------------------------------------------------------------- imtiyoz, majburiyat, ariza

export function AppealSheet({ appeal, onClose }) {
  const [copied, setCopied] = useState(false);
  if (!appeal) return null;
  return (
    <div className="fixed inset-0 z-30 flex items-end justify-center" style={{ background: "rgba(5,12,25,.55)" }} onClick={onClose} role="dialog" aria-modal="true">
      <div className="card max-h-[88vh] w-full max-w-lg overflow-y-auto rounded-b-none p-4" onClick={(e) => e.stopPropagation()}>
        <div className="mb-2 flex items-start gap-2">
          <div className="min-w-0">
            <h3 className="font-semibold">📝 {appeal.title}</h3>
            <p className="muted text-xs">{appeal.hint}</p>
          </div>
          <button className="btn ml-auto px-3" onClick={onClose} aria-label="Yopish">✕</button>
        </div>
        {appeal.error ? <Err error={appeal.error} /> : (
          <>
            {appeal.to_check?.length > 0 && (
              <div className="mb-2 text-sm"><span className="badge badge-warn">❔ Tekshirilishi kerak</span> <span className="secondary">{appeal.to_check.join("; ")}</span></div>
            )}
            <pre className="card whitespace-pre-wrap p-3 text-sm" style={{ fontFamily: "inherit", background: "var(--surface-2)", boxShadow: "none" }}>{appeal.text}</pre>
            <div className="mt-3 flex flex-wrap gap-2">
              <button className="btn btn-primary" onClick={() => { copy(appeal.text); setCopied(true); }}>{copied ? "✅ Nusxa olindi" : "📋 Nusxa olish"}</button>
              {(appeal.submit_channels || []).map((c) => <a key={c.url + c.name} className="btn" href={c.url} target="_blank" rel="noreferrer">↗ {c.name}</a>)}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function Benefit({ b, onAppeal, busy }) {
  return (
    <div className="card p-4">
      <div className="flex items-start gap-3">
        <span className="text-2xl" aria-hidden>{b.icon}</span>
        <div className="min-w-0 flex-1">
          <div className="font-semibold leading-snug">{b.title}</div>
          <div className="mt-1 flex flex-wrap gap-1.5">
            <span className="badge badge-ok">✓ {b.status_text}</span>
            {b.verified ? <span className="badge badge-ok">✅ Huquqshunos tasdiqlagan</span>
              : b.source_checked ? <span className="badge badge-acc">{b.badge}</span>
              : <span className="badge badge-warn">⚠️ Tekshirilmagan (demo)</span>}
          </div>
        </div>
      </div>
      <p className="secondary mt-2 text-sm">{b.summary}</p>
      {b.status_note && <p className="mt-2 text-sm" style={{ color: "var(--warn-ink)" }}>{b.status_note}</p>}
      <ul className="mt-2 space-y-0.5 text-sm">
        {b.met.map((m) => <li key={m}>✓ {m}</li>)}
        {b.to_check.map((m) => <li key={m} className="secondary">❔ {m} <span className="muted">— tekshirilishi kerak</span></li>)}
      </ul>
      <div className="source mt-2">{b.source_line}</div>
      <button className="btn btn-primary mt-3 w-full" disabled={busy} onClick={() => onAppeal(b)}>{busy ? "Tayyorlanmoqda…" : `📝 ${b.appeal_label} — tayyor ariza`}</button>
    </div>
  );
}

function Obligation({ o, onRemind, note }) {
  const disc = o.discount_deadline != null;
  const left = disc ? o.discount_days_left : o.days_left;
  return (
    <div className="card p-4">
      <div className="flex items-start gap-2">
        <div className="min-w-0 flex-1">
          <div className="font-semibold leading-snug">{o.title}</div>
          <div className="muted text-xs">{o.issuer}{o.invoice ? ` · invoys ${o.invoice}` : ""}</div>
        </div>
        <div className="tabnum text-right font-semibold">{o.amount_text}</div>
      </div>
      {disc && <div className="mt-2 text-sm">💸 Chegirma bilan <b className="tabnum">{money(o.discount_amount)}</b> ({o.discount_pct}%) — <b className="tabnum">{dmy(o.discount_deadline)}</b> gacha</div>}
      {!disc && o.deadline && <div className="mt-2 text-sm">📅 Muddat: <b className="tabnum">{dmy(o.deadline)}</b></div>}
      {o.warning && <div className="mt-1 text-sm" style={{ color: "var(--warn-ink)" }}>⚠️ {o.warning}</div>}
      <div className="mt-2 flex flex-wrap items-center gap-2">
        {left != null && <span className={`badge ${left <= 7 ? "badge-crit" : left <= 14 ? "badge-warn" : "badge-acc"}`}>⏳ {left} kun qoldi</span>}
        {o.reminder_date && <button className="btn px-3 text-sm" onClick={() => onRemind(o)}>⏰ {dmy(o.reminder_date)} kuni eslatish</button>}
      </div>
      {note && <div className="muted mt-1 text-xs">{note}</div>}
    </div>
  );
}

// ---------------------------------------------------------------- bosh sahifa

export function Home({ me }) {
  return (
    <div className="space-y-6">
      <section className="pt-4">
        <span className="badge badge-acc">LexHackathon 2026 · Huquqiy targ'ibot va ta'lim</span>
        <h1 className="mt-3 text-3xl font-extrabold leading-tight">Huquqingizni murojaatdan oldin, oddiy tilda biling.</h1>
        <p className="secondary mt-2">{APP_NAME} vaziyatingizni sodda tushuntiradi, har bir javobga rasmiy manba (lex.uz) havolasini qo'yadi va kerak bo'lsa tayyor ariza beradi. Telegram bot, sayt va Mini App — bitta platforma.</p>
      </section>
      <section className="grid gap-3 sm:grid-cols-2">
        <button className="card p-5 text-left" onClick={() => go(me?.logged_in ? "/kabinet" : "/kirish?next=oneid")}>
          <div className="text-3xl" aria-hidden>✅</div>
          <div className="mt-2 text-lg font-bold">OneID bilan tasdiqlash</div>
          <p className="secondary mt-1 text-sm">Shaxsiy imtiyozlar, jarima va qarz muddatlari, sizga ta'sir qiluvchi qonun o'zgarishlari, bir bosishda ariza.</p>
          <span className="btn btn-primary mt-3 w-full">Davom etish</span>
        </button>
        <button className="card p-5 text-left" onClick={() => go("/anonim")}>
          <div className="text-3xl" aria-hidden>👤</div>
          <div className="mt-2 text-lg font-bold">Anonim foydalanish</div>
          <p className="secondary mt-1 text-sm">Ro'yxatsiz: savol, SMS va feyk tekshiruvi, maqomingizga oid umumiy huquqlar. Shaxsiy ma'lumot so'ralmaydi.</p>
          <span className="btn mt-3 w-full">Boshlash</span>
        </button>
      </section>
      <section className="card p-5">
        <h2 className="font-bold">Nega {APP_NAME}?</h2>
        <ul className="secondary mt-2 space-y-1 text-sm">
          <li>• Murojaatlarning katta qismi «huquqiy ma'lumot berish» bilan yakunlanadi — biz uni murojaatdan oldin beramiz.</li>
          <li>• Har bir yozuvda hujjat nomi, raqami, sanasi va lex.uz havolasi; manbasiz ma'lumot ko'rsatilmaydi.</li>
          <li>• O'zbekiston fuqarosi, chet el fuqarosi va fuqaroligi bo'lmagan shaxslar uchun alohida huquqlar bo'limi.</li>
          <li>• Telegram: <a className="underline" href="https://t.me/Huquqim_official_bot" target="_blank" rel="noreferrer">@Huquqim_official_bot</a> — matn va ovoz.</li>
        </ul>
      </section>
      <p className="muted text-xs">⚠️ Demo versiya: huquqiy mazmun huquqshunos tomonidan to'liq tekshirilmagan. OneID — simulyatsiya (DEMO ID), barcha shaxslar o'ylab topilgan. AI tushuntiradi; rasmiy manba — qonun hujjatining o'zi.</p>
    </div>
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
  useEffect(() => { localStorageSafe("anonStatus", status); localStorageSafe("anonSituations", sits.join(",")); }, [status, sits]);
  useEffect(() => {
    if (!status) return;
    api.get(`/api/rights?status=${encodeURIComponent(status)}&situations=${encodeURIComponent(sits.join(","))}`).then((r) => !r?.error && setData(r));
  }, [status, sits]);
  const toggle = (id) => setSits((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]));

  return (
    <div className="space-y-5">
      {!compact && (
        <div>
          <h1 className="text-2xl font-bold">👤 Anonim rejim</h1>
          <p className="secondary mt-1 text-sm">Ro'yxatsiz ishlaydi. Shaxsiy ma'lumot so'ralmaydi va saqlanmaydi; tanlovingiz faqat shu qurilmada qoladi.</p>
        </div>
      )}
      <section className="card p-4">
        <h2 className="font-semibold">Huquqiy maqomingiz <span className="muted text-sm font-normal">(ixtiyoriy)</span></h2>
        <div className="mt-2 flex flex-wrap gap-2">
          {(meta?.statuses || []).map((s) => <button key={s.id} className="chip" aria-pressed={status === s.id} onClick={() => setStatus(s.id)}>{s.icon} {s.title}</button>)}
        </div>
        <h2 className="mt-4 font-semibold">Holatingiz <span className="muted text-sm font-normal">(ixtiyoriy, bir nechta)</span></h2>
        <div className="mt-2 flex flex-wrap gap-2">
          {(meta?.situations || []).map((s) => <button key={s.id} className="chip" aria-pressed={sits.includes(s.id)} onClick={() => toggle(s.id)}>{s.icon} {s.title}</button>)}
        </div>
      </section>
      <div className="tabs" role="tablist">
        {[["rights", "⚖️ Umumiy huquqlar"], ["laws", "📚 Siz uchun qonunlar"], ["ask", "❓ Savol · SMS · Feyk"]].map(([id, label]) => (
          <button key={id} role="tab" className="tab" aria-selected={tab === id} onClick={() => setTab(id)}>{label}</button>
        ))}
      </div>
      {tab === "ask" && <AskPanel legalStatus={status} headers={headers} suggestions={data?.status?.suggested_questions || []} />}
      {tab !== "ask" && !status && <div className="card secondary p-4 text-sm">Avval maqomni tanlang (yoki «Bilmayman»).</div>}
      {tab === "rights" && status && data && <RightsView status={data.status} situations={data.situations} />}
      {tab === "laws" && status && data && <LawsList laws={data.laws} />}
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
  return (
    <div className="mx-auto max-w-md space-y-4 pt-2">
      <div>
        <h1 className="text-2xl font-bold">{mode === "register" ? "Huquqim hisobini ochish" : "Huquqim hisobiga kirish"}</h1>
        <p className="secondary mt-1 text-sm">Bu — {APP_NAME} platformasining o'z hisobi. Keyingi qadamda uni OneID (demo) orqali tasdiqlaysiz.</p>
      </div>
      <div className="tabs" role="tablist">
        <button role="tab" className="tab" aria-selected={mode === "register"} onClick={() => setMode("register")}>Ro'yxatdan o'tish</button>
        <button role="tab" className="tab" aria-selected={mode === "login"} onClick={() => setMode("login")}>Kirish</button>
      </div>
      <form className="card space-y-3 p-4" onSubmit={submit}>
        <div>
          <label className="secondary mb-1 block text-sm" htmlFor="u">Login</label>
          <input id="u" className="w-full" autoComplete="username" value={username} onChange={(e) => setU(e.target.value)} required minLength={3} maxLength={30} placeholder="masalan: malika94" />
        </div>
        <div>
          <label className="secondary mb-1 block text-sm" htmlFor="p">Parol</label>
          <input id="p" className="w-full" type="password" autoComplete={mode === "register" ? "new-password" : "current-password"} value={password} onChange={(e) => setP(e.target.value)} required minLength={8} maxLength={128} placeholder="kamida 8 belgi" />
        </div>
        <Err error={error} />
        <button className="btn btn-primary w-full" disabled={busy}>{busy ? "…" : mode === "register" ? "Hisob ochish" : "Kirish"}</button>
      </form>
      <p className="muted text-xs">Parol xeshlangan holda saqlanadi. Hisobda F.I.Sh., PINFL yoki telefon saqlanmaydi.</p>
    </div>
  );
}

// ---------------------------------------------------------------- kabinet

function TelegramPanel({ linked, onChange }) {
  const [link, setLink] = useState(null);
  const [error, setError] = useState(null);
  const make = async () => {
    const r = await api.post("/api/me/telegram/link", {});
    if (r?.error) setError(r.error); else setLink(r);
  };
  const unlink = async () => { await api.post("/api/me/telegram/unlink", {}); setLink(null); onChange?.(); };
  return (
    <div className="card p-4">
      <h3 className="font-semibold">📲 Telegram bot</h3>
      {linked ? (
        <>
          <p className="secondary mt-1 text-sm">✅ Hisobingiz @Huquqim_official_bot'ga ulangan: eslatma va o'zgarishlar botga keladi.</p>
          <button className="btn mt-3" onClick={unlink}>🔌 Uzish</button>
        </>
      ) : (
        <>
          <p className="secondary mt-1 text-sm">Bir martalik havola (10 daqiqa amal qiladi) — botda «Start» bosing.</p>
          {link ? (
            <a className="btn btn-primary mt-3 w-full" href={link.url} target="_blank" rel="noreferrer">↗ Telegram'da ochish va ulash</a>
          ) : (
            <button className="btn btn-primary mt-3 w-full" onClick={make}>Telegram'ni ulash</button>
          )}
          {link && <button className="btn btn-ghost mt-2 w-full" onClick={() => onChange?.()}>Uladim — yangilash</button>}
        </>
      )}
      <Err error={error} />
    </div>
  );
}

function ConsentPanel({ me, onRevoked }) {
  const [busy, setBusy] = useState(false);
  const revoke = async () => {
    if (!window.confirm("Rozilikni bekor qilasizmi? OneID (demo) bilan bog'lanish uziladi.")) return;
    setBusy(true);
    await api.post("/api/oneid/revoke", {});
    setBusy(false);
    onRevoked();
  };
  return (
    <div className="card p-4">
      <h3 className="font-semibold">🔐 Rozilik (OneID — DEMO)</h3>
      <p className="secondary mt-1 text-sm">Berilgan: {dmy(me?.consent_at)}. {APP_NAME} quyidagilarni kerak bo'lganda so'raydi, bazada saqlamaydi:</p>
      <ul className="secondary mt-1 list-disc pl-5 text-sm">{(me?.consent_scope || []).map((s) => <li key={s}>{s}</li>)}</ul>
      <button className="btn mt-3" disabled={busy} onClick={revoke}>Rozilikni bekor qilish</button>
    </div>
  );
}

const SECTIONS = [
  ["benefits", "🎁 Imtiyozlarim"], ["rights", "⚖️ Huquqlarim"], ["obligations", "📅 Majburiyatlar"],
  ["laws", "📚 Qonunlar"], ["changes", "🔔 O'zgarishlar"], ["ask", "❓ Savol · SMS · Feyk"], ["account", "⚙️ Hisob"],
];

export function CabinetView({ me, headers = {}, onReload, inMiniApp = false }) {
  const [v, setV] = useState(null);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState(() => new URLSearchParams(window.location.search).get("tab") || "benefits");
  const [appeal, setAppeal] = useState(null);
  const [busyId, setBusyId] = useState(null);
  const [notes, setNotes] = useState({});
  const load = useCallback(async () => {
    const r = await api.get("/api/me/cabinet", { headers });
    if (r?.error) setError(r.error); else setV(r);
  }, [headers]);
  useEffect(() => { load(); }, [load]);

  if (error) return <Err error={error} />;
  if (!v) return <div className="muted py-10 text-center">Yuklanmoqda…</div>;
  const p = v.person;
  const sections = [...SECTIONS];
  if (!inMiniApp && v.roles.includes("student")) sections.push(["edu", "🎓 Ta'lim"]);
  if (!inMiniApp && v.roles.includes("gov")) sections.push(["gov", "🏛️ Davlat kabineti"]);
  if (inMiniApp) sections.splice(sections.findIndex((s) => s[0] === "account"), 1);

  const makeAppeal = async (b) => {
    setBusyId(b.id);
    const r = await api.post("/api/me/appeal", { benefit_id: b.id }, { headers });
    setBusyId(null);
    setAppeal(r?.error ? { title: b.title, error: r.error } : r);
  };
  const remind = async (o) => {
    const r = await api.post("/api/me/remind", { obligation_id: o.id }, { headers });
    setNotes((n) => ({ ...n, [o.id]: r?.error ? `⚠️ ${r.error}` : r.text }));
  };

  return (
    <div className="space-y-4">
      <div className="card p-4">
        <div className="flex items-center gap-3">
          <span className="text-4xl" aria-hidden>{p.icon}</span>
          <div className="min-w-0">
            <div className="text-xl font-bold">Salom, {p.first_name}!</div>
            <div className="secondary text-sm">{p.full_name} · {p.persona}</div>
          </div>
        </div>
        <div className="mt-3 flex flex-wrap gap-1.5">
          <span className="badge badge-ok">✅ Tasdiqlangan (DEMO ID)</span>
          <span className="badge badge-acc">{p.status_title}</span>
          {v.situations.map((s) => <span key={s.id} className="badge badge-acc">{s.icon} {s.title}</span>)}
          {v.roles.includes("gov") && <span className="badge badge-warn">🏛️ Davlat xodimi (admin ro'yxati)</span>}
        </div>
        <p className="muted mt-2 text-xs">{p.document} · {p.region_name} · {v.source}</p>
      </div>

      <div className="tabs" role="tablist">
        {sections.map(([id, label]) => <button key={id} role="tab" className="tab" aria-selected={tab === id} onClick={() => setTab(id)}>{label}</button>)}
      </div>

      {tab === "benefits" && (
        <section className="space-y-3">
          <h2 className="font-semibold">Haqli bo'lishingiz mumkin <span className="muted tabnum">({v.benefits.length})</span></h2>
          {v.benefits.length === 0 && <div className="card secondary p-4 text-sm">Hozircha mos imtiyoz topilmadi.</div>}
          {v.benefits.map((b) => <Benefit key={b.id} b={b} onAppeal={makeAppeal} busy={busyId === b.id} />)}
          {v.not_eligible.length > 0 && (
            <details className="text-sm"><summary className="muted cursor-pointer">Mos kelmagan imtiyozlar ({v.not_eligible.length})</summary>
              <ul className="secondary mt-1 space-y-0.5">{v.not_eligible.map((n) => <li key={n.id}>— {n.title}: {n.failed.join("; ")}</li>)}</ul></details>
          )}
          <p className="muted text-xs">«Haqli bo'lishingiz mumkin» — yakuniy qarorni vakolatli organ qabul qiladi. {v.disclaimer}</p>
        </section>
      )}
      {tab === "rights" && <RightsView status={v.rights.status} situations={v.rights.situations} />}
      {tab === "obligations" && (
        <section className="space-y-3">
          {v.obligations.length === 0 && <div className="card secondary p-4 text-sm">Muddatli majburiyat (jarima, qarz) yo'q ✅</div>}
          {v.obligations.map((o) => <Obligation key={o.id} o={o} onRemind={remind} note={notes[o.id]} />)}
          {v.rights.status?.duties?.length > 0 && (<>
            <h3 className="mt-2 font-semibold">Maqomingiz bo'yicha umumiy majburiyatlar</h3>
            <ul className="space-y-2">{v.rights.status.duties.map((i) => <RightItem key={i.id} i={i} />)}</ul>
          </>)}
        </section>
      )}
      {tab === "laws" && <LawsList laws={v.laws} />}
      {tab === "changes" && (
        <section className="space-y-2">
          {v.changes.length === 0 ? <div className="card secondary p-4 text-sm">Hozircha yo'q. Sizga taalluqli qonun o'zgarsa, shu yerda va Telegram'da ko'rasiz.</div>
            : v.changes.map((c) => (
              <div key={c.id} className="card p-4 text-sm" style={{ boxShadow: "inset 3px 0 0 var(--accent)" }}>
                <div className="muted tabnum text-xs">{dmy(c.date)}</div>
                <div className="font-medium">{c.summary}</div>
                <div className="secondary mt-1">{c.reason}</div>
              </div>))}
          <button className="btn" onClick={load}>🔄 Yangilash</button>
        </section>
      )}
      {tab === "ask" && <AskPanel legalStatus={p.status} headers={headers} suggestions={v.rights.status?.suggested_questions || []} />}
      {tab === "account" && (
        <section className="space-y-3">
          <TelegramPanel linked={v.telegram_linked} onChange={load} />
          <ConsentPanel me={me} onRevoked={() => { onReload?.(); go("/kabinet"); }} />
        </section>
      )}
      {tab === "edu" && <Suspense fallback={<div className="muted">Yuklanmoqda…</div>}><Edu /></Suspense>}
      {tab === "gov" && (
        <Suspense fallback={<div className="muted">Yuklanmoqda…</div>}>
          <div className="card mb-3 p-3 text-sm" style={{ background: "var(--warn-bg)", color: "var(--warn-ink)", boxShadow: "none" }}>
            🔒 Simulyatsiya xabarlari FAQAT demo hisoblar va ularga ulangan Telegram chatlarga yuboriladi (cheklov bilan). Real foydalanuvchilarga ommaviy xabar yuborilmaydi.
          </div>
          <Dashboard apiBase="/api/cabinet/gov" />
        </Suspense>
      )}
      <AppealSheet appeal={appeal} onClose={() => setAppeal(null)} />
    </div>
  );
}

export function CabinetPage({ me, onReload }) {
  const flag = new URLSearchParams(window.location.search).get("oneid");
  useEffect(() => { if (me && !me.logged_in) go("/kirish"); }, [me]);
  if (!me) return <div className="muted py-10 text-center">Yuklanmoqda…</div>;
  if (!me.logged_in) return null;
  const logout = async () => { await api.post("/api/auth/logout", {}); onReload(); go("/"); };
  return (
    <div className="space-y-4">
      {flag === "ok" && <div className="badge badge-ok" role="status">✅ OneID (demo) orqali tasdiqlandi</div>}
      {flag === "denied" && <div className="badge badge-warn" role="status">Rozilik berilmadi — hisob tasdiqlanmadi</div>}
      {flag === "error" && <div className="badge badge-crit" role="alert">Tasdiqlashda xato. Qayta urinib ko'ring.</div>}
      {me.verified ? <CabinetView me={me} onReload={onReload} /> : (
        <div className="space-y-4">
          <div className="card p-5">
            <h1 className="text-xl font-bold">Hisobingiz: {me.username}</h1>
            <p className="secondary mt-1 text-sm">Shaxsiy bo'limlar (imtiyozlar, majburiyatlar, siz uchun qonunlar) uchun hisobni OneID orqali tasdiqlang.</p>
            <a className="btn btn-primary mt-3 w-full" href="/api/oneid/start">✅ OneID orqali tasdiqlash (DEMO)</a>
            <p className="muted mt-2 text-xs">Siz alohida DEMO ID sahifasiga o'tasiz. U yerda haqiqiy OneID login/parolingizni kiritmang.</p>
          </div>
          <div className="card p-4"><h2 className="mb-3 font-semibold">Hozircha anonim imkoniyatlar</h2><AnonView compact /></div>
        </div>
      )}
      <button className="btn btn-ghost" onClick={logout}>🚪 Hisobdan chiqish</button>
    </div>
  );
}
