// AppealForm — murojaat generatori: qonundagi rekvizitlar → maydonlar → tayyor matn → nusxa olish / PDF (brauzer print).
// Rekvizitlar faqat shu murojaatga tatbiq etiladigan qonundan, lex.uz abzasi bilan (backend: /api/appeal/templates).
import { useEffect, useId, useMemo, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Alert, Badge, Button, Skeleton, toast, spring } from "../ui";
import { featuresApi } from "./api.js";
import { LawExcerpt } from "./LawView.jsx";

const LABELS = {
  individual: { applicant_name: "Familiya, ism, otasining ismi", address: "Yashash joyi (manzil)" },
  legal_entity: { applicant_name: "Yuridik shaxsning to'liq nomi", address: "Joylashgan yeri (pochta manzili)" },
};
const REQUIRED = ["applicant_name", "address", "situation"];

function Field({ id, label, hint, error, children }) {
  return (
    <div>
      <label htmlFor={id} className="small mb-1 block font-semibold" style={{ color: "var(--text-primary)" }}>{label}</label>
      {children}
      {error ? <p className="small mt-1" style={{ color: "var(--danger-ink)" }} role="alert">{error}</p>
        : hint ? <p className="tiny muted mt-1">{hint}</p> : null}
    </div>
  );
}

