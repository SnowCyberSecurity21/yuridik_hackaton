import { useCallback, useEffect, useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "./api.js";
import { ChartTooltip, ErrorNote, Section, StatusBadge, Wow, fmt } from "./components.jsx";

const AXIS = { fontSize: 12, fill: "var(--text-muted)" };

function Kpi({ label, value, sub, hint }) {
  return (
    <div className="card p-4" title={hint}>
      <div className="muted text-xs font-medium uppercase tracking-wide">{label}</div>
      <div className="tabnum mt-1 text-3xl font-bold">{value}</div>
      {sub && <div className="mt-1 text-sm">{sub}</div>}
    </div>
  );
}

function RegionChart({ data, topicTitle, titles }) {
  const [table, setTable] = useState(false);
  const rows = useMemo(
    () => [...data].sort((a, b) => b.count - a.count).map((r) => ({ ...r, topTitle: titles[r.top_topic] })),
    [data, titles]
  );
  return (
    <Section
      title="Huquqiy tushunmovchilik xaritasi — 14 hudud"
      subtitle={topicTitle ? `Mavzu: ${topicTitle}` : "Barcha mavzular bo'yicha savollar soni"}
      right={<button className="btn" onClick={() => setTable((v) => !v)}>{table ? "📊 Grafik" : "📋 Jadval"}</button>}
    >
      {table ? (
        <table className="w-full text-sm">
          <thead><tr className="muted text-left"><th className="py-1">Hudud</th><th className="text-right">Savollar</th><th className="pl-4">Eng ko'p mavzu</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.region} className="border-t" style={{ borderColor: "var(--border)" }}>
                <td className="py-1.5">{r.name}</td><td className="tabnum text-right">{fmt(r.count)}</td><td className="secondary pl-4">{r.topTitle || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div style={{ height: 420 }}>
          <ResponsiveContainer>
            <BarChart data={rows} layout="vertical" margin={{ left: 8, right: 24, top: 4, bottom: 4 }} barCategoryGap={4}>
              <CartesianGrid horizontal={false} stroke="var(--grid)" />
              <XAxis type="number" tick={AXIS} axisLine={false} tickLine={false} tickFormatter={fmt} />
              <YAxis type="category" dataKey="name" width={150} interval={0} tick={{ ...AXIS, fill: "var(--text-secondary)" }} axisLine={false} tickLine={false} />
              <Tooltip content={<ChartTooltip />} cursor={{ fill: "var(--surface-2)" }} />
              <Bar dataKey="count" fill="var(--series-1)" radius={[0, 4, 4, 0]} barSize={16} isAnimationActive={false} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </Section>
  );
}

function TrendChart({ data, topicTitle }) {
  const rows = data.map((d) => ({ ...d, name: d.date.slice(5).split("-").reverse().join(".") }));
  return (
    <Section title="Kunlik savollar (28 kun)" subtitle={`${topicTitle || "Barcha mavzular"} · kechagi kun holatiga`}>
      <div style={{ height: 220 }}>
        <ResponsiveContainer>
          <LineChart data={rows} margin={{ left: 0, right: 12, top: 8, bottom: 0 }}>
            <CartesianGrid vertical={false} stroke="var(--grid)" />
            <XAxis dataKey="name" tick={AXIS} axisLine={false} tickLine={false} interval={6} />
            <YAxis tick={AXIS} axisLine={false} tickLine={false} width={36} />
            <Tooltip content={<ChartTooltip />} cursor={{ stroke: "var(--text-muted)", strokeDasharray: "3 3" }} />
            <Line dataKey="count" stroke="var(--series-1)" strokeWidth={2} dot={false} activeDot={{ r: 5 }} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Section>
  );
}

function TopicsTable({ topics, selected, onSelect, onGenerate, generating }) {
  return (
    <Section title="Top-10 mavzu" subtitle="Qatorni bosing — xarita va trend shu mavzuga filtrlanadi">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-sm">
          <thead>
            <tr className="muted text-left text-xs uppercase tracking-wide">
              <th className="py-2">Mavzu</th><th className="text-right">Jami</th><th className="text-right">Shu hafta</th>
              <th className="text-right">Haftalik</th><th className="text-right" title="'Tushunmadim / rozi emasman' ulushi">Tushunmovchilik</th>
              <th className="pl-4">Holat</th><th />
            </tr>
          </thead>
          <tbody>
            {topics.map((t) => (
              <tr key={t.topic_id} onClick={() => onSelect(t.topic_id === selected ? null : t.topic_id)}
                className={`row-hover cursor-pointer border-t ${t.topic_id === selected ? "row-active" : ""}`} style={{ borderColor: "var(--border)" }}>
                <td className="py-2.5 pr-3 font-medium">{t.title}</td>
                <td className="tabnum text-right">{fmt(t.count)}</td>
                <td className="tabnum text-right">{fmt(t.week)}</td>
                <td className="text-right"><Wow pct={t.wow_change_pct} /></td>
                <td className="tabnum text-right">{t.misunderstanding_rate != null ? `${t.misunderstanding_rate}%` : "—"}</td>
                <td className="pl-4"><StatusBadge verified={t.verified} reverify={t.needs_reverification} sourceChecked={t.source_checked} /></td>
                <td className="pl-2 text-right">
                  <button className="btn btn-primary" disabled={generating === t.topic_id}
                    onClick={(e) => { e.stopPropagation(); onGenerate(t.topic_id); }}>
                    {generating === t.topic_id ? "⏳" : "✨"} Targ'ibot kontenti
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Section>
  );
}

function copy(text) {
  try { navigator.clipboard.writeText(text); } catch { /* ruxsat yo'q */ }
}

function ContentPanel({ content, onClose }) {
  const [answers, setAnswers] = useState({});
  if (!content) return null;
  if (content.error) return <ErrorNote error={content.error} />;
  return (
    <Section title={`✨ Targ'ibot kontenti: ${content.title}`}
      subtitle={`Manba — faqat vaziyat kartasi · ${content.generated_by === "llm" ? "AI generatsiya" : "shablon (LLM kaliti yo'q)"}`}
      right={<><StatusBadge verified={content.verified} /><button className="btn" onClick={onClose}>✕</button></>}>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card p-4" style={{ background: "var(--surface-2)" }}>
          <h3 className="mb-2 font-semibold">🎬 30 soniyalik video ssenariy</h3>
          <ol className="space-y-2 text-sm">
            {content.video_script.map((s, i) => (
              <li key={i}><span className="tabnum muted mr-2">{s.t}</span><b>{s.scene}:</b> {s.text}</li>
            ))}
          </ol>
        </div>
        <div className="card p-4" style={{ background: "var(--surface-2)" }}>
          <div className="mb-2 flex items-center"><h3 className="font-semibold">📣 Telegram post</h3>
            <button className="btn ml-auto" onClick={() => copy(content.telegram_post)}>📋 Nusxa</button></div>
          <pre className="whitespace-pre-wrap text-sm" style={{ fontFamily: "inherit" }}>{content.telegram_post}</pre>
        </div>
        <div className="card p-4" style={{ background: "var(--surface-2)" }}>
          <h3 className="mb-2 font-semibold">🖼 Infografika matni</h3>
          <div className="text-lg font-bold">{content.infographic.headline}</div>
          <div className="mt-2 grid gap-2 sm:grid-cols-2">
            {content.infographic.blocks.map((b, i) => (
              <div key={i} className="card p-3"><div className="text-sm font-semibold">{b.title}</div><div className="secondary text-sm">{b.text}</div></div>
            ))}
          </div>
          <div className="muted mt-2 text-xs">{content.infographic.footer}</div>
        </div>
        <div className="card p-4" style={{ background: "var(--surface-2)" }}>
          <h3 className="mb-2 font-semibold">❓ 3 savollik quiz</h3>
          {content.quiz.map((q, qi) => (
            <div key={qi} className="mb-3">
              <div className="text-sm font-medium">{qi + 1}. {q.q}</div>
              <div className="mt-1 flex flex-wrap gap-1.5">
                {q.options.map((o, oi) => {
                  const picked = answers[qi] === oi;
                  const cls = picked ? (oi === q.answer ? "badge badge-ok" : "badge badge-crit") : "badge";
                  return (
                    <button key={oi} className={cls} style={picked ? {} : { background: "var(--surface-1)", border: "1px solid var(--border)" }}
                      onClick={() => setAnswers((a) => ({ ...a, [qi]: oi }))}>
                      {picked ? (oi === q.answer ? "✅ " : "❌ ") : ""}{o}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
}

function SignalsPanel({ signals, regionName }) {
  if (!signals) return null;
  const VERDICT = { notogri: "❌ Noto'g'ri", qisman: "🟡 Qisman" };
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Section title="🚨 Tarqalayotgan feyk da'volar" subtitle="Fakt-tekshiruv loglaridan, oxirgi 14 kun">
        {signals.fake_claims.length === 0 && <p className="muted text-sm">Signal yo'q.</p>}
        <ul className="space-y-3">
          {signals.fake_claims.map((c) => (
            <li key={c.claim_id + c.verdict} className="flex gap-3 text-sm">
              <span className={`badge ${c.verdict === "notogri" ? "badge-crit" : "badge-warn"} h-fit`}>{VERDICT[c.verdict]}</span>
              <div className="min-w-0">
                <div className="font-medium">«{c.claim}»</div>
                <div className="muted text-xs">{fmt(c.count)} ta tekshiruv · ko'proq: {c.top_regions.map(regionName).join(", ")}</div>
              </div>
            </li>
          ))}
        </ul>
      </Section>
      <Section title="🧩 Eng ko'p tushunilmayotgan mavzular" subtitle="Soddalashtirish va qo'shimcha targ'ibot talab qiladi">
        <ul className="space-y-2">
          {signals.misunderstood_topics.map((t) => (
            <li key={t.topic_id} className="flex items-center gap-3 text-sm">
              <span className="font-medium">{t.title}</span>
              <span className="tabnum secondary ml-auto">{t.misunderstanding_rate}% tushunmadi</span>
              <span className="badge badge-warn">✏️ Soddalashtirish</span>
            </li>
          ))}
        </ul>
      </Section>
    </div>
  );
}

function AmendmentPanel({ onApplied }) {
  const [changes, setChanges] = useState([]);
  const [profiles, setProfiles] = useState([]);
  const [choice, setChoice] = useState("");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const load = useCallback(async () => {
    const [c, p] = await Promise.all([api.get(BASE + "/changes"), api.get(BASE + "/profiles")]);
    if (Array.isArray(c)) setChanges(c);
    if (Array.isArray(p)) setProfiles(p);
  }, []);
  useEffect(() => { load(); }, [load]);

  const pendingList = changes.filter((c) => !c.applied);
  const simulate = async () => {
    setBusy(true);
    const r = await api.post(BASE + "/simulate-amendment", choice ? { change_id: choice } : {});
    setResult(r);
    setChoice("");
    setBusy(false);
    load();
    onApplied();
  };
  const reset = async () => {
    setBusy(true);
    await api.post(BASE + "/reset-demo", {});
    setResult(null);
    setBusy(false);
    load();
    onApplied();
  };
  const impact = result && !result.error ? result.profiles : null;

  return (
    <Section title="⚖️ Qonun o'zgarishlari → faqat ta'sir qiladigan fuqarolarga"
      subtitle="Yangi tahrir demo ID shaxslari bilan solishtiriladi: xabar faqat shu o'zgarish taalluqli bo'lganlarga boradi"
      right={<>
        <select className="w-full max-w-full sm:w-auto" value={choice} onChange={(e) => setChoice(e.target.value)} aria-label="O'zgarishni tanlash" disabled={busy || pendingList.length === 0}>
          <option value="">Navbatdagi o'zgarish</option>
          {pendingList.map((c) => <option key={c.id} value={c.id}>{c.date} · {c.summary_uz.replace("[DEMO] ", "").slice(0, 48)}…</option>)}
        </select>
        <button className="btn btn-primary" onClick={simulate} disabled={busy || pendingList.length === 0}>⚡ O'zgarishni simulyatsiya qilish</button>
        <button className="btn" onClick={reset} disabled={busy}>↺ Demo'ni tiklash</button>
      </>}>
      <ul className="mb-3 space-y-1 text-sm">
        {changes.map((c) => (
          <li key={c.id} className="flex flex-wrap items-center gap-x-2 gap-y-0.5">
            <span className={`badge ${c.applied ? "badge-ok" : ""}`} style={c.applied ? {} : { background: "var(--surface-2)" }}>{c.applied ? "qo'llangan" : "kutilmoqda"}</span>
            <span className="tabnum muted">{c.date}</span><span>{c.summary_uz}</span>
          </li>
        ))}
      </ul>
      <ErrorNote error={result?.error} />

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="card p-4 lg:col-span-2" style={{ background: "var(--surface-2)" }}>
          <h3 className="mb-2 font-semibold">👤 Demo ID shaxslari — kimga ta'sir qiladi?</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="muted text-left text-xs">
                <th className="py-1 pr-2 font-medium">Profil</th><th className="py-1 pr-2 font-medium">Imtiyozlari</th>
                <th className="py-1 pr-2 text-right font-medium">Ulangan</th><th className="py-1 font-medium">{impact ? "Natija" : "Holat"}</th>
              </tr></thead>
              <tbody>
                {profiles.map((p) => {
                  const hit = impact?.find((i) => i.profile_id === p.profile_id);
                  return (
                    <tr key={p.profile_id} className="border-t" style={{ borderColor: "var(--border)" }}>
                      <td className="py-2 pr-2 font-medium">{p.icon} {p.persona}</td>
                      <td className="secondary py-2 pr-2">{p.benefits.join(" · ") || "—"}</td>
                      <td className="tabnum py-2 pr-2 text-right">{p.linked_users}</td>
                      <td className="py-2">
                        {!hit ? <span className="muted">—</span> : hit.affected
                          ? <span className="badge badge-ok" title={hit.reason}>🔔 Xabar yuborildi · {hit.reason}</span>
                          : <span className="badge" style={{ background: "var(--surface-1)" }}>🔕 Taalluqli emas — xabar yo'q</span>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="muted mt-2 text-xs">Profil ma'lumoti saqlanmaydi: faqat "foydalanuvchi ↔ profil" bog'lanishi va rozilik yozuvi SQLite'da.</p>
        </div>
        <div className="card p-4" style={{ background: "var(--surface-2)" }}>
          <h3 className="mb-2 font-semibold">🔔 Xabar</h3>
          {!result || result.error ? <p className="muted text-sm">Simulyatsiyadan keyin shu yerda fuqaroga boradigan xabar ko'rinadi.</p> : (
            <>
              <div className="text-sm"><b className="tabnum">{result.alerts.profile_users_notified}</b> ta profil egasiga
                {result.alerts.topic_subscribers_notified ? <>, <b className="tabnum">{result.alerts.topic_subscribers_notified}</b> ta mavzu obunachisiga</> : null}
                {result.alerts.telegram_enabled ? ` · Telegram: ${result.alerts.delivered_via_telegram} ta yuborildi` : " · Telegram token yo'q — navbatda"}</div>
              {result.alerts.preview && <pre className="card mt-2 whitespace-pre-wrap p-3 text-sm" style={{ fontFamily: "inherit" }}>{result.alerts.preview}</pre>}
              {result.affected_cards.length > 0 && (
                <div className="mt-3 text-sm">
                  <div className="font-medium">🔄 Qayta tekshiruvga:</div>
                  <ul>{result.affected_cards.map((c) => <li key={c.id}>• {c.title} <span className="badge badge-crit">qayta tekshirish</span></li>)}</ul>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </Section>
  );
}

// API manzili: /api/gov (basic auth) yoki /api/cabinet/gov (Davlat kabineti, gov roli)
let BASE = "/api/gov";

export default function Dashboard({ apiBase = "/api/gov" }) {
  BASE = apiBase;
  const [overview, setOverview] = useState(null);
  const [topics, setTopics] = useState([]);
  const [regions, setRegions] = useState([]);
  const [trend, setTrend] = useState([]);
  const [signals, setSignals] = useState(null);
  const [selected, setSelected] = useState(null);
  const [content, setContent] = useState(null);
  const [generating, setGenerating] = useState(null);
  const [error, setError] = useState(null);

  const titles = useMemo(() => Object.fromEntries(topics.map((t) => [t.topic_id, t.title])), [topics]);
  const regionNames = useMemo(() => Object.fromEntries(regions.map((r) => [r.region, r.name])), [regions]);

  const loadAll = useCallback(async () => {
    const [o, t, s] = await Promise.all([api.get(BASE + "/overview"), api.get(BASE + "/topics?limit=10"), api.get(BASE + "/signals")]);
    if (o?.error) setError(o.error); else { setOverview(o); setError(null); }
    if (Array.isArray(t)) setTopics(t);
    if (s && !s.error) setSignals(s);
  }, []);

  const loadFiltered = useCallback(async () => {
    const q = selected ? `?topic_id=${encodeURIComponent(selected)}` : "";
    const [r, tr] = await Promise.all([api.get(`${BASE}/regions${q}`), api.get(`${BASE}/trend${q}`)]);
    if (Array.isArray(r)) setRegions(r);
    if (Array.isArray(tr)) setTrend(tr);
  }, [selected]);

  useEffect(() => { loadAll(); }, [loadAll]);
  useEffect(() => { loadFiltered(); }, [loadFiltered]);

  const generate = async (topicId) => {
    setGenerating(topicId);
    setContent(await api.post(BASE + "/content", { topic_id: topicId }));
    setGenerating(null);
    setTimeout(() => document.getElementById("content-panel")?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
  };

  const o = overview || {};
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold">Fuqarolar nimani tushunmayapti?</h1>
        <p className="secondary mt-1 text-sm">Anonim analitika: mavzu, hudud, til, kanal. Shaxsiy ma'lumot (PINFL, F.I.Sh., telefon) saqlanmaydi.</p>
      </div>
      <ErrorNote error={error} />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        <Kpi label="Savollar (7 kun)" value={fmt(o.week_questions)} sub={<Wow pct={o.wow_change_pct} />} />
        <Kpi label="Jami savollar" value={fmt(o.total_questions)} sub={<span className="muted">{o.topics_total} ta vaziyat kartasi</span>} />
        <Kpi label="Konsultatsiya murojaati oldi olindi" value={fmt(o.deflected)}
          hint="Kartadan javob olgan va murojaat yozishga ehtiyoj qolmagan holatlar (PF-51: 'konsultatsiya talab qiluvchi' toifa)"
          sub={<span className="muted">murojaatsiz hal qilindi</span>} />
        <Kpi label="Tayyor murojaatlar" value={fmt(o.appeals_generated)} sub={<span className="muted">«rozi emasman» → to'g'ri adresatga</span>} />
        <Kpi label="Foydali deb baholandi" value={o.helpful_rate != null ? `${o.helpful_rate}%` : "—"} sub={<span className="muted">{fmt(o.factchecks)} fakt-tekshiruv</span>} />
      </div>

      <div className="grid gap-5 lg:grid-cols-5">
        <div className="lg:col-span-3"><RegionChart data={regions} topicTitle={titles[selected]} titles={titles} /></div>
        <div className="space-y-5 lg:col-span-2">
          <TrendChart data={trend} topicTitle={titles[selected]} />
          <Section title="Nima uchun muhim" subtitle="Rasmiy statistikadan (taqdimot uchun)">
            <ul className="secondary space-y-1.5 text-sm">
              <li>• Xalq qabulxonasiga 2026-yilda <b className="tabnum">557 254</b> murojaat; bolalar nafaqasi — <b className="tabnum">48 778</b> (+38%).</li>
              <li>• Oliy ta'lim vazirligi, 2026 1-chorak: murojaatlarning <b>65,2%</b>i shunchaki «huquqiy tushuntirish» bilan yopilgan.</li>
              <li>• Atigi <b>8,6%</b> aholi advokat yollay oladi; har 3 kishidan 1 tasi qonunni yetarli tushunmaydi (UNDP 2025).</li>
            </ul>
          </Section>
        </div>
      </div>

      <TopicsTable topics={topics} selected={selected} onSelect={setSelected} onGenerate={generate} generating={generating} />
      <div id="content-panel"><ContentPanel content={content} onClose={() => setContent(null)} /></div>
      <SignalsPanel signals={signals} regionName={(id) => regionNames[id] || id} />
      <AmendmentPanel onApplied={loadAll} />
    </div>
  );
}
