// LawView — qonun abzasi: «Qonunda» (lex.uz'dan aynan, serif) ↔ «Oddiy tilda» (AI soddalashtirgan, marker).
// Desktop'da yonma-yon; telefonda bitta ustun va almashtirgich (avval «Oddiy tilda»).
import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Badge, Skeleton, Tabs, useMediaQuery, springSnappy } from "../ui";
import { featuresApi } from "./api.js";

const cx = (...a) => a.filter(Boolean).join(" ");
const LONG = 420; // shundan uzun asl matn yig'iladi

function dmy(iso) {
  const [y, m, d] = String(iso || "").slice(0, 10).split("-");
  return d ? `${d}.${m}.${y}` : iso || "";
}

function OriginalText({ text }) {
  const [open, setOpen] = useState(false);
  const long = text.length > LONG;
  const shown = !long || open ? text : text.slice(0, LONG).replace(/\s+\S*$/, "") + " …";
  return (
    <div>
      <blockquote className="law-quote whitespace-pre-line text-[0.95rem]" lang="uz">
        {shown}
      </blockquote>
      {long && (
        <button type="button" className="link small mt-2" onClick={() => setOpen((v) => !v)} aria-expanded={open}>
          {open ? "Qisqartirish" : "To'liq matnni ko'rish"}
        </button>
      )}
    </div>
  );
}

function PlainText({ text }) {
  return (
    <p className="text-[1.02rem] leading-relaxed" style={{ color: "var(--text-primary)" }}>
      <span className="plain-mark">{text}</span>
    </p>
  );
}

function Column({ label, hint, children }) {
  return (
    <div className="min-w-0">
      <div className="mb-2 flex items-baseline gap-2">
        <span className="small font-semibold" style={{ color: "var(--text-primary)" }}>{label}</span>
        {hint && <span className="tiny muted">{hint}</span>}
      </div>
      {children}
    </div>
  );
}

/** Bitta abzas. `compact` — karta ichida (sarlavhasiz, kichik oraliqlar). */
export function LawExcerpt({ excerpt: e, compact = false, lang = "uz" }) {
  const wide = useMediaQuery("(min-width: 768px)");
  const [view, setView] = useState("plain");
  const plain = (lang === "ru" && e.plain_ru) || e.plain || e.plain_uz;
  const ref = [e.article, e.paragraph].filter(Boolean).join(", ");

  const original = (
    <Column label="Qonunda" hint="lex.uz'dan aynan">
      <OriginalText text={e.original_text} />
    </Column>
  );
  const simple = plain ? (
    <Column label="Oddiy tilda">
      <PlainText text={plain} />
    </Column>
  ) : null;

  return (
    <article className={cx("card", compact ? "card-inset p-3 sm:p-4" : "p-4 sm:p-5")} aria-label={`${e.doc}, ${ref}`}>
      {!compact && (
        <header className="mb-3">
          <p className="h3">{ref || "Qonun abzasi"}</p>
          <p className="source mt-0.5">{e.doc}</p>
        </header>
      )}

      {wide || !simple ? (
        <div className={cx("grid gap-5", simple && "md:grid-cols-2 md:gap-8")}>
          {original}
          {simple}
        </div>
      ) : (
        <div>
          <Tabs className="mb-3" ariaLabel="Matn ko'rinishi" value={view} onChange={setView}
            items={[{ id: "plain", label: "Oddiy tilda" }, { id: "law", label: "Qonunda" }]} />

          <AnimatePresence mode="wait" initial={false}>
            <motion.div key={view} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              transition={{ ...springSnappy, duration: 0.18 }}>
              {view === "plain" ? simple : original}
            </motion.div>
          </AnimatePresence>
        </div>
      )}

      <footer className="mt-4 flex flex-wrap items-center gap-x-3 gap-y-2">
        {plain && e.simplified_by === "ai" && (
          <Badge tone="info" title="Oddiy tildagi matnni AI soddalashtirgan. Rasmiy matn — chapda (lex.uz).">
            AI soddalashtirdi — rasmiy matn yonida
          </Badge>
        )}
        {!e.verified && <Badge tone="unverified">Huquqshunos tekshirmagan</Badge>}
        <span className="source">
          {compact && <>{e.doc.split(" — ")[0]}{ref ? `, ${ref}` : ""} · </>}
          <a href={e.lex_url} target="_blank" rel="noopener noreferrer">lex.uz'da ochish</a>
          {e.retrieved_at && <> · olindi {dmy(e.retrieved_at)}</>}
        </span>
      </footer>
    </article>
  );
}

/**
 * LawView — bir yoki bir nechta abzas.
 * Props: excerpts (tayyor ro'yxat) YOKI ids / category / item (o'zi yuklaydi); compact; lang; limit.
 */
export default function LawView({ excerpts, ids, category, item, compact = false, lang = "uz", limit, emptyText }) {
  const [state, setState] = useState({ loading: !excerpts, items: excerpts || [], error: null });
  const key = excerpts ? null : JSON.stringify({ ids, category, item, lang });

  useEffect(() => {
    if (excerpts) {
      setState({ loading: false, items: excerpts, error: null });
      return undefined;
    }
    let alive = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    featuresApi.excerpts({ ids, category, item, lang }).then((r) => {
      if (!alive) return;
      setState(r.error ? { loading: false, items: [], error: r.error } : { loading: false, items: r.excerpts || [], error: null });
    });
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, excerpts]);

  if (state.loading) {
    return (
      <div className="card p-4 sm:p-5" aria-busy="true">
        <Skeleton className="mb-3 h-4 w-1/3" />
        <Skeleton className="mb-2 h-3 w-full" />
        <Skeleton className="h-3 w-4/5" />
      </div>
    );
  }
  if (state.error) return <p className="alert alert-warn small" role="status">Qonun matnini yuklab bo'lmadi: {state.error}</p>;
  if (!state.items.length) return emptyText ? <p className="muted small">{emptyText}</p> : null;

  const list = limit ? state.items.slice(0, limit) : state.items;
  return (
    <div className={cx("grid", compact ? "gap-3" : "gap-4")}>
      {list.map((e) => <LawExcerpt key={e.id} excerpt={e} compact={compact} lang={lang} />)}
    </div>
  );
}