function escapeHtml(s) {
  return s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

// PDF: brauzerning «Chop etish → PDF sifatida saqlash» oynasi (yashirin iframe — pop-up bloklanmaydi)
function printAsPdf(title, text) {
  const iframe = document.createElement("iframe");
  iframe.setAttribute("aria-hidden", "true");
  Object.assign(iframe.style, { position: "fixed", right: "0", bottom: "0", width: "0", height: "0", border: "0" });
  document.body.appendChild(iframe);
  const doc = iframe.contentDocument;
  doc.open();
  doc.write(`<!doctype html><html lang="uz"><head><meta charset="utf-8"><title>${escapeHtml(title)}</title>
<style>@page{size:A4;margin:22mm 20mm}body{font:12.5pt/1.55 "Times New Roman",Georgia,serif;color:#000;margin:0}
pre{white-space:pre-wrap;font:inherit;margin:0}</style></head><body><pre>${escapeHtml(text)}</pre></body></html>`);
  doc.close();
  const done = () => setTimeout(() => iframe.remove(), 1000);
  iframe.contentWindow.onafterprint = done;
  setTimeout(() => { iframe.contentWindow.focus(); iframe.contentWindow.print(); done(); }, 150);
}

/**
 * Props: cardId?, defaults? {applicant_name, address, contact, region, situation}, onDone?(result)
 */
export default function AppealForm({ cardId: initialCard, defaults = {}, onDone }) {
  const uid = useId();
  const [cards, setCards] = useState(null);
  const [templates, setTemplates] = useState(null);
  const [cardId, setCardId] = useState(initialCard || "");
  const [fields, setFields] = useState({ applicant_name: "", address: "", contact: "", region: "", situation: "", ...defaults });
  const [touched, setTouched] = useState({});
  const [state, setState] = useState({ loading: false, res: null, error: null });
  const [text, setText] = useState("");
  const [openEx, setOpenEx] = useState(null);

  useEffect(() => {
    featuresApi.appealTemplates().then((r) => setTemplates(r.error ? [] : r.templates));
    if (!initialCard) featuresApi.cards().then((r) => setCards(Array.isArray(r) ? r : []));
  }, [initialCard]);

  const tpl = useMemo(() => templates?.find((t) => t.cards.some((c) => c.card_id === cardId)) || null, [templates, cardId]);
  const kind = tpl?.applicant_type === "legal_entity" ? "legal_entity" : "individual";
  const exById = useMemo(() => Object.fromEntries((tpl?.excerpts || []).map((e) => [e.id, e])), [tpl]);
  const errors = Object.fromEntries(REQUIRED.filter((k) => !fields[k]?.trim()).map((k) => [k, "Bu maydon qonun bo'yicha majburiy"]));
  const set = (k) => (e) => setFields((f) => ({ ...f, [k]: e.target.value }));
  const blur = (k) => () => setTouched((t) => ({ ...t, [k]: true }));

  const submit = async (e) => {
    e.preventDefault();
    if (!cardId) return;
    setTouched({ applicant_name: true, address: true, situation: true });
    setState((s) => ({ ...s, loading: true, error: null }));
    const res = await featuresApi.appeal(cardId, fields);
    if (res.error) return setState({ loading: false, res: null, error: res.error });
    setText(res.text);
    setState({ loading: false, res, error: null });
    onDone?.(res);
  };

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      toast("Ariza matni nusxalandi", { tone: "ok" });
    } catch {
      toast("Nusxa olib bo'lmadi — matnni belgilab nusxalang", { tone: "danger" });
    }
  };

  return (
    <div className="grid gap-5">
      {!initialCard && (
        <Field id={`${uid}-topic`} label="Mavzu">
          {cards ? (
            <select id={`${uid}-topic`} value={cardId} onChange={(e) => { setCardId(e.target.value); setState({ loading: false, res: null, error: null }); }} className="w-full">
              <option value="">— Vaziyatingizni tanlang —</option>
              {cards.map((c) => <option key={c.id} value={c.id}>{c.title_uz}</option>)}
            </select>
          ) : <Skeleton className="h-11 w-full" />}
        </Field>
      )}

      {cardId && tpl && (
        <section className="card card-inset p-4" aria-label="Qonun talablari">
          <div className="flex flex-wrap items-baseline gap-2">
            <h3 className="h3">{tpl.title}</h3>
            {kind === "legal_entity" && <Badge tone="info">Yuridik shaxs</Badge>}
          </div>
          {tpl.legal_regime && <p className="source mt-1">Qaysi qonun bo'yicha: {tpl.legal_regime}</p>}
          {tpl.requirements?.length > 0 && (
            <ul className="mt-3 grid gap-2">
              {tpl.requirements.map((r, i) => (
                <li key={i} className="small">
                  <span className="secondary">✓ {r.text}</span>
                  {r.excerpt_id && exById[r.excerpt_id] && (
                    <button type="button" className="link tiny ml-2" aria-expanded={openEx === i}
                      onClick={() => setOpenEx(openEx === i ? null : i)}>
                      {openEx === i ? "yopish" : `qonunda: ${exById[r.excerpt_id].article}`}
                    </button>
                  )}
                  <AnimatePresence initial={false}>
                    {openEx === i && (
                      <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }} transition={spring} style={{ overflow: "hidden" }}>
                        <div className="mt-2"><LawExcerpt excerpt={exById[r.excerpt_id]} compact /></div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </li>
              ))}
            </ul>
          )}
          {tpl.review_term && <p className="small mt-3"><b>Ko'rib chiqish muddati:</b> <span className="secondary">{tpl.review_term}</span></p>}
        </section>
      )}

      {cardId && (
        <form className="grid gap-4" onSubmit={submit} noValidate>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field id={`${uid}-n`} label={LABELS[kind].applicant_name} error={touched.applicant_name && errors.applicant_name}>
              <input id={`${uid}-n`} value={fields.applicant_name} onChange={set("applicant_name")} onBlur={blur("applicant_name")}
                autoComplete={kind === "individual" ? "name" : "organization"} className="w-full" />
            </Field>
            <Field id={`${uid}-a`} label={LABELS[kind].address} error={touched.address && errors.address}>
              <input id={`${uid}-a`} value={fields.address} onChange={set("address")} onBlur={blur("address")} autoComplete="street-address" className="w-full" />
            </Field>
            <Field id={`${uid}-c`} label="Aloqa (telefon yoki e-pochta)" hint="Ixtiyoriy — javob tezroq kelishi uchun">
              <input id={`${uid}-c`} value={fields.contact} onChange={set("contact")} className="w-full" />
            </Field>
            {kind === "individual" && (
              <Field id={`${uid}-r`} label="Hudud" hint="Masalan: Samarqand viloyati">
                <input id={`${uid}-r`} value={fields.region} onChange={set("region")} className="w-full" />
              </Field>
            )}
          </div>
          <Field id={`${uid}-s`} label="Vaziyat: nima bo'ldi va nima so'rayapsiz" error={touched.situation && errors.situation}
            hint="Qachon, qaysi organ, qaysi qaror. Faktlarni yozing — huquqiy asosni biz qo'shamiz.">
            <textarea id={`${uid}-s`} rows={4} value={fields.situation} onChange={set("situation")} onBlur={blur("situation")} className="w-full resize-y" />
          </Field>
          <p className="tiny muted">Ma'lumotlaringiz saqlanmaydi — faqat ariza matniga qo'yiladi. Imzoni qog'ozda o'zingiz qo'yasiz.</p>
          <div className="flex flex-wrap gap-2">
            <Button type="submit" variant="primary" loading={state.loading} icon="📝">Ariza matnini tayyorlash</Button>
          </div>
        </form>
      )}

      {state.error && <Alert tone="warn" title="Ariza tayyorlanmadi">{state.error}</Alert>}

      <AnimatePresence initial={false}>
        {state.res && (
          <motion.section key="result" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            transition={spring} className="card p-4 sm:p-5" aria-label="Tayyor ariza">
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <h3 className="h3 flex-1">Tayyor matn</h3>
              <Badge tone="unverified">Huquqshunos tekshirmagan</Badge>
            </div>
            {state.res.missing_fields?.length > 0 && (
              <Alert tone="info" className="mb-3">Qavs ichidagi [ ] joylarni to'ldiring — ular qonun bo'yicha majburiy rekvizitlar.</Alert>
            )}
            <label htmlFor={`${uid}-out`} className="sr-only">Ariza matni (tahrirlash mumkin)</label>
            <textarea id={`${uid}-out`} value={text} onChange={(e) => setText(e.target.value)} rows={16}
              className="law w-full resize-y text-[0.95rem]" spellCheck={false} />
            <div className="mt-3 flex flex-wrap gap-2">
              <Button variant="primary" icon="📋" onClick={copy}>Nusxa olish</Button>
              <Button icon="🖨️" onClick={() => printAsPdf(state.res.title || "Ariza", text)}>PDF / chop etish</Button>
            </div>
            {state.res.submit_channels?.length > 0 && (
              <p className="source mt-3">
                Qayerga topshirish:{" "}
                {state.res.submit_channels.map((s, i) => (
                  <span key={s.name}>{i > 0 && "; "}{s.url ? <a href={s.url} target="_blank" rel="noopener noreferrer">{s.name}</a> : s.name}</span>
                ))}
              </p>
            )}
            {state.res.checklist?.length > 0 && (
              <details className="mt-3">
                <summary className="small cursor-pointer font-semibold">Topshirishdan oldin tekshiring</summary>
                <ul className="small secondary mt-2 list-disc pl-5">
                  {state.res.checklist.map((c) => <li key={c}>{c}</li>)}
                </ul>
              </details>
            )}
          </motion.section>
        )}
      </AnimatePresence>
    </div>
  );
}
