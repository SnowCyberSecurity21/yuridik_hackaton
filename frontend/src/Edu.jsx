import { useEffect, useState } from "react";
import { api } from "./api.js";
import { DiffBlock, ErrorNote } from "./components.jsx";

// Ta'lim (talaba roli): AI simulyator, hujjat trenajyori, Darslik qo'riqchisi.

function Simulator({ cases }) {
  const [cardId, setCardId] = useState("");
  const [history, setHistory] = useState([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [score, setScore] = useState(null);
  const [error, setError] = useState(null);
  const start = async (id) => {
    setCardId(id); setScore(null); setError(null);
    const r = await api.post("/api/edu/sim/start", { card_id: id, history: [] });
    if (r?.error) { setError(r.error); return; }
    setHistory([{ role: "citizen", text: r.reply }]);
  };
  const send = async () => {
    if (!text.trim()) return;
    const h = [...history, { role: "student", text }];
    setHistory(h); setText(""); setBusy(true);
    const r = await api.post("/api/edu/sim/reply", { card_id: cardId, history: h });
    setBusy(false);
    if (r?.error) setError(r.error); else setHistory([...h, { role: "citizen", text: r.reply }]);
  };
  const finish = async () => {
    const r = await api.post("/api/edu/sim/score", { card_id: cardId, history });
    if (r?.error) setError(r.error); else setScore(r);
  };
  return (
    <section className="card space-y-3 p-4">
      <h3 className="font-semibold">🎭 AI simulyator — fuqaro bilan maslahat suhbati</h3>
      <label className="secondary block text-sm" htmlFor="case">Holatni tanlang</label>
      <select id="case" className="w-full" value={cardId} onChange={(e) => start(e.target.value)}>
        <option value="">—</option>
        {cases.map((c) => <option key={c.id} value={c.id}>{c.title}</option>)}
      </select>
      <ErrorNote error={error} />
      {history.length > 0 && (
        <div className="space-y-2">
          {history.map((m, i) => (
            <div key={i} className={`card p-3 text-sm ${m.role === "student" ? "ml-8" : "mr-8"}`}
              style={{ background: m.role === "student" ? "var(--accent-soft)" : "var(--surface-2)", boxShadow: "none" }}>
              <div className="muted text-xs">{m.role === "student" ? "Siz (maslahatchi)" : "Fuqaro (AI)"}</div>{m.text}
            </div>
          ))}
          <textarea className="w-full" rows={2} value={text} onChange={(e) => setText(e.target.value)} placeholder="Savolingiz yoki maslahatingiz…" />
          <div className="flex gap-2">
            <button className="btn btn-primary flex-1" disabled={busy || !text.trim()} onClick={send}>{busy ? "…" : "Yuborish"}</button>
            <button className="btn" onClick={finish}>🏁 Baholash</button>
          </div>
        </div>
      )}
      {score && (
        <div className="card p-3" style={{ boxShadow: "none" }}>
          <div className="text-lg font-bold">Baho: {score.score} / {score.max}</div>
          <ul className="mt-1 space-y-0.5 text-sm">{score.rubric.map((r) => <li key={r.id}>{r.ok ? "✅" : "⬜"} {r.label}</li>)}</ul>
          {score.reference?.steps?.length > 0 && <div className="secondary mt-2 text-sm"><b>Namunaviy qadamlar:</b> {score.reference.steps.join(" → ")}</div>}
          <p className="muted mt-1 text-xs">{score.note}</p>
        </div>
      )}
    </section>
  );
}

const SAMPLE = "Tuman «Inson» ijtimoiy xizmatlar markazi rahbariga\nfuqaro Aliyev Vali (manzil: ..., tel: ...)dan\n\nARIZA\n\nMen bolalar nafaqasi so'rab murojaat qilgan edim, rad etildi.\n\nSo'rayman: rad etish sababini yozma ravishda berishingizni.\n";

function Trainer({ cases }) {
  const [cardId, setCardId] = useState("");
  const [text, setText] = useState(SAMPLE);
  const [res, setRes] = useState(null);
  const check = async () => setRes(await api.post("/api/edu/trainer/check", { card_id: cardId || null, text }));
  return (
    <section className="card space-y-3 p-4">
      <h3 className="font-semibold">📝 Hujjat trenajyori</h3>
      <p className="secondary text-sm">Ariza yoki shikoyat loyihasini yozing — rekvizitlar, adresat, huquqiy asos va talab tekshiriladi.</p>
      <select className="w-full" value={cardId} onChange={(e) => setCardId(e.target.value)} aria-label="Holat">
        <option value="">Holat (ixtiyoriy)</option>
        {cases.map((c) => <option key={c.id} value={c.id}>{c.title}</option>)}
      </select>
      <textarea className="w-full" rows={8} value={text} onChange={(e) => setText(e.target.value)} />
      <button className="btn btn-primary w-full" onClick={check}>Tekshirish</button>
      <ErrorNote error={res?.error} />
      {res && !res.error && (
        <div className="space-y-1 text-sm">
          <div className="font-bold">Natija: {res.ok_count} / {res.total} · {res.score}/10</div>
          {res.results.map((r) => (
            <div key={r.id}>{r.ok ? "✅" : "❌"} {r.label}{r.explain && <div className="secondary ml-6">{r.explain}</div>}</div>
          ))}
          <p className="muted text-xs">{res.note}</p>
        </div>
      )}
    </section>
  );
}

function Textbook() {
  const [chunks, setChunks] = useState(null);
  const [error, setError] = useState(null);
  useEffect(() => {
    api.get("/api/edu/textbook").then((r) => (Array.isArray(r) ? setChunks(r) : setError(r?.error)));
  }, []);
  const outdated = (chunks || []).filter((c) => c.status === "outdated").length;
  return (
    <section className="card space-y-3 p-4">
      <h3 className="font-semibold">📕 Darslik qo'riqchisi</h3>
      <p className="secondary text-sm">Bo'limlar qonun moddalariga bog'langan. Modda o'zgarsa — «ESKIRGAN» va yangilangan matn taklifi.</p>
      <ErrorNote error={error} />
      {chunks && <div className="muted text-xs">{chunks.length} bo'lim · {outdated} ta eskirgan</div>}
      {(chunks || []).map((c) => (
        <article key={c.id} className="card p-3" style={{ boxShadow: "none", ...(c.status === "outdated" ? { borderColor: "var(--crit-ink)" } : {}) }}>
          <div className="flex flex-wrap items-center gap-2">
            <h4 className="font-semibold">{c.title}</h4>
            {c.status === "outdated" ? <span className="badge badge-crit">📕 ESKIRGAN</span> : <span className="badge badge-ok">✅ Dolzarb</span>}
          </div>
          <p className="secondary mt-1 text-sm">{c.text}</p>
          {c.status === "outdated" && (
            <div className="mt-2 space-y-2">
              <DiffBlock oldText={c.diff?.old} newText={c.diff?.new} />
              <div className="text-sm"><b>Taklif:</b> {c.suggested_text}</div>
            </div>
          )}
        </article>
      ))}
    </section>
  );
}

export default function Edu() {
  const [cases, setCases] = useState([]);
  useEffect(() => { api.get("/api/edu/cases").then((r) => Array.isArray(r) && setCases(r)); }, []);
  return (
    <div className="space-y-4">
      <Simulator cases={cases} />
      <Trainer cases={cases} />
      <Textbook />
    </div>
  );
}
