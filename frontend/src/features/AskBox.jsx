// AskBox — «Savol bering»: savol → kartadan javob + manba + qonundan asl iqtibos va oddiy til (LawView).
// Manba topilmasa — «tasdiqlangan ma'lumot topilmadi», taxmin qilinmaydi (backend kafolatlaydi).
import { useId, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Alert, Badge, Button, TrustBadge, toast, spring } from "../ui";
import { featuresApi } from "./api.js";
import LawView from "./LawView.jsx";

const EXAMPLES = [
  "Stipendiya nega berilmadi?",
  "Dekret ta'tili necha kun?",
  "Soliq tekshiruvi keldi, nima qilay?",
  "Bolamga nafaqa nega berilmadi?",
  "Jarimani chegirma bilan qachongacha to'lash mumkin?",
];

// Javob matnidan sarlavha, iqtibos va manba qatorlarini ajratib, qolgan tanani ko'rsatamiz
function bodyLines(text = "") {
  return text.split("\n").filter((l) => l.trim() && !/^(📌|📖|💬|📚|ℹ️)/u.test(l.trim()));
}

function Answer({ res, onAppeal }) {
  const lines = bodyLines(res.text);
  const notFound = res.type === "not_found";
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(res.text);
      toast("Javob nusxalandi", { tone: "ok" });
    } catch {
      toast("Nusxa olib bo'lmadi", { tone: "danger" });
    }
  };
  return (
    <article className="card p-4 sm:p-5" aria-live="polite">
      <header className="mb-3 flex flex-wrap items-start gap-2">
        <h3 className="h3 min-w-0 flex-1">{notFound ? "Tasdiqlangan ma'lumot topilmadi" : res.title || "Javob"}</h3>
        {!notFound && <TrustBadge verified={res.verified} sourceChecked={/tekshirildi/i.test(res.badge || "")} reverify={res.needs_reverification} />}
      </header>

      <ul className="grid gap-2">
        {lines.map((l, i) => <li key={i} className="secondary leading-relaxed">{l}</li>)}
      </ul>

      {res.status_note && <Alert tone="info" className="mt-3">{res.status_note}</Alert>}

      {res.quotes?.length > 0 && (
        <section className="mt-5" aria-label="Qonundan iqtibos">
          <p className="small mb-2 font-semibold">Qonunda nima yozilgan</p>
          <LawView excerpts={res.quotes} compact limit={2} />
        </section>
      )}

      {res.sources?.length > 0 && (
        <p className="source mt-4">
          Manba:{" "}
          {res.sources.map((s, i) => (
            <span key={i}>
              {i > 0 && "; "}
              <a href={s.url} target="_blank" rel="noopener noreferrer">{s.doc}{s.article ? `, ${s.article}` : ""}</a>
            </span>
          ))}
        </p>
      )}
      <p className="source mt-1">{res.disclaimer}</p>

      <div className="mt-4 flex flex-wrap gap-2">
        {res.card_id && onAppeal && (
          <Button variant="primary" size="sm" icon="📝" onClick={() => onAppeal(res.card_id)}>Ariza tayyorlash</Button>
        )}
        <Button size="sm" variant="secondary" icon="📋" onClick={copy}>Nusxa olish</Button>
      </div>
      {res.alternatives?.length > 0 && (
        <p className="small muted mt-3">O'xshash mavzular: {res.alternatives.map((a) => a.title).join(" · ")}</p>
      )}
    </article>
  );
}

/**
 * Props: legalStatus?, region?, placeholder?, onAppeal?(cardId)
 */
export default function AskBox({ legalStatus, region, placeholder = "Masalan: Stipendiya nega berilmadi?", onAppeal }) {
  const [text, setText] = useState("");
  const [state, setState] = useState({ loading: false, res: null, error: null });
  const inputId = useId();
  const inputRef = useRef(null);

  const ask = async (q) => {
    const question = (q ?? text).trim();
    if (question.length < 3) {
      inputRef.current?.focus();
      return;
    }
    setText(question);
    setState((s) => ({ ...s, loading: true, error: null }));
    const res = await featuresApi.ask(question, { legalStatus, region });
    setState(res.error ? { loading: false, res: null, error: res.error } : { loading: false, res, error: null });
  };

  return (
    <div className="grid gap-4">
      <form className="card p-4 sm:p-5" onSubmit={(e) => { e.preventDefault(); ask(); }}>
        <label htmlFor={inputId} className="h3 mb-2 block">Savol bering</label>
        <p className="small muted mb-3">Vaziyatingizni oddiy so'z bilan yozing. Javob qonundan iqtibos va manba bilan keladi.</p>
        <textarea id={inputId} ref={inputRef} rows={3} value={text} maxLength={4000}
          onChange={(e) => setText(e.target.value)} placeholder={placeholder}
          onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) ask(); }}
          className="w-full resize-y" />
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <Button type="submit" variant="primary" loading={state.loading}>Javob olish</Button>
          <Badge tone="info">Ism, PINFL, telefon saqlanmaydi</Badge>
        </div>
        <div className="mt-4 flex flex-wrap gap-2" aria-label="Namuna savollar">
          {EXAMPLES.map((q) => (
            <button key={q} type="button" className="btn btn-ghost btn-sm" onClick={() => ask(q)} disabled={state.loading}>{q}</button>
          ))}
        </div>
      </form>

      {state.error && <Alert tone="warn" title="Javob olib bo'lmadi">{state.error}</Alert>}
      <AnimatePresence mode="wait" initial={false}>
        {state.res && (
          <motion.div key={state.res.event_id ?? state.res.text} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }} transition={spring}>
            <Answer res={state.res} onAppeal={onAppeal} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
